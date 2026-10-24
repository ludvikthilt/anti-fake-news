"""Hébergement éphémère des images (dossier §7, problème 5).

Les moteurs de recherche inversée exigent une URL publique. On sert la miniature
depuis la mémoire via un jeton aléatoire, quelques minutes seulement. Rien n'est
jamais écrit en base ni sur disque.
"""
import secrets

from django.core.cache import cache

TTL_SECONDS = 300


def store_image(data_url: str, ttl: int = TTL_SECONDS) -> str:
    """Stocke la miniature en mémoire et renvoie le jeton d'accès."""
    b64 = data_url.split(",", 1)[1] if "," in data_url else data_url
    token = secrets.token_urlsafe(24)
    cache.set(f"ephemeral:{token}", b64, ttl)
    return token


def get_image(token: str) -> str | None:
    """Renvoie le base64 stocké, ou None si expiré/absent."""
    return cache.get(f"ephemeral:{token}")
