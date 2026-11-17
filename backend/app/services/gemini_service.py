"""Cliente mínimo de la API de Gemini para generar imágenes (sin SDK: solo la biblioteca estándar).

La clave se lee de GEMINI_API_KEY en .env; nunca se escribe en el código, en Git ni en los registros.
"""
import base64
import binascii
import json
import re
import time
import urllib.error
import urllib.request

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


CHAT_SYSTEM = (
    "Eres el asistente de LUMIA AI, un estudio de edición de imágenes. Responde SIEMPRE en español, "
    "con calidez y en pocas líneas (máximo 6 líneas o 4 pasos cortos). Solo ayudas con: edición de fotos, "
    "retratos generados por IA y el uso de LUMIA. Si preguntan otra cosa, dilo amablemente y vuelve al tema. "
    "Herramientas disponibles (usa estos identificadores): humanizar (piel, ojos y luz más naturales en "
    "retratos generados por IA), restaurar (fotos antiguas: ruido, tonos, rayas pequeñas), quitar_lunar "
    "(lunares o manchas pequeñas), cambiar_fondo (color, desenfocado o transparente), desenfoque (gaussiano, "
    "de todo o solo del fondo), mejorar_calidad (doble resolución, nitidez, menos ruido), ajustes (brillo, "
    "contraste, saturación, calidez, rotación), textura_piel (poros y grano natural cuando la piel se ve lisa "
    "o de plástico; es un filtro digital rápido), galeria (subir y organizar en álbumes), generar (crear imágenes "
    "desde texto). No puedes ver las imágenes del usuario: si hace falta, pide que las describa. Nunca ayudes a "
    "suplantar identidades, quitar marcas de edición con IA ni hacer pasar una imagen sintética por la foto de "
    "una persona real. Si recomiendas una herramienta, termina con una línea exacta: HERRAMIENTA: <identificador>."
)
CHAT_TOOLS = {"humanizar", "restaurar", "quitar_lunar", "cambiar_fondo", "desenfoque", "mejorar_calidad",
              "ajustes", "textura_piel", "galeria", "generar"}


def chat(messages: list[dict], api_key: str, model: str, timeout: int = 30) -> tuple[str, str | None]:
    """Conversación de texto con Gemini. messages = [{role: user|model, text}]. Devuelve (respuesta, herramienta)."""
    if not api_key:
        raise GeminiError("gemini_no_configurado")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", model):
        raise GeminiError("gemini_servicio")
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": CHAT_SYSTEM}]},
        "contents": [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in messages],
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 600},
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
