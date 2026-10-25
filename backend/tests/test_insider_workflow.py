"""Parcours insider : statuer sur une information, proposer une fiche, valider côté admin."""

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.analyses.models import Analysis, Certification
from apps.core.models import QuotaUsage
from apps.knowledge.models import WikiPage


@pytest.fixture
def api():
    return APIClient()


def make_user(email, role):
    return User.objects.create_user(email=email, password="pass12345", role=role)


def make_analysis():
    """Dossier déjà analysé, avec deux sources fiables et aucune contradiction."""
    return Analysis.objects.create(
        input_type=Analysis.InputType.TEXT,
        input_text="Le stade a été inauguré en 2024",
        status=Analysis.Status.DONE,
        result={
            "status": "corroboree",
            "status_label": "Corroborée",
            "status_phrase": "…",
            "sources": [
                {"domain": "a.cm", "score": 85, "url": "https://a.cm/x", "title": "A", "excerpt": "", "type": "media", "position": "corroborates", "date": None, "date_origin": "", "found_by": ""},
                {"domain": "b.cm", "score": 80, "url": "https://b.cm/x", "title": "B", "excerpt": "", "type": "media", "position": "corroborates", "date": None, "date_origin": "", "found_by": ""},
            ],
            "factchecks": [],
            "certifications": [],
            "criteria": [
                {"key": "certifications", "label": "Certifications des insiders", "value": "0 avis (certifie/conteste)", "ok": False, "explanation": ""}
            ],
            "missing": [],
            "created_at": timezone.now().isoformat(),
        },
    )


def reading_payload(analysis, **overrides):
    payload = {
        "target_type": "analysis",
        "target_id": str(analysis.id),
        "verdict": "certify",
        "proposed_status": "corroboree",
        "comment": "Sources concordantes.",
        "source_url": "https://exemple.fr/article",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_insider_reading_is_updated_not_duplicated(api):
    insider = make_user("insider@test.fr", "insider")
    analysis = make_analysis()
    api.force_authenticate(insider)

    first = api.post("/api/certifications/", reading_payload(analysis), format="json")
    assert first.status_code == 201

    second = api.post(
        "/api/certifications/",
        reading_payload(analysis, verdict="contest", proposed_status="contredite"),
        format="json",
    )
    assert second.status_code == 200
    assert Certification.objects.filter(user=insider, target_type="analysis").count() == 1
    reading = Certification.objects.get(user=insider)
    assert reading.verdict == "contest"
    assert reading.proposed_status == "contredite"
    assert reading.updated_at is not None


@pytest.mark.django_db
def test_readings_change_proposed_status(api):
    analysis = make_analysis()
    first = make_user("insider1@test.fr", "insider")
    second = make_user("insider2@test.fr", "insider")

    api.force_authenticate(first)
    assert api.post("/api/certifications/", reading_payload(analysis, verdict="contest"), format="json").status_code == 201
    analysis.refresh_from_db()
    assert analysis.result["status"] == "contredite"

    api.force_authenticate(second)
    assert api.post("/api/certifications/", reading_payload(analysis, verdict="certify"), format="json").status_code == 201
    analysis.refresh_from_db()
    # Un désaccord entre insiders ne tranche pas : les deux sources fiables reprennent l'information.
    assert analysis.result["status"] == "corroboree"
    assert len(analysis.result["certifications"]) == 2


@pytest.mark.django_db
def test_insider_can_retract_own_reading(api):
    insider = make_user("insider@test.fr", "insider")
    analysis = make_analysis()
    api.force_authenticate(insider)
    created = api.post("/api/certifications/", reading_payload(analysis), format="json").json()

    assert api.delete(f"/api/certifications/{created['id']}/").status_code == 204
    assert not Certification.objects.filter(id=created["id"]).exists()


@pytest.mark.django_db
def test_admin_withdrawal_recomputes_status(api):
    insider = make_user("insider@test.fr", "insider")
    admin = make_user("admin@test.fr", "admin")
    analysis = make_analysis()
    api.force_authenticate(insider)
    created = api.post(
        "/api/certifications/", reading_payload(analysis, verdict="contest"), format="json"
    ).json()
    analysis.refresh_from_db()
    assert analysis.result["status"] == "contredite"

    api.force_authenticate(admin)
    listed = api.get("/api/admin/certifications/").json()
    assert listed[0]["target_label"] == f"Dossier #{analysis.public_id}"
    assert listed[0]["target_url"] == f"/analyses/{analysis.public_id}"
    assert api.post(f"/api/admin/certifications/{created['id']}/withdraw/", {}, format="json").status_code == 200
    analysis.refresh_from_db()
    assert analysis.result["status"] == "corroboree"
    assert analysis.result["certifications"] == []


@pytest.mark.django_db
def test_wiki_proposal_waits_for_admin_validation(api):
    insider = make_user("insider@test.fr", "insider")
    admin = make_user("admin@test.fr", "admin")
    api.force_authenticate(insider)

    created = api.post(
        "/api/wiki/pages/",
        {"title": "Reconnaître une image recyclée", "content": "## Méthode\n\n- vérifier la date"},
        format="json",
    )
    assert created.status_code == 201
    page = WikiPage.objects.get(slug=created.json()["slug"])
    assert page.published is False
    assert page.review_status == WikiPage.ReviewStatus.PENDING

    # Invisible dans le wiki public tant qu'elle n'est pas validée.
    assert api.get("/api/wiki/pages/").json() == []

    api.force_authenticate(admin)
    pending = api.get("/api/admin/wiki/pending/")
    assert pending.status_code == 200
    assert [p["slug"] for p in pending.json()] == [page.slug]

    approved = api.post(f"/api/admin/wiki/{page.slug}/review/", {"decision": "approve"}, format="json")
    assert approved.status_code == 200
    page.refresh_from_db()
    assert page.published is True
    assert page.review_status == WikiPage.ReviewStatus.APPROVED

    api.force_authenticate(None)
    assert [p["slug"] for p in api.get("/api/wiki/pages/").json()] == [page.slug]


@pytest.mark.django_db
def test_wiki_pending_list_is_admin_only(api):
    insider = make_user("insider@test.fr", "insider")
    api.force_authenticate(insider)
    assert api.get("/api/admin/wiki/pending/").status_code == 403


@pytest.mark.django_db
def test_admin_stats_expose_remaining_quota(api, settings):
    settings.QUOTA_LIMITS = {"tavily": 1000}
    QuotaUsage.objects.create(account="tavily", period=timezone.now().strftime("%Y-%m"), used=120, limit=1000)
    admin = make_user("admin@test.fr", "admin")
    api.force_authenticate(admin)

    stats = api.get("/api/admin/stats/").json()
    row = next(q for q in stats["quotas"] if q["account"] == "tavily")
    assert row["used"] == 120
    assert row["limit"] == 1000
    assert row["remaining"] == 880
    assert row["percent"] == 12


@pytest.mark.django_db
def test_insider_workspace_lists_queue_and_pages(api):
    insider = make_user("insider@test.fr", "insider")
    analysis = make_analysis()
    WikiPage.objects.create(author=insider, title="Fiche en attente")
    api.force_authenticate(insider)

    data = api.get("/api/insider/workspace/").json()
    assert data["role"] == "insider"
    assert [p["title"] for p in data["wiki_pages"]] == ["Fiche en attente"]
    assert [q["public_id"] for q in data["to_review"]] == [analysis.public_id]
    assert data["counts"]["pending_wiki"] == 1


@pytest.mark.django_db
def test_workspace_rejects_regular_users(api):
    user = make_user("user@test.fr", "user")
    api.force_authenticate(user)
    assert api.get("/api/insider/workspace/").status_code == 403
