"""Canaux gratuits : Telegram (bot) et Web Push (VAPID)."""
import base64

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import ConsentRecord, PushSubscription, TelegramContact, User
from apps.notifications import push, telegram
from apps.notifications.models import AwarenessCampaign
from apps.notifications.services import notify_analysis_done, send_campaign


def _telegram_settings(settings):
    settings.TELEGRAM_BOT_TOKEN = "123:abc"
    settings.TELEGRAM_BOT_USERNAME = "antifake_bot"
    settings.TELEGRAM_WEBHOOK_SECRET = "secret-tg"


def test_telegram_send_payload(monkeypatch, settings):
    _telegram_settings(settings)
    calls = []

    class Resp:
        status_code = 200
        content = b'{"ok":true,"result":{"message_id":1}}'

        def json(self):
            return {"ok": True, "result": {"message_id": 1}}

    def fake_post(url, json=None, timeout=12):
        calls.append((url, json))
        return Resp()

    monkeypatch.setattr(telegram.httpx, "post", fake_post)
    assert telegram.send(42, "Analyse terminée", "Corroborée", "https://x/analyses/1") == "telegram"

    url, payload = calls[0]
    assert url == "https://api.telegram.org/bot123:abc/sendMessage"
    assert payload["chat_id"] == 42
    assert payload["parse_mode"] == "HTML"
    assert "<b>Analyse terminée</b>" in payload["text"]
    assert "https://x/analyses/1" in payload["text"]


def test_telegram_requires_configuration(settings):
    settings.TELEGRAM_BOT_TOKEN = ""
    settings.TELEGRAM_BOT_USERNAME = ""
    assert telegram.configured() is False
    with pytest.raises(telegram.NotConfigured):
        telegram.send(1, "titre", "corps")


@pytest.mark.django_db
def test_telegram_start_links_account(monkeypatch, settings):
    _telegram_settings(settings)
    monkeypatch.setattr(telegram, "_reply", lambda *args: None)
    user = User.objects.create_user(email="tg@test.fr", password="pass12345")
    contact = TelegramContact.objects.create(user=user, link_code="abc123def456")

    stats = telegram.handle_update(
        {"message": {"chat": {"id": 777, "username": "lud"}, "text": "/start abc123def456"}}
    )
    contact.refresh_from_db()
    assert stats["linked"] == 1
    assert contact.chat_id == 777
    assert contact.verified is True
    assert contact.link_code is None
    assert ConsentRecord.objects.get(user=user, key="notif_telegram").granted is True


@pytest.mark.django_db
def test_telegram_start_rejects_unknown_code(monkeypatch, settings):
    _telegram_settings(settings)
    monkeypatch.setattr(telegram, "_reply", lambda *args: None)
    stats = telegram.handle_update({"message": {"chat": {"id": 1}, "text": "/start inconnu"}})
    assert stats["linked"] == 0
    assert not TelegramContact.objects.exists()


@pytest.mark.django_db
def test_telegram_stop_opts_out(monkeypatch, settings):
    _telegram_settings(settings)
    monkeypatch.setattr(telegram, "_reply", lambda *args: None)
    user = User.objects.create_user(email="stop-tg@test.fr", password="pass12345")
    TelegramContact.objects.create(user=user, chat_id=99, verified=True)
    ConsentRecord.objects.create(user=user, key="notif_telegram", granted=True)

    stats = telegram.handle_update({"message": {"chat": {"id": 99}, "text": "/stop"}})
    assert stats["optout"] == 1
    assert TelegramContact.objects.get(user=user).opted_out is True
    assert ConsentRecord.objects.get(user=user, key="notif_telegram").granted is False


@pytest.mark.django_db
def test_telegram_endpoint_issues_deep_link(settings):
    _telegram_settings(settings)
    user = User.objects.create_user(email="link@test.fr", password="pass12345")
    api = APIClient()
    api.force_authenticate(user)

    refused = api.post("/api/auth/me/telegram/", {"consent": False}, format="json")
    assert refused.status_code == 400

    resp = api.post("/api/auth/me/telegram/", {"consent": True}, format="json")
    assert resp.status_code == 201
    assert resp.json()["deep_link"].startswith("https://t.me/antifake_bot?start=")

    status = api.get("/api/auth/me/telegram/")
    assert status.json()["available"] is True
    assert status.json()["registered"] is False


def test_telegram_webhook_rejects_bad_secret(settings):
    _telegram_settings(settings)
    api = APIClient()
    ok = api.post("/api/webhooks/telegram/", {"message": {}}, format="json")
    assert ok.status_code == 403
    wrong = api.post(
        "/api/webhooks/telegram/", {"message": {}}, format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="faux"
    )
    assert wrong.status_code == 403
    good = api.post(
        "/api/webhooks/telegram/",
        {"message": {}},
        format="json",
        HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="secret-tg",
    )
    assert good.status_code == 200


# ------------------------------------------------------------------ Web Push


def _vapid(settings):
    raw = bytes(range(32))
    settings.VAPID_PRIVATE_KEY = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    settings.VAPID_SUBJECT = "mailto:test@example.org"


def test_push_public_key_is_derived(settings):
    _vapid(settings)
    key = push.public_key()
    assert push.configured() is True
    assert len(key) == 87
    assert "=" not in key
    decoded = base64.urlsafe_b64decode(key + "=" * (-len(key) % 4))
    assert decoded[0] == 4  # point non compressé
    assert len(decoded) == 65


def test_push_requires_configuration(settings):
    settings.VAPID_PRIVATE_KEY = ""
    assert push.configured() is False
    with pytest.raises(push.NotConfigured):
        push.send(object(), "titre", "corps")


@pytest.mark.django_db
@pytest.mark.django_db
def test_push_send_payload(monkeypatch, settings):
    _vapid(settings)
    user = User.objects.create_user(email="push-send@test.fr", password="pass12345")
    subscription = PushSubscription.objects.create(
        user=user, endpoint="https://push.example/abc", p256dh="p256dh-xyz", auth="auth-xyz"
    )
    calls = []

    def fake_webpush(subscription_info=None, data=None, vapid_private_key=None, vapid_claims=None, ttl=0):
        calls.append({"info": subscription_info, "data": data, "claims": vapid_claims, "key": vapid_private_key})

    monkeypatch.setattr("pywebpush.webpush", fake_webpush)
    assert push.send(subscription, "Analyse terminée", "Corroborée", "https://app/analyses/1") == "push"

    call = calls[0]
    assert call["info"]["endpoint"] == "https://push.example/abc"
    assert call["info"]["keys"] == {"p256dh": "p256dh-xyz", "auth": "auth-xyz"}
    payload = __import__("json").loads(call["data"])
    assert payload == {"title": "Analyse terminée", "body": "Corroborée", "url": "https://app/analyses/1"}
    assert call["claims"]["sub"] == "mailto:test@example.org"
    subscription.refresh_from_db()
    assert subscription.last_ok_at is not None


@pytest.mark.django_db
def test_push_subscription_endpoint(settings):
    _vapid(settings)
    user = User.objects.create_user(email="push@test.fr", password="pass12345")
    api = APIClient()
    api.force_authenticate(user)

    incomplete = api.post("/api/auth/me/push/", {"endpoint": "https://push.example/1"}, format="json")
    assert incomplete.status_code == 400

    payload = {
        "endpoint": "https://push.example/1",
        "keys": {"p256dh": "cle-publique", "auth": "secret-auth"},
        "consent": True,
    }
    created = api.post("/api/auth/me/push/", payload, format="json")
    assert created.status_code == 201
    assert PushSubscription.objects.filter(user=user).count() == 1
    assert ConsentRecord.objects.get(user=user, key="notif_push").granted is True

    status = api.get("/api/auth/me/push/")
    assert status.json()["count"] == 1
    assert status.json()["available"] is True
    assert status.json()["public_key"] == push.public_key()

    assert api.delete("/api/auth/me/push/").status_code == 204
    assert PushSubscription.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_analysis_notification_uses_telegram_and_push(monkeypatch):
    from apps.analyses.models import Analysis
    from apps.notifications import services

    user = User.objects.create_user(email="notif2@test.fr", password="pass12345")
    TelegramContact.objects.create(user=user, chat_id=4242, verified=True)
    ConsentRecord.objects.create(user=user, key="notif_telegram", granted=True)
    ConsentRecord.objects.create(user=user, key="notif_push", granted=True)

    sent = []
    monkeypatch.setattr(services, "_send_telegram", lambda u, t, b, url="": sent.append("telegram") or "telegram")
    monkeypatch.setattr(services, "_send_push", lambda u, t, b, url="": sent.append("push") or "push")

    analysis = Analysis.objects.create(input_type="text", input_text="x", result={"status_label": "Corroborée"})
    notify_analysis_done(user, analysis)
    assert sent == ["telegram", "push"]


@pytest.mark.django_db
def test_campaign_telegram_channel(monkeypatch):
    from apps.notifications import services

    user = User.objects.create_user(email="camp-tg@test.fr", password="pass12345")
    TelegramContact.objects.create(user=user, chat_id=555, verified=True)
    ConsentRecord.objects.create(user=user, key="awareness_telegram", granted=True)

    campaign = AwarenessCampaign.objects.create(
        title="Semaine EMI", body="Vérifiez avant de partager.", channel=AwarenessCampaign.Channel.TELEGRAM
    )
    monkeypatch.setattr(services.telegram, "send", lambda chat_id, title, body, url="": "telegram")
    assert send_campaign(campaign) == 1
    campaign.refresh_from_db()
    assert campaign.status == AwarenessCampaign.Status.SENT
