"""M2 — Extraction fine d'un lien (dossier technique §8).

- Article : trafilatura (texte, auteur, date) avec repli BeautifulSoup.
- Mots-clés : YAKE (français).
- Post de réseau social : oEmbed pour Mastodon, Bluesky, TikTok (repli : collage manuel).
"""
from urllib.parse import urlparse

import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; anti-fake-news/1.0)"}


def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:  # noqa: BLE001
        return url


def extract_article(url: str) -> dict:
    """Extrait titre, texte, auteur et date d'un article web (M2)."""
    import trafilatura
    from bs4 import BeautifulSoup

    result = {"url": url, "title": "", "text": "", "author": "", "date": "", "date_origin": ""}
    try:
        resp = httpx.get(url, timeout=8, follow_redirects=True, headers=HEADERS)
        resp.raise_for_status()
    except Exception:  # noqa: BLE001
        return result

    html = resp.text
    doc = None
    try:
        doc = trafilatura.bare_extraction(html, url=url, with_metadata=True)
    except Exception:  # noqa: BLE001
        doc = None

    if doc is not None:
        result["title"] = getattr(doc, "title", "") or ""
        result["author"] = getattr(doc, "author", "") or ""
        date_str = getattr(doc, "date", "") or ""
        if date_str:
            result["date"] = str(date_str)
            result["date_origin"] = "declared"
        result["text"] = (getattr(doc, "text", "") or getattr(doc, "raw_text", "") or "").strip()

    if not result["text"]:
        # Repli : suppression des scripts/styles puis extraction du corps.
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()
        og = soup.find("meta", attrs={"property": "og:title"})
        if not result["title"]:
            result["title"] = og["content"] if og and og.get("content") else (soup.title.string if soup.title else "")
        result["text"] = " ".join(soup.get_text(" ", strip=True).split())[:5000]

    result["text"] = result["text"][:5000]
    return result


def extract_keywords(text: str, top: int = 8) -> list[str]:
    """Extrait les mots-clés principaux (YAKE, français)."""
    import yake

    if not text or len(text) < 20:
        return []
    try:
        extractor = yake.KeywordExtractor(lan="fr", top=top, n=2, dedupLim=0.9)
        return [kw for kw, _ in extractor.extract_keywords(text)]
    except Exception:  # noqa: BLE001
        return []


def social_platform(url: str) -> str | None:
    host = domain_of(url)
    if host.endswith("bsky.app"):
        return "bluesky"
    if host.endswith("tiktok.com"):
        return "tiktok"
    # Mastodon : instance auto-hébergée (mastodon.social, etc.)
    if any(k in host for k in ("mastodon.", "mstdn.", "social.", "piaille.", "framapiaf.")):
        return "mastodon"
    return None


def _oembed(endpoint: str, url: str) -> dict:
    try:
        resp = httpx.get(endpoint, params={"url": url}, timeout=8, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()
    except Exception:  # noqa: BLE001
        return {}


def extract_social(url: str) -> dict:
    """Récupère un post Mastodon / Bluesky / TikTok via oEmbed (M2)."""
    platform = social_platform(url)
    if platform == "bluesky":
        data = _oembed("https://embed.bsky.app/oembed", url)
    elif platform == "tiktok":
        data = _oembed("https://www.tiktok.com/oembed", url)
    elif platform == "mastodon":
        instance = urlparse(url).netloc
        data = _oembed(f"https://{instance}/api/oembed", url)
    else:
        return {"url": url, "platform": None, "title": "", "author": "", "text": ""}

    return {
        "url": url,
        "platform": platform,
        "title": data.get("title", ""),
        "author": data.get("author_name", "") or data.get("author_url", ""),
        "text": " ".join(str(data.get("title", "")).split())[:2000],
    }
