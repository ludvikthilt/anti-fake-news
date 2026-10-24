from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    name = "apps.knowledge"
    label = "knowledge"

    def ready(self):
        from . import signals  # noqa: F401 - branche l'indexation du wiki dans le corpus RAG
