from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import telegram
from .models import Notification


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)[:50]
        return Response([{"id": n.id, "kind": n.kind, "title": n.title, "body": n.body, "read": n.read, "created_at": n.created_at} for n in qs])


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        Notification.objects.filter(pk=pk, user=request.user).update(read=True)
        return Response({"ok": True})


class TelegramWebhookView(APIView):
    """Webhook Telegram : `/start <code>` lie le compte, `/stop` le désinscrit.

    `X-Telegram-Bot-Api-Secret-Token` est comparé à `TELEGRAM_WEBHOOK_SECRET`.
    Telegram réessaie tant qu'il ne reçoit pas 200 : on répond toujours 200 hors secret.
    """

    authentication_classes: list = []
    permission_classes: list = []
    throttle_classes: list = []  # Telegram réessaie : ne jamais lui répondre 429

    def get(self, request):
        return Response({"ok": True, "provider": "telegram", "available": telegram.configured()})

    def post(self, request):
        if not telegram.verify_secret(request.headers.get("X-Telegram-Bot-Api-Secret-Token")):
            return Response({"detail": "Secret invalide."}, status=403)
        stats = telegram.handle_update(request.data or {})
        return Response({"ok": True, **stats}, status=200)
