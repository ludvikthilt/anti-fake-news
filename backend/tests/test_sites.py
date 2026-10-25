"""Reconnaissance automatique d'un site fiable : quotas système + insiders distincts."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.analyses.models import Analysis, Certification
from apps.knowledge import sites
from apps.knowledge.models import SiteProfile


@pytest.fixture
def api():
    return APIClient()


def make_user(email, role="insider"):
    return User.objects.create_user(email=email, password="pass12345", role=role)


def make_site(domain="exemple.cm", validations=0):
    return SiteProfile.objects.create(
        domain=domain, name="Exemple", nature="media", score=80, system_validations=validations
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
def test_one_insider_never_certifies_a_site(settings):
    # Même avec un quota mal configuré, une lecture isolée ne suffit jamais.
    settings.SITE_SYSTEM_QUOTA = 1
    settings.SITE_INSIDER_QUOTA = 1
    site = make_site(validations=50)
    certify(site.domain, make_user("seul@test.fr"))

    state = sites.evaluate(site)
    site.refresh_from_db()
    assert state["insider_quota"] == 2
    assert site.certified is False
    assert site.certified_at is None


@pytest.mark.django_db
def test_quotas_must_all_be_reached(settings):
    settings.SITE_SYSTEM_QUOTA = 2
    settings.SITE_INSIDER_QUOTA = 2
    site = make_site(validations=1)
    certify(site.domain, make_user("un@test.fr"))
    certify(site.domain, make_user("deux@test.fr"))

    # Assez d'insiders, pas assez de corroborations système.
    assert sites.evaluate(site)["certified"] is False

    site.system_validations = 2
    site.save(update_fields=["system_validations"])
    assert sites.evaluate(site)["certified"] is True
    site.refresh_from_db()
    assert site.certified is True
    assert site.certified_at is not None


@pytest.mark.django_db
def test_contest_can_withdraw_recognition(settings):
    settings.SITE_SYSTEM_QUOTA = 1
    settings.SITE_INSIDER_QUOTA = 3
    site = make_site(validations=5)
    for i in range(3):
        certify(site.domain, make_user(f"p{i}@test.fr"))
    assert sites.evaluate(site)["certified"] is True

    certify(site.domain, make_user("contre@test.fr"), verdict="contest", proposed="contredite")
    state = sites.evaluate(site)
    site.refresh_from_db()
    assert state["insider_net"] == 2
    assert state["certified"] is False
    assert site.certified is False
    assert site.certified_at is None


@pytest.mark.django_db
def test_proposed_status_counts_in_the_process(settings):
    settings.SITE_SYSTEM_QUOTA = 1
    settings.SITE_INSIDER_QUOTA = 2
    site = make_site(validations=1)
    first = make_user("nuance@test.fr")
    second = make_user("clair@test.fr")
    certify(site.domain, first, proposed="non_corroboree")
    certify(site.domain, second, proposed="corroboree")

    state = sites.evaluate(site)
    assert state["insider_net"] == 1  # certifier sans corroborer ne valide pas
    assert state["certified"] is False

    reading = Certification.objects.get(user=first, target_type="site")
    reading.proposed_status = "corroboree"
    reading.save(update_fields=["proposed_status"])
    assert sites.evaluate(site)["certified"] is True


@pytest.mark.django_db
def test_system_corroborations_advance_the_site(settings):
    settings.SITE_SYSTEM_QUOTA = 2
    settings.SITE_INSIDER_QUOTA = 2
    site = make_site(validations=0)
    certify(site.domain, make_user("un@test.fr"))
    certify(site.domain, make_user("deux@test.fr"))

    assert sites.record_corroborations([site.domain, site.domain]) == []
    site.refresh_from_db()
    assert site.system_validations == 1
    assert site.certified is False

    assert sites.record_corroborations([site.domain]) == [site.domain]
    site.refresh_from_db()
    assert site.system_validations == 2
    assert site.certified is True


@pytest.mark.django_db
def test_same_analysis_counts_once(settings):
    settings.SITE_SYSTEM_QUOTA = 2
    site = make_site(validations=0)
    first = Analysis.objects.create(input_type=Analysis.InputType.TEXT, input_text="a")
    second = Analysis.objects.create(input_type=Analysis.InputType.TEXT, input_text="b")

    sites.record_corroborations([site.domain], analysis=first)
    sites.record_corroborations([site.domain], analysis=first)
    site.refresh_from_db()
    assert site.system_validations == 1

    sites.record_corroborations([site.domain], analysis=second)
    site.refresh_from_db()
    assert site.system_validations == 2


@pytest.mark.django_db
def test_certified_site_gains_reliability_bonus(settings):
    settings.SITE_CERTIFY_BONUS = 10
    site = make_site(domain="bonus.cm", validations=0)
    assert sites.site_score("bonus.cm", 80) == 80

    site.certified = True
    site.save(update_fields=["certified"])
    assert sites.site_score("bonus.cm", 80) == 90
    assert sites.site_score("inconnu.cm", 80) == 80


@pytest.mark.django_db
def test_api_site_reading_updates_recognition(api, settings):
    settings.SITE_SYSTEM_QUOTA = 1
    settings.SITE_INSIDER_QUOTA = 2
    site = make_site(validations=1)
    first = make_user("insider1@test.fr")
    second = make_user("insider2@test.fr")
    payload = {
        "target_type": "site",
        "target_id": site.domain,
        "verdict": "certify",
        "proposed_status": "corroboree",
        "comment": "Site institutionnel, sources citées.",
        "source_url": "https://exemple.fr/preuve",
    }

    api.force_authenticate(first)
    assert api.post("/api/certifications/", payload, format="json").status_code == 201
    site.refresh_from_db()
    assert site.certified is False  # un seul insider : jamais suffisant

    api.force_authenticate(second)
    assert api.post("/api/certifications/", payload, format="json").status_code == 201
    site.refresh_from_db()
    assert site.certified is True

    # Le retrait d'une lecture peut retirer la reconnaissance.
    reading = Certification.objects.get(user=second, target_type="site")
    assert api.delete(f"/api/certifications/{reading.id}/").status_code == 204
    site.refresh_from_db()
    assert site.certified is False


@pytest.mark.django_db
def test_site_reading_requires_insider_and_known_site(api):
    user = make_user("user@test.fr", role="user")
    api.force_authenticate(user)
    payload = {
        "target_type": "site",
        "target_id": "exemple.cm",
        "verdict": "certify",
        "source_url": "https://exemple.fr",
    }
    assert api.post("/api/certifications/", payload, format="json").status_code == 403

    insider = make_user("insider@test.fr")
    api.force_authenticate(insider)
    payload["target_id"] = "absent.cm"
    assert api.post("/api/certifications/", payload, format="json").status_code == 404


@pytest.mark.django_db
def test_site_api_exposes_progress(api, settings):
    settings.SITE_SYSTEM_QUOTA = 2
    settings.SITE_INSIDER_QUOTA = 2
    site = make_site(validations=1)
    certify(site.domain, make_user("un@test.fr"))

    data = api.get(f"/api/sites/{site.domain}/").json()
    assert data["system_validations"] == 1
    assert data["system_quota"] == 2
    assert data["system_remaining"] == 1
    assert data["insider_certifications"] == 1
    assert data["insider_quota"] == 2
    assert data["insider_remaining"] == 1
    assert data["certified"] is False
