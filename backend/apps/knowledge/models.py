from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.utils.text import slugify

# Config de recherche créée par la migration 0004 : français sans accents.
SEARCH_CONFIG = "fr_unaccent"


class SiteProfile(models.Model):
    class Nature(models.TextChoices):
        AGENCY = "agency", "Agence de presse"
        INSTITUTION = "institution", "Institution publique"
        MEDIA = "media", "Média d'information reconnu"
        BLOG = "blog", "Blog"
        SOCIAL = "social", "Réseau social"
        UNKNOWN = "unknown", "Site inconnu"

    domain = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    nature = models.CharField(max_length=16, choices=Nature.choices, default=Nature.UNKNOWN)
    score = models.IntegerField(default=20)
    description = models.TextField(blank=True)
    # Reconnaissance automatique (dossier §12) : la confiance d'un site se gagne par
    # les corroborations constatées par le système ET les lectures d'insiders.
    certified = models.BooleanField(default=False)
    certified_at = models.DateTimeField(null=True, blank=True)
    system_validations = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["domain"]

    def __str__(self):
        return self.domain


class SiteValidation(models.Model):
    """Une corroboration constatée par le système : un dossier conclu « Corroborée »
    cite ce site parmi ses sources fiables. Une seule validation par dossier et par site."""

    site = models.ForeignKey(SiteProfile, on_delete=models.CASCADE, related_name="validations")
    analysis = models.ForeignKey(
        "analyses.Analysis", on_delete=models.CASCADE, related_name="site_validations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("site", "analysis")

    def __str__(self):
        return f"{self.site.domain} ← dossier {self.analysis.public_id}"


class KnowledgeChunk(models.Model):
    """Corpus indexé du RAG : fiches de sites, pages wiki, vérifications rencontrées (dossier §11).

    `search_vector` est la colonne tsvector (recherche plein texte PostgreSQL, config
    `fr_unaccent` = french + unaccent) utilisée quand les embeddings sont indisponibles.
    """

    ref_type = models.CharField(max_length=16)  # site | wiki | factcheck
    ref_id = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    search_vector = SearchVectorField(null=True, editable=False)
    # RAG vectoriel (mode « gemini » du dossier §11) : vecteur Gemini stocké en JSON.
    embedding = models.JSONField(null=True, blank=True, editable=False)
    embedding_model = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [GinIndex(fields=["search_vector"], name="knowledge_chunk_sv_gin")]

    def __str__(self):
        return f"{self.ref_type}:{self.ref_id}"

    def save(self, *args, **kwargs):
        self.embedding = None  # le texte a changé : l'embedding sera recalculé à la prochaine recherche
        self.embedding_model = ""
        super().save(*args, **kwargs)
        KnowledgeChunk.objects.filter(pk=self.pk).update(
            search_vector=SearchVector("title", weight="A", config=SEARCH_CONFIG)
            + SearchVector("content", weight="B", config=SEARCH_CONFIG)
        )


class WikiPage(models.Model):
    """Page du wiki. Une proposition d'insider reste non publiée tant qu'un
    administrateur ne l'a pas validée (dossier §10 et M11)."""

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "En attente de validation"
        APPROVED = "approved", "Validée"
        REJECTED = "rejected", "Refusée"

    slug = models.SlugField(max_length=140, unique=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="wiki_pages")
    published = models.BooleanField(default=False)
    review_status = models.CharField(
        max_length=16, choices=ReviewStatus.choices, default=ReviewStatus.PENDING
    )
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def _unique_slug(self) -> str:
        base = slugify(self.title)[:130] or "fiche"
        candidate = base
        index = 2
        while WikiPage.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{base}-{index}"
            index += 1
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class WikiRevision(models.Model):
    page = models.ForeignKey(WikiPage, on_delete=models.CASCADE, related_name="revisions")
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.page.title} @ {self.created_at}"
