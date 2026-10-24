"""Recherche inversée d'image (M4) — Google Lens via Apify, sans rupture visible.

L'acteur Apify travaille en base64 (aucune URL publique n'est nécessaire) mais prend
environ une minute : il est donc lancé dès le début de l'analyse, l'OCR et la recherche
de texte aboutissent normalement, puis les correspondances visuelles sont fusionnées
dans le résultat dès qu'elles arrivent (même après l'affichage de la page).
"""
import threading
import time
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings

from . import providers


def manual_tools() -> list[dict]:
    return providers.ManualImageProvider().call({}).get("items", [])


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:  # noqa: BLE001
        return ""


def parse_items(items: list[dict]) -> list[dict]:
    """Transforme le jeu de données Apify (une ligne par type de recherche) en sources."""
    rows = []
    for item in items:
        block = item.get("visual-match") or {}
        for match in (block.get("results") or [])[:5]:
            link = (match.get("link") or "").strip()
            if not link.startswith("http"):
                continue
            snippet = " ".join(part for part in (match.get("source", ""), match.get("price", "")) if part)
            rows.append(
                {
                    "url": link,
                    "domain": _domain(link),
                    "title": (match.get("title") or "")[:250],
                    "excerpt": snippet[:500],
                    "type": "unknown",
                    "score": 20,
                    "position": "neutral",
                    "date": None,
                    "date_origin": "indexation",
                    "found_by": "Apify (Google Lens)",
                }
            )
    return rows


def start(image_b64: str, search_types: tuple[str, ...] = ("visual-match",)) -> dict | None:
    if not settings.APIFY_API_KEY:
        return None
    try:
        return providers.ApifyImageProvider().start(image_b64, search_types=search_types)
    except Exception:  # noqa: BLE001 - la recherche d'image ne casse jamais l'analyse
        return None


def launch(analysis_id, image_b64: str) -> dict | None:
    """Lance l'exécution Apify et la fusion différée ; renvoie l'identifiant de suivi."""
    started = start(image_b64)
    if not started or not started.get("dataset_id"):
        return None
    threading.Thread(
        target=wait_and_enrich,
        args=(analysis_id, started["dataset_id"]),
        daemon=True,
        name=f"lens-{analysis_id}",
    ).start()
    return started


def wait_and_enrich(analysis_id, dataset_id: str, budget: int | None = None):
    """Attend (au plus IMAGE_ENRICH_BUDGET_SECONDS) le résultat Apify puis le fusionne."""
    deadline = time.monotonic() + (budget or settings.IMAGE_ENRICH_BUDGET_SECONDS)
    provider = providers.ApifyImageProvider()
    while time.monotonic() < deadline:
        try:
            rows = parse_items(provider.fetch(dataset_id))
        except Exception:  # noqa: BLE001 - exécution encore en cours ou réseau
            rows = []
        if rows:
            merge(analysis_id, rows)
            return
        time.sleep(5)
    clear_pending(analysis_id)


def clear_pending(analysis_id):
    from .models import Analysis

    analysis = Analysis.objects.filter(id=analysis_id).first()
    if not analysis or not analysis.result:
        return
    extraction = analysis.result.get("extraction") or {}
    if extraction.get("image_pending"):
        extraction["image_pending"] = False
        analysis.result["extraction"] = extraction
        analysis.save(update_fields=["result", "updated_at"])


def merge(analysis_id, rows: list[dict]):
    """Ajoute les correspondances visuelles au résultat et recalcule le statut."""
    from . import reliability
    from .models import Analysis, Source

    analysis = Analysis.objects.filter(id=analysis_id).first()
    if not analysis or not analysis.result:
        return

    result = dict(analysis.result)
    sources = list(result.get("sources") or [])
    known = {s.get("url") for s in sources}
    added = [row for row in rows if row["url"] not in known]
    extraction = dict(result.get("extraction") or {})
    extraction["image_pending"] = False

    if not added:
        result["extraction"] = extraction
        analysis.result = result
        analysis.save(update_fields=["result", "updated_at"])
        return

    sources.extend(added)
    result = reliability.build_result(
        analysis,
        sources,
        result.get("factchecks") or [],
        result.get("certifications") or [],
        result.get("missing") or [],
        extraction,
    )
    analysis.result = result
    analysis.save(update_fields=["result", "updated_at"])

    Source.objects.filter(analysis=analysis, found_by="Apify (Google Lens)").delete()
    for row in added:
        Source.objects.create(
            analysis=analysis,
            url=row.get("url", ""),
            domain=row.get("domain", ""),
            title=row.get("title", "")[:255],
            excerpt=row.get("excerpt", ""),
            source_type=row.get("type", "unknown"),
            reliability_score=row.get("score", 0),
            position=row.get("position", "neutral"),
            date_value=_parse_dt(row.get("date")),
            date_origin=row.get("date_origin", ""),
            found_by=row.get("found_by", ""),
        )


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:  # noqa: BLE001
        return None
