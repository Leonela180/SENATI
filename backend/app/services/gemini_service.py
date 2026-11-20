"""MÓDULO CHATBOT y GENERAR · Conexión con la API de Gemini (Google), sin SDK: solo la biblioteca estándar.

- chat(): conversación de texto del asistente. Sus instrucciones están en asistente_instrucciones.py.
- generate_image(): generación de imágenes (desactivada por defecto con GEMINI_IMAGE_ENABLED=0).

La clave se lee de GEMINI_API_KEY en .env; nunca se escribe en el código, en Git ni en los registros.
"""
import base64
import binascii
import json
import re
import time
import urllib.error
import urllib.request

from .asistente_instrucciones import CHAT_SYSTEM, CHAT_TOOLS, MAX_TOKENS_RESPUESTA, TEMPERATURA

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


class GeminiError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def generate_image(prompt: str, api_key: str, model: str, timeout: int = 90) -> tuple[bytes, float]:
    """Devuelve (bytes de la imagen, segundos). Lanza GeminiError con un código seguro."""
    if not api_key:
        raise GeminiError("gemini_no_configurado")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", model):
        raise GeminiError("gemini_servicio")
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT.format(model=model), data=body, method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": api_key})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise GeminiError("imagen_invalida")
            data = json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise GeminiError({400: "gemini_solicitud", 401: "gemini_clave", 403: "gemini_clave",
                           429: "gemini_limite"}.get(e.code, "gemini_servicio")) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise GeminiError("gemini_red") from None
    except (ValueError, UnicodeError):
        raise GeminiError("gemini_servicio") from None
    try:
        for cand in data.get("candidates") or []:
            for part in (cand.get("content") or {}).get("parts") or []:
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"], validate=True), round(time.perf_counter() - t0, 2)
    except (AttributeError, TypeError, ValueError, binascii.Error):
        raise GeminiError("gemini_servicio") from None
    raise GeminiError("gemini_sin_imagen")                 # bloqueo por políticas o respuesta sin imagen


def chat(messages: list[dict], api_key: str, model: str, timeout: int = 30) -> tuple[str, str | None]:
    """Conversación de texto con Gemini. messages = [{role: user|model, text}]. Devuelve (respuesta, herramienta)."""
    if not api_key:
        raise GeminiError("gemini_no_configurado")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", model):
        raise GeminiError("gemini_servicio")
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": CHAT_SYSTEM}]},
        "contents": [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in messages],
        "generationConfig": {"temperature": TEMPERATURA, "maxOutputTokens": MAX_TOKENS_RESPUESTA},
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT.format(model=model), data=body, method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read(2 * 1024 * 1024).decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise GeminiError({400: "gemini_solicitud", 401: "gemini_clave", 403: "gemini_clave",
                           429: "gemini_limite"}.get(e.code, "gemini_servicio")) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise GeminiError("gemini_red") from None
    except (ValueError, UnicodeError):
        raise GeminiError("gemini_servicio") from None
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        raise GeminiError("gemini_sin_texto") from None
    if not text:
        raise GeminiError("gemini_sin_texto")
    tool = None
    match = re.search(r"HERRAMIENTA:\s*([a-z_]+)\s*$", text)
    if match:
        text = text[:match.start()].rstrip()
        tool = match.group(1) if match.group(1) in CHAT_TOOLS else None
    return text, tool
