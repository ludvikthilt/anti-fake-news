"""Administration des sites (reconnaissance) + seeder de démonstration."""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import ConsentRecord, TelegramContact, User
from apps.analyses.models import Analysis, Certification
from apps.core.models import AuditLog, QuotaUsage
from apps.knowledge import sites
from apps.knowledge.models import KnowledgeChunk, SiteProfile, WikiPage


@pytest.fixture
def api():
    return APIClient()


def make_admin():
    return User.objects.create_user(email="admin@test.fr", password="pass12345", role="admin")


def make_site(domain="exemple.cm", validations=0, certified=False):
    return SiteProfile.objects.create(
        domain=domain, name="Exemple", nature="media", score=80,
        system_validations=validations, certified=certified,
    )


def certify(domain, user, verdict="certify", proposed="corroboree"):
    return Certification.objects.create(
        user=user,
        target_type=Certification.TargetType.SITE,
        target_id=domain,
        verdict=verdict,
        proposed_status=proposed,
        source_url="https://exemple.fr/preuve",
    )


@pytest.mark.django_db
def test_sites_list_requires_admin(api):
    user = User.objects.create_user(email="user@test.fr", password="pass12345", role="user")
    api.force_authenticate(user)
    assert api.get("/api/admin/sites/").status_code == 403

    api.force_authenticate(make_admin())
    assert api.get("/api/admin/sites/").status_code == 200


@pytest.mark.django_db
def test_sites_list_shows_near_certified_progress(settings):
    settings.SITE_SYSTEM_QUOTA = 5
    settings.SITE_INSIDER_QUOTA = 3
    admin = make_admin()

    near = make_site(domain="proche.cm", validations=4)
    certify("proche.cm", User.objects.create_user(email="un@test.fr", password="pass12345", role="insider"))
    certify("proche.cm", User.objects.create_user(email="deux@test.fr", password="pass12345", role="insider"))

    certified = make_site(domain="sur.cm", validations=5, certified=True)
    for i in range(3):
        certify(
            "sur.cm",
            User.objects.create_user(email=f"c{i}@test.fr", password="pass12345", role="insider"),
        )
    make_site(domain="neuf.cm", validations=0)

    api = APIClient()
    api.force_authenticate(admin)
    data = api.get("/api/admin/sites/").json()

    assert data["system_quota"] == 5
    assert data["insider_quota"] == 3
    assert data["near"] == 1
    assert data["certified"] == 1

    rows = {row["domain"]: row for row in data["sites"]}
    assert rows["proche.cm"]["near"] is True
    assert rows["proche.cm"]["system_validations"] == 4
    assert rows["proche.cm"]["insider_net"] == 2
    assert rows["proche.cm"]["progress"] == 75  # (4/5 + 2/3) / (5 + 3)
    assert rows["proche.cm"]["readings"] == 2
    assert rows["sur.cm"]["certified"] is True
    assert rows["neuf.cm"]["near"] is False
    # Certifiés d'abord, quasi-certifiés ensuite, sites sans progression à la fin.
    order = [row["domain"] for row in data["sites"]]
    assert order.index("sur.cm") < order.index("proche.cm") < order.index("neuf.cm")


@pytest.mark.django_db
def test_admin_can_revoke_and_restore_recognition(api, settings):
    settings.SITE_SYSTEM_QUOTA = 1
    settings.SITE_INSIDER_QUOTA = 2
    admin = make_admin()
    site = make_site(domain="retirable.cm", validations=5, certified=True)
    certify("retirable.cm", User.objects.create_user(email="i1@test.fr", password="pass12345", role="insider"))
    certify("retirable.cm", User.objects.create_user(email="i2@test.fr", password="pass12345", role="insider"))
    api.force_authenticate(admin)

    res = api.post("/api/admin/sites/retirable.cm/revoke/", {"reason": "Signalements répétés"}, format="json")
    assert res.status_code == 200
    site.refresh_from_db()
    assert site.certified is False
    assert site.recognition_revoked is True
    assert site.revoked_reason == "Signalements répétés"
    assert AuditLog.objects.filter(action="site_recognition_revoke", target="retirable.cm").exists()

    # Les quotas restent atteints mais la reconnaissance reste retirée.
    assert sites.evaluate(site)["certified"] is False
    state = api.get("/api/admin/sites/").json()
    revoked = next(row for row in state["sites"] if row["domain"] == "retirable.cm")
    assert revoked["revoked"] is True
    assert revoked["near"] is False

    res = api.post("/api/admin/sites/retirable.cm/restore/", {}, format="json")
    assert res.status_code == 200
    site.refresh_from_db()
    assert site.certified is True
    assert site.recognition_revoked is False
    assert AuditLog.objects.filter(action="site_recognition_restore", target="retirable.cm").exists()


@pytest.mark.django_db
def test_site_recognition_endpoints_edge_cases(api):
    admin = make_admin()
    api.force_authenticate(admin)
    assert api.post("/api/admin/sites/absent.cm/revoke/", {}, format="json").status_code == 404
    make_site(domain="autre.cm")
    assert api.post("/api/admin/sites/autre.cm/pas-une-action/", {}, format="json").status_code == 400

    user = User.objects.create_user(email="user@test.fr", password="pass12345", role="user")
    api.force_authenticate(user)
    assert api.post("/api/admin/sites/autre.cm/revoke/", {}, format="json").status_code == 403


@pytest.mark.django_db
def test_seed_demo_is_complete_and_idempotent(monkeypatch):
    call_command("seed_demo")
    call_command("seed_demo")  # relance : rien ne doit se dupliquer

    # Comptes fictifs, aucun compte Telegram lié, aucun mot de passe utilisable.
    demo_users = User.objects.filter(email__endswith="@example.org")
    assert demo_users.count() == 6
    assert TelegramContact.objects.count() == 0
    assert all(not u.has_usable_local_password for u in demo_users)
    assert ConsentRecord.objects.filter(key="awareness_email", granted=True).count() >= 6
    assert not ConsentRecord.objects.filter(key="notif_telegram").exists()

    # Les quatre statuts sont représentés.
    statuses = {a.result.get("status") for a in Analysis.objects.all()}
    assert {"corroboree", "non_corroboree", "contredite", "indeterminee"} <= statuses
    assert Analysis.objects.filter(input_hash__startswith="seed:").count() == 9
    assert Analysis.objects.filter(status=Analysis.Status.PARTIAL).exists()

    # Corpus RAG alimenté : le chatbot retrouve des passages et des liens.
    # (hors réseau : pas d'appel aux modèles, retrieval plein texte uniquement)
    assert KnowledgeChunk.objects.count() >= 25
    from apps.knowledge import embeddings, services

    monkeypatch.setattr(embeddings, "vector_search", lambda q, k=5: [])
    monkeypatch.setattr(services, "AI_CHAIN", [])
    answer = services.answer("quels sont les quatre statuts d'une information")
    assert answer["answer"]
    assert answer["sources"]

    # Reconnaissance : un site certifié, un quasi-certifié (insuffisant).
    bbc = SiteProfile.objects.get(domain="bbc.com")
    assert bbc.certified is True
    crtv = SiteProfile.objects.get(domain="crtv.cm")
    state = sites.evaluation(crtv)
    assert crtv.certified is False
    assert state["near"] is True
    assert state["system_validations"] < state["system_quota"] or state["insider_net"] < state["insider_quota"]

    # Administration garnie : demandes, fiches, campagnes, quotas, notifications.
    from apps.accounts.models import InsiderRequest
    from apps.notifications.models import AwarenessCampaign, Notification

    assert InsiderRequest.objects.filter(status="pending").count() == 2
    assert WikiPage.objects.filter(review_status="pending").count() == 2
    assert WikiPage.objects.filter(review_status="approved").exists()
    assert AwarenessCampaign.objects.filter(status="approved").exists()
    assert AwarenessCampaign.objects.filter(status="draft").exists()
    assert Notification.objects.filter(read=False).exists()
    period = timezone.now().strftime("%Y-%m")
    assert QuotaUsage.objects.filter(period=period).count() >= 5

    # Lectures d'insiders sur les dossiers et sur les sites.
    assert Certification.objects.filter(target_type="analysis").exists()
    assert Certification.objects.filter(target_type="site").count() >= 5

    # Relance : pas de doublon.
    before = (User.objects.count(), Analysis.objects.count(), Certification.objects.count())
    call_command("seed_demo")
    after = (User.objects.count(), Analysis.objects.count(), Certification.objects.count())
    assert before == after
