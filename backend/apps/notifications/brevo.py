"""Brevo (M7/M8) — e-mail transactionnel uniquement.

Les canaux instantanés (Telegram, Web Push) ont leurs propres modules.
"""
import httpx
from django.conf import settings

BASE_URL = "https://api.brevo.com/v3"


class NotConfigured(Exception):
    """Canal non configuré : ce n'est pas une panne, on passe au canal suivant."""


def _headers() -> dict:
    return {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
        "accept": "application/json",
    }


def email_configured() -> bool:
    return bool(settings.BREVO_API_KEY)


def send_email(to: str, subject: str, html: str) -> str:
    if not email_configured():
        raise NotConfigured("clé Brevo absente")
    resp = httpx.post(
        f"{BASE_URL}/smtp/email",
        headers=_headers(),
        json={
            "sender": {"name": "Plateforme anti-fake news", "email": settings.EMAIL_FROM},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html,
        },
        timeout=12,
    )
    resp.raise_for_status()
    return "brevo"

