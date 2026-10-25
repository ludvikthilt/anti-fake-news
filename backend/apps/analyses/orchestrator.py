"""Orchestrateur d'analyse (M1) — dossier technique §6.

Exécution en thread (pool de 2 max), budget total de 25 s, chaque fournisseur 8 s.
Un module en erreur ou hors quota => résultat partial + « Modules indisponibles ».
"""
import logging
import threading
import time
from datetime import datetime

from django.utils import timezone

from . import extraction, providers, reliability
from .models import Analysis, Certification, FactCheck, MissingService, Source
from .readings import certification_rows

_semaphore = threading.Semaphore(2)
logger = logging.getLogger(__name__)

NORMALIZE_RE = __import__("re").compile(r"\s+")


def normalize(text: str) -> str:
    return NORMALIZE_RE.sub(" ", text or "").strip().lower()


def trigger_analysis(analysis_id):
    def _run():
        if not _semaphore.acquire(timeout=1):
            return
        try:
            run_analysis(analysis_id)
        except Exception:  # noqa: BLE001 - une analyse ne doit jamais rester « en cours »
            logger.exception("Analyse %s interrompue", analysis_id)
            Analysis.objects.filter(
                id=analysis_id, status__in=[Analysis.Status.PENDING, Analysis.Status.RUNNING]
            ).update(status=Analysis.Status.FAILED)
        finally:
            _semaphore.release()

    threading.Thread(target=_run, daemon=True).start()


def extract_link(url: str) -> str:
    import httpx
    from bs4 import BeautifulSoup

    try:
        resp = httpx.get(url, timeout=8, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    except Exception:  # noqa: BLE001
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup.find_all(["script", "style", "nav", "footer"]):
        tag.decompose()
    og = soup.find("meta", attrs={"property": "og:title"})
    title = og["content"] if og and og.get("content") else (soup.title.string if soup.title else "")
    body = " ".join(soup.get_text(" ", strip=True).split())[:2000]
    return f"{title} {body}".strip()


def _score_for_type(source_type: str) -> int:
    return reliability.BASE_SCORE.get(source_type, 20)


def _source_score(domain: str, source_type: str) -> int:
    """Score d'une source : nature du site, fiche locale et reconnaissance automatique."""
    from apps.knowledge import sites

    base = _score_for_type(source_type)
    if domain:
        sites.remember_domain(domain, nature=source_type, score=base)
        return sites.site_score(domain, base)
    return base


def _guess_type(domain: str, title: str) -> str:
    text = f"{domain} {title}".lower()
    for kw in ["gouvernement", ".gouv", "gov.", "un.org", "who.int", "minesec", "presidence"]:
        if kw in text:
            return "institution"
    for kw in ["crtv", "cameroon tribune", "lemonde", "rfi", "afp", "reuters", "bbc", "fr.news"]:
        if kw in text:
            return "media"
    for kw in ["twitter.com", "x.com", "facebook.com", "instagram", "tiktok", "youtube", "whatsapp", "t.me"]:
        if kw in text:
            return "social"
    if "blog" in text:
        return "blog"
    return "unknown"


def _date_from_item(item: dict):
    for key in ("published_date", "date", "publishedDate", "published_at"):
        if item.get(key):
            try:
                text = str(item[key]).replace("Z", "+00:00")
                return datetime.fromisoformat(text)
            except Exception:  # noqa: BLE001
                continue
    return None


def run_analysis(analysis_id):
    analysis = Analysis.objects.get(id=analysis_id)
    analysis.status = Analysis.Status.RUNNING
    analysis.save(update_fields=["status", "updated_at"])

    missing: list[dict] = []
    sources: list[dict] = []
    factchecks: list[dict] = []

    text = analysis.input_text or ""
    meta: dict = {}
    image_sources: list[dict] = []

    if analysis.input_type == Analysis.InputType.IMAGE and analysis.input_thumb:
        raw_b64 = analysis.input_thumb.split(",", 1)[1] if "," in analysis.input_thumb else analysis.input_thumb

        # OCR : OCR.space, puis saisie manuelle.
        # Le passage d'un moteur à l'autre est silencieux côté utilisateur (§7).
        ocr_result = providers_run([cls() for cls in providers.OCR_CHAIN], {"image_b64": raw_b64})
        ocr_text = (ocr_result.get("text") or "").strip()
        if ocr_text:
            text = ocr_text[:5000]
        ocr_engine = ocr_result.get("engine") or ("manuel" if ocr_result.get("manual") else "")
        if not ocr_text:
            missing += [{"service": m.get("provider", "OCR"), "reason": m.get("reason", "")} for m in ocr_result.get("missing", [])]

        from django.conf import settings

        from . import image_search, media as media_store

        token = media_store.store_image(analysis.input_thumb)
        image_url = f"{settings.BACKEND_BASE_URL}/api/media/{token}/"
        image_result = providers_run([cls() for cls in providers.IMAGE_CHAIN], {"image_url": image_url})
        started = image_search.launch(analysis.id, raw_b64)
        if started:
            meta["image_pending"] = True
            meta["image_search"] = "Apify (Google Lens)"
        if image_result.get("manual"):
            meta["image_tools"] = image_result.get("items", [])
        elif not started and not image_result.get("items"):
            # Aucun moteur n'a répondu et Lens n'a pas pu démarrer : on propose les moteurs publics.
            meta["image_tools"] = image_search.manual_tools()
        else:
            for item in image_result.get("items", []):
                link = item.get("link") or ""
                image_domain = providers.domain_of(link)
                image_sources.append({
                    "url": link,
                    "domain": image_domain,
                    "title": item.get("title", ""),
                    "excerpt": (item.get("snippet") or "")[:500],
                    "type": "unknown",
                    "score": _source_score(image_domain, "unknown"),
                    "position": "neutral",
                    "date": None,
                    "date_origin": "indexation",
                    "found_by": image_result.get("provider") or "recherche d'image",
                })
        if not started:
            missing += [{"service": m.get("provider", "recherche d'image"), "reason": m.get("reason", "")} for m in image_result.get("missing", [])]
        meta["source"] = "image"
        meta["ocr_text"] = ocr_text[:500]
        meta["ocr_engine"] = ocr_engine
        meta["phash"] = analysis.input_hash.removeprefix("image|")

    if analysis.input_type == Analysis.InputType.LINK and analysis.input_url:
        platform = extraction.social_platform(analysis.input_url)
        if platform:
            social = extraction.extract_social(analysis.input_url)
            if social.get("text"):
                text = social["text"]
                meta = {
                    "source": "post social",
                    "platform": platform,
                    "author": social.get("author", ""),
                    "title": social.get("title", ""),
                    "keywords": extraction.extract_keywords(text),
                }
        if not meta:
            art = extraction.extract_article(analysis.input_url)
            text = art.get("text") or text
            meta = {
                "source": "article",
                "author": art.get("author", ""),
                "title": art.get("title", ""),
                "date": art.get("date", ""),
                "date_origin": art.get("date_origin", ""),
                "keywords": extraction.extract_keywords(text),
            }

    query = normalize(text)[:300]

    # --- M3 : recherche de texte (chaîne de repli) ---
    if query:
        chain = [cls() for cls in providers.TEXT_CHAIN]
        result = providers_run(chain, {"query": query})
        for item in result.get("items", []):
            url = item.get("link") or item.get("url") or ""
            title = item.get("title") or ""
            domain = providers.domain_of(url)
            source_type = _guess_type(domain, title)
            sources.append({
                "url": url,
                "domain": domain,
                "title": title,
                "excerpt": (item.get("snippet") or item.get("content") or "")[:500],
                "type": source_type,
                "score": _source_score(domain, source_type),
                "position": "neutral",
                "date": None,
                "date_origin": "",
                "found_by": result.get("provider") or "recherche",
            })
        missing += [{"service": m.get("provider", "recherche de texte"), "reason": m.get("reason", "")} for m in result.get("missing", [])]

    # --- Vérifications de faits (M3) ---
    if query:
        chain = [cls() for cls in providers.FACTCHECK_CHAIN]
        result = providers_run(chain, {"query": query})
        factchecks += _parse_factchecks(result.get("items", []), query)
        missing += [{"service": m.get("provider", "vérifications de faits"), "reason": m.get("reason", "")} for m in result.get("missing", [])]

    # --- Base propre (repli ultime) : wiki + fiches de sites déjà rencontrés ---
    local_sources = _search_local_base(query)
    for ls in local_sources:
        if not any(s["domain"] == ls["domain"] for s in sources):
            sources.append(ls)
    for ims in image_sources:
        if ims["url"] and not any(s["url"] == ims["url"] for s in sources):
            sources.append(ims)

    # --- M5 : dates (plus ancienne trouvée, jamais « la première ») ---
    resolver = providers.DateResolver()
    for src in sources:
        if src.get("url") and not src.get("date"):
            d = resolver.call({"url": src["url"]}, timeout=8)
            if d.get("date"):
                src["date"] = d["date"].isoformat()
                src["date_origin"] = d.get("origin", "")
                src["position"] = _position_for(src, query)

    # --- Reconnaissance des sites cités (fiche locale, certification affichée) ---
    from apps.knowledge.models import SiteProfile
    from apps.knowledge import sites

    profiles = {
        p.domain: p
        for p in SiteProfile.objects.filter(
            domain__in={s.get("domain") for s in sources if s.get("domain")}
        )
    }
    for src in sources:
        profile = profiles.get(src.get("domain"))
        src["certified"] = bool(profile and profile.certified)

    # --- Lectures des insiders déjà déposées ---
    certifications = certification_rows(Certification.TargetType.ANALYSIS, analysis.id)

    result = reliability.build_result(analysis, sources, factchecks, certifications, missing, meta)

    # --- Corroboration constatée par le système : elle fait progresser les sites cités ---
    if result["status"] == reliability.STATUS_OK:
        reliable_domains = [s["domain"] for s in sources if (s.get("score") or 0) >= 70 and s.get("domain")]
        try:
            sites.record_corroborations(reliable_domains, analysis=analysis)
        except Exception:  # noqa: BLE001 - la reconnaissance ne doit pas casser l'analyse
            logger.exception("Reconnaissance des sites impossible pour l'analyse %s", analysis.id)

    # Persistance
    Source.objects.filter(analysis=analysis).delete()
    FactCheck.objects.filter(analysis=analysis).delete()
    MissingService.objects.filter(analysis=analysis).delete()

    for s in sources:
        Source.objects.create(
            analysis=analysis,
            url=(s.get("url") or "")[:1000],
            domain=(s.get("domain") or "")[:255],
            title=s.get("title", "")[:255],
            excerpt=s.get("excerpt", ""),
            source_type=s.get("type", "unknown"),
            reliability_score=s.get("score", 0),
            position=s.get("position", "neutral"),
            date_value=_parse_dt(s.get("date")),
            date_origin=s.get("date_origin", ""),
            found_by=s.get("found_by", ""),
        )
    for fc in factchecks:
        FactCheck.objects.create(
            analysis=analysis,
            organization=fc.get("organization", "")[:255],
            verdict=fc.get("verdict", "")[:500],
            url=fc.get("url", "")[:1000],
            summary=fc.get("summary", ""),
            contradicts=fc.get("contradicts", False),
        )
    for m in missing:
        MissingService.objects.create(analysis=analysis, service=m.get("service", "")[:64], reason=m.get("reason", "")[:255])

    analysis.result = result
    analysis.status = Analysis.Status.PARTIAL if missing else Analysis.Status.DONE
    analysis.save(update_fields=["result", "status", "updated_at"])

    if analysis.user:
        try:
            from apps.notifications.services import notify_analysis_done

            notify_analysis_done(analysis.user, analysis)
        except Exception:  # noqa: BLE001 - la notification ne doit jamais casser l'analyse
            pass


def providers_run(chain, payload):
    """Chaîne de repli avec coupe-circuit et quotas (règle générale du dossier §6)."""
    from django.conf import settings

    from apps.core.services import breaker, quota

    missing = []
    deadline = time.monotonic() + settings.ANALYSIS_BUDGET_SECONDS
    for provider in chain:
        if time.monotonic() > deadline:
            missing.append({"provider": provider.name, "reason": "budget total épuisé"})
            break
        account = getattr(provider, "account", provider.name)
        if breaker.is_open(account):
            missing.append({"provider": provider.name, "reason": "indisponible (coupe-circuit)"})
            continue
        if not quota.can_call(account):
            missing.append({"provider": provider.name, "reason": "quota épuisé"})
            continue
        try:
            out = provider.call(payload, timeout=min(settings.PROVIDER_TIMEOUT_SECONDS, max(1, deadline - time.monotonic())))
            quota.record(account)
            out["provider"] = provider.name
            out["missing"] = missing
            return out
        except providers.ProviderUnavailable as exc:
            # clé absente / non configurée : pas une panne, on ne déclenche pas le coupe-circuit
            missing.append({"provider": provider.name, "reason": str(exc)[:120]})
        except Exception as exc:  # noqa: BLE001 - 429/5xx/délai : on ouvre le coupe-circuit
            breaker.open(account)
            missing.append({"provider": provider.name, "reason": str(exc)[:120]})
    return {"empty": True, "missing": missing}


def _tokens(text: str) -> set[str]:
    import re

    return {w for w in re.findall(r"\w+", (text or "").lower()) if len(w) >= 3}


def _claim_coverage(claim_text: str, query: str) -> float:
    """Part des mots significatifs de la vérification présents dans la demande.

    L'API Fact Check Tools renvoie des affirmations *approchantes* : sans ce contrôle,
    une vérification sur un autre sujet (« un stadier décède après la finale ») suffirait
    à déclarer « Contredite » une information qui n'a rien à voir.
    """
    claim_tokens = _tokens(claim_text)
    if not claim_tokens:
        return 0.0
    return len(claim_tokens & _tokens(query)) / len(claim_tokens)


def _parse_factchecks(items, query: str = ""):
    from django.conf import settings

    threshold = getattr(settings, "FACTCHECK_MIN_COVERAGE", 0.5)
    rows = []
    for claim in items[:5]:
        claim_text = claim.get("text", "")
        if query and _claim_coverage(claim_text, query) < threshold:
            continue  # affirmation différente : elle n'établit rien sur celle-ci
        reviews = claim.get("claimReview") or []
        for review in reviews[:2]:
            verdict = review.get("textualRating") or claim.get("text", "")[:200]
            rows.append({
                "organization": (review.get("publisher") or {}).get("name", "Organisme de vérification"),
                "verdict": verdict,
                "url": review.get("url", ""),
                "published_date": review.get("reviewDate"),
                "summary": claim_text[:300],
                "contradicts": any(kw in verdict.lower() for kw in ["faux", "fausse", "trompeur", "trompeuse", "false", "fake", "misleading", "fabricat"]),
            })
    return rows


def _search_local_base(query: str):
    """Repli ultime : recherche par mots-clés dans la base propre (wiki, fiches de sites)."""
    import re

    from django.db.models import Q

    from apps.knowledge.models import KnowledgeChunk, SiteProfile

    if not query:
        return []
    words = [w for w in re.split(r"\W+", normalize(query)) if len(w) >= 4][:8]
    if not words:
        return []

    q = Q()
    for w in words:
        q |= Q(content__icontains=w)
    chunks = KnowledgeChunk.objects.filter(q)[:12]

    rows = []
    for chunk in chunks:
        if not chunk.url:
            continue  # fragments wiki sans lien citable : réservés au chatbot, pas à la chronologie
        lowered = chunk.content.lower()
        matched = sum(1 for w in words if w in lowered)
        if not matched:
            continue
        profile = SiteProfile.objects.filter(domain=chunk.ref_id).first() if chunk.ref_type == "site" else None
        score = (_score_for_type(profile.nature) if profile else 20) + min(10, 4 * matched)
        if profile and profile.certified:
            from apps.knowledge import sites

            score = min(score + sites.quota_bonus(), 98)
        rows.append({
            "url": chunk.url or "",
            "domain": providers.domain_of(chunk.url) if chunk.url else (profile.domain if profile else ""),
            "title": chunk.title or "",
            "excerpt": chunk.content[:300],
            "type": profile.nature if profile else "unknown",
            "score": score,
            "position": "corroborates",
            "date": None,
            "date_origin": "",
            "found_by": "base propre",
        })
    rows.sort(key=lambda r: -r["score"])
    return rows[:5]


def _position_for(source: dict, query: str) -> str:
    if (source.get("score") or 0) >= 70 and query and query[:40] in (source.get("excerpt") or "").lower():
        return "corroborates"
    return "neutral"


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:  # noqa: BLE001
        return None
