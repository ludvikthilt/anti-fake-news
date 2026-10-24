from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.throttling import AuthThrottle, RegisterThrottle
from apps.notifications import push, telegram

from . import services
from .models import (
    ConsentRecord,
    InsiderRequest,
    PushSubscription,
    SocialIdentity,
    TelegramContact,
    User,
)
from .serializers import (
    ConsentRecordSerializer,
    GoogleAuthSerializer,
    InsiderRequestSerializer,
    LoginSerializer,
    RegisterSerializer,
    SocialIdentitySerializer,
    UserSerializer,
)


def _tokens_for(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh), "user": UserSerializer(user).data}


class RegisterView(APIView):
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(_tokens_for(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(_tokens_for(serializer.validated_data["user"]))


class GoogleAuthView(APIView):
    """POST /auth/google/ : échange le code, valide l'ID token, applique les règles de liaison (§9.4)."""

    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            tokens = services.exchange_code(data["code"], data["redirect_uri"])
            payload = services.validate_id_token(tokens.get("id_token", ""), data.get("nonce"))
            user, _ = services.link_google_account(payload)
        except Exception as exc:  # noqa: BLE001 - erreur générique côté client
            return Response({"detail": "Connexion impossible, réessayez."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_tokens_for(user))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IdentitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(SocialIdentitySerializer(request.user.identities.all(), many=True).data)


class GoogleIdentityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payload = services.validate_id_token(
            services.exchange_code(data["code"], data["redirect_uri"]).get("id_token", ""), data.get("nonce")
        )
        identity, created = SocialIdentity.objects.get_or_create(
            provider="google", subject=payload["sub"], defaults={"user": request.user, "email": payload.get("email", ""), "name": payload.get("name", "")}
        )
        return Response(SocialIdentitySerializer(identity).data, status=201 if created else 200)

    def delete(self, request):
        identity = request.user.identities.filter(provider="google").first()
        if identity and not request.user.has_usable_local_password:
            return Response({"detail": "Définissez d'abord un mot de passe avant de retirer Google."}, status=400)
        if identity:
            identity.delete()
        return Response(status=204)


class InsiderRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(InsiderRequestSerializer(request.user.insider_requests.all(), many=True).data)

    def post(self, request):
        serializer = InsiderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)


class TelegramContactView(APIView):
    """Liaison Telegram : code court → `t.me/<bot>?start=<code>`, puis webhook.

    Aucun numéro de téléphone, aucun coût : l'utilisateur ouvre le bot, le compte est lié.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        contact = TelegramContact.objects.filter(user=request.user).first()
        pending = bool(
            contact and contact.link_code and contact.link_code_expires and contact.link_code_expires > timezone.now()
        )
        return Response(
            {
                "registered": bool(contact and contact.verified),
                "available": telegram.configured(),
                "opted_out": bool(contact and contact.opted_out),
                "username": contact.username if contact else "",
                "deep_link": telegram.deep_link(contact.link_code) if pending else "",
            }
        )

    def post(self, request):
        if not telegram.configured():
            return Response({"detail": "Bot Telegram non configuré côté serveur."}, status=503)
        if not request.data.get("consent"):
            return Response({"detail": "Consentement explicite requis pour Telegram."}, status=400)
        contact, _ = TelegramContact.objects.get_or_create(user=request.user)
        code = telegram.new_link_code(contact)
        return Response(
            {
                "deep_link": telegram.deep_link(code),
                "expires_in_minutes": telegram.LINK_CODE_TTL_MINUTES,
            },
            status=201,
        )

    def delete(self, request):
        contact = TelegramContact.objects.filter(user=request.user).first()
        if contact:
            contact.chat_id = None
            contact.verified = False
            contact.opted_out = True
            contact.link_code = None
            contact.save(update_fields=["chat_id", "verified", "opted_out", "link_code"])
        for key in ("notif_telegram", "awareness_telegram"):
            ConsentRecord.objects.filter(user=request.user, key=key).update(
                granted=False, withdrawn_at=timezone.now()
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PushSubscriptionView(APIView):
    """Abonnements Web Push de l'appareil courant (un par navigateur)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "available": push.configured(),
                "public_key": push.public_key(),
                "count": PushSubscription.objects.filter(user=request.user).count(),
            }
        )

    def post(self, request):
        if not push.configured():
            return Response({"detail": "Notifications push non configurées côté serveur."}, status=503)
        endpoint = str(request.data.get("endpoint", "")).strip()
        keys = request.data.get("keys") or {}
        p256dh = str(keys.get("p256dh", "")).strip()
        auth = str(keys.get("auth", "")).strip()
        if not endpoint or not p256dh or not auth:
            return Response({"detail": "Abonnement push incomplet."}, status=400)
        if not request.data.get("consent"):
            return Response({"detail": "Consentement explicite requis pour les notifications."}, status=400)
        # le même abonnement ne doit appartenir qu'à un compte
        PushSubscription.objects.filter(endpoint=endpoint).exclude(user=request.user).delete()
        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "user": request.user,
                "p256dh": p256dh[:200],
                "auth": auth[:64],
                "user_agent": (request.headers.get("User-Agent") or "")[:200],
                "failed_at": None,
            },
        )
        ConsentRecord.objects.update_or_create(
            user=request.user,
            key="notif_push",
            defaults={"granted": True, "granted_at": timezone.now(), "withdrawn_at": None},
        )
        return Response({"subscribed": True}, status=201)

    def delete(self, request):
        endpoint = str(request.data.get("endpoint", "")).strip()
        qs = PushSubscription.objects.filter(user=request.user)
        if endpoint:
            qs = qs.filter(endpoint=endpoint)
        qs.delete()
        if not PushSubscription.objects.filter(user=request.user).exists():
            ConsentRecord.objects.filter(user=request.user, key="notif_push").update(
                granted=False, withdrawn_at=timezone.now()
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ConsentRecordSerializer(request.user.consents.all(), many=True).data)

    def put(self, request):
        allowed = {
            "notif_email",
            "notif_telegram",
            "notif_push",
            "awareness_email",
            "awareness_telegram",
            "awareness_push",
        }
        result = []
        for key, granted in request.data.items():
            if key not in allowed or not isinstance(granted, bool):
                continue
            record, _ = ConsentRecord.objects.get_or_create(user=request.user, key=key)
            record.granted = granted
            if granted and not record.granted_at:
                record.granted_at = timezone.now()
            if not granted:
                record.withdrawn_at = timezone.now()
            record.save()
            result.append(record)
        return Response(ConsentRecordSerializer(result, many=True).data)
