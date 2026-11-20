"""Prueba manual real autorizada. Nunca imprime la clave ni respuestas externas completas."""
import io
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from app.config import Config, ROOT
from app.services.gemini_service import GeminiError, generate_image, chat


def main(argv=None):
    parser = argparse.ArgumentParser(description="Valida Gemini solo texto por defecto, sin mostrar claves ni respuestas.")
    parser.add_argument("--imagenes", action="store_true", help="Exige GEMINI_IMAGE_ENABLED=1 y autorizacion para imagenes")
    args = parser.parse_args(argv)
    print("Clave configurada:", bool(Config.GEMINI_API_KEY))
    if not args.imagenes:
        print("Modelo de texto:", Config.GEMINI_CHAT_MODEL)
        try:
            reply, tool = chat([{"role": "user", "text": "En una frase, indica como ampliar una imagen en LUMIA sin prometer recuperar detalles."}],
                               Config.GEMINI_API_KEY, Config.GEMINI_CHAT_MODEL, Config.GEMINI_CHAT_TIMEOUT)
            print("Resultado: respuesta de texto recibida; caracteres:", len(reply), "herramienta:", tool)
            return 0
        except GeminiError as error:
            print("Resultado:", error.code)
            return 1
    if not Config.GEMINI_IMAGE_ENABLED:
        print("Resultado: imagenes desactivadas; no se realizo ninguna llamada de imagenes.")
        return 2
    print("Modelo:", Config.GEMINI_IMAGE_MODEL)
    try:
        data, seconds = generate_image(
            "Crea una fotografía de una taza de cerámica blanca sobre una mesa de madera, "
            "luz natural suave, fondo beige, composición minimalista, sin texto.",
            Config.GEMINI_API_KEY, Config.GEMINI_IMAGE_MODEL, Config.GEMINI_TIMEOUT,
        )
        image = Image.open(io.BytesIO(data))
        image.load()
        destination = ROOT / "private_data" / "validacion_gemini.png"
        image.save(destination, "PNG")
        print("Resultado: imagen real verificada", image.size, "segundos:", seconds)
        return 0
    except GeminiError as error:
        print("Resultado:", error.code)
        return 1
    except Exception as error:
        print("Resultado: fallo de validación", type(error).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
