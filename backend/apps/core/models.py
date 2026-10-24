from django.db import models


class QuotaUsage(models.Model):
    """Compteur d'utilisation d'un fournisseur externe (par compte fournisseur)."""

    account = models.CharField(max_length=64, db_index=True)
    period = models.CharField(max_length=16, db_index=True)  # YYYY-MM (mois)
    used = models.IntegerField(default=0)
    limit = models.IntegerField(default=0)
    # Date du premier avertissement « 80 % du quota » (un seul par période).
    alerted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("account", "period")

    def __str__(self):
        return f"{self.account} {self.period}: {self.used}/{self.limit}"


class AuditLog(models.Model):
    """Journal d'audit des actions sensibles."""

    actor = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=64)
    target = models.CharField(max_length=255, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} par {self.actor} le {self.created_at}"
