"""Données de démonstration complètes : toutes les fonctionnalités observables.

Usage (local ou Render) :

    python manage.py seed_demo

La commande appelle d'abord `seed` (profils de sites, wiki de référence, fragments RAG),
puis ajoute des données de démonstration :

- des comptes fictifs (adresses `@example.org`, **aucun** compte Telegram lié) ;
- des dossiers d'analyse répartis sur les quatre statuts, avec sources et vérifications ;
- des lectures d'insiders (dossiers + sites) ;
- un site certifié automatiquement et un site « en observation » ;
- des demandes d'insider et des fiches wiki en attente ;
- des notifications, des campagnes et la consommation des quotas du mois.

La commande est idempotente : relancer ne crée rien deux fois.
Un mot de passe démo unique est défini si la variable `DEMO_PASSWORD` est fournie
(sinon les comptes fictifs n'ont aucun mot de passe utilisable).
"""
import os
from datetime import date, datetime, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import ConsentRecord, InsiderRequest, Role, User
from apps.analyses import reliability
from apps.analyses.models import Analysis, Certification, FactCheck, MissingService, Source
from apps.analyses.readings import refresh_analysis
from apps.core import seed_data
from apps.core.models import QuotaUsage
from apps.knowledge import sites
from apps.knowledge.models import KnowledgeChunk, SiteProfile, WikiPage
from apps.notifications.models import AwarenessCampaign, Notification

# Miniature 1×1 : l'analyse d'image de démonstration n'a pas d'original conservé.
THUMB = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _d(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Peuple la base avec des données de démonstration (idempotent)."

    def handle(self, *args, **options):
        call_command("seed")
        self._users()
        self._requests()
        self._wiki()
        self._chunks()
        analyses = self._analyses()
        self._analysis_readings(analyses)
        self._site_readings()
        self._campaigns()
        self._notifications()
        self._quotas()
        self.stdout.write(self.style.SUCCESS("Données de démonstration en place."))

    # --- Comptes fictifs : aucune adresse réelle, aucun canal Telegram -------------
    def _users(self) -> dict:
        password = os.environ.get("DEMO_PASSWORD") or None
        made = {}
        for email, name, role in seed_data.DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"name": name, "role": role, "is_email_verified": True},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            made[email] = user
        # Consentements explicites : e-mail uniquement (jamais Telegram ni push).
        for email in made:
            for key in ("awareness_email",):
                ConsentRecord.objects.get_or_create(
                    user=made[email],
                    key=key,
                    defaults={"granted": True, "granted_at": timezone.now()},
                )
        ConsentRecord.objects.get_or_create(
            user=made["yann.temguia@example.org"],
            key="notif_email",
            defaults={"granted": True, "granted_at": timezone.now()},
        )
        self.stdout.write(f"{len(made)} comptes de démonstration (aucun Telegram lié).")
        return made

    # --- Demandes d'insider --------------------------------------------------------
    def _requests(self):
        admin = User.objects.filter(role=Role.ADMIN).first()
        for email, motivation in seed_data.DEMO_REQUESTS:
            InsiderRequest.objects.get_or_create(
                user=User.objects.get(email=email),
                motivation=motivation,
                defaults={"status": InsiderRequest.Status.PENDING},
            )
        amina = User.objects.get(email="amina.ngono@example.org")
        InsiderRequest.objects.get_or_create(
            user=amina,
            motivation="Rédactrice, je vérifie les rumeurs sanitaires avec des sources officielles.",
            defaults={
                "status": InsiderRequest.Status.ACCEPTED,
                "reviewed_by": admin,
                "reviewed_at": timezone.now(),
            },
        )
        self.stdout.write("Demandes d'insider (en attente + acceptée).")

    # --- Wiki : propositions en attente et fiche publiée ---------------------------
    def _wiki(self):
        for slug, title, content, author in seed_data.DEMO_WIKI_PENDING:
            WikiPage.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "content": content,
                    "author": User.objects.get(email=author),
                    "published": False,
                    "review_status": WikiPage.ReviewStatus.PENDING,
                },
            )
        for slug, title, content, author in seed_data.DEMO_WIKI_PUBLISHED:
            page, created = WikiPage.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "content": content,
                    "author": User.objects.get(email=author),
                    "published": True,
                    "review_status": WikiPage.ReviewStatus.APPROVED,
                    "reviewed_at": timezone.now(),
                },
            )
            if created:
                KnowledgeChunk.objects.get_or_create(
                    ref_type="wiki",
                    ref_id=str(page.id),
                    defaults={"title": title, "content": content[:4000]},
                )
        self.stdout.write("Wiki : propositions en attente + fiche publiée.")

    # --- Fragments RAG supplémentaires (chatbot) -----------------------------------
    def _chunks(self):
        for index, (ref_type, url, title, content) in enumerate(seed_data.DEMO_CHUNKS, start=1):
            KnowledgeChunk.objects.get_or_create(
                ref_type=ref_type,
                ref_id=url or f"demo-{index}",
                defaults={"url": url, "title": title, "content": content},
            )
        total = KnowledgeChunk.objects.count()
        self.stdout.write(f"Corpus RAG : {total} fragments indexés (le chatbot répond sur cette base).")

    # --- Dossiers d'analyse --------------------------------------------------------
    def _analyses(self) -> dict:
        made = {}
        for spec in seed_data.ANALYSES:
            owner = User.objects.filter(email=spec.get("owner", "")).first()
            analysis, created = Analysis.objects.get_or_create(
                input_hash=f"seed:{spec['key']}",
                defaults={
                    "user": owner,
                    "input_type": spec["input_type"],
                    "input_text": spec.get("input_text", ""),
                    "input_url": spec.get("input_url", ""),
                    "input_thumb": THUMB if spec["input_type"] == "image" else "",
                    "status": Analysis.Status.DONE,
                    "result": {},
                },
            )
            made[spec["key"]] = analysis
            if analysis.result and analysis.sources.exists():
                continue  # déjà rempli lors d'une exécution précédente

            sources = spec["sources"]
            factchecks = spec["factchecks"]
            missing = spec["missing"]
            result = reliability.build_result(
                analysis, sources, factchecks, [], missing, spec.get("meta") or {}
            )

            Source.objects.filter(analysis=analysis).delete()
            FactCheck.objects.filter(analysis=analysis).delete()
            MissingService.objects.filter(analysis=analysis).delete()

            for s in sources:
                Source.objects.create(
                    analysis=analysis,
                    url=(s.get("url") or "")[:1000],
                    domain=(s.get("domain") or "")[:255],
                    title=(s.get("title") or "")[:255],
                    excerpt=s.get("excerpt", ""),
                    source_type=s.get("type", "unknown"),
                    reliability_score=s.get("score", 0),
                    position=s.get("position", "neutral"),
                    date_value=_dt(s.get("date")),
                    date_origin=s.get("date_origin", ""),
                    found_by=s.get("found_by", ""),
                )
            for fc in factchecks:
                FactCheck.objects.create(
                    analysis=analysis,
                    organization=fc.get("organization", ""),
                    verdict=fc.get("verdict", ""),
                    url=(fc.get("url") or "")[:1000],
                    published_date=_d(fc.get("published_date")),
                    summary=fc.get("summary", ""),
                    contradicts=bool(fc.get("contradicts")),
                )
            for m in missing:
                MissingService.objects.create(
                    analysis=analysis, service=m.get("service", "")[:64], reason=m.get("reason", "")[:255]
                )

            analysis.result = result
            analysis.status = (
                Analysis.Status.PARTIAL if missing else Analysis.Status.DONE
            )
            analysis.save(update_fields=["result", "status", "updated_at"])

            when = timezone.now() - timedelta(days=int(spec.get("days_ago", 0)))
            Analysis.objects.filter(pk=analysis.pk).update(created_at=when, updated_at=when)

            # Corroboration constatée par le système : elle fait progresser les sites fiables.
            if result["status"] == reliability.STATUS_OK:
                reliable = [s["domain"] for s in sources if (s.get("score") or 0) >= 70]
                sites.record_corroborations(reliable, analysis=analysis)
        self.stdout.write(f"{len(made)} dossiers d'analyse (statuts variés).")
        return made

    # --- Lectures d'insiders sur les dossiers --------------------------------------
    def _analysis_readings(self, analyses: dict):
        for key, email, verdict, proposed, comment, source in seed_data.ANALYSIS_READINGS:
            analysis = analyses.get(key)
            if not analysis:
                continue
            Certification.objects.update_or_create(
                user=User.objects.get(email=email),
                target_type=Certification.TargetType.ANALYSIS,
                target_id=str(analysis.id),
                defaults={
                    "verdict": verdict,
                    "proposed_status": proposed,
                    "comment": comment,
                    "source_url": source,
                },
            )
            refresh_analysis(analysis)  # les lectures entrent dans le statut affiché
        self.stdout.write("Lectures d'insiders sur les dossiers.")

    # --- Lectures d'insiders sur les sites (reconnaissance) ------------------------
    def _site_readings(self):
        domains = set()
        for domain, email, verdict, proposed, comment, source in seed_data.SITE_READINGS:
            domains.add(domain)
            Certification.objects.update_or_create(
                user=User.objects.get(email=email),
                target_type=Certification.TargetType.SITE,
                target_id=domain,
                defaults={
                    "verdict": verdict,
                    "proposed_status": proposed,
                    "comment": comment,
                    "source_url": source,
                },
            )
        for domain in domains:
            profile = SiteProfile.objects.filter(domain=domain).first()
            if profile:
                state = sites.evaluate(profile)
                label = "certifié" if state["certified"] else (
                    "retrait" if state["revoked"] else "en observation"
                )
                self.stdout.write(f"  {domain} -> {label} ({state['system_validations']}"
                                  f"/{state['system_quota']} système, {state['insider_net']}"
                                  f"/{state['insider_quota']} insiders)")

    # --- Campagnes, notifications, quotas ------------------------------------------
    def _campaigns(self):
        admin = User.objects.filter(role=Role.ADMIN).first()
        for title, body, channel, status in seed_data.CAMPAIGNS:
            AwarenessCampaign.objects.get_or_create(
                title=title,
                defaults={"body": body, "channel": channel, "status": status, "created_by": admin},
            )
        self.stdout.write("Campagnes de sensibilisation (approuvée + brouillon).")

    def _notifications(self):
        for email, title, body, unread in seed_data.NOTIFICATIONS:
            Notification.objects.get_or_create(
                user=User.objects.get(email=email),
                title=title,
                defaults={"body": body, "read": not unread},
            )
        self.stdout.write("Notifications in-app.")

    def _quotas(self):
        period = timezone.now().strftime("%Y-%m")
        for account, (used, limit) in seed_data.QUOTA_USAGE.items():
            QuotaUsage.objects.get_or_create(
                account=account,
                period=period,
                defaults={"used": used, "limit": limit},
            )
        self.stdout.write(f"Consommation des quotas pour {period}.")
