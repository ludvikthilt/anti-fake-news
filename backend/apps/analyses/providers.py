"""Fournisseurs externes réels — dossier technique §7-8-11 et récapitulatif §2.

Chaque fournisseur est derrière une interface `call(payload, timeout)`.
Sans clé, `call` lève ProviderUnavailable : la chaîne passe au fournisseur suivant
puis au repli manuel, sans faire échouer l'analyse.
"""
import base64
import re
from datetime import datetime
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from django.conf import settings


class ProviderUnavailable(Exception):
    pass


class BaseProvider:
    name = "base"
    account = "base"

    def call(self, payload: dict, timeout: float = 8):
        raise NotImplementedError


# ---------------------------------------------------------------- recherche web (M3)


class TavilyProvider(BaseProvider):
    name = "Tavily"
    account = "tavily"

    def call(self, payload, timeout=8):
        if not settings.TAVILY_API_KEY:
            raise ProviderUnavailable("clé Tavily absente")
        resp = httpx.post(
            "https://api.tavily.com/search",
            json={"api_key": settings.TAVILY_API_KEY, "query": payload.get("query", ""), "max_results": 5, "include_answer": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "text", "items": resp.json().get("results", [])}


class SerperProvider(BaseProvider):
    name = "Serper"
    account = "serper"

    def call(self, payload, timeout=8):
        if not settings.SERPER_API_KEY:
            raise ProviderUnavailable("clé Serper absente")
        resp = httpx.post(
            "https://google.serper.dev/search",
            json={"q": payload.get("query", ""), "gl": "cm", "hl": "fr"},
            headers={"X-API-KEY": settings.SERPER_API_KEY},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"kind": "text", "items": data.get("organic", [])}


class SerpApiProvider(BaseProvider):
    name = "SerpApi"
    account = "serpapi"
    engine = "google"

    def call(self, payload, timeout=8):
        if not settings.SERPAPI_API_KEY:
            raise ProviderUnavailable("clé SerpApi absente")
        resp = httpx.get(
            "https://serpapi.com/search.json",
            params={"engine": self.engine, "q": payload.get("query", ""), "api_key": settings.SERPAPI_API_KEY, "hl": "fr", "gl": "cm"},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"kind": "text", "items": data.get("organic_results", [])}


class SearchAPIProvider(BaseProvider):
    name = "SearchAPI.io"
    account = "searchapi"

    def call(self, payload, timeout=8):
        if not settings.SEARCHAPI_API_KEY:
            raise ProviderUnavailable("clé SearchAPI.io absente")
        resp = httpx.get(
            "https://www.searchapi.io/api/v1/search",
            params={"engine": "google", "q": payload.get("query", ""), "api_key": settings.SEARCHAPI_API_KEY, "hl": "fr"},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "text", "items": resp.json().get("organic_results", [])}


class ExaProvider(BaseProvider):
    name = "Exa"
    account = "exa"

    def call(self, payload, timeout=8):
        if not settings.EXA_API_KEY:
            raise ProviderUnavailable("clé Exa absente")
        resp = httpx.post(
            "https://api.exa.ai/search",
            json={"query": payload.get("query", ""), "numResults": 5},
            headers={"x-api-key": settings.EXA_API_KEY},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "text", "items": resp.json().get("results", [])}


class ManualTextProvider(BaseProvider):
    name = "Base propre"
    account = "manual"

    def call(self, payload, timeout=8):
        return {"kind": "text", "items": [], "manual": True}


TEXT_CHAIN = [TavilyProvider, SerperProvider, SerpApiProvider, SearchAPIProvider, ExaProvider, ManualTextProvider]


# ---------------------------------------------------------------- fact-check


class FactCheckToolsProvider(BaseProvider):
    name = "Fact Check Tools"
    account = "factcheck"

    def call(self, payload, timeout=8):
        if not settings.FACTCHECK_API_KEY:
            raise ProviderUnavailable("clé Fact Check Tools absente")
        resp = httpx.get(
            "https://factchecktools.googleapis.com/v1alpha1/claims:search",
            params={"query": payload.get("query", ""), "key": settings.FACTCHECK_API_KEY, "languageCode": "fr"},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "factcheck", "items": resp.json().get("claims", [])}


class ManualFactCheckProvider(BaseProvider):
    name = "Base des vérifications"
    account = "manual_factcheck"

    def call(self, payload, timeout=8):
        from .models import FactCheck  # noqa: PLC0415

        qs = FactCheck.objects.none()
        return {"kind": "factcheck", "items": list(qs), "manual": True}


FACTCHECK_CHAIN = [FactCheckToolsProvider, ManualFactCheckProvider]


# ---------------------------------------------------------------- OCR (M4)


class OCRSpaceProvider(BaseProvider):
    name = "OCR.space"
    account = "ocrspace"

    def call(self, payload, timeout=8):
        if not settings.OCRSPACE_API_KEY:
            raise ProviderUnavailable("clé OCR.space absente")
        image = payload.get("image_b64", "")
        resp = httpx.post(
            "https://api.ocr.space/parse/image",
            data={"apikey": settings.OCRSPACE_API_KEY, "language": "fre", "base64Image": f"data:image/jpeg;base64,{image}", "isOverlayRequired": "false"},
            timeout=timeout,
        )
        resp.raise_for_status()
        parsed = resp.json()
        if parsed.get("IsErroredOnProcessing"):
            raise ProviderUnavailable(str(parsed.get("ErrorMessage") or "OCR.space : erreur")[:120])
        text = "".join(item.get("ParsedText", "") for item in parsed.get("ParsedResults", []))
        if not text.strip():
            raise ProviderUnavailable("OCR.space : aucun texte détecté")
        return {"kind": "ocr", "text": text, "engine": self.name}


class ManualOCRProvider(BaseProvider):
    name = "OCR manuel"
    account = "manual_ocr"

    def call(self, payload, timeout=8):
        return {"kind": "ocr", "text": "", "manual": True}


OCR_CHAIN = [OCRSpaceProvider, ManualOCRProvider]


# ---------------------------------------------------------------- recherche inversée d'image (M4)


def _image_results(data: dict, key: str) -> list[dict]:
    rows = []
    for item in data.get(key, [])[:5]:
        link = item.get("link") or item.get("source") or item.get("original") or ""
        if not link:
            continue
        rows.append({"link": link, "title": item.get("title", "") or item.get("source", ""), "snippet": item.get("source", "") or ""})
    return rows


class SerpApiYandexImagesProvider(BaseProvider):
    name = "SerpApi (Yandex images)"
    account = "serpapi_images"

    def call(self, payload, timeout=8):
        if not settings.SERPAPI_API_KEY:
            raise ProviderUnavailable("clé SerpApi absente")
        resp = httpx.get(
            "https://serpapi.com/search.json",
            params={"engine": "yandex_images", "url": payload.get("image_url", ""), "api_key": settings.SERPAPI_API_KEY},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "image", "items": _image_results(resp.json(), "images_results")}


class SerpApiGoogleLensProvider(BaseProvider):
    name = "SerpApi (Google Lens)"
    account = "serpapi_lens"

    def call(self, payload, timeout=8):
        if not settings.SERPAPI_API_KEY:
            raise ProviderUnavailable("clé SerpApi absente")
        resp = httpx.get(
            "https://serpapi.com/search.json",
            params={"engine": "google_lens", "url": payload.get("image_url", ""), "api_key": settings.SERPAPI_API_KEY},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "image", "items": _image_results(resp.json(), "visual_matches")}


class SearchApiGoogleLensProvider(BaseProvider):
    name = "SearchAPI.io (Google Lens)"
    account = "searchapi_lens"

    def call(self, payload, timeout=8):
        if not settings.SEARCHAPI_API_KEY:
            raise ProviderUnavailable("clé SearchAPI.io absente")
        resp = httpx.get(
            "https://www.searchapi.io/api/v1/search",
            params={"engine": "google_lens", "url": payload.get("image_url", ""), "api_key": settings.SEARCHAPI_API_KEY},
            timeout=timeout,
        )
        resp.raise_for_status()
        return {"kind": "image", "items": _image_results(resp.json(), "visual_matches")}


class ApifyImageProvider(BaseProvider):
    """Google Lens via Apify — démarrage asynchrone (§7 : le traitement ne bloque pas l'analyse).

    L'acteur `borderline~google-lens` travaille en base64 (aucune URL publique requise) et
    prend ~1 min : `start` lance l'exécution, `fetch` lit le jeu de données dès qu'il est prêt.
    """

    name = "Apify (Google Lens)"
    account = "apify_lens"

    def start(self, image_b64: str, search_types: tuple[str, ...] = ("visual-match",), timeout=8):
        if not settings.APIFY_API_KEY:
            raise ProviderUnavailable("clé Apify absente")
        # L'API Apify attend « utilisateur~acteur », pas « utilisateur/acteur ».
        actor = settings.APIFY_LENS_ACTOR.replace("/", "~")
        resp = httpx.post(
            f"https://api.apify.com/v2/acts/{actor}/runs",
            params={"token": settings.APIFY_API_KEY},
            json={"searchTypes": list(search_types), "imagesBase64": [image_b64], "language": "fr"},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {"run_id": data.get("id", ""), "dataset_id": data.get("defaultDatasetId", "")}

    def fetch(self, dataset_id: str, timeout=8) -> list[dict]:
        resp = httpx.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
            params={"token": settings.APIFY_API_KEY, "clean": "true"},
            timeout=timeout,
        )
        resp.raise_for_status()
        items = resp.json()
        return items if isinstance(items, list) else []

    def call(self, payload, timeout=8):
        raise ProviderUnavailable("Apify Lens : exécution asynchrone")


class ManualImageProvider(BaseProvider):
    name = "Moteurs d'image publics"
    account = "manual_image"

    def call(self, payload, timeout=8):
        return {
            "kind": "image",
            "items": [
                {"link": "https://lens.google.com/", "title": "Google Lens", "snippet": "Ouvrir Google Lens et importer l'image"},
                {"link": "https://tineye.com/", "title": "TinEye", "snippet": "Recherche inversée d'image"},
                {"link": "https://yandex.com/images/", "title": "Yandex Images", "snippet": "Recherche inversée d'image"},
            ],
            "manual": True,
        }


# Chaîne synchrone : seuls les moteurs qui répondent en quelques secondes (URL publique).
# Apify Lens (base64, ~1 min) est lancé en parallèle et fusionné dès réception.
IMAGE_CHAIN = [SerpApiYandexImagesProvider, SerpApiGoogleLensProvider, SearchApiGoogleLensProvider, ManualImageProvider]


# ---------------------------------------------------------------- dates (M5)


class DateResolver:
    """Lit article:published_time, datePublished ou Last-Modified (jamais sans origine)."""

    name = "DateResolver"
    account = "dateresolver"

    def call(self, payload, timeout=8):
        url = payload.get("url", "")
        try:
            resp = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as exc:  # noqa: BLE001
            return {"kind": "date", "date": None, "origin": None, "reason": str(exc)[:80]}
        soup = BeautifulSoup(resp.text, "html.parser")
        declared = soup.find("meta", attrs={"property": "article:published_time"})
        if not declared:
            declared = soup.find("meta", attrs={"itemprop": "datePublished"})
        if declared and declared.get("content"):
            dt = self._parse(declared["content"])
            if dt:
                return {"kind": "date", "date": dt, "origin": "declared"}
        lastmod = resp.headers.get("Last-Modified")
        if lastmod:
            dt = self._parse(lastmod)
            if dt:
                return {"kind": "date", "date": dt, "origin": "metadata"}
        return {"kind": "date", "date": None, "origin": None, "reason": "date absente"}

    def _parse(self, value):
        try:
            text = value.strip()
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            return None


# ---------------------------------------------------------------- IA (M9)


class StubAIProvider(BaseProvider):
    name = "Stub"
    account = "stub"

    def call(self, payload, timeout=8):
        return {"kind": "ai", "mode": "stub", "answer": "", "sources": payload.get("sources", [])}


class GroqProvider(BaseProvider):
    name = "Groq"
    account = "groq"

    def call(self, payload, timeout=8):
        if not settings.GROQ_API_KEY:
            raise ProviderUnavailable("clé Groq absente")
        from groq import Groq  # noqa: PLC0415

        client = Groq(api_key=settings.GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "system", "content": CHATBOT_SYSTEM}, {"role": "user", "content": payload.get("prompt", "")}],
            max_tokens=200,
        )
        return {"kind": "ai", "mode": "groq", "answer": resp.choices[0].message.content, "sources": payload.get("sources", [])}


class GeminiProvider(BaseProvider):
    """1re option de génération ; en cas de saturation (503), bascule de modèle sans bruit."""

    name = "Gemini"
    account = "gemini"

    def call(self, payload, timeout=8):
        if not settings.GEMINI_API_KEY:
            raise ProviderUnavailable("clé Gemini absente")
        from google import genai  # noqa: PLC0415

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        models = list(
            dict.fromkeys(
                [settings.GEMINI_MODEL, getattr(settings, "GEMINI_MODEL_FALLBACK", ""), "gemini-3.5-flash"]
            )
        )
        last_error = None
        for model in [m for m in models if m]:
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=f"{CHATBOT_SYSTEM}\n\n{payload.get('prompt', '')}",
                )
                text = (getattr(resp, "text", "") or "").strip()
                if text:
                    return {"kind": "ai", "mode": "gemini", "model": model, "answer": text, "sources": payload.get("sources", [])}
                last_error = ProviderUnavailable(f"Gemini ({model}) : réponse vide")
            except Exception as exc:  # noqa: BLE001 - modèle saturé ou indisponible : on essaie le suivant
                last_error = exc
                continue
        raise last_error or ProviderUnavailable("Gemini indisponible")


AI_CHAIN = [GeminiProvider, GroqProvider, StubAIProvider]

CHATBOT_SYSTEM = (
    "Tu es l'assistant de redirection d'une plateforme de vérification de l'information. "
    "Réponds en français, en 3 phrases au plus, uniquement à partir des PASSAGES fournis. "
    "Cite les passages par leur numéro [n]. Si les passages ne suffisent pas, dis-le et propose "
    "de lancer une analyse. Ne dis jamais qu'une information est vraie ou fausse."
)


def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:  # noqa: BLE001
        return url
