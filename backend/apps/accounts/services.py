"""Connexion Google (OpenID Connect) — dossier technique §9."""
import httpx
import jwt
from django.conf import settings
from django.utils import timezone

GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")

_jwks_cache: dict = {}


def _google_public_keys() -> dict:
    if not _jwks_cache:
        with httpx.Client(timeout=8) as client:
            resp = client.get(GOOGLE_JWKS_URI)
            resp.raise_for_status()
            for jwk in resp.json()["keys"]:
                _jwks_cache[jwk["kid"]] = jwt.PyJWK(jwk)
    return _jwks_cache


def exchange_code(code: str, redirect_uri: str) -> dict:
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise ValueError("Connexion Google non configurée")
    with httpx.Client(timeout=8) as client:
        resp = client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        resp.raise_for_status()
        return resp.json()


def validate_id_token(id_token: str, nonce: str | None = None) -> dict:
    """Valide signature, iss, aud, exp, nonce et email_verified (dossier §9.1)."""
    header = jwt.get_unverified_header(id_token)
    key = _google_public_keys().get(header.get("kid"))
    if key is None:
        raise ValueError("Clé de signature Google introuvable")
    payload = jwt.decode(
        id_token,
        key=key.key,
        algorithms=["RS256"],
        audience=settings.GOOGLE_OAUTH_CLIENT_ID,
        issuer=GOOGLE_ISSUERS,
        options={"verify_exp": True},
    )
    if nonce and payload.get("nonce") != nonce:
        raise ValueError("nonce invalide")
    if not payload.get("email_verified"):
        raise ValueError("email non vérifié")
    return payload


def link_google_account(payload: dict):
    """Règles de liaison du dossier §9.4 (aucune fusion automatique par e-mail)."""
    from .models import SocialIdentity, User

    sub = payload["sub"]
    email = payload.get("email", "")
    name = payload.get("name", "")

    identity = SocialIdentity.objects.filter(provider="google", subject=sub).select_related("user").first()
    if identity:
        return identity.user, False

    # sub inconnu : jamais de fusion automatique par e-mail.
    user = User.objects.create_user(email=email, name=name, is_email_verified=True)
    user.set_unusable_password()
    user.save(update_fields=["password"])
    SocialIdentity.objects.create(provider="google", subject=sub, user=user, email=email, name=name)
    return user, True
