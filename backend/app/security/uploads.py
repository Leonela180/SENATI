import io
from PIL import Image as PILImage, UnidentifiedImageError
from flask import current_app

ALLOWED = {"JPEG": ("image/jpeg", "jpg"), "PNG": ("image/png", "png"), "WEBP": ("image/webp", "webp")}


class UploadError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


def validate_image(file_storage) -> dict:
    """RF-06: valida por bytes reales, tamaño, píxeles y decodificación completa (no por extensión)."""
    max_mb = current_app.config["MAX_UPLOAD_MB"]
    max_px = current_app.config["MAX_IMAGE_PIXELS"]
    data = file_storage.read(max_mb * 1024 * 1024 + 1)
    if not data:
        raise UploadError("archivo_vacio", "El archivo está vacío.")
    if len(data) > max_mb * 1024 * 1024:
        raise UploadError("archivo_grande", f"El archivo supera {max_mb} MB.")
    PILImage.MAX_IMAGE_PIXELS = max_px * 2           # Pillow corta las «bombas» de descompresión
    try:
        probe = PILImage.open(io.BytesIO(data))
        fmt, (w, h) = probe.format, probe.size
        probe.verify()
        if fmt not in ALLOWED:
            raise UploadError("tipo_no_permitido", "Solo se aceptan imágenes JPG, PNG o WebP.")
        if w * h > max_px:
            raise UploadError("demasiados_pixeles", f"La imagen supera {max_px // 1_000_000} megapíxeles.")
        PILImage.open(io.BytesIO(data)).load()       # decodificación completa
    except UploadError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, PILImage.DecompressionBombError):
        raise UploadError("imagen_invalida", "El archivo no es una imagen JPG, PNG o WebP válida.")
    mime, ext = ALLOWED[fmt]
    return {"bytes": data, "mime": mime, "ext": ext, "width": w, "height": h}
