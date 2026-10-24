"""Limitation de débit (dossier §6) — appliquée aux vues, pas seulement déclarée.

Les taux suivent le statut du demandeur : visiteur (par IP) ou inscrit (par compte).
Les scopes sont définis dans `DEFAULT_THROTTLE_RATES` (settings.py).
"""
from rest_framework.exceptions import Throttled
from rest_framework.throttling import SimpleRateThrottle


class DualRateThrottle(SimpleRateThrottle):
    """Un scope pour les visiteurs, un autre pour les inscrits."""

    anon_scope = "default_anon"
    user_scope = "default_user"

    def __init__(self):
        # Le taux dépend de la requête : il est calculé dans allow_request().
        self.rate = None
        self.num_requests = None
        self.duration = None
        self.scope = self.user_scope

    def allow_request(self, request, view):
        self.scope = self.user_scope if request.user.is_authenticated else self.anon_scope
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def throttle_failure(self):
        # DRF complète le message avec le délai exact (« Disponible à nouveau dans… »).
        raise Throttled(detail="Trop de requêtes.", wait=int(self.wait()) + 1)


class AnalysisThrottle(DualRateThrottle):
    """Soumission d'analyse : action coûteuse (fournisseurs externes payants)."""

    anon_scope = "analysis_anon"
    user_scope = "analysis_user"


class ChatThrottle(DualRateThrottle):
    anon_scope = "chat_anon"
    user_scope = "chat_user"


class CertificationThrottle(DualRateThrottle):
    anon_scope = "certify_anon"
    user_scope = "certify_user"


class IpRateThrottle(SimpleRateThrottle):
    """Taux par IP uniquement — connexion, inscription, jeton interne."""

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}

    def throttle_failure(self):
        raise Throttled(detail="Trop de tentatives.", wait=int(self.wait()) + 1)


class AuthThrottle(IpRateThrottle):
    scope = "auth"


class RegisterThrottle(IpRateThrottle):
    scope = "register"


class InternalThrottle(IpRateThrottle):
    scope = "internal"
