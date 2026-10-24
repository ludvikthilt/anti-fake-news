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

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "[entrée] compte administrateur"
    python manage.py createsuperuser --noinput 2>/dev/null || echo "  (déjà existant)"
fi

echo "[entrée] gunicorn"
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
