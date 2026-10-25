#!/bin/sh
# Démarrage du conteneur backend : migrations idempotentes puis gunicorn.
set -e

: "${DJANGO_SECRET_KEY:?DJANGO_SECRET_KEY doit être défini}"

echo "[entrée] migrations"
python manage.py migrate --noinput

echo "[entrée] fichiers statiques (admin, DRF)"
python manage.py collectstatic --noinput

if [ "${CACHE_BACKEND:-locmem}" = "db" ]; then
    echo "[entrée] table de cache partagée"
    python manage.py createcachetable
fi

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] || [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    if [ -z "${DJANGO_SUPERUSER_EMAIL:-}" ] || [ -z "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
        echo "[entrée] DJANGO_SUPERUSER_EMAIL et DJANGO_SUPERUSER_PASSWORD doivent être définis ensemble" >&2
        exit 1
    fi
    echo "[entrée] compte administrateur"
    python manage.py ensure_superuser
fi

# Données de démonstration : peuplées automatiquement au premier démarrage (et à chaque
# redémarrage, la commande est idempotente). Désactivable avec SEED_DEMO=false.
if [ "${SEED_DEMO:-true}" = "true" ]; then
    echo "[entrée] données de démonstration (idempotent)"
    python manage.py seed_demo || {
        echo "[entrée] seed_demo a échoué : base non peuplée (relancer après correction)" >&2
    }
    # Indexe les fragments du chatbot (embeddings Gemini) ; sans clé, la commande le signale
    # et le chatbot reste en recherche plein texte.
    python manage.py index_knowledge || {
        echo "[entrée] index_knowledge a échoué : chatbot en recherche plein texte" >&2
    }
fi

echo "[entrée] gunicorn"
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-${WEB_CONCURRENCY:-3}}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
