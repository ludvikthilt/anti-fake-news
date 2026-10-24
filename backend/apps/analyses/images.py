"""M4 — Traitement d'image : miniature locale + empreinte perceptuelle (pHash).

L'original n'est jamais conservé en base : on ne stocke qu'une miniature
(≤ 512 px, JPEG) le temps de l'analyse, et l'empreinte pHash pour le cache/dédoublonnage.
"""
import base64
import io

from PIL import Image, UnidentifiedImageError
import imagehash

# Bornes du dossier (§M1) : 5 Mo et 4 096 px par côté.
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_SIDE = 4096


def validate_data_url(data_url: str) -> tuple[int, int, int]:
    """Contrôle explicite des bornes d'image ; lève ValueError avec un message affichable."""
    try:
        raw = decode_data_url(data_url)
    except Exception as exc:  # base64 invalide, ou en-tête data URL absent
        raise ValueError("Image illisible : encodage invalide.") from exc
    size = len(raw)
    if not size:
        raise ValueError("Image vide.")
    if size > MAX_IMAGE_BYTES:
        raise ValueError("Image trop lourde : 5 Mo maximum.")
    try:
        with Image.open(io.BytesIO(raw)) as img:
            width, height = img.size
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Image illisible : format non pris en charge.") from exc
    if max(width, height) > MAX_IMAGE_SIDE:
        raise ValueError("Image trop grande : 4 096 px maximum par côté.")
    return width, height, size


def decode_data_url(data_url: str) -> bytes:
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    return base64.b64decode(data_url)


def open_image(data_url: str) -> Image.Image:
    raw = decode_data_url(data_url)
    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Image illisible.") from exc


def make_thumbnail(data_url: str, max_side: int = 512) -> str:
    """Renvoie une miniature JPEG base64 (data URL) — jamais l'original."""
    img = open_image(data_url)
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def phash_of(data_url: str) -> str:
    """Empreinte perceptuelle pHash (base de dédoublonnage)."""
    img = open_image(data_url)
    return str(imagehash.phash(img))
