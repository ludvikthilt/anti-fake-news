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
from apps.knowledge.models import WikiPage
from apps.notifications.models import AwarenessCampaign
from apps.notifications import services as notif_services

# Libellés des comptes fournisseurs affichés dans le tableau des quotas.
QUOTA_LABELS = {
    "tavily": "Tavily — recherche web",
    "serper": "Serper — recherche web",
    "serpapi": "SerpApi — recherche web et images",
    "serpapi_images": "SerpApi — recherche d'images",
    "serpapi_lens": "SerpApi — Google Lens",
    "searchapi": "SearchApi.io — recherche web et images",
    "searchapi_lens": "SearchApi.io — Google Lens",
    "exa": "Exa — recherche web",
    "factcheck": "Google Fact Check Tools",
    "ocrspace": "OCR.space — lecture d'image",
    "apify_lens": "Apify Google Lens — recherche inversée",
    "groq": "Groq — assistant et RAG",
    "gemini": "Gemini — assistant et embeddings",
}


def _is_admin(user) -> bool:
    return user.is_authenticated and user.role == Role.ADMIN


def _quota_rows() -> list[dict]:
    """Quotas du mois : une ligne par fournisseur connu, même sans appel."""
    period = timezone.now().strftime("%Y-%m")
    stored = {q.account: q for q in QuotaUsage.objects.filter(period=period)}
    # Seuls les comptes fournisseurs réels sont affichés (pas les replis internes).
    accounts = [
        account
        for account in dict.fromkeys([*settings.QUOTA_LIMITS.keys(), *stored.keys()])
        if account in QUOTA_LABELS
    ]
    rows = []
    for account in accounts:
        obj = stored.get(account)
        used = obj.used if obj else 0
        limit = settings.QUOTA_LIMITS.get(account) or (obj.limit if obj else 0)
        remaining = max(limit - used, 0) if limit else None
        percent = min(round(used / limit * 100), 100) if limit else None
        rows.append(
            {
                "account": account,
                "label": QUOTA_LABELS.get(account, account),
                "period": period,
                "used": used,
                "limit": limit,
                "remaining": remaining,
                "percent": percent,
                "alerted": bool(obj and obj.alerted_at),
            }
        )
    rows.sort(key=lambda r: (r["percent"] is None, -(r["percent"] or 0), r["label"]))
    return rows


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        today = timezone.now().date()
        return Response({
            "analyses_today": Analysis.objects.filter(created_at__date=today).count(),
            "analyses_total": Analysis.objects.count(),
            "pending_insider_requests": InsiderRequest.objects.filter(status=InsiderRequest.Status.PENDING).count(),
            "certifications": Certification.objects.count(),
            "pending_wiki": WikiPage.objects.filter(review_status=WikiPage.ReviewStatus.PENDING).count(),
            "quotas": _quota_rows(),
        })


def _insider_request_row(obj: InsiderRequest) -> dict:
    return {
        "id": obj.id,
        "user": obj.user.name or obj.user.email if obj.user else "",
        "email": obj.user.email if obj.user else "",
        "motivation": obj.motivation,
        "status": obj.status,
        "reason": obj.reason,
        "created_at": obj.created_at.isoformat(),
        "reviewed_at": obj.reviewed_at.isoformat() if obj.reviewed_at else None,
    }


class InsiderRequestAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        qs = InsiderRequest.objects.select_related("user").order_by("-created_at")
        wanted = request.query_params.get("status", "")
        if wanted in InsiderRequest.Status.values:
            qs = qs.filter(status=wanted)
        return Response([_insider_request_row(obj) for obj in qs[:50]])

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


def _wiki_admin_row(page: WikiPage) -> dict:
    return {
        "slug": page.slug,
        "title": page.title,
        "content": page.content,
        "published": page.published,
        "review_status": page.review_status,
        "review_note": page.review_note,
        "author": (page.author.name or page.author.email) if page.author else "",
        "created_at": page.created_at.isoformat(),
        "updated_at": page.updated_at.isoformat(),
    }


class WikiPendingAdminView(APIView):
    """M10/M11 — fiches proposées par les insiders, en attente de validation."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        qs = WikiPage.objects.select_related("author")
        wanted = request.query_params.get("status", "pending")
        if wanted in WikiPage.ReviewStatus.values:
            qs = qs.filter(review_status=wanted)
        if request.query_params.get("status") != "all":
            qs = qs.order_by("created_at")
        else:
            qs = qs.order_by("-updated_at")
        return Response([_wiki_admin_row(page) for page in qs[:50]])


class WikiReviewAdminView(APIView):
    """Valider (publication) ou refuser une fiche proposée par un insider."""

    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        page = WikiPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Fiche introuvable."}, status=404)
        decision = request.data.get("decision")
        note = (request.data.get("note") or "").strip()
        if decision == "approve":
            page.review_status = WikiPage.ReviewStatus.APPROVED
            page.published = True
        elif decision == "reject":
            page.review_status = WikiPage.ReviewStatus.REJECTED
            page.published = False
        else:
            return Response({"detail": "Décision invalide."}, status=400)
        page.review_note = note
        page.reviewed_by = request.user
        page.reviewed_at = timezone.now()
        page.save()
        return Response(_wiki_admin_row(page))


class CertificationAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        certs = list(Certification.objects.select_related("user").order_by("-created_at")[:50])
        analysis_ids = [
            c.target_id for c in certs if c.target_type == Certification.TargetType.ANALYSIS
        ]
        analyses = {str(a.id): a for a in Analysis.objects.filter(id__in=analysis_ids)}
        rows = []
        for cert in certs:
            if cert.target_type == Certification.TargetType.ANALYSIS:
                analysis = analyses.get(cert.target_id)
                target_label = f"Dossier #{analysis.public_id}" if analysis else "Dossier supprimé"
                target_url = f"/analyses/{analysis.public_id}" if analysis else ""
            else:
                target_label = f"Site {cert.target_id}"
                target_url = f"/wiki?q={cert.target_id}"
            rows.append(
                {
                    "id": cert.id,
                    "target_type": cert.target_type,
                    "target_id": cert.target_id,
                    "target_label": target_label,
                    "target_url": target_url,
                    "verdict": cert.verdict,
                    "proposed_status": cert.proposed_status,
                    "insider": (cert.user.name or cert.user.email) if cert.user else "",
                    "source_url": cert.source_url,
                    "comment": cert.comment,
                    "created_at": cert.created_at.isoformat(),
                }
            )
        return Response(rows)

    def post(self, request, pk):
        if not _is_admin(request.user):
            return Response({"detail": "Réservé aux administrateurs."}, status=403)
        cert = Certification.objects.filter(pk=pk).first()
        if not cert:
            return Response({"detail": "Certification introuvable."}, status=404)
        reason = request.data.get("reason", "")
        target_type, target_id = cert.target_type, cert.target_id
        from apps.core.models import AuditLog

        AuditLog.objects.create(
            actor=request.user.email,
            action="certification_withdraw",
            target=f"{target_type}:{target_id}",
            reason=reason,
        )
        cert.delete()

        # Le statut du dossier dépend des lectures : on le recalcule après retrait.
        if target_type == Certification.TargetType.ANALYSIS:
            from apps.analyses.models import Analysis as AnalysisModel
            from apps.analyses.readings import refresh_analysis

            analysis = AnalysisModel.objects.filter(id=target_id).first()
            if analysis:
                refresh_analysis(analysis)
        else:
            from apps.knowledge import sites
            from apps.knowledge.models import SiteProfile

            profile = SiteProfile.objects.filter(domain=target_id).first()
            if profile:
                sites.evaluate(profile)
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
