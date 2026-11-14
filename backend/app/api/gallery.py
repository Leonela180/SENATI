"""Galería: álbumes, listado, mover y borrar imágenes propias."""
from flask import Blueprint, g, request
from sqlalchemy import func, select
from . import fail, ok
from ..extensions import db
from ..models import Album, Image, ProcessingJob, audit
from ..services.image_service import delete_image, image_json
from ..services.permission_service import get_image_or_404, login_required

bp = Blueprint("gallery", __name__)
PER_PAGE = 24


def _album_or_404(album_id):
    album = db.session.get(Album, album_id)
    if not album or album.owner_user_id != g.user.id:
        return None
    return album


def album_json(a, count):
    return {"id": a.id, "name": a.name, "count": count, "created_at": a.created_at.isoformat()}


@bp.get("/albums")
@login_required
def albums():
    rows = db.session.execute(
        select(Album, func.count(Image.id)).outerjoin(Image, Image.album_id == Album.id)
        .where(Album.owner_user_id == g.user.id).group_by(Album.id).order_by(Album.name)).all()
    return ok([album_json(a, n) for a, n in rows])


@bp.post("/albums")
@login_required
def new_album():
    name = ((request.get_json(silent=True) or {}).get("name") or "").strip()
    if not (1 <= len(name) <= 80):
        return fail("nombre_invalido", "El nombre del álbum debe tener entre 1 y 80 caracteres.", 400)
    if db.session.query(Album).filter_by(owner_user_id=g.user.id, name=name).first():
        return fail("ya_existe", "Ya tienes un álbum con ese nombre.", 409)
    album = Album(owner_user_id=g.user.id, name=name)
    db.session.add(album)
    db.session.flush()
    audit(g.user.id, "album.create", "album", album.id)
    db.session.commit()
    return ok(album_json(album, 0), 201)


@bp.patch("/albums/<int:album_id>")
@login_required
def rename_album(album_id):
    album = _album_or_404(album_id)
    if not album:
        return fail("no_encontrado", "No encontrado.", 404)
    name = ((request.get_json(silent=True) or {}).get("name") or "").strip()
    if not (1 <= len(name) <= 80):
        return fail("nombre_invalido", "El nombre del álbum debe tener entre 1 y 80 caracteres.", 400)
    album.name = name
    db.session.commit()
    return ok({"id": album.id, "name": album.name})


@bp.delete("/albums/<int:album_id>")
@login_required
def remove_album(album_id):
    """Borra solo el álbum: sus imágenes quedan en la galería sin álbum."""
    album = _album_or_404(album_id)
    if not album:
        return fail("no_encontrado", "No encontrado.", 404)
    db.session.query(Image).filter_by(album_id=album.id).update({"album_id": None})
    db.session.delete(album)
    audit(g.user.id, "album.delete", "album", album_id)
    db.session.commit()
    return ok({"deleted": album_id})


@bp.get("/images")
@login_required
def list_images():
    page = max(1, request.args.get("page", 1, type=int))
    q = select(Image).where(Image.owner_user_id == g.user.id)
    album = request.args.get("album")
    if album == "none":
        q = q.where(Image.album_id.is_(None))
    elif album:
        try:
            q = q.where(Image.album_id == int(album))
        except ValueError:
            return fail("datos_invalidos", "Álbum inválido.", 400)
    term = (request.args.get("q") or "").strip()
    if term:
        q = q.where(Image.original_filename.ilike(f"%{term[:60]}%"))
    total = db.session.scalar(select(func.count()).select_from(q.subquery())) or 0
    items = db.session.scalars(q.order_by(Image.created_at.desc()).limit(PER_PAGE).offset((page - 1) * PER_PAGE)).all()
    # Último resultado completado de cada imagen, para mostrar su miniatura editada
    last = {}
    if items:
        rows = db.session.execute(
            select(ProcessingJob.image_id, func.max(ProcessingJob.id))
            .where(ProcessingJob.image_id.in_([i.id for i in items]), ProcessingJob.status == "completed")
            .group_by(ProcessingJob.image_id)).all()
        last = dict(rows)
    return ok({"items": [{**image_json(i), "last_job_id": last.get(i.id)} for i in items],
               "page": page, "pages": max(1, -(-total // PER_PAGE)), "total": total})


@bp.patch("/images/<int:image_id>/album")
@login_required
def move_image(image_id):
    image = get_image_or_404(image_id)
    if image.owner_user_id != g.user.id:
        return fail("no_encontrado", "No encontrado.", 404)
    album_id = (request.get_json(silent=True) or {}).get("album_id")
    if album_id is not None and not _album_or_404(album_id):
        return fail("no_encontrado", "Álbum no encontrado.", 404)
    image.album_id = album_id
    db.session.commit()
    return ok(image_json(image))


@bp.delete("/images/<int:image_id>")
@login_required
def remove_image(image_id):
    image = get_image_or_404(image_id)
    if image.owner_user_id != g.user.id:
        return fail("no_encontrado", "No encontrado.", 404)
    files = delete_image(g.user, image)
    db.session.commit()
    for f in files:                                   # los archivos se borran después de confirmar en la BD
        f.unlink(missing_ok=True)
    return ok({"deleted": image_id})
