"""Telegram Bot API — canal gratuit et illimité (M12).

Aucun numéro de téléphone, aucun modèle à faire approuver, aucune facturation : le bot
répond à l'utilisateur qui a ouvert la conversation. C'est le canal instantané gratuit
de la plateforme.

Liaison : la plateforme génère un code court, l'utilisateur ouvre
`https://t.me/<bot>?start=<code>` et envoie le message ; le webhook associe alors le
`chat_id` au compte. C'est l'opt-in explicite du canal.
"""
import hmac
import html
import logging
import secrets
from datetime import timedelta

import httpx
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

API = "https://api.telegram.org"
LINK_CODE_TTL_MINUTES = 30


class NotConfigured(Exception):
    """Bot absent (jeton ou nom d'utilisateur manquant) : simple saut, pas une panne."""


class Blocked(Exception):
    """L'utilisateur a bloqué le bot ou supprimé la conversation."""


def configured() -> bool:
    return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_USERNAME)


def _call(method: str, payload: dict, timeout: float = 12) -> dict:
    if not configured():
        raise NotConfigured("bot Telegram non configuré")
    resp = httpx.post(f"{API}/bot{settings.TELEGRAM_BOT_TOKEN}/{method}", json=payload, timeout=timeout)
    data = resp.json() if resp.content else {}
    if resp.status_code >= 400 or not data.get("ok", False):
        description = str(data.get("description", ""))[:200]
        if resp.status_code == 403 or "blocked" in description.lower() or "chat not found" in description.lower():
            raise Blocked(description or "conversation fermée")
        raise RuntimeError(f"Telegram {resp.status_code} : {description}")
    return data.get("result", {}) or {}


def send(chat_id: int, title: str, body: str, url: str = "") -> str:
    """Message texte HTML. `url` devient un lien « Ouvrir » en fin de message."""
    text = f"<b>{html.escape(title)}</b>\n\n{html.escape(body)}"
    if url:
        text += f'\n\n<a href="{html.escape(url, quote=True)}">Ouvrir</a>'
    _call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
    )
    return "telegram"


def new_link_code(contact) -> str:
    """Code court à usage unique, valable 30 minutes."""
    code = secrets.token_hex(8)  # 16 caractères, acceptés par le start payload Telegram
    contact.link_code = code
    contact.link_code_expires = timezone.now() + timedelta(minutes=LINK_CODE_TTL_MINUTES)
    contact.save(update_fields=["link_code", "link_code_expires"])
    return code


def deep_link(code: str) -> str:
    if not configured():
        return ""
    return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={code}"


def verify_secret(header: str | None) -> bool:
    """Contrôle `X-Telegram-Bot-Api-Secret-Token` (secret posé à `setWebhook`)."""
    expected = settings.TELEGRAM_WEBHOOK_SECRET
    if not expected:
        return True  # dev sans secret : l'URL du webhook reste non devinable
    return bool(header) and hmac.compare_digest(expected, header)


def _reply(chat_id: int, text: str) -> None:
    try:
        _call("sendMessage", {"chat_id": chat_id, "text": text[:4096], "disable_web_page_preview": True})
    except Exception:  # noqa: BLE001 - réponse best-effort
        logger.warning("Réponse Telegram impossible")


def handle_update(update: dict) -> dict:
    """Traite un update Telegram : /start <code> lie le compte, /stop le délie."""
    from apps.accounts.models import ConsentRecord, TelegramContact

    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()
    if not chat_id:
        return {"messages": 0}

    stats = {"messages": 1, "linked": 0, "optout": 0, "inbound": 0}
    command, _, payload = text.partition(" ")
    command = command.strip().lower().split("@")[0]
    payload = payload.strip()

    if command == "/start" and payload:
        candidate = TelegramContact.objects.filter(link_code=payload).first()
        expires = candidate.link_code_expires if candidate else None
        if not candidate or (expires and expires < timezone.now()):
            _reply(chat_id, "Ce code de liaison est invalide ou expiré. Ouvrez « Mon compte » sur la plateforme pour en obtenir un nouveau.")
            return stats
        # un chat ne peut être lié qu'à un seul compte
        TelegramContact.objects.filter(chat_id=chat_id).exclude(pk=candidate.pk).update(
            chat_id=None, verified=False
        )
        candidate.chat_id = chat_id
        candidate.username = (chat.get("username") or chat.get("first_name") or "")[:64]
        candidate.verified = True
        candidate.opted_out = False
        candidate.link_code = None
        candidate.link_code_expires = None
        candidate.save()
        ConsentRecord.objects.update_or_create(
            user=candidate.user,
            key="notif_telegram",
            defaults={"granted": True, "granted_at": timezone.now(), "withdrawn_at": None},
        )
        stats["linked"] = 1
        _reply(
            chat_id,
            "Compte lié. Vous recevrez ici le résultat de vos analyses et les campagnes de "
            "sensibilisation. Envoyez /stop pour ne plus rien recevoir.",
        )
        return stats

    contact = TelegramContact.objects.filter(chat_id=chat_id, verified=True).first()
    if not contact:
        _reply(chat_id, "Ce compte n'est pas encore lié. Ouvrez « Mon compte » sur la plateforme et suivez le lien Telegram.")
        return stats

    contact.last_inbound_at = timezone.now()
    contact.save(update_fields=["last_inbound_at"])
    stats["inbound"] = 1

    if command in {"/stop", "stop", "arrêt", "arret", "désabonner", "desabonner"}:
        contact.opted_out = True
        contact.save(update_fields=["opted_out"])
        ConsentRecord.objects.filter(
            user=contact.user, key__in=["notif_telegram", "awareness_telegram"]
        ).update(granted=False, withdrawn_at=timezone.now())
        stats["optout"] = 1
        _reply(chat_id, "Vous ne recevrez plus de messages. Envoyez /start avec un nouveau code pour réactiver.")
    elif command in {"/aide", "/help", "aide", "help"}:
        _reply(chat_id, "Plateforme anti-fake news : analyses et campagnes d'éducation aux médias. Envoyez /stop pour vous désinscrire.")
    return stats
