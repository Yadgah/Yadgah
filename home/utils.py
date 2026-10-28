"""
Shared image-optimization helpers.

The blog app used to convert uploaded post images to WebP inline in its
views. That mechanism now lives here so the `home` app can reuse it for
slide thumbnails (and avatars) -- see issue #175.
"""

import logging
import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

#: Default upper bound (width, height) images are down-scaled to.
DEFAULT_MAX_SIZE = (1920, 1920)


def convert_image_to_webp(image_file, *, quality=85, max_size=DEFAULT_MAX_SIZE):
    """
    Convert an uploaded image to an optimized WebP image.

    The image is down-scaled to fit inside ``max_size`` (never enlarged),
    EXIF orientation is applied and transparency is preserved.

    Args:
        image_file: A file-like object or FieldFile holding the image.
        quality: WebP quality (0-100).
        max_size: ``(width, height)`` bounds for down-scaling.

    Returns:
        A ``(filename, ContentFile)`` tuple with the new ``.webp``
        filename, or ``None`` when the image is already a WebP file or
        the conversion failed (callers should keep the original file).
    """
    name = getattr(image_file, "name", "") or ""
    if name.lower().endswith(".webp"):
        return None

    try:
        image_file.seek(0)
        raw = image_file.read()
        # Keep the original usable if the caller falls back to it.
        image_file.seek(0)

        img = Image.open(BytesIO(raw))
        img = ImageOps.exif_transpose(img)

        if "A" in img.getbands():  # has an alpha channel
            img = img.convert("RGBA")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail(max_size, Image.LANCZOS)

        webp_io = BytesIO()
        img.save(webp_io, format="WEBP", quality=quality)

        filename_without_ext, _ = os.path.splitext(os.path.basename(name))
        webp_filename = f"{filename_without_ext or 'image'}.webp"
        return webp_filename, ContentFile(webp_io.getvalue())
    except Exception as e:  # UnidentifiedImageError, OSError, ...
        logger.warning("Could not convert image %r to WebP: %s", name, e)
        return None


def optimize_image_field(
    instance, field_name, *, quality=85, max_size=DEFAULT_MAX_SIZE
):
    """
    Optimize a model instance's ``ImageField`` in place (WebP conversion).

    Intended to be called from a model's ``save()`` before
    ``super().save()``. Silently keeps the original file when there is
    nothing to do (no file, already WebP, or conversion failed).
    """
    field_file = getattr(instance, field_name, None)
    if not field_file:
        return

    result = convert_image_to_webp(field_file, quality=quality, max_size=max_size)
    if result is None:
        return

    webp_filename, webp_content = result
    # save=False: the file is written to storage now, the model row is
    # persisted by the caller's super().save().
    field_file.save(webp_filename, webp_content, save=False)
