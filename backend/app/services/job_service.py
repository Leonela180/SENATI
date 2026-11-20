import re
from sqlalchemy.exc import IntegrityError
from flask import current_app
from ..ai.prompts import DEFAULT_SEED, PRESETS
from ..extensions import db
from ..models import ProcessingJob, audit

STATUS_ES = {"queued": "En cola", "processing": "Procesando", "completed": "Completado", "failed": "Error"}
ERROR_ES = {
    "filtro_no_disponible": "No se pudo comprobar el filtro de seguridad. No se publicó ningún resultado.",
    "tiempo_agotado": "El procesamiento superó el tiempo máximo. Prueba una imagen más pequeña.",
    "motor_ocupado": "El motor local está procesando otra imagen. Inténtalo de nuevo al terminar.",
    "memoria_insuficiente": "No hay suficiente RAM disponible para el motor local. Cierra aplicaciones que no uses y vuelve a intentarlo.",
    "motor_error": "El motor de IA falló al procesar la imagen.",
    "modelo_no_disponible": "El modelo de IA no está instalado o no se pudo cargar.",
    "resultado_inexistente": "El resultado no se guardó correctamente.",
    "contenido_bloqueado": "El filtro de seguridad del modelo bloqueó el resultado.",
    "gpu_memoria": "La GPU se quedó sin memoria. Prueba con una imagen más pequeña.",
    "parametros_invalidos": "Los ajustes de la herramienta no son válidos.",
    "sin_rostro": "No se encontró un rostro de frente en la imagen. Prueba con un retrato donde la cara se vea completa.",
}
TOOL_ES = {"realista": "Ilustración a retrato realista", "restaurar": "Restaurar fotografía", "humanizar": "Humanización", "quitar_lunar": "Quitar lunar o mancha", "cambiar_fondo": "Cambiar fondo",
           "desenfoque": "Desenfoque gaussiano", "mejorar_calidad": "Mejorar calidad", "ajustes": "Ajustes de imagen",
           "textura_piel": "Textura de piel realista"}
PUBLIC_PARAMS = ("strength", "steps", "guidance", "seed", "work_size", "seconds", "vram_gb", "device", "filtro_seguridad",
                 "scale", "sharpen", "denoise", "radius", "scope", "mode", "color", "puntos", "width", "height",
                 "brightness", "contrast", "saturation", "warmth", "rotate", "runtime", "blend", "ram_free_min_gib",
                 "facial_detail_applied", "eyes_enhanced", "pores_intensity", "facial_detail_method", "intensity",
                 "pecas", "rostro_detectado", "ojos_protegidos", "cobertura_piel", "conversion_mode", "character")


class ToolParamsError(ValueError):
    pass


def clean_tool_params(tool, params, image):
    """Valida y normaliza los ajustes de cada herramienta del Estudio (nunca se confía en el navegador)."""
    p = params if isinstance(params, dict) else {}

    def num(key, lo, hi, default):
        try:
            v = float(p.get(key, default))
        except (TypeError, ValueError):
            raise ToolParamsError(key)
        if not lo <= v <= hi:
            raise ToolParamsError(key)
        return v

    if tool in ("quitar_lunar", "restaurar"):
        pts = p.get("points", [] if tool == "restaurar" else None)
        if not isinstance(pts, list) or not (0 if tool == "restaurar" else 1) <= len(pts) <= 20:
            raise ToolParamsError("points")
        clean = []
        for q in pts:
            try:
                x, y, r = int(q["x"]), int(q["y"]), int(q["r"])
            except (TypeError, KeyError, ValueError):
                raise ToolParamsError("points")
            if not (0 <= x < image.width and 0 <= y < image.height and 2 <= r <= 80):
                raise ToolParamsError("points")
            clean.append({"x": x, "y": y, "r": r})
        result = {"points": clean, "puntos": len(clean)}
        if tool == "restaurar":
            result["intensity"] = round(num("intensity", 0.1, 1, 0.6), 2)
        return result
    if tool == "textura_piel":
        return {"intensity": round(num("intensity", 0.1, 1, 0.7), 2), "pecas": p.get("pecas", False) is True}
    if tool == "cambiar_fondo":
        mode = p.get("mode")
        if mode not in ("color", "desenfocado", "transparente"):
            raise ToolParamsError("mode")
        color = str(p.get("color", "#ffffff"))
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ToolParamsError("color")
        return {"mode": mode, "color": color.lower(), "radius": num("radius", 2, 40, 12)}
    if tool == "desenfoque":
        scope = p.get("scope", "todo")
        if scope not in ("todo", "fondo"):
            raise ToolParamsError("scope")
        return {"scope": scope, "radius": num("radius", 0.5, 40, 6)}
    if tool == "mejorar_calidad":
        scale = num("scale", 1, 4, 2)
        if scale not in (1, 2, 4):
            raise ToolParamsError("scale")
        scale = int(scale)
        return {"scale": scale, "sharpen": round(num("sharpen", 0, 2, 0.6), 2), "denoise": bool(p.get("denoise", True))}
    if tool == "ajustes":
        rotate = int(num("rotate", 0, 270, 0))
        if rotate not in (0, 90, 180, 270):
            raise ToolParamsError("rotate")
        return {"brightness": round(num("brightness", 0.5, 1.5, 1), 2), "contrast": round(num("contrast", 0.5, 1.5, 1), 2),
                "saturation": round(num("saturation", 0, 2, 1), 2), "warmth": round(num("warmth", -1, 1, 0), 2), "rotate": rotate}
    raise ToolParamsError("tool")


def job_json(job, user):
    return {
        "id": job.id, "image_id": job.image_id, "image_filename": job.image.original_filename,
        "status": job.status, "status_label": STATUS_ES[job.status], "preset": job.preset,
        "tool": job.tool, "tool_label": TOOL_ES.get(job.tool, job.tool),
        "model_id": job.model_id, "model_version": job.model_version,
        "parameters": {k: v for k, v in (job.parameters or {}).items() if k in PUBLIC_PARAMS},
        "error_code": job.error_code, "error_message": ERROR_ES.get(job.error_code) if job.error_code else None,
        "attempt_count": job.attempt_count, "visibility": job.image.visibility,
        "is_owner": job.image.owner_user_id == user.id,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }


def create_job(user, image, preset, idem_key, tool="humanizar", tool_params=None):
    """RF-09: misma clave de idempotencia = mismo trabajo (CU03 flujo 3a). Lanza ToolParamsError si los ajustes no valen."""
    existing = db.session.query(ProcessingJob).filter_by(requested_by=user.id, idempotency_key=idem_key).first()
    if existing:
        return existing, False
    if tool == "realista":
        preset = "natural"
        character = (tool_params or {}).get("character", "adult_person") if isinstance(tool_params, dict) or tool_params is None else None
        if character not in ("adult_person", "adult_man", "adult_woman"):
            raise ToolParamsError("character")
        params = {"strength": .74, "steps": 28, "guidance": 6.5, "seed": 1234, "character": character, "conversion_mode": "ilustracion_a_realista"}
    elif tool == "humanizar":
        if current_app.config["AI_ENGINE"] != "local" or preset not in PRESETS or current_app.config.get("AI_LOCAL_RUNTIME") == "cpp":
            preset = "natural"
        params = dict(PRESETS[preset], seed=DEFAULT_SEED)    # RNF-10: parámetros y semilla registrados
    else:
        preset = "natural"
        params = clean_tool_params(tool, tool_params, image)
    job = ProcessingJob(image_id=image.id, requested_by=user.id, idempotency_key=idem_key, tool=tool,
                        preset=preset, parameters=params, status="queued")
    db.session.add(job)
    try:
        db.session.flush()
    except IntegrityError:                                   # dos solicitudes simultáneas con la misma clave
        db.session.rollback()
        return db.session.query(ProcessingJob).filter_by(requested_by=user.id, idempotency_key=idem_key).one(), False
    audit(user.id, "job.create", "job", job.id, preset=preset, tool=tool)
    return job, True
