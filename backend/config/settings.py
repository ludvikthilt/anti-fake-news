"""Configuration Django d'InfoxVerify (MVP)."""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-change-me")
DEBUG = os.environ.get("DEBUG", "true").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "apps.core",
    "apps.accounts",
    "apps.analyses",
    "apps.knowledge",
    "apps.notifications",
    "apps.adminpanel",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://postgres:postgres@localhost:5432/antifake",
        conn_max_age=600,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # Limitation de débit appliquée à toutes les vues API : le taux suit le statut
    # du demandeur (visiteur par IP, inscrit par compte) — dossier §6.
    "DEFAULT_THROTTLE_CLASSES": ("apps.core.throttling.DualRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "default_anon": "60/min",
        "default_user": "120/min",
        # Actions coûteuses : une soumission consomme des crédits fournisseurs.
        "analysis_anon": "10/min",
        "analysis_user": "30/min",
        "chat_anon": "20/min",
        "chat_user": "60/min",
        "certify_anon": "10/min",
        "certify_user": "30/min",
        # Authentification : freine les essais de mots de passe.
        "auth": "10/min",
        "register": "5/hour",
        "internal": "10/min",
    },
}

from datetime import timedelta  # noqa: E402 - après les réglages qui l'entourent

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "InfoxVerify — API",
    "VERSION": "1.1",
}

CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()
]
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# --- Services externes (clés en variables d'environnement) ---
SEARCH_PROVIDER = os.environ.get("SEARCH_PROVIDER", "manual")  # tavily | serper | serpapi | searchapi | exa | manual
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")
SEARCHAPI_API_KEY = os.environ.get("SEARCHAPI_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
FACTCHECK_API_KEY = os.environ.get("FACTCHECK_API_KEY", "")
OCRSPACE_API_KEY = os.environ.get("OCRSPACE_API_KEY", "")
APIFY_API_KEY = os.environ.get("APIFY_API_KEY", "")
APIFY_LENS_ACTOR = os.environ.get("APIFY_LENS_ACTOR", "borderline~google-lens")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")
# Modèle de secours si le premier est saturé (503 très fréquent sur les modèles « latest »).
GEMINI_MODEL_FALLBACK = os.environ.get("GEMINI_MODEL_FALLBACK", "gemini-3.5-flash")
GEMINI_EMBED_MODEL = os.environ.get("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
AI_MODE = os.environ.get("AI_MODE", "groq")  # stub | groq | gemini
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@antifake.local")
# Telegram — canal gratuit et illimité : bot, webhook signé par un secret dédié.
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME", "")
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
# Web Push (VAPID) — clé privée base64url (32 octets), publique dérivée automatiquement.
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:contact@antifake.local")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN", "")  # jeton du planificateur (GitHub Actions)
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://127.0.0.1:8000")  # base publique du backend (hébergement éphémère)

PROVIDER_TIMEOUT_SECONDS = int(os.environ.get("PROVIDER_TIMEOUT_SECONDS", "8"))
ANALYSIS_BUDGET_SECONDS = int(os.environ.get("ANALYSIS_BUDGET_SECONDS", "25"))
# Recherche inversée d'image (Apify Lens) : démarrage immédiat, résultats fusionnés dès réception.
IMAGE_ENRICH_BUDGET_SECONDS = int(os.environ.get("IMAGE_ENRICH_BUDGET_SECONDS", "180"))
# RAG : dimension des embeddings Gemini (gemini-embedding-001 accepte 768/1536/3072).
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", "768"))
CACHE_TTL_TEXT_HOURS = int(os.environ.get("CACHE_TTL_TEXT_HOURS", "6"))
CACHE_TTL_IMAGE_HOURS = int(os.environ.get("CACHE_TTL_IMAGE_HOURS", "24"))
# Seuil d'alerte des quotas fournisseurs (journal + AuditLog, une fois par mois).
QUOTA_ALERT_RATIO = float(os.environ.get("QUOTA_ALERT_RATIO", "0.8"))
# Plafonds mensuels par compte fournisseur (dossier §6 : pool de quotas).
# 0 = pas de plafond connu ; surchargeable par QUOTA_LIMIT_<COMPTE>.
def _quota(account: str, default: int) -> int:
    return int(os.environ.get(f"QUOTA_LIMIT_{account.upper()}", str(default)))


# Reconnaissance automatique d'un site fiable (aucune lecture isolée ne suffit) :
# corroborations constatées par le système + insiders distincts qui le certifient.
SITE_SYSTEM_QUOTA = int(os.environ.get("SITE_SYSTEM_QUOTA", "5"))
SITE_INSIDER_QUOTA = int(os.environ.get("SITE_INSIDER_QUOTA", "3"))
SITE_CERTIFY_BONUS = int(os.environ.get("SITE_CERTIFY_BONUS", "10"))

QUOTA_LIMITS = {
    "tavily": _quota("tavily", 1000),
    "serper": _quota("serper", 2500),
    "serpapi": _quota("serpapi", 100),
    "searchapi": _quota("searchapi", 100),
    "exa": _quota("exa", 1000),
    "factcheck": _quota("factcheck", 0),
    "ocrspace": _quota("ocrspace", 25000),
    "apify_lens": _quota("apify_lens", 0),
    "groq": _quota("groq", 0),
    "gemini": _quota("gemini", 0),
}
# Part minimale des mots d'une vérification de faits retrouvés dans la demande.
# En dessous, la vérification porte sur une autre affirmation : elle n'est pas retenue.
FACTCHECK_MIN_COVERAGE = float(os.environ.get("FACTCHECK_MIN_COVERAGE", "0.5"))

GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_OAUTH_REDIRECT_URI = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", "")

# --- Exploitation : sécurité, cache partagé, journaux, limites de requête ---
if not DEBUG and (not SECRET_KEY or SECRET_KEY == "dev-secret-change-me"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY doit être défini (et long) quand DEBUG=false.")
if not DEBUG and ALLOWED_HOSTS == ["*"]:
    raise ImproperlyConfigured("ALLOWED_HOSTS doit lister les domaines réels quand DEBUG=false.")

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", FRONTEND_URL).split(",") if o.strip()
]
# Derrière un reverse proxy (nginx, Caddy, plateforme PaaS) : le client parle en HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = os.environ.get("USE_X_FORWARDED_HOST", "false").lower() in ("1", "true", "yes")
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", str(not DEBUG).lower()).lower() in ("1", "true", "yes")
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", str(not DEBUG).lower()).lower() in ("1", "true", "yes")
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Une image de 5 Mo arrive encodée en base64 (~6,7 Mo) dans un corps JSON.
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("MAX_REQUEST_BYTES", str(12 * 1024 * 1024)))

# Cache : LocMem suffit en développement (un seul processus) ; en production avec
# plusieurs workers, « db » partage le cache (limitation de débit, jetons d'image).
CACHE_BACKEND = os.environ.get("CACHE_BACKEND", "locmem")
if CACHE_BACKEND == "db":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "antifake",
        }
    }

if not DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        # httpx journalise l'URL complète en INFO : elle contient les jetons passés en
        # paramètre (Telegram, OCR, recherche). Jamais de secret dans les journaux.
        "httpx": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "httpcore": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

# En production le repli console n'écrit nulle part : les e-mails passent par Brevo.
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
