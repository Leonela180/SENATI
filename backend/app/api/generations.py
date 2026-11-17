"""Generar imágenes con Gemini (servicio externo de Google). Requiere consentimiento explícito."""
import io
from flask import Blueprint, current_app, g, request
from werkzeug.datastructures import FileStorage
from . import fail, ok
from ..extensions import db, limiter
from ..models import Generation, audit
from ..security.uploads import UploadError
from ..services.gemini_service import GeminiError, generate_image
from ..services.image_service import create_image, image_json
from ..services.permission_service import login_required

bp = Blueprint("generations", __name__)
ERRORS = {
    "gemini_no_configurado": ("La generación no está configurada: falta GEMINI_API_KEY en el archivo .env.", 503),
    "gemini_clave": ("La clave de Gemini no es válida o no tiene permiso.", 502),
    "gemini_limite": ("Google indica que no hay cuota disponible para generar imágenes. El administrador debe revisar la cuota o facturación de Gemini. Puedes seguir usando el Estudio y la galería.", 429),
    "gemini_red": ("No se pudo conectar con Gemini. Revisa tu conexión a internet.", 502),
    "gemini_solicitud": ("Gemini rechazó la solicitud. Cambia la descripción.", 400),
    "gemini_sin_imagen": ("Gemini no devolvió una imagen (puede haberla bloqueado por sus políticas).", 422),
    "gemini_servicio": ("El servicio de Gemini respondió con un error.", 502),
    "imagen_invalida": ("La imagen recibida no es válida.", 502),
}


def generation_json(gen):
    return {"id": gen.id, "prompt": gen.prompt, "model": gen.model, "status": gen.status, "image_id": gen.image_id,
            "error_code": gen.error_code, "seconds": gen.seconds, "created_at": gen.created_at.isoformat()}


@bp.get("/generations/status")
@login_required
def status():
    return ok({"configured": bool(current_app.config["GEMINI_API_KEY"]), "model": current_app.config["GEMINI_IMAGE_MODEL"]})


@bp.get("/generations")
@login_required
def history():
    rows = (db.session.query(Generation).filter_by(user_id=g.user.id)
            .order_by(Generation.created_at.desc()).limit(30).all())
    return ok([generation_json(r) for r in rows])


@bp.post("/generations")
@login_required
@limiter.limit("20/hour")
def generate():
    d = request.get_json(silent=True) or {}
    if d.get("consent") is not True:
        return fail("sin_consentimiento", "Confirma que aceptas enviar la descripción a Google (Gemini).", 400)
    prompt = (d.get("prompt") or "").strip()
    if not (5 <= len(prompt) <= 1000):
        return fail("datos_invalidos", "Escribe una descripción de 5 a 1000 caracteres.", 400)
    album_id = d.get("album_id")
    if album_id is not None:
        from ..models import Album
        album = db.session.get(Album, album_id) if isinstance(album_id, int) else None
        if not album or album.owner_user_id != g.user.id:
            return fail("no_encontrado", "Álbum no encontrado.", 404)
    cfg = current_app.config
    gen = Generation(user_id=g.user.id, prompt=prompt, model=cfg["GEMINI_IMAGE_MODEL"], status="failed")
    try:
        data, seconds = generate_image(prompt, cfg["GEMINI_API_KEY"], cfg["GEMINI_IMAGE_MODEL"], cfg["GEMINI_TIMEOUT"])
        gen.seconds = seconds
        image = create_image(g.user, FileStorage(stream=io.BytesIO(data), filename="gemini.png"), album_id=album_id)
        gen.status, gen.image_id = "completed", image.id
    except GeminiError as e:
        gen.error_code = e.code
    except UploadError:
        gen.error_code = "imagen_invalida"
    db.session.add(gen)
    db.session.flush()
    audit(g.user.id, "generation.create", "generation", gen.id, status=gen.status, model=gen.model)
    db.session.commit()
    if gen.status != "completed":
        message, code = ERRORS[gen.error_code]
        return fail(gen.error_code, message, code)
    return ok({**generation_json(gen), "image": image_json(image)}, 201)
