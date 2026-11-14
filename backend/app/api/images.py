from flask import Blueprint, g, request, send_file
from . import fail, ok
from ..extensions import db
from ..security.uploads import UploadError
from ..services.image_service import create_image, image_json
from ..services.permission_service import get_image_or_404, login_required
from ..services.team_service import TeamError, set_visibility
from ..storage.local_private import path_for

bp = Blueprint("images", __name__)


@bp.post("/images")
@login_required
def upload():
    if request.form.get("declaracion_ia") != "true":                                   # RF-07, CP-06
        return fail("sin_declaracion", "Confirma que la imagen es generada por IA y que tienes permiso de uso.", 400)
    file = request.files.get("file")
    if not file:
        return fail("sin_archivo", "Selecciona una imagen.", 400)
    album_id = request.form.get("album_id", type=int)
    if album_id is not None:
        from ..models import Album
        album = db.session.get(Album, album_id)
        if not album or album.owner_user_id != g.user.id:
            return fail("no_encontrado", "Álbum no encontrado.", 404)
    try:
        image = create_image(g.user, file, album_id=album_id)
    except UploadError as e:
        return fail(e.code, e.message, 400)                                             # CP-05
    db.session.commit()
    return ok(image_json(image), 201)


@bp.get("/images/<int:image_id>")
@login_required
def detail(image_id):
    return ok(image_json(get_image_or_404(image_id)))


@bp.get("/images/<int:image_id>/content")
@login_required
def content(image_id):
    image = get_image_or_404(image_id)
    resp = send_file(path_for("originals", image.original_storage_key), mimetype=image.mime_type)
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


@bp.patch("/images/<int:image_id>/visibility")
@login_required
def visibility(image_id):
    image = get_image_or_404(image_id)
    if image.owner_user_id != g.user.id:
        return fail("no_encontrado", "No encontrado.", 404)
    value = (request.get_json(silent=True) or {}).get("visibility")
    if value not in ("private", "team"):
        return fail("valor_invalido", "La visibilidad debe ser private o team.", 400)
    try:
        set_visibility(g.user, image, value)
    except TeamError as e:
        return fail(e.code, e.message, e.status)
    db.session.commit()
    return ok(image_json(image))
