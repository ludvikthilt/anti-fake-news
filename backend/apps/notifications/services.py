"""Notifications multicanal (M7/M12) — dossier technique §10.

En application : toujours. E-mail : Brevo. Telegram : bot gratuit. Web Push : PWA.
Chaque canal a son consentement ; si l'un n'est pas prêt (clé, bot, clés VAPID), on
n'échoue pas : la notification dans l'application et l'e-mail restent la référence.
"""
from django.conf import settings
from django.core.mail import send_mail

from . import brevo, push, telegram
from .models import Notification


def _send_email(to: str, subject: str, html: str) -> str:
    """Envoi e-mail : Brevo (clé configurée) sinon console Django (local)."""
    if brevo.email_configured():
        return brevo.send_email(to, subject, html)
    send_mail(subject, "", settings.EMAIL_FROM, [to], html_message=html, fail_silently=True)
    return "console"


def _send_telegram(user, title: str, body: str, url: str = "") -> str:
    contact = getattr(user, "telegram_contact", None)
    if not contact or not contact.verified or contact.opted_out or not contact.chat_id:
        raise telegram.NotConfigured("compte Telegram non lié")
    return telegram.send(contact.chat_id, title, body, url)


def _send_push(user, title: str, body: str, url: str = "") -> str:
    subscriptions = list(user.push_subscriptions.filter(failed_at__isnull=True)[:20])
    if not subscriptions:
        raise push.NotConfigured("aucun abonnement push")
    sent = 0
    for subscription in subscriptions:
        try:
            if push.send(subscription, title, body, url) == "push":
                sent += 1
        except Exception:  # noqa: BLE001 - un abonnement mort n'arrête pas les autres
            continue
    if not sent:
        raise push.NotConfigured("aucun abonnement push actif")
    return "push"


def consent_ok(user, key: str) -> bool:
    record = user.consents.filter(key=key).first()
    return bool(record and record.granted)


def notify_analysis_done(user, analysis):
    Notification.objects.create(
        user=user,
        kind="analysis_done",
        title="Analyse terminée",
        body=f"Analyse {analysis.public_id} : {analysis.result.get('status_label', '')}. Voir : {settings.FRONTEND_URL}/analyses/{analysis.public_id}",
    )
    if consent_ok(user, "notif_email") and user.email:
        try:
            url = f"{settings.FRONTEND_URL}/analyses/{analysis.public_id}"
            _send_email(
                user.email,
                "Votre analyse est prête",
                f"<p>Statut : <strong>{analysis.result.get('status_label', '')}</strong>.</p>"
                f"<p>Voir le résultat : <a href=\"{url}\">{url}</a></p>",
            )
        except Exception:  # noqa: BLE001 - e-mail best-effort, l'in-app reste
            pass

    url = f"{settings.FRONTEND_URL}/analyses/{analysis.public_id}"
    label = analysis.result.get("status_label", "")
    if consent_ok(user, "notif_telegram"):
        try:
            _send_telegram(user, "Analyse terminée", f"Analyse {analysis.public_id} : {label}.", url)
        except Exception:  # noqa: BLE001
            pass

    if consent_ok(user, "notif_push"):
        try:
            _send_push(user, "Analyse terminée", f"Analyse {analysis.public_id} : {label}.", url)
        except Exception:  # noqa: BLE001
            pass


def send_campaign(campaign, limit: int = 200) -> int:
    """Envoie une campagne approuvée aux utilisateurs consentants (M13)."""
    from apps.accounts.models import PushSubscription, TelegramContact, User

    from .models import AwarenessCampaign

    channel = campaign.channel
    sent = 0

    if channel == AwarenessCampaign.Channel.EMAIL:
        for user in User.objects.filter(is_active=True)[:limit]:
            if consent_ok(user, "awareness_email") and user.email:
                try:
                    _send_email(user.email, campaign.title, campaign.body)
                    sent += 1
                except Exception:  # noqa: BLE001
                    continue

    elif channel == AwarenessCampaign.Channel.TELEGRAM:
        contacts = (
            TelegramContact.objects.filter(verified=True, opted_out=False, user__is_active=True)
            .exclude(chat_id=None)
            .select_related("user")[:limit]
        )
        for contact in contacts:
            if not consent_ok(contact.user, "awareness_telegram"):
                continue
            try:
                telegram.send(
                    contact.chat_id,
                    campaign.title,
                    campaign.body,
                    f"{settings.FRONTEND_URL}/comment-ca-marche",
                )
                sent += 1
            except Exception:  # noqa: BLE001
                continue

    elif channel == AwarenessCampaign.Channel.PUSH:
        subscriptions = (
            PushSubscription.objects.filter(failed_at__isnull=True, user__is_active=True)
            .select_related("user")[: limit * 2]
        )
        for subscription in subscriptions:
            if not consent_ok(subscription.user, "awareness_push"):
                continue
            try:
                if push.send(subscription, campaign.title, campaign.body, f"{settings.FRONTEND_URL}/") == "push":
                    sent += 1
            except Exception:  # noqa: BLE001
                continue

    campaign.status = AwarenessCampaign.Status.SENT
    campaign.save(update_fields=["status"])
    return sent
