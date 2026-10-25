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


def _resolve_target(target_type: str, raw_id: str):
    """Retrouve la cible d'une lecture : dossier (UUID ou identifiant court) ou site."""
    from django.core.exceptions import ValidationError as DjangoValidationError

    from apps.knowledge.models import SiteProfile

    raw = (raw_id or "").strip()
    if not raw:
        return None
    if target_type == Certification.TargetType.SITE:
        return SiteProfile.objects.filter(domain=raw.lower()).first()
    analysis = Analysis.objects.filter(public_id=raw).first()
    if analysis:
        return analysis
    try:
        return Analysis.objects.filter(id=raw).first()
    except (DjangoValidationError, ValueError):
        return None


class CertificationView(APIView):
    """M8 — les insiders certifient ou contestent une information, avec une source."""

    throttle_classes = [CertificationThrottle]

    def get(self, request):
        target_type = request.query_params.get("target_type", Certification.TargetType.ANALYSIS)
        target_id = request.query_params.get("target_id", "")
        if target_type not in Certification.TargetType.values:
            return Response({"detail": "Type de cible inconnu."}, status=400)
        qs = Certification.objects.filter(target_type=target_type, target_id=str(target_id))
        return Response(CertificationSerializer(qs, many=True).data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Connexion requise."}, status=401)
        if request.user.role not in ("insider", "admin"):
            return Response({"detail": "Seuls les insiders peuvent statuer sur une information."}, status=403)

        target_type = request.data.get("target_type", Certification.TargetType.ANALYSIS)
        if target_type not in Certification.TargetType.values:
            return Response({"detail": "Type de cible inconnu."}, status=400)
        target = _resolve_target(target_type, request.data.get("target_id", ""))
        if not target:
            message = "Site inconnu du wiki." if target_type == Certification.TargetType.SITE else "Dossier introuvable."
            return Response({"detail": message}, status=404)
        target_id = target.domain if target_type == Certification.TargetType.SITE else str(target.id)

        payload = {
            "target_type": target_type,
            "target_id": target_id,
            "verdict": request.data.get("verdict", ""),
            "proposed_status": request.data.get("proposed_status", ""),
            "comment": request.data.get("comment", ""),
            "source_url": request.data.get("source_url", ""),
        }
        existing = Certification.objects.filter(
            user=request.user, target_type=target_type, target_id=target_id
        ).first()
        serializer = CertificationSerializer(existing, data=payload) if existing else CertificationSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save(user=request.user)

        if target_type == Certification.TargetType.ANALYSIS:
            from .readings import refresh_analysis

            refresh_analysis(target)
        else:
            from apps.knowledge import sites

            sites.evaluate(target)

        return Response(
            CertificationSerializer(reading).data,
            status=status.HTTP_200_OK if existing else status.HTTP_201_CREATED,
        )


class CertificationDetailView(APIView):
    """Retrait d'une lecture : par son auteur, ou par un administrateur (M11)."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        reading = Certification.objects.filter(pk=pk).select_related("user").first()
        if not reading:
            return Response({"detail": "Lecture introuvable."}, status=404)
        if reading.user_id != request.user.id and request.user.role != "admin":
            return Response({"detail": "Seul l'auteur ou un administrateur peut retirer cette lecture."}, status=403)
        target_type, target_id = reading.target_type, reading.target_id
        if reading.user_id != request.user.id:
            from apps.core.models import AuditLog

            AuditLog.objects.create(
                actor=request.user.email,
                action="certification_withdraw",
                target=f"{target_type}:{target_id}",
                reason=request.data.get("reason", "") if hasattr(request, "data") else "",
            )
        reading.delete()

        if target_type == Certification.TargetType.ANALYSIS:
            from .models import Analysis as AnalysisModel
            from .readings import refresh_analysis

            analysis = AnalysisModel.objects.filter(id=target_id).first()
            if analysis:
                refresh_analysis(analysis)
        else:
            from apps.knowledge import sites
            from apps.knowledge.models import SiteProfile

            site = SiteProfile.objects.filter(domain=target_id).first()
            if site:
                sites.evaluate(site)
        return Response(status=204)


class InsiderWorkspaceView(APIView):
    """Espace de travail des insiders : lectures signées, propositions wiki, file à statuer."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ("insider", "admin"):
            return Response({"detail": "Espace réservé aux insiders."}, status=403)

        from apps.knowledge.models import WikiPage

        readings = []
        for reading in Certification.objects.filter(user=request.user).select_related("user").order_by("-updated_at")[:50]:
            item = CertificationSerializer(reading).data
            if reading.target_type == Certification.TargetType.ANALYSIS:
                analysis = Analysis.objects.filter(id=reading.target_id).first()
                item["target_label"] = (
                    f"Dossier #{analysis.public_id}" if analysis else "Dossier supprimé"
                )
                item["target_url"] = f"/analyses/{analysis.public_id}" if analysis else ""
            else:
                item["target_label"] = f"Site {reading.target_id}"
                item["target_url"] = f"/wiki?q={reading.target_id}"
            readings.append(item)

        pages = WikiPage.objects.filter(author=request.user).order_by("-updated_at")
        wiki_pages = [
            {
                "slug": page.slug,
                "title": page.title,
                "review_status": page.review_status,
                "review_note": page.review_note,
                "published": page.published,
                "updated_at": page.updated_at.isoformat() if page.updated_at else None,
            }
            for page in pages[:50]
        ]

        read_ids = {
            r.target_id
            for r in Certification.objects.filter(
                user=request.user, target_type=Certification.TargetType.ANALYSIS
            )
        }
        queue = []
        recent = Analysis.objects.filter(
            status__in=[Analysis.Status.DONE, Analysis.Status.PARTIAL]
        ).order_by("-created_at")[:40]
        for analysis in recent:
            if str(analysis.id) in read_ids:
                continue
            queue.append(
                {
                    "public_id": analysis.public_id,
                    "status": analysis.result.get("status", "indeterminee") if analysis.result else "indeterminee",
                    "status_label": analysis.result.get("status_label", "") if analysis.result else "",
                    "input_type": analysis.input_type,
                    "excerpt": (analysis.input_text or analysis.input_url or "Image soumise")[:140],
                    "created_at": analysis.created_at.isoformat(),
                }
            )
            if len(queue) >= 10:
                break

        return Response(
            {
                "role": request.user.role,
                "readings": readings,
                "wiki_pages": wiki_pages,
                "to_review": queue,
                "counts": {
                    "readings": len(readings),
                    "pending_wiki": sum(1 for p in wiki_pages if p["review_status"] == "pending"),
                    "to_review": len(queue),
                },
            }
        )


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
