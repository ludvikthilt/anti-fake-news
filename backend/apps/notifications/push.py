"""Web Push (VAPID) — canal gratuit pour la PWA installée (M12).

Le navigateur crée un abonnement (endpoint + clés), le serveur le stocke et envoie un
message chiffré. Aucun tiers payant, aucune vérification : c'est le canal le plus
économique, à condition que l'app soit installée (iOS ≥ 16.4).

La clé privée VAPID est stockée en base64url (32 octets) dans `VAPID_PRIVATE_KEY` ;
la clé publique, exigée par le navigateur, est dérivée à la volée.
"""
import base64
import json
import logging

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotConfigured(Exception):
    """Clés VAPID absentes : simple saut, pas une panne."""


def _private_bytes() -> bytes:
    raw = (settings.VAPID_PRIVATE_KEY or "").strip()
    padded = raw + "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(padded)


def _vapid():
    """Objet py_vapid construit depuis la clé brute (pas de fichier PEM à gérer)."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from py_vapid import Vapid

    key = ec.derive_private_key(int.from_bytes(_private_bytes(), "big"), ec.SECP256R1())
    vapid = Vapid()
    vapid.private_key = key
    return vapid


def configured() -> bool:
    return bool(settings.VAPID_PRIVATE_KEY)


def public_key() -> str:
    """Clé publique au format base64url non rembourré (applicationServerKey)."""
    if not configured():
        return ""
    numbers = _vapid().private_key.public_key().public_numbers()
    raw = b"\x04" + numbers.x.to_bytes(32, "big") + numbers.y.to_bytes(32, "big")
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def send(subscription, title: str, body: str, url: str = "") -> str:
    """Envoie une notification. Renvoie `push-gone` si l'abonnement est mort (404/410)."""
    from pywebpush import WebPushException, webpush

    if not configured():
        raise NotConfigured("clés VAPID absentes")
    payload = json.dumps({"title": title, "body": body, "url": url}, ensure_ascii=False)
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
            },
            data=payload,
            vapid_private_key=_vapid(),
            vapid_claims={"sub": settings.VAPID_SUBJECT},
            ttl=3600,
        )
    except WebPushException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status in (404, 410):
            subscription.failed_at = timezone.now()
            subscription.save(update_fields=["failed_at"])
            return "push-gone"
        raise

    subscription.last_ok_at = timezone.now()
    subscription.failed_at = None
    subscription.save(update_fields=["last_ok_at", "failed_at"])
    return "push"
