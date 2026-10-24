"""Indexe le corpus RAG avec les embeddings Gemini (M9).

Usage : python manage.py index_knowledge [--reset]
Sans clé Gemini, la commande le signale : le chatbot continue en plein texte tsvector.
"""
from django.core.management.base import BaseCommand

from apps.knowledge import embeddings
from apps.knowledge.models import KnowledgeChunk


class Command(BaseCommand):
    help = "Calcule les embeddings Gemini des fragments du corpus (RAG vectoriel)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Recalcule tous les embeddings.")

    def handle(self, *args, **options):
        if not embeddings.available():
            self.stderr.write("Clé Gemini absente : le chatbot reste en recherche plein texte.")
            return

        if options["reset"]:
            KnowledgeChunk.objects.update(embedding=None, embedding_model="")

        total = 0
        while True:
            done = embeddings.ensure_indexed(limit=100)
            if not done:
                break
            total += done
            self.stdout.write(f"{total} fragment(s) indexé(s)…")

        remaining = KnowledgeChunk.objects.filter(embedding__isnull=True).count()
        self.stdout.write(
            self.style.SUCCESS(f"{total} fragment(s) indexé(s) avec {embeddings._model()} ; {remaining} en attente.")
        )
