from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.throttling import ChatThrottle

from . import services
from .models import SiteProfile, WikiPage, WikiRevision
from .serializers import (
    SiteProfileSerializer,
    WikiPageDetailSerializer,
    WikiPageListSerializer,
    WikiRevisionSerializer,
    WikiSubmissionSerializer,
)

INSIDER_ROLES = ("insider", "admin")


def _can_write(user) -> bool:
    return user.is_authenticated and user.role in INSIDER_ROLES


def _can_preview(user, page) -> bool:
    """Un brouillon ou une proposition n'est visible que par son auteur et l'admin."""
    if not user.is_authenticated:
        return False
    if user.role == "admin":
        return True
    return user.role == "insider" and page.author_id == user.id


class ChatView(APIView):
    throttle_classes = [ChatThrottle]

    def post(self, request):
        question = (request.data.get("question") or "").strip()[:500]
        if not question:
            return Response({"detail": "Question vide."}, status=400)
        return Response(services.answer(question))


class SiteListView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "")
        qs = SiteProfile.objects.all()
        if q:
            qs = qs.filter(domain__icontains=q)
        if request.query_params.get("certified") == "1":
            qs = qs.filter(certified=True)
        # Les sites reconnus d'abord, puis les plus renseignés.
        qs = qs.order_by("-certified", "domain")
        return Response(SiteProfileSerializer(qs[:50], many=True).data)


class SiteDetailView(APIView):
    def get(self, request, domain):
        try:
            site = SiteProfile.objects.get(domain=domain)
        except SiteProfile.DoesNotExist:
            return Response({"detail": "Site introuvable."}, status=404)
        return Response(SiteProfileSerializer(site).data)


class WikiListView(APIView):
    """Wiki public + propositions de l'insider connecté (`?mine=1`)."""

    def get(self, request):
        q = request.query_params.get("q", "")
        if request.query_params.get("mine") == "1":
            if not _can_write(request.user):
                return Response({"detail": "Réservé aux insiders."}, status=403)
            qs = WikiPage.objects.filter(author=request.user)
        else:
            qs = WikiPage.objects.filter(published=True, review_status=WikiPage.ReviewStatus.APPROVED)
        if q:
            qs = qs.filter(title__icontains=q)
        return Response(WikiPageListSerializer(qs, many=True).data)

    def post(self, request):
        if not _can_write(request.user):
            return Response({"detail": "Réservé aux insiders."}, status=403)
        serializer = WikiSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_admin = request.user.role == "admin"
        page = WikiPage(
            author=request.user,
            title=serializer.validated_data["title"],
            content=serializer.validated_data.get("content", ""),
            published=is_admin,
            review_status=(
                WikiPage.ReviewStatus.APPROVED if is_admin else WikiPage.ReviewStatus.PENDING
            ),
        )
        if is_admin:
            page.reviewed_by = request.user
            page.reviewed_at = timezone.now()
        page.save()
        return Response(WikiPageDetailSerializer(page).data, status=201)


class WikiDetailView(APIView):
    def get(self, request, slug):
        page = WikiPage.objects.filter(slug=slug).first()
        if not page or (not page.published and not _can_preview(request.user, page)):
            return Response({"detail": "Page introuvable."}, status=404)
        return Response(WikiPageDetailSerializer(page).data)

    def patch(self, request, slug):
        if not _can_write(request.user):
            return Response({"detail": "Réservé aux insiders."}, status=403)
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Page introuvable."}, status=404)
        is_admin = request.user.role == "admin"
        if not is_admin and page.author_id != request.user.id:
            return Response({"detail": "Seul l'auteur peut modifier cette fiche."}, status=403)

        new_title = request.data.get("title")
        new_content = request.data.get("content")
        if new_title is None and new_content is None and not (is_admin and "published" in request.data):
            return Response({"detail": "Rien à modifier."}, status=400)

        if new_title is None and new_content is None:
            # L'administrateur ne fait que publier/dépublier : pas de nouvelle version.
            page.published = bool(request.data.get("published"))
            if page.published:
                page.review_status = WikiPage.ReviewStatus.APPROVED
            page.reviewed_by = request.user
            page.reviewed_at = timezone.now()
            page.save()
            return Response(WikiPageDetailSerializer(page).data)

        WikiRevision.objects.create(page=page, title=page.title, content=page.content, author=request.user)
        if new_title is not None:
            page.title = str(new_title).strip()[:255] or page.title
        if new_content is not None:
            page.content = new_content
        if is_admin:
            page.review_status = WikiPage.ReviewStatus.APPROVED
            page.review_note = ""
            page.reviewed_by = request.user
            page.reviewed_at = timezone.now()
            if "published" in request.data:
                page.published = bool(request.data.get("published"))
        else:
            # Toute modification d'un insider repasse par la validation.
            page.published = False
            page.review_status = WikiPage.ReviewStatus.PENDING
            page.review_note = ""
            page.reviewed_by = None
            page.reviewed_at = None
        page.save()
        return Response(WikiPageDetailSerializer(page).data)


class WikiRevisionsView(APIView):
    def get(self, request, slug):
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Page introuvable."}, status=404)
        return Response(WikiRevisionSerializer(page.revisions.all(), many=True).data)

    def post(self, request, slug):
        if not _can_write(request.user):
            return Response({"detail": "Réservé aux insiders."}, status=403)
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Page introuvable."}, status=404)
        is_admin = request.user.role == "admin"
        if not is_admin and page.author_id != request.user.id:
            return Response({"detail": "Seul l'auteur peut restaurer une version."}, status=403)
        rev = page.revisions.filter(id=request.data.get("revision_id")).first()
        if not rev:
            return Response({"detail": "Version introuvable."}, status=404)
        page.title = rev.title
        page.content = rev.content
        if not is_admin:
            page.published = False
            page.review_status = WikiPage.ReviewStatus.PENDING
        page.save()
        return Response(WikiPageDetailSerializer(page).data)
