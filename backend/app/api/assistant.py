"""Asistente conversacional (chat). Usa Gemini para texto si hay clave y consentimiento; nunca envía imágenes.

Si Gemini no está disponible, el frontend responde con la guía local de recorridos.
El contenido de los mensajes no se guarda en la base de datos ni en los registros.
"""
from flask import Blueprint, current_app, g, request
from . import fail, ok
from ..extensions import limiter
from ..models import audit
from ..extensions import db
from ..services.gemini_service import GeminiError, chat
from ..services.permission_service import login_required

bp = Blueprint("assistant", __name__)
MAX_TURNS, MAX_CHARS = 12, 1000
ERRORS = {
    "gemini_no_configurado": "El chat con IA no está configurado (falta GEMINI_API_KEY).",
    "gemini_clave": "La clave de Gemini no es válida o no tiene permiso.",
    "gemini_limite": "Gemini no tiene cuota disponible en este momento.",
    "gemini_red": "No se pudo conectar con Gemini. Revisa la conexión a internet.",
    "gemini_solicitud": "Gemini rechazó el mensaje.",
    "gemini_sin_texto": "Gemini no devolvió una respuesta (puede haberla bloqueado por sus políticas).",
    "gemini_servicio": "El servicio de Gemini respondió con un error.",
}


@bp.get("/assistant/status")
@login_required
def status():
    cfg = current_app.config
    return ok({"configured": bool(cfg["GEMINI_API_KEY"]), "model": cfg["GEMINI_CHAT_MODEL"]})


@bp.post("/assistant/chat")
@login_required
@limiter.limit("40/hour")
def send():
    d = request.get_json(silent=True) or {}
    if d.get("consent") is not True:
        return fail("sin_consentimiento", "Confirma que aceptas enviar tus mensajes de texto a Google (Gemini).", 400)
    messages = d.get("messages")
    if not isinstance(messages, list) or not messages:
        return fail("datos_invalidos", "Escribe un mensaje.", 400)
    clean = []
    for m in messages[-MAX_TURNS:]:
        if not isinstance(m, dict) or m.get("role") not in ("user", "model") or not isinstance(m.get("text"), str):
            return fail("datos_invalidos", "Mensaje inválido.", 400)
        text = m["text"].strip()[:MAX_CHARS]
        if text:
            clean.append({"role": m["role"], "text": text})
    if not clean or clean[-1]["role"] != "user":
        return fail("datos_invalidos", "El último mensaje debe ser tuyo.", 400)
    cfg = current_app.config
    try:
        reply, tool = chat(clean, cfg["GEMINI_API_KEY"], cfg["GEMINI_CHAT_MODEL"], cfg["GEMINI_CHAT_TIMEOUT"])
    except GeminiError as e:
        audit(g.user.id, "assistant.chat", "assistant", None, status="failed", error=e.code)
        db.session.commit()
        return fail(e.code, ERRORS.get(e.code, ERRORS["gemini_servicio"]), 503)
    audit(g.user.id, "assistant.chat", "assistant", None, status="completed")
    db.session.commit()
    return ok({"reply": reply, "tool": tool, "source": "gemini"})
