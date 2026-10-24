"""Indexation automatique du wiki dans le corpus du chatbot (§11).

Une page publiée (ou modifiée) met à jour son fragment RAG ; une page dépubliée le retire.
L'embedding est invalidé par `KnowledgeChunk.save` et recalculé à la recherche suivante.
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import KnowledgeChunk, WikiPage


def _sync_chunk(page: WikiPage):
    ref = {"ref_type": "wiki", "ref_id": str(page.id)}
    if not page.published:
        KnowledgeChunk.objects.filter(**ref).delete()
        return
    existing = KnowledgeChunk.objects.filter(**ref).first()
    content = page.content[:4000]
    if existing and existing.title == page.title and existing.content == content:
        return
    KnowledgeChunk.objects.update_or_create(
        **ref,
        defaults={"url": "", "title": page.title, "content": content},
    )


@receiver(post_save, sender=WikiPage)
def wiki_page_saved(sender, instance, **kwargs):
    _sync_chunk(instance)


@receiver(post_delete, sender=WikiPage)
def wiki_page_deleted(sender, instance, **kwargs):
    KnowledgeChunk.objects.filter(ref_type="wiki", ref_id=str(instance.id)).delete()
