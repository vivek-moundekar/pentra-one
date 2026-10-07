"""Validate and normalize a photo locally; never persist student uploads."""
import base64
from io import BytesIO
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000


def prepare_image(upload):
    if not upload.size or upload.size > MAX_IMAGE_BYTES:
        raise ValueError("Each photo must be non-empty and at most 10 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            upload.seek(0)
            with Image.open(upload) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValueError("Please select a JPG, PNG or WebP photo.")
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Photo resolution is too large. Resize it below 25 megapixels.")
                source.verify()
            upload.seek(0)
            with Image.open(upload) as source:
                photo = ImageOps.exif_transpose(source)
                photo.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                rgba = photo.convert("RGBA")
                rgb = Image.new("RGB", rgba.size, "white")
                rgb.paste(rgba, mask=rgba.getchannel("A"))
                output = BytesIO()
                rgb.save(output, format="JPEG", quality=90)
                return base64.b64encode(output.getvalue()).decode("ascii")
    except (UnidentifiedImageError, OSError, SyntaxError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("This photo is damaged or unsupported. Try another JPG, PNG or WebP.") from exc
