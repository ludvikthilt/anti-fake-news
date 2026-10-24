from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import InsiderRequest, Role, User
from apps.analyses.models import Analysis, Certification
from apps.core.models import QuotaUsage
from apps.core.throttling import InternalThrottle
from apps.notifications.models import AwarenessCampaign
from apps.notifications import services as notif_services


def _is_admin(user) -> bool:
    return user.is_authenticated and user.role == Role.ADMIN


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        today = timezone.now().date()
        quotas = [{"account": q.account, "used": q.used, "limit": q.limit} for q in QuotaUsage.objects.all()[:20]]
        return Response({
            "analyses_today": Analysis.objects.filter(created_at__date=today).count(),
            "analyses_total": Analysis.objects.count(),
            "pending_insider_requests": InsiderRequest.objects.filter(status=InsiderRequest.Status.PENDING).count(),
            "certifications": Certification.objects.count(),
            "quotas": quotas,
        })


class InsiderRequestAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        obj = InsiderRequest.objects.filter(pk=pk).first()
        if not obj:
            return Response({"detail": "Demande introuvable."}, status=404)
        decision = request.data.get("status")
        if decision == InsiderRequest.Status.ACCEPTED:
            obj.status = InsiderRequest.Status.ACCEPTED
            obj.user.role = Role.INSIDER
            obj.user.save(update_fields=["role"])
        elif decision == InsiderRequest.Status.REJECTED:
            obj.status = InsiderRequest.Status.REJECTED
            obj.reason = request.data.get("reason", "")
        else:
            return Response({"detail": "Décision invalide."}, status=400)
        obj.reviewed_by = request.user
        obj.reviewed_at = timezone.now()
        obj.save()
        return Response({"id": obj.id, "status": obj.status, "reason": obj.reason})


class CertificationAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        cert = Certification.objects.filter(pk=pk).first()
        if not cert:
            return Response({"detail": "Certification introuvable."}, status=404)
        reason = request.data.get("reason", "")
        cert.delete()
        return Response({"withdrawn": True, "reason": reason})


class UserAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({"detail": "Utilisateur introuvable."}, status=404)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"suspended": True})


def _campaign_dict(c):
    return {"id": c.id, "title": c.title, "channel": c.channel, "status": c.status, "created_at": c.created_at}


class CampaignAdminView(APIView):
    """M13 — campagnes de sensibilisation : liste + création (brouillon)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        return Response([_campaign_dict(c) for c in AwarenessCampaign.objects.all()[:50]])

    def post(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        title = (request.data.get("title") or "").strip()
        body = (request.data.get("body") or "").strip()
        channel = request.data.get("channel", AwarenessCampaign.Channel.EMAIL)
        if not title or not body:
            return Response({"detail": "Titre et corps requis."}, status=400)
        if channel not in AwarenessCampaign.Channel.values:
            return Response({"detail": "Canal invalide."}, status=400)
        campaign = AwarenessCampaign.objects.create(
            title=title, body=body, channel=channel,
            status=AwarenessCampaign.Status.DRAFT, created_by=request.user,
        )
        return Response(_campaign_dict(campaign), status=201)


class CampaignSendView(APIView):
    """M13 — envoi d'une campagne approuvée aux utilisateurs consentants."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        campaign = AwarenessCampaign.objects.filter(pk=pk).first()
        if not campaign:
            return Response({"detail": "Campagne introuvable."}, status=404)
        sent = notif_services.send_campaign(campaign)
        return Response({"id": campaign.id, "status": campaign.status, "sent": sent})


class InternalSendCampaignsView(APIView):
    """M13 — point d'entrée du planificateur (GitHub Actions), protégé par un jeton interne."""

    permission_classes = [AllowAny]
    throttle_classes = [InternalThrottle]

    def post(self, request):
        token = request.headers.get("X-Internal-Token", "")
        if not settings.INTERNAL_TOKEN or token != settings.INTERNAL_TOKEN:
            return Response({"detail": "Non autorisé."}, status=403)
        total = 0
        for campaign in AwarenessCampaign.objects.filter(status=AwarenessCampaign.Status.APPROVED):
            total += notif_services.send_campaign(campaign)
        return Response({"sent": total})
