import secrets
import uuid

from django.conf import settings
from django.db import models


def short_id() -> str:
    return secrets.token_urlsafe(9)


class Analysis(models.Model):
    class InputType(models.TextChoices):
        TEXT = "text", "Texte"
        IMAGE = "image", "Image"
        LINK = "link", "Lien"

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        RUNNING = "running", "En cours"
        DONE = "done", "Terminée"
        PARTIAL = "partial", "Partielle"
        FAILED = "failed", "Échouée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_id = models.CharField(max_length=16, default=short_id, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="analyses")
    input_type = models.CharField(max_length=8, choices=InputType.choices)
    input_text = models.TextField(blank=True)
    input_url = models.URLField(max_length=1000, blank=True)
    input_thumb = models.TextField(blank=True)  # miniature base64, original jamais conservé
    input_hash = models.CharField(max_length=64, blank=True)  # empreinte pHash / SHA-256
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
    result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.public_id}"


class Source(models.Model):
    class SourceType(models.TextChoices):
        AGENCY = "agency", "Agence"
        MEDIA = "media", "Média"
        INSTITUTION = "institution", "Institution"
        BLOG = "blog", "Blog"
        SOCIAL = "social", "Réseau social"
        UNKNOWN = "unknown", "Site inconnu"

    class DateOrigin(models.TextChoices):
        DECLARED = "declared", "Déclarée"
        OBSERVED = "observed", "Observée"
        METADATA = "metadata", "Métadonnée"
        INDEXATION = "indexation", "Indexation"

    class Position(models.TextChoices):
        NEUTRAL = "neutral", "Neutre"
        CORROBORATES = "corroborates", "Corrobore"
        CONTRADICTS = "contradicts", "Contredit"

    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="sources")
    url = models.URLField(max_length=1000, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    excerpt = models.TextField(blank=True)
    source_type = models.CharField(max_length=16, choices=SourceType.choices, default=SourceType.UNKNOWN)
    reliability_score = models.IntegerField(default=0)
    position = models.CharField(max_length=16, choices=Position.choices, default=Position.NEUTRAL)
    date_value = models.DateTimeField(null=True, blank=True)
    date_origin = models.CharField(max_length=16, choices=DateOrigin.choices, blank=True)
    found_by = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["date_value", "id"]

    def __str__(self):
        return self.domain or self.url


class FactCheck(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="factchecks")
    organization = models.CharField(max_length=255)
    verdict = models.CharField(max_length=500)  # tel que publié
    url = models.URLField(max_length=1000, blank=True)
    published_date = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    contradicts = models.BooleanField(default=False)  # faux / trompeur détecté

    def __str__(self):
        return f"{self.organization}: {self.verdict[:60]}"


class Certification(models.Model):
    """Lecture d'insider : certifie ou conteste une information (ou un site).

    Le statut proposé reprend le vocabulaire des quatre statuts de la plateforme.
    Une lecture est signée (auteur), datée et sourcée ; un insider ne peut avoir
    qu'une lecture par cible, qu'il peut modifier ou retirer.
    """

    class TargetType(models.TextChoices):
        ANALYSIS = "analysis", "Information"
        SITE = "site", "Site"

    class Verdict(models.TextChoices):
        CERTIFY = "certify", "Certifie"
        CONTEST = "contest", "Conteste"

    class ProposedStatus(models.TextChoices):
        CORROBOREE = "corroboree", "Corroborée"
        NON_CORROBOREE = "non_corroboree", "Non corroborée"
        CONTREDITE = "contredite", "Contredite"
        INDETERMINEE = "indeterminee", "Indéterminée"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certifications")
    target_type = models.CharField(max_length=16, choices=TargetType.choices)
    target_id = models.CharField(max_length=64)
    verdict = models.CharField(max_length=16, choices=Verdict.choices)
    proposed_status = models.CharField(max_length=20, choices=ProposedStatus.choices, blank=True)
    comment = models.TextField(blank=True)
    source_url = models.URLField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.email} {self.verdict} {self.target_type}"


class MissingService(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="missing_services")
    service = models.CharField(max_length=64)
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.service}: {self.reason}"
