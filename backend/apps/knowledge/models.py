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
    certified = models.BooleanField(default=False)

    class Meta:
        ordering = ["domain"]

    def __str__(self):
        return self.domain


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
    slug = models.SlugField(max_length=140, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="wiki_pages")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:140]
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
