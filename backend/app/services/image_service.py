from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Image, audit
from ..security.uploads import validate_image
from ..storage.local_private import new_key, save_bytes
from .permission_service import personal_workspace


def image_json(image):
    return {"id": image.id, "filename": image.original_filename, "mime": image.mime_type,
            "width": image.width, "height": image.height, "byte_size": image.byte_size,
            "visibility": image.visibility, "album_id": image.album_id, "created_at": image.created_at.isoformat()}


def create_image(user, file_storage, album_id=None) -> Image:
    """CU03 pasos 1–2: valida, guarda el original en privado y registra la imagen (RF-06 a RF-08)."""
    info = validate_image(file_storage)                     # lanza UploadError si algo falla
    key = new_key(info["ext"])
    save_bytes("originals", key, info["bytes"])
    image = Image(owner_user_id=user.id, workspace_id=personal_workspace(user).id, original_storage_key=key,
                  original_filename=(secure_filename(file_storage.filename or "") or "imagen")[:255],
                  mime_type=info["mime"], byte_size=len(info["bytes"]),
                  width=info["width"], height=info["height"], source_type="ai_generated", album_id=album_id)
    db.session.add(image)
    db.session.flush()
    audit(user.id, "image.upload", "image", image.id, mime=info["mime"], byte_size=len(info["bytes"]))
    return image


def delete_image(user, image):
    """Galería: borra la imagen, sus trabajos y los archivos privados (original y resultados)."""
    from ..models import Generation, ProcessingJob
    from ..storage.local_private import path_for
    files = [path_for("originals", image.original_storage_key)]
    for job in db.session.query(ProcessingJob).filter_by(image_id=image.id).all():
        if job.result_storage_key:
            files.append(path_for("results", job.result_storage_key))
        db.session.delete(job)
    db.session.query(Generation).filter_by(image_id=image.id).update({"image_id": None})
    db.session.delete(image)
    audit(user.id, "image.delete", "image", image.id)
    return files
