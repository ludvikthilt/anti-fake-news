import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def api():
    return APIClient()


CERT_PAYLOAD = {
    "target_type": "analysis",
    "target_id": "x",
    "verdict": "certify",
    "comment": "ok",
    "source_url": "https://exemple.fr",
}


@pytest.mark.django_db
def test_certification_requires_insider(api):
    user = User.objects.create_user(email="user@test.fr", password="pass12345", role="user")
    api.force_authenticate(user)
    assert api.post("/api/certifications/", CERT_PAYLOAD, format="json").status_code == 403


@pytest.mark.django_db
def test_certification_allowed_for_insider(api):
    user = User.objects.create_user(email="insider@test.fr", password="pass12345", role="insider")
    api.force_authenticate(user)
    assert api.post("/api/certifications/", CERT_PAYLOAD, format="json").status_code == 201


@pytest.mark.django_db
def test_certification_requires_source(api):
    user = User.objects.create_user(email="insider2@test.fr", password="pass12345", role="insider")
    api.force_authenticate(user)
    payload = {**CERT_PAYLOAD, "source_url": ""}
    assert api.post("/api/certifications/", payload, format="json").status_code == 400


@pytest.mark.django_db
def test_admin_stats_requires_admin(api):
    user = User.objects.create_user(email="user2@test.fr", password="pass12345", role="user")
    api.force_authenticate(user)
    assert api.get("/api/admin/stats/").status_code == 403

    user.role = "admin"
    user.save(update_fields=["role"])
    assert api.get("/api/admin/stats/").status_code == 200
