"""Reconnaissance automatique des sites fiables (M6 / dossier §12).

Un site ne devient pas « certifié » sur la seule parole d'un insider. La reconnaissance
se gagne quand deux quotas sont atteints :

1. des **corroborations constatées par le système** — une analyse conclue « Corroborée »
   et le site figure parmi les sources fiables qui reprennent l'information ;
2. des **insiders distincts** qui certifient le site, chaque contestation annulant une
   certification. Le quota minimum est de deux insiders, même mal configuré.

Les deux quotas sont réglables par environnement (`SITE_SYSTEM_QUOTA`,
`SITE_INSIDER_QUOTA`). Le statut proposé par chaque insider reste une donnée affichée
et journalisée, mais c'est le verdict (certifie/conteste) qui pèse dans le calcul.
"""

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from apps.analyses.models import Certification

from .models import SiteProfile, SiteValidation


def quotas() -> tuple[int, int]:
    """(corroborations système requises, insiders certifiants requis)."""
    system_quota = max(1, int(getattr(settings, "SITE_SYSTEM_QUOTA", 5)))
    # Un insider seul ne valide jamais un site : plancher à deux.
    insider_quota = max(2, int(getattr(settings, "SITE_INSIDER_QUOTA", 3)))
    return system_quota, insider_quota


def insider_tally(domain: str) -> dict:
    """Lectures d'insiders sur un site : certifiants, contestataires, solde.

    Le statut proposé compte : certifier tout en proposant « Non corroborée » ou
    « Indéterminée » ne valide pas le site ; proposer « Contredite » vaut contestation.
    """
    readings = Certification.objects.filter(
        target_type=Certification.TargetType.SITE, target_id=domain.lower()
    ).values_list("user_id", "verdict", "proposed_status")

    certifiers = {
        user
        for user, verdict, status in readings
        if verdict == Certification.Verdict.CERTIFY
        and status in ("", Certification.ProposedStatus.CORROBOREE)
    }
    contesters = {
        user
        for user, verdict, status in readings
        if verdict == Certification.Verdict.CONTEST
        or status == Certification.ProposedStatus.CONTREDITE
    }
    net = max(len(certifiers) - len(contesters), 0)
    return {
        "certifiers": len(certifiers),
        "contesters": len(contesters),
        "net": net,
    }


def evaluation(site: SiteProfile) -> dict:
    """État de reconnaissance d'un site et ce qu'il lui reste à accomplir."""
    system_quota, insider_quota = quotas()
    tally = insider_tally(site.domain)
    certified = site.system_validations >= system_quota and tally["net"] >= insider_quota
    return {
        "domain": site.domain,
        "certified": certified,
        "certified_at": site.certified_at.isoformat() if site.certified_at else None,
        "system_validations": site.system_validations,
        "system_quota": system_quota,
        "system_remaining": max(system_quota - site.system_validations, 0),
        "insider_certifications": tally["certifiers"],
        "insider_contests": tally["contesters"],
        "insider_net": tally["net"],
        "insider_quota": insider_quota,
        "insider_remaining": max(insider_quota - tally["net"], 0),
    }


def evaluate(site: SiteProfile) -> dict:
    """Recalcule et enregistre la reconnaissance automatique du site."""
    state = evaluation(site)
    changed = []
    if state["certified"] != site.certified:
        site.certified = state["certified"]
        changed.append("certified")
        if state["certified"]:
            site.certified_at = timezone.now()
            state["certified_at"] = site.certified_at.isoformat()
        else:
            # Une contestation peut retirer une reconnaissance acquise.
            site.certified_at = None
            state["certified_at"] = None
        changed.append("certified_at")
    if changed:
        site.save(update_fields=changed)
    return state


def remember_domain(domain: str, name: str = "", nature: str = "unknown", score: int = 20) -> SiteProfile | None:
    """Inscrit un domaine rencontré dans la base locale, sans écraser une fiche existante."""
    domain = (domain or "").lower().strip()
    if not domain:
        return None
    site, created = SiteProfile.objects.get_or_create(
        domain=domain,
        defaults={
            "name": (name or domain)[:255],
            "nature": nature,
            "score": score,
        },
    )
    if not created and not site.name and name:
        site.name = name[:255]
        site.save(update_fields=["name"])
    return site


def record_corroborations(domains, analysis=None) -> list[str]:
    """Ajoute une corroboration système par domaine, puis réévalue sa reconnaissance.

    Quand le dossier est fourni, une même analyse ne peut valider deux fois le même site :
    le quota compte des informations distinctes, pas des passages répétés.
    """
    verified = []
    for domain in {d.lower() for d in domains if d}:
        site = SiteProfile.objects.filter(domain=domain).first()
        if not site:
            site = remember_domain(domain)
        if analysis is not None:
            _, created = SiteValidation.objects.get_or_create(site=site, analysis=analysis)
            if not created:
                continue
        SiteProfile.objects.filter(pk=site.pk).update(system_validations=F("system_validations") + 1)
        site.refresh_from_db(fields=["system_validations", "certified", "certified_at"])
        if evaluate(site)["certified"]:
            verified.append(domain)
    return verified


def quota_bonus() -> int:
    """Bonus de fiabilité accordé à un site reconnu."""
    return int(getattr(settings, "SITE_CERTIFY_BONUS", 10))


def site_score(domain: str, base: int) -> int:
    """Score de fiabilité d'une source, enrichi par la fiche de site et sa reconnaissance."""
    site = SiteProfile.objects.filter(domain=(domain or "").lower()).first()
    if not site:
        return base
    score = max(site.score, base)
    if site.certified:
        score = min(score + quota_bonus(), 98)
    return score
