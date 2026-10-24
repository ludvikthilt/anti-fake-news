"""Chaînes d'image (OCR.space → saisie manuelle) et RAG (Gemini → plein texte)."""
import pytest

from apps.analyses import providers
from apps.analyses.orchestrator import providers_run
from apps.core.services import breaker


@pytest.fixture(autouse=True)
def _reset_breaker():
    breaker._open_until.clear()
    yield
    breaker._open_until.clear()


def _chain(*classes):
    return [cls() for cls in classes]


# ------------------------------------------------------------------ OCR / image


@pytest.mark.django_db
def test_ocrspace_reads_image_text(monkeypatch):
    def ocrspace(self, payload, timeout=8):
        return {"kind": "ocr", "text": "Le Cameroun a gagné la CAN 2025", "engine": self.name}

    def manual(self, payload, timeout=8):
        raise AssertionError("la saisie manuelle ne doit pas être proposée quand l'OCR lit le texte")

    monkeypatch.setattr(providers.OCRSpaceProvider, "call", ocrspace)
    monkeypatch.setattr(providers.ManualOCRProvider, "call", manual)

    out = providers_run(_chain(providers.OCRSpaceProvider, providers.ManualOCRProvider), {"image_b64": "x"})
    assert out["provider"] == "OCR.space"
    assert "CAN 2025" in out["text"]
    assert out["missing"] == []


@pytest.mark.django_db
def test_ocr_failure_falls_back_to_manual_without_alert(monkeypatch):
    def ocrspace(self, payload, timeout=8):
        # clé absente ou quota : indisponibilité de configuration, pas une panne
        raise providers.ProviderUnavailable("clé OCR.space absente")

    monkeypatch.setattr(providers.OCRSpaceProvider, "call", ocrspace)

    out = providers_run(_chain(providers.OCRSpaceProvider, providers.ManualOCRProvider), {"image_b64": "x"})
    assert out["provider"] == "OCR manuel"
    assert out["manual"] is True
    # le coupe-circuit n'est pas ouvert : le passage est silencieux et réversible
    assert not breaker.is_open("ocrspace")


@pytest.mark.django_db
def test_apify_lens_parses_visual_matches():
    from apps.analyses.image_search import parse_items

    items = [
        {
            "searchType": "visual-match",
            "visual-match": {
                "results": [
                    {"title": "Reprise sur un blog", "link": "https://exemple.cm/a", "source": "Blog"},
                    {"title": "sans lien", "link": ""},
                ]
            },
        }
    ]
    rows = parse_items(items)
    assert len(rows) == 1
    assert rows[0]["domain"] == "exemple.cm"
    assert rows[0]["found_by"] == "Apify (Google Lens)"


# ------------------------------------------------------------------ RAG


@pytest.mark.django_db
def test_vector_retrieval_is_preferred(monkeypatch):
    from apps.knowledge import embeddings
    from apps.knowledge.models import KnowledgeChunk
    from apps.knowledge.services import retrieve_with_mode

    chunk = KnowledgeChunk.objects.create(ref_type="wiki", ref_id="9", title="Statuts", content="Quatre statuts.")
    monkeypatch.setattr(embeddings, "vector_search", lambda q, k=5: [chunk])

    hits, mode = retrieve_with_mode("statuts ?")
    assert mode == "vectoriel"
    assert hits == [chunk]


@pytest.mark.django_db
def test_vector_unavailable_falls_back_to_full_text(monkeypatch, settings):
    from apps.knowledge import embeddings
    from apps.knowledge.models import KnowledgeChunk
    from apps.knowledge.services import retrieve_with_mode

    settings.GEMINI_API_KEY = ""
    KnowledgeChunk.objects.create(
        ref_type="wiki",
        ref_id="10",
        title="Les quatre statuts",
        content="Les statuts possibles sont : corroborée, non corroborée, contredite, indéterminée.",
    )
    monkeypatch.setattr(embeddings, "vector_search", lambda q, k=5: None)

    hits, mode = retrieve_with_mode("Quels sont les statuts ?")
    assert mode == "plein texte"
    assert hits and hits[0].title == "Les quatre statuts"


@pytest.mark.django_db
def test_answer_falls_back_to_groq_then_stub(monkeypatch):
    from apps.analyses import providers as p
    from apps.knowledge import services

    def gemini_down(self, payload, timeout=8):
        raise p.ProviderUnavailable("Gemini indisponible")

    def groq_ok(self, payload, timeout=8):
        return {"kind": "ai", "mode": "groq", "answer": "réponse Groq", "sources": payload.get("sources", [])}

    monkeypatch.setattr(p.GeminiProvider, "call", gemini_down)
    monkeypatch.setattr(p.GroqProvider, "call", groq_ok)
    out = services.answer("une question")
    assert out["mode"] == "groq"
    assert out["answer"] == "réponse Groq"

    def groq_down(self, payload, timeout=8):
        raise p.ProviderUnavailable("Groq indisponible")

    monkeypatch.setattr(p.GroqProvider, "call", groq_down)
    out = services.answer("une question")
    assert out["mode"] == "stub"
    assert out["answer"]
