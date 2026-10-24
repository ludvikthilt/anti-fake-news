"""RAG vectoriel (M9) — embeddings Gemini stockés en base, repli plein texte puis stub.

Le dossier technique prévoit pgvector ; l'installation PostgreSQL locale (Windows, PG 18)
n'expose pas l'extension `vector`. Les vecteurs sont donc conservés dans une colonne JSON
native et la similarité cosinus est calculée en Python : le corpus (fiches de sites, pages
wiki, vérifications) reste petit, la recherche demeure exacte et sans dépendance externe.

Chaîne : Gemini (`gemini-embedding-001`) → recherche plein texte tsvector → mots-clés.
"""
import math

import httpx
from django.conf import settings
from django.core.cache import cache

DIM_DEFAULT = 768


def _api_key() -> str:
    return getattr(settings, "GEMINI_API_KEY", "") or ""


def _model() -> str:
    return getattr(settings, "GEMINI_EMBED_MODEL", "gemini-embedding-001")


def _dim() -> int:
    return int(getattr(settings, "EMBEDDING_DIM", DIM_DEFAULT))


def available() -> bool:
    return bool(_api_key())


def embed_texts(texts: list[str], timeout: float = 12) -> list[list[float]] | None:
    """Embeddings batch (max 100 textes). None si Gemini est indisponible."""
    texts = [t[:6000] for t in texts if t and t.strip()]
    if not texts or not available():
        return None
    model = _model()
    payload = {
        "requests": [
            {
                "model": f"models/{model}",
                "content": {"parts": [{"text": text}]},
                "outputDimensionality": _dim(),
            }
            for text in texts[:100]
        ]
    }
    try:
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:batchEmbedContents",
            headers={"x-goog-api-key": _api_key()},
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        rows = resp.json().get("embeddings") or []
        vectors = [row.get("values") or [] for row in rows]
        if len(vectors) != len(texts) or any(not v for v in vectors):
            return None
        return vectors
    except Exception:  # noqa: BLE001 - repli silencieux vers le plein texte
        return None


def embed_text(text: str, timeout: float = 12) -> list[float] | None:
    key = f"emb:{_model()}:{hash(text)}"
    cached = cache.get(key)
    if cached:
        return cached
    vectors = embed_texts([text], timeout=timeout)
    if not vectors:
        return None
    cache.set(key, vectors[0], timeout=60 * 60 * 24)
    return vectors[0]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return -1.0
    return dot / (na * nb)


def ensure_indexed(limit: int = 200) -> int:
    """Indexe les fragments qui n'ont pas encore d'embedding à jour."""
    from .models import KnowledgeChunk

    pending = list(
        KnowledgeChunk.objects.filter(embedding__isnull=True).only("id", "title", "content")[:limit]
    )
    if not pending:
        return 0
    vectors = embed_texts([f"{c.title}\n{c.content}" for c in pending])
    if not vectors:
        return 0
    for chunk, vector in zip(pending, vectors):
        KnowledgeChunk.objects.filter(pk=chunk.pk).update(embedding=vector, embedding_model=_model())
    return len(vectors)


def vector_search(question: str, k: int = 5, min_score: float = 0.35):
    """Top-k par similarité cosinus. None si Gemini indisponible."""
    from .models import KnowledgeChunk

    query = embed_text(question)
    if not query:
        return None
    ensure_indexed()
    rows = list(KnowledgeChunk.objects.exclude(embedding__isnull=True).only("embedding", "title", "content", "ref_id", "ref_type", "url", "search_vector", "created_at", "embedding_model"))
    scored = [(cosine(query, row.embedding), row) for row in rows]
    scored = [pair for pair in scored if pair[0] >= min_score]
    scored.sort(key=lambda pair: -pair[0])
    if not scored:
        return []
    return [row for _, row in scored[:k]]
