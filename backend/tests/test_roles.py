import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.analyses.models import Analysis


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def analysis():
    return Analysis.objects.create(input_type=Analysis.InputType.TEXT, input_text="information à vérifier")


def cert_payload(analysis, **overrides):
    payload = {
        "target_type": "analysis",
        "target_id": str(analysis.id),
        "verdict": "certify",
        "comment": "ok",
        "source_url": "https://exemple.fr",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_certification_requires_insider(api, analysis):
    user = User.objects.create_user(email="user@test.fr", password="pass12345", role="user")
    api.force_authenticate(user)
    assert api.post("/api/certifications/", cert_payload(analysis), format="json").status_code == 403


@pytest.mark.django_db
def test_certification_allowed_for_insider(api, analysis):
    user = User.objects.create_user(email="insider@test.fr", password="pass12345", role="insider")
    api.force_authenticate(user)
    assert api.post("/api/certifications/", cert_payload(analysis), format="json").status_code == 201


@pytest.mark.django_db
def test_certification_requires_source(api, analysis):
    user = User.objects.create_user(email="insider2@test.fr", password="pass12345", role="insider")
    api.force_authenticate(user)
    payload = cert_payload(analysis, source_url="")
    assert api.post("/api/certifications/", payload, format="json").status_code == 400


@pytest.mark.django_db
def test_admin_stats_requires_admin(api):
    user = User.objects.create_user(email="user2@test.fr", password="pass12345", role="user")
    api.force_authenticate(user)
    assert api.get("/api/admin/stats/").status_code == 403

    user.role = "admin"
    user.save(update_fields=["role"])
    assert api.get("/api/admin/stats/").status_code == 200


@pytest.mark.django_db
def test_ensure_superuser_creates_configured_account(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "admin@test.fr")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "strong-admin-password")

    call_command("ensure_superuser")

    user = User.objects.get(email="admin@test.fr")
    assert user.is_superuser is True
    assert user.is_staff is True
    assert user.role == "admin"
    assert user.check_password("strong-admin-password")


@pytest.mark.django_db
def test_ensure_superuser_promotes_existing_account(monkeypatch):
    user = User.objects.create_user(email="admin@test.fr", password="old-password", role="user")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", user.email)
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "strong-admin-password")

    call_command("ensure_superuser")

    user.refresh_from_db()
    assert user.is_superuser is True
    assert user.is_staff is True
    assert user.is_active is True
    assert user.is_email_verified is True
    assert user.role == "admin"
    assert user.check_password("strong-admin-password")


@pytest.mark.django_db
def test_ensure_superuser_sets_configured_password_for_existing_admin(monkeypatch):
    user = User.objects.create_superuser(email="admin@test.fr", password="existing-password")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", user.email)
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "strong-admin-password")

    call_command("ensure_superuser")

    user.refresh_from_db()
    assert user.check_password("strong-admin-password")
    assert not user.check_password("existing-password")
