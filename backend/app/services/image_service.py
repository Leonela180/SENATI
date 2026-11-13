from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Image, audit
from ..security.uploads import validate_image
from ..storage.local_private import new_key, save_bytes
from .permission_service import personal_workspace


def image_json(image):
    return {"id": image.id, "filename": image.original_filename, "mime": image.mime_type,
            "width": image.width, "height": image.height, "byte_size": image.byte_size,
            "visibility": image.visibility, "created_at": image.created_at.isoformat()}


def create_image(user, file_storage) -> Image:
    """CU03 pasos 1–2: valida, guarda el original en privado y registra la imagen (RF-06 a RF-08)."""
    info = validate_image(file_storage)                     # lanza UploadError si algo falla
    key = new_key(info["ext"])
    save_bytes("originals", key, info["bytes"])
    image = Image(owner_user_id=user.id, workspace_id=personal_workspace(user).id, original_storage_key=key,
                  original_filename=(secure_filename(file_storage.filename or "") or "imagen")[:255],
                  mime_type=info["mime"], byte_size=len(info["bytes"]),
                  width=info["width"], height=info["height"], source_type="ai_generated")
    db.session.add(image)
    db.session.flush()
    audit(user.id, "image.upload", "image", image.id, mime=info["mime"], byte_size=len(info["bytes"]))
    return image
