import os
from google import genai
from dotenv import load_dotenv

# 1. Cargar la clave de API de forma segura desde el archivo .env
load_dotenv()

# Inicializar el cliente oficial
client = genai.Client()

# 2. Definir la ruta del archivo que quieres que la IA lea y modifique
# (Reemplaza 'mi_codigo.py' por el nombre real del archivo en tu proyecto)
archivo_entrada = "mi_codigo.py"
archivo_salida = "codigo_optimizado.py"

def procesar_codigo_con_ia():
    # Verificar que el archivo exista antes de leerlo
    if not os.path.exists(archivo_entrada):
        print(f"Error: No se encontró el archivo '{archivo_entrada}' en tu proyecto.")
        return

    # Leer el contenido del archivo de código
    with open(archivo_entrada, "r", encoding="utf-8") as f:
        codigo_original = f.read()

    print(f" Leyendo '{archivo_entrada}' y enviándolo a Gemini para su análisis...")

    # 3. Construir el prompt (instrucción) para la IA
    prompt = f"""
    Eres un asistente experto en ingeniería de software. A continuación, te comparto el código fuente de un archivo.
    Por favor, revísalo, detecta posibles errores, optimízalo y devuelve únicamente el código corregido y limpio, 
    sin explicaciones adicionales ni bloques de texto extra fuera del formato de código.

    Código original:
    {codigo_original}
    """

    # 4. Enviar la solicitud al modelo Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    codigo_modificado = response.text

    # Limpiar marcas de formato de código comunes si las hubiera (opcional)
    codigo_limpio = codigo_modificado.replace("```python", "").replace("```", "").strip()

    # 5. Guardar el resultado en un nuevo archivo (o sobrescribir el original si estás seguro)
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(codigo_limpio)

    print(f" ¡Listo! El código modificado se ha guardado exitosamente en '{archivo_salida}'.")

if __name__ == "__main__":
    procesar_codigo_con_ia()