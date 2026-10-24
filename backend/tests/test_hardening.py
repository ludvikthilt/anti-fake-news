"""Durcissement avant déploiement : débit, cache expirant, bornes d'image, quotas, santé."""
import base64
import io
from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from apps.analyses.models import Analysis
from apps.core.models import AuditLog, QuotaUsage
from apps.core.services import quota


@pytest.fixture(autouse=True)
def _clean_cache():
    cache.clear()
    yield
    cache.clear()


def _png(width: int, height: int) -> str:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), "white").save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ------------------------------------------------------------------ limitation de débit


@pytest.mark.django_db
def test_anonymous_requests_are_throttled_after_sixty():
    client = APIClient()
    codes = [client.get("/api/wiki/pages/", REMOTE_ADDR="10.9.9.1").status_code for _ in range(61)]
    assert codes[:60] == [200] * 60
    assert codes[-1] == 429

    blocked = client.get("/api/wiki/pages/", REMOTE_ADDR="10.9.9.1")
    assert "Trop de requêtes" in blocked.json()["detail"]


@pytest.mark.django_db
def test_throttling_is_per_client_address():
    client = APIClient()
    for _ in range(61):
        client.get("/api/wiki/pages/", REMOTE_ADDR="10.9.9.2")
    assert client.get("/api/wiki/pages/", REMOTE_ADDR="10.9.9.3").status_code == 200


# ------------------------------------------------------------------ cache expirant


@pytest.mark.django_db
def test_fresh_cache_is_reused(monkeypatch):
    from apps.analyses import views

    monkeypatch.setattr(views, "trigger_analysis", lambda analysis_id: None)

    first = APIClient().post("/api/analyses/", {"input_type": "text", "input_text": "Le stade est plein"}, format="json")
    # Le cache ne sert que les analyses terminées.
    Analysis.objects.update(status=Analysis.Status.DONE)
    second = APIClient().post("/api/analyses/", {"input_type": "text", "input_text": "Le stade est plein"}, format="json")

    assert first.status_code == 202
    assert second.status_code == 200
    assert second.json()["public_id"] == first.json()["public_id"]
    assert Analysis.objects.count() == 1


@pytest.mark.django_db
def test_expired_cache_triggers_a_new_analysis(monkeypatch, settings):
    from apps.analyses import views

    monkeypatch.setattr(views, "trigger_analysis", lambda analysis_id: None)
    settings.CACHE_TTL_TEXT_HOURS = 6

    first = APIClient().post("/api/analyses/", {"input_type": "text", "input_text": "Une rumeur ancienne"}, format="json")
    Analysis.objects.update(
        status=Analysis.Status.DONE,
        created_at=timezone.now() - timedelta(hours=7),
    )

    second = APIClient().post("/api/analyses/", {"input_type": "text", "input_text": "Une rumeur ancienne"}, format="json")

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["public_id"] != first.json()["public_id"]
    assert Analysis.objects.count() == 2


# ------------------------------------------------------------------ bornes d'image


@pytest.mark.django_db
def test_oversized_image_is_rejected(monkeypatch):
    from apps.analyses import views

    monkeypatch.setattr(views, "trigger_analysis", lambda analysis_id: None)

    huge_side = APIClient().post(
        "/api/analyses/", {"input_type": "image", "image": _png(4100, 8)}, format="json"
    )
    assert huge_side.status_code == 400
    assert "4 096 px" in str(huge_side.json())

    from apps.analyses import images

    monkeypatch.setattr(images, "MAX_IMAGE_BYTES", 1)
    too_heavy = APIClient().post(
        "/api/analyses/", {"input_type": "image", "image": _png(32, 32)}, format="json"
    )
    assert too_heavy.status_code == 400
    assert "5 Mo" in str(too_heavy.json())


@pytest.mark.django_db
def test_corrupt_image_is_rejected(monkeypatch):
    from apps.analyses import views

    monkeypatch.setattr(views, "trigger_analysis", lambda analysis_id: None)
    bad = "data:image/png;base64," + base64.b64encode(b"pas une image").decode()
    response = APIClient().post("/api/analyses/", {"input_type": "image", "image": bad}, format="json")
    assert response.status_code == 400


def test_valid_image_passes_the_bounds():
    from apps.analyses.images import validate_data_url

    width, height, size = validate_data_url(_png(64, 48))
    assert (width, height) == (64, 48)
    assert size > 0


# ------------------------------------------------------------------ quotas


@pytest.mark.django_db
def test_quota_alerts_once_at_eighty_percent():
    from datetime import date

    period = date.today().strftime("%Y-%m")
    QuotaUsage.objects.create(account="tavily", period=period, limit=10, used=7)

    quota.record("tavily")
    usage = QuotaUsage.objects.get(account="tavily", period=period)
    assert usage.alerted_at is not None
    assert AuditLog.objects.filter(action="quota_80").count() == 1

    quota.record("tavily")
    assert AuditLog.objects.filter(action="quota_80").count() == 1


@pytest.mark.django_db
def test_quota_without_limit_never_alerts():
    quota.record("exa")
    assert AuditLog.objects.filter(action="quota_80").count() == 0


# ------------------------------------------------------------------ santé


@pytest.mark.django_db
def test_health_reports_database_and_cache():
    response = APIClient().get("/api/health/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["cache"] == "ok"
