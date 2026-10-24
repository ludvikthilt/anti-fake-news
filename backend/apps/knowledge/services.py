"""Chatbot de redirection (M9) — dossier technique §11.

Les liens sont construits par le serveur, jamais par le modèle.
Récupération : Gemini (embeddings vectoriels) → plein texte tsvector → mots-clés.
Génération : Gemini → Groq → stub ; sans clé, le stub renvoie les liens de la base.
"""
import re

from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import F

from apps.analyses.providers import AI_CHAIN

from . import embeddings
from .models import SEARCH_CONFIG, KnowledgeChunk

SYSTEM = (
    "Tu es l'assistant de redirection d'une plateforme de vérification de l'information. "
    "Réponds en français, en 3 phrases au plus, uniquement à partir des PASSAGES fournis. "
    "Cite les passages par leur numéro [n]. Si les passages ne suffisent pas, dis-le et propose "
    "de lancer une analyse. Ne dis jamais qu'une information est vraie ou fausse."
)


def retrieve(question: str, k: int = 5) -> list[KnowledgeChunk]:
    return retrieve_with_mode(question, k)[0]


def retrieve_with_mode(question: str, k: int = 5) -> tuple[list[KnowledgeChunk], str]:
    """Récupération à 4 niveaux (dossier §11) :

    1. Embeddings Gemini + similarité cosinus (mode « gemini ») ;
    2. Recherche plein texte tsvector (config `french`, index GIN) + classement SearchRank ;
    3. Similarité trigramme (pg_trgm) pour les fautes de frappe ;
    4. Repli mots-clés icontains puis corpus complet.
    """
    q = (question or "").strip()
    if not q:
        return [], "vide"

    vector_hits = embeddings.vector_search(q, k=k)
    if vector_hits:
        return vector_hits, "vectoriel"

    # Question naturelle : on combine les termes en OU (sinon « quels sont les… »
    # ne trouve rien, faute de contenir tous les mots interrogatifs).
    terms = [w for w in re.findall(r"\w+", q.lower()) if len(w) >= 3][:8]
    query = SearchQuery(" | ".join(terms), config=SEARCH_CONFIG, search_type="raw") if terms else SearchQuery(q, config=SEARCH_CONFIG)
    full_text = (
        KnowledgeChunk.objects.annotate(rank=SearchRank(F("search_vector"), query))
        .filter(search_vector=query)
        .order_by("-rank")[:k]
    )
    hits = list(full_text)
    if hits:
        return hits, "plein texte"

    fuzzy = (
        KnowledgeChunk.objects.annotate(sim=TrigramSimilarity("content", q))
        .filter(sim__gt=0.12)
        .order_by("-sim")[:k]
    )
    hits = list(fuzzy)
    if hits:
        return hits, "approchant"

    terms = [t for t in q.lower().split() if len(t) > 2][:6]
    if terms:
        kw = KnowledgeChunk.objects.all()
        for term in terms:
            kw = kw.filter(content__icontains=term)
        hits = list(kw[:k])
        if hits:
            return hits, "mots-clés"
    return list(KnowledgeChunk.objects.all()[:k]), "corpus"


def build_sources(chunks: list[KnowledgeChunk]) -> list[dict]:
    """Liens construits côté serveur : pages wiki internes + sources externes."""
    from .models import WikiPage

    seen = set()
    rows = []
    for c in chunks:
        url = c.url
        if not url and c.ref_type == "wiki" and str(c.ref_id).isdigit():
            page = WikiPage.objects.filter(id=int(c.ref_id)).first()
            if page:
                url = f"/wiki/{page.slug}"
        if not url or url in seen:
            continue
        seen.add(url)
        rows.append({"title": c.title or c.ref_id, "url": url})
    return rows


def answer(question: str) -> dict:
    chunks, retrieval = retrieve_with_mode(question)
    sources = build_sources(chunks)
    passages = "\n".join(f"[{i}] {c.title or c.ref_id}: {c.content[:700]}" for i, c in enumerate(chunks))
    prompt = f"Question : {question}\n\nPASSAGES :\n{passages}" if passages else f"Question : {question}"

    for provider_cls in AI_CHAIN:
        provider = provider_cls()
        try:
            out = provider.call({"prompt": prompt, "sources": sources}, timeout=20)
        except Exception:  # noqa: BLE001 - repli au mode suivant
            continue
        if out.get("mode") == "stub" or out.get("answer"):
            text = out.get("answer") or _stub_answer(chunks)
            return {"answer": text, "sources": sources, "mode": out.get("mode", "stub"), "retrieval": retrieval}

    return {"answer": _stub_answer(chunks), "sources": sources, "mode": "stub", "retrieval": retrieval}


def _stub_answer(chunks: list[KnowledgeChunk]) -> str:
    if not chunks:
        return "Aucun passage trouvé dans la base. Je vous invite à lancer une analyse pour vérifier cette information."
    titles = ", ".join(c.title or c.ref_id for c in chunks[:3])
    return f"Voici des éléments issus de la base : {titles}. Je vous invite à lancer une analyse pour aller plus loin."
