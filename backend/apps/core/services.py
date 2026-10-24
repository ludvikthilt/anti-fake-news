"""Services transverses : coupe-circuit, quotas, chaîne de repli (dossier §6, récap §1)."""
import logging
import time
from datetime import date

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Coupe-circuit par compte fournisseur (60 s après 429/5xx/délai)."""

    def __init__(self, seconds: int = 60):
        self.seconds = seconds
        self._open_until: dict[str, float] = {}

    def is_open(self, account: str) -> bool:
        return time.monotonic() < self._open_until.get(account, 0)

    def open(self, account: str):
        self._open_until[account] = time.monotonic() + self.seconds


breaker = CircuitBreaker()


class QuotaService:
    """Pool de quotas par fournisseur, persisté en base."""

    def __init__(self):
        self._cache: dict[str, tuple[str, int, int]] = {}

    def _key(self, account: str) -> tuple[str, int, int]:
        now = date.today()
        period = now.strftime("%Y-%m")
        return account, period, 0

    def can_call(self, account: str, limit: int | None = None) -> bool:
        from .models import QuotaUsage

        now = date.today()
        obj, _ = QuotaUsage.objects.get_or_create(account=account, period=now.strftime("%Y-%m"))
        if limit is not None and obj.limit != limit:
            obj.limit = limit
            obj.save(update_fields=["limit"])
        if obj.limit and obj.used >= obj.limit:
            return False
        return True

    def record(self, account: str):
        from .models import QuotaUsage

        now = date.today()
        obj, _ = QuotaUsage.objects.get_or_create(account=account, period=now.strftime("%Y-%m"))
        QuotaUsage.objects.filter(pk=obj.pk).update(used=models_F("used") + 1)
        self._alert_if_needed(obj.pk)

    def _alert_if_needed(self, pk: int):
        """Avertit une seule fois par période dès le seuil (défaut 80 %) atteint."""
        from .models import AuditLog, QuotaUsage

        obj = QuotaUsage.objects.filter(pk=pk).first()
        if not obj or not obj.limit or obj.alerted_at:
            return
        ratio = getattr(settings, "QUOTA_ALERT_RATIO", 0.8)
        if obj.used < obj.limit * ratio:
            return
        updated = QuotaUsage.objects.filter(pk=pk, alerted_at__isnull=True).update(alerted_at=timezone.now())
        if not updated:
            return
        logger.warning("Quota %s %s : %s/%s utilisés", obj.account, obj.period, obj.used, obj.limit)
        AuditLog.objects.create(
            actor="système",
            action="quota_80",
            target=f"{obj.account} {obj.period}",
            reason=f"{obj.used}/{obj.limit} appels utilisés",
        )


def models_F(value):
    from django.db.models import F

    return F(value)


quota = QuotaService()


def run_chain(function: str, payload, budget: float | None = None, providers: list | None = None):
    """Exécute la chaîne ordonnée de fournisseurs d'une fonction.

    Règle générale de repli (identique pour tous les profils) :
    délai > 8 s, 429/5xx, quota épuisé ou coupe-circuit ouvert => fournisseur suivant.
    Budget total (défaut : ANALYSIS_BUDGET_SECONDS) épuisé => repli manuel.
    """
    from django.core.cache import cache

    budget = budget if budget is not None else settings.ANALYSIS_BUDGET_SECONDS
    key = f"chain:{function}:{hash(str(payload))}"
    hit = cache.get(key)
    if hit is not None:
        return {"cached": True, **hit}

    missing = []
    providers = providers or []

    for provider in providers:
        if budget <= 0:
            break
        account = getattr(provider, "account", provider.name)
        if breaker.is_open(account) or not quota.can_call(account):
            missing.append({"provider": provider.name, "reason": "indisponible ou quota"})
            continue
        start = time.monotonic()
        try:
            timeout = min(settings.PROVIDER_TIMEOUT_SECONDS, budget)
            result = provider.call(payload, timeout=timeout)
        except Exception as exc:  # noqa: BLE001 - on capture tout échec fournisseur
            breaker.open(account)
            missing.append({"provider": provider.name, "reason": str(exc)[:120]})
            budget -= time.monotonic() - start
            continue
        budget -= time.monotonic() - start
        quota.record(account)
        cache.set(key, result, timeout=60)
        return {**result, "missing": missing}

    return {"empty": True, "missing": missing}
