from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.throttling import ChatThrottle

from . import services
from .models import SiteProfile, WikiPage, WikiRevision
from .serializers import SiteProfileSerializer, WikiPageDetailSerializer, WikiPageListSerializer, WikiRevisionSerializer


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
        return Response(SiteProfileSerializer(qs[:50], many=True).data)


class SiteDetailView(APIView):
    def get(self, request, domain):
        try:
            site = SiteProfile.objects.get(domain=domain)
        except SiteProfile.DoesNotExist:
            return Response({"detail": "Site introuvable."}, status=404)
        return Response(SiteProfileSerializer(site).data)


class WikiListView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "")
        qs = WikiPage.objects.filter(published=True)
        if q:
            qs = qs.filter(title__icontains=q)
        return Response(WikiPageListSerializer(qs, many=True).data)

    def post(self, request):
        if not request.user.is_authenticated or request.user.role not in ("insider", "admin"):
            return Response({"detail": "Réservé aux insiders."}, status=403)
        serializer = WikiPageDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        page = WikiPage.objects.create(author=request.user, **serializer.validated_data)
        return Response(WikiPageDetailSerializer(page).data, status=201)


class WikiDetailView(APIView):
    def get(self, request, slug):
        page = WikiPage.objects.filter(slug=slug).first()
        if not page or (not page.published and not (request.user.is_authenticated and request.user.role in ("insider", "admin"))):
            return Response({"detail": "Page introuvable."}, status=404)
        return Response(WikiPageDetailSerializer(page).data)

    def patch(self, request, slug):
        if not request.user.is_authenticated or request.user.role not in ("insider", "admin"):
            return Response({"detail": "Réservé aux insiders."}, status=403)
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Page introuvable."}, status=404)
        WikiRevision.objects.create(page=page, title=page.title, content=page.content, author=request.user)
        for field in ("title", "content", "published"):
            if field in request.data:
                setattr(page, field, request.data[field])
        page.save()
        return Response(WikiPageDetailSerializer(page).data)


class WikiRevisionsView(APIView):
    def get(self, request, slug):
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Page introuvable."}, status=404)
        return Response(WikiRevisionSerializer(page.revisions.all(), many=True).data)

    def post(self, request, slug):
        if not request.user.is_authenticated or request.user.role not in ("insider", "admin"):
            return Response({"detail": "Réservé aux insiders."}, status=403)
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Page introuvable."}, status=404)
        rev = WikiRevision.objects.get(id=request.data.get("revision_id"))
        page.title = rev.title
        page.content = rev.content
        page.save()
        return Response(WikiPageDetailSerializer(page).data)
