"""Fiabilité des sources et statut (M6) — dossier technique §12.

Le statut à 4 niveaux est calculé à partir des traces/sources.
La classification EMI (nature + désordre) provient du vocabulaire du document scanné
et reste une étiquette secondaire distincte du statut (DESIGN.md §7).
"""

STATUS_OK = "corroboree"
STATUS_WARN = "non_corroboree"
STATUS_BAD = "contredite"
STATUS_UNK = "indeterminee"

STATUS_LABELS = {
    STATUS_OK: "Corroborée",
    STATUS_WARN: "Non corroborée",
    STATUS_BAD: "Contredite",
    STATUS_UNK: "Indéterminée",
}

STATUS_PHRASES = {
    STATUS_OK: "Plusieurs sources indépendantes et fiables reprennent cette information, sans contradiction trouvée.",
    STATUS_WARN: "Des traces existent, mais trop peu de sources fiables et indépendantes. Ce n'est pas un « faux ».",
    STATUS_BAD: "Une vérification de faits publiée ou plusieurs sources fiables contredisent cette information.",
    STATUS_UNK: "Pas assez d'éléments, analyse partielle, ou désaccord entre insiders.",
}

NATURE_INFORMATION = "Information"
NATURE_OPINION = "Opinion"
NATURE_RUMEUR = "Rumeur"
NATURE_INFOX = "Infox"

DISORDER_MESINFORMATION = "Mésinformation"
DISORDER_DESINFORMATION = "Désinformation"
DISORDER_MALINFORMATION = "Malinformation"

# Mots-clés indiquant une tromperie/intention dans un verdict de fact-check (fr/en).
_DECEPTION_KEYWORDS = [
    "faux", "fausse", "trompeur", "trompeuse", "fabrication", "fabriqué", "détourné",
    "hors contexte", "false", "fake", "misleading", "fabricated", "doctored",
]
_OPINION_MARKERS = [
    "je pense que", "à mon avis", "selon moi", "je trouve que", "mon avis", "je crois que",
]

# Score de base par nature de site (dossier §12).
BASE_SCORE = {
    "agency": 90,
    "institution": 85,
    "media": 80,
    "blog": 40,
    "social": 30,
    "unknown": 20,
}


def classify_nature(text: str, has_sources: bool, contradicted: bool, corroborated: bool) -> str:
    lowered = (text or "").lower()
    if any(marker in lowered for marker in _OPINION_MARKERS):
        return NATURE_OPINION
    if contradicted:
        return NATURE_INFOX
    if corroborated and has_sources:
        return NATURE_INFORMATION
    return NATURE_RUMEUR


def classify_disorder(nature: str, factcheck_verdicts: list[str]) -> str | None:
    if nature != NATURE_INFOX:
        return None
    joined = " ".join(factcheck_verdicts).lower()
    if any(kw in joined for kw in _DECEPTION_KEYWORDS):
        return DISORDER_DESINFORMATION
    return DISORDER_MESINFORMATION


def _contradicts(fc) -> bool:
    """Les vérifications circulent en dict (résultat JSON) ou en objet (modèle)."""
    if isinstance(fc, dict):
        return bool(fc.get("contradicts"))
    return bool(getattr(fc, "contradicts", False))


def _verdict_of(fc) -> str:
    return (fc.get("verdict") or "") if isinstance(fc, dict) else (getattr(fc, "verdict", "") or "")


def compute_status(sources, factchecks, certifications, missing_essential: bool):
    """Applique les règles du dossier §12 dans l'ordre prescrit."""
    contradictions = [fc for fc in factchecks if _contradicts(fc)]
    contest_certs = [c for c in certifications if c["verdict"] == "contest"]
    certify_certs = [c for c in certifications if c["verdict"] == "certify"]

    if contradictions or (contest_certs and not certify_certs):
        return STATUS_BAD

    reliable = [s for s in sources if (s.get("score") or 0) >= 70]
    independent_domains = {s.get("domain") for s in reliable if s.get("domain")}

    if not sources and missing_essential:
        return STATUS_UNK

    if contradictions == [] and len(independent_domains) >= 2:
        return STATUS_OK

    if sources:
        return STATUS_WARN

    return STATUS_UNK


def build_result(analysis, sources, factchecks, certifications, missing, meta=None):
    """Construit le résultat complet d'une analyse (JSON servi au front)."""
    meta = meta or {}
    source_rows = [
        {
            "url": s.get("url", ""),
            "domain": s.get("domain", ""),
            "title": s.get("title", ""),
            "excerpt": s.get("excerpt", ""),
            "type": s.get("type", "unknown"),
            "score": s.get("score", 0),
            "position": s.get("position", "neutral"),
            "date": s.get("date"),
            "date_origin": s.get("date_origin", ""),
            "found_by": s.get("found_by", ""),
        }
        for s in sources
    ]

    factcheck_rows = [
        {
            "organization": fc.get("organization", ""),
            "verdict": fc.get("verdict", ""),
            "url": fc.get("url", ""),
            "published_date": fc.get("published_date"),
            "summary": fc.get("summary", ""),
            "contradicts": bool(fc.get("contradicts", False)),
        }
        for fc in factchecks
    ]

    missing_essential = any(m["service"] in {"recherche de texte", "recherche d'image"} for m in missing)

    status_key = compute_status(source_rows, factcheck_rows, certifications, missing_essential)
    nature = classify_nature(
        analysis.input_text or analysis.input_url or "",
        has_sources=bool(source_rows),
        contradicted=status_key == STATUS_BAD,
        corroborated=status_key == STATUS_OK,
    )
    disorder = classify_disorder(nature, [_verdict_of(fc) for fc in factcheck_rows])

    # Critères (5 lignes, dossier §6.3)
    independent = len({s.get("domain") for s in source_rows if (s.get("score") or 0) >= 70})
    criteria = [
        {
            "key": "sources_independantes",
            "label": "Sources indépendantes",
            "value": f"{independent} source(s) fiable(s) indépendante(s)",
            "ok": independent >= 2,
            "explanation": "Une source par domaine racine ; les reprises d'une même dépêche comptent pour une seule.",
        },
        {
            "key": "fiabilite",
            "label": "Fiabilité des sources",
            "value": _reliability_phrase(source_rows),
            "ok": any((s.get("score") or 0) >= 70 for s in source_rows),
            "explanation": "Score de base par nature de site (agence 90, institution 85, média 80, blog 40, réseau social 30, site inconnu 20).",
        },
        {
            "key": "verification_faits",
            "label": "Vérification de faits publiée",
            "value": f"{len(factcheck_rows)} vérification(s) recensée(s)",
            "ok": bool(factcheck_rows),
            "explanation": "Vérifications déjà publiées par des organismes de fact-checking.",
        },
        {
            "key": "anteriorite",
            "label": "Antériorité",
            "value": _anteriority_phrase(source_rows),
            "ok": bool(source_rows and any(s.get("date") for s in source_rows)),
            "explanation": "La plus ancienne trace trouvée, jamais « la première apparition » (aucune API ne la garantit).",
        },
        {
            "key": "certifications",
            "label": "Certifications des insiders",
            "value": f"{len(certifications)} avis (certifie/conteste)",
            "ok": bool(certify_certs_count(certifications)),
            "explanation": "Certifications signées, datées et journalisées ; les désaccords sont affichés sans trancher.",
        },
    ]

    return {
        "public_id": analysis.public_id,
        "status": status_key,
        "status_label": STATUS_LABELS[status_key],
        "status_phrase": STATUS_PHRASES[status_key],
        "nature": nature,
        "disorder": disorder,
        "extraction": meta,
        "criteria": criteria,
        "sources": source_rows,
        "factchecks": factcheck_rows,
        "certifications": certifications,
        "missing": missing,
        "created_at": analysis.created_at.isoformat(),
    }


def _reliability_phrase(sources):
    if not sources:
        return "Aucune source évaluée"
    best = max((s.get("score") or 0) for s in sources)
    if best >= 80:
        return "Élevée (agence / institution / média reconnu)"
    if best >= 70:
        return "Moyenne"
    return "Faible (blog / réseau social / site inconnu)"


def _anteriority_phrase(sources):
    dated = sorted([s for s in sources if s.get("date")], key=lambda s: s["date"])
    if not dated:
        return "Inconnue"
    return f"Plus ancienne trace : {dated[0]['date'][:10]} ({dated[0].get('date_origin', 'origine inconnue')})"


def certify_certs_count(certifications):
    return sum(1 for c in certifications if c["verdict"] == "certify")
