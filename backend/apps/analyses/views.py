import base64 as b64
import hashlib
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.throttling import AnalysisThrottle, CertificationThrottle

from .models import Analysis, Certification, MissingService
from .orchestrator import normalize, trigger_analysis
from .serializers import AnalysisCreateSerializer, AnalysisDetailSerializer, AnalysisListSerializer, CertificationSerializer


def _cache_key(input_type: str, text: str, url: str, image: str) -> str:
    raw = normalize(f"{input_type}|{text}|{url}|{image}")
    return hashlib.sha256(raw.encode()).hexdigest()


class AnalysisListView(APIView):
    throttle_classes = [AnalysisThrottle]

    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        image = data.get("image", "")
        if data["input_type"] == Analysis.InputType.IMAGE and image:
            from . import images

            try:
                thumb = images.make_thumbnail(image)
                key = f"image|{images.phash_of(image)}"
            except ValueError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            thumb = ""
            key = _cache_key(data["input_type"], data.get("input_text", ""), data.get("input_url", ""), "")

        # Le cache expire (6 h pour un texte, 24 h pour une image) : au-delà, une
        # nouvelle analyse interroge de nouveau les fournisseurs.
        ttl_hours = (
            settings.CACHE_TTL_IMAGE_HOURS
            if data["input_type"] == Analysis.InputType.IMAGE
            else settings.CACHE_TTL_TEXT_HOURS
        )
        cached = Analysis.objects.filter(
            input_hash=key,
            status__in=[Analysis.Status.DONE, Analysis.Status.PARTIAL],
            created_at__gte=timezone.now() - timedelta(hours=ttl_hours),
        ).first()
        if cached:
            return Response(AnalysisDetailSerializer(cached).data, status=status.HTTP_200_OK)

        analysis = Analysis.objects.create(
            user=user,
            input_type=data["input_type"],
            input_text=data.get("input_text", ""),
            input_url=data.get("input_url", ""),
            input_thumb=thumb,
            input_hash=key,
            status=Analysis.Status.PENDING,
        )
        trigger_analysis(analysis.id)
        return Response(AnalysisDetailSerializer(analysis).data, status=status.HTTP_202_ACCEPTED)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Connexion requise pour l'historique."}, status=401)
        qs = Analysis.objects.filter(user=request.user)
        return Response(AnalysisListSerializer(qs, many=True).data)


class AnalysisDetailView(APIView):
    """Lecture publique via le lien partageable (toute personne qui possède le lien peut le voir)."""

    def get(self, request, pk):
        try:
            analysis = Analysis.objects.get(public_id=pk)
        except Analysis.DoesNotExist:
            return Response({"detail": "Analyse introuvable."}, status=404)
        return Response(AnalysisDetailSerializer(analysis).data)

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"detail": "Connexion requise."}, status=401)
        try:
            analysis = Analysis.objects.get(public_id=pk, user=request.user)
        except Analysis.DoesNotExist:
            return Response({"detail": "Analyse introuvable."}, status=404)
        analysis.delete()
        return Response(status=204)


class CertificationView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CertificationThrottle]

    def get(self, request):
        target_type = request.query_params.get("target_type", "analysis")
        target_id = request.query_params.get("target_id", "")
        qs = Certification.objects.filter(target_type=target_type, target_id=target_id)
        return Response(CertificationSerializer(qs, many=True).data)

    def post(self, request):
        if request.user.role not in ("insider", "admin"):
            return Response({"detail": "Seuls les insiders peuvent certifier."}, status=403)
        serializer = CertificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)


class StatusView(APIView):
    """Sonde de supervision : base, cache et mode actif — jamais limitée ni authentifiée."""

    throttle_classes = []

    def get(self, request):
        from django.core.cache import cache
        from django.db import connection

        checks = {}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            checks["database"] = "ok"
        except Exception as exc:  # noqa: BLE001 - on rapporte l'état, on ne lève pas
            checks["database"] = f"indisponible: {exc}"[:120]
        try:
            cache.set("healthcheck", "ok", 5)
            checks["cache"] = "ok" if cache.get("healthcheck") == "ok" else "indisponible"
        except Exception as exc:  # noqa: BLE001
            checks["cache"] = f"indisponible: {exc}"[:120]

        healthy = checks["database"] == "ok"
        return Response(
            {
                "status": "ok" if healthy else "degraded",
                **checks,
                "ai_mode": settings.AI_MODE,
                "search_provider": settings.SEARCH_PROVIDER,
            },
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class MediaImageView(APIView):
    """Sert une miniature éphémère (jeton aléatoire, quelques minutes)."""

    permission_classes = [AllowAny]
    throttle_classes = []  # un moteur d'image peut lire la même URL plusieurs fois

    def get(self, request, token):
        from . import media

        image_b64 = media.get_image(token)
        if not image_b64:
            return Response({"detail": "Image expirée ou introuvable."}, status=404)
        try:
            raw = b64.b64decode(image_b64)
        except Exception:  # noqa: BLE001
            return Response({"detail": "Image invalide."}, status=400)
        return HttpResponse(raw, content_type="image/jpeg", headers={"Cache-Control": "private, max-age=300"})
