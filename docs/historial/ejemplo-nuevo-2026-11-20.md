# Retrato nuevo y comparación visible

La imagen original se generó con la herramienta integrada `image_gen` de esta
conversación, sin usar las claves API del `.env` ni controlar la aplicación de
ChatGPT instalada. Se conservó en
`private_data/demo_senati/retrato_nuevo/original-generado.png`.

Modo: generación nueva, `photorealistic-natural`, fondo opaco.

## Prompt exacto del original

Use case: photorealistic-natural. Asset type: original synthetic BEFORE photograph for LUMIA AI student photo-editing demonstration. Create one fictional adult Peruvian woman age 32, head-and-shoulders, looking directly at the camera, relaxed neutral smile, dark wavy shoulder-length hair, sage green blouse, warm beige studio background. Photographic anatomy and natural-size aligned brown eyes with round pupils and small subtle consistent catchlights. Skin is noticeably beauty-smoothed with little pore texture, as a typical polished AI-generated portrait, but not cartoon or doll. Soft frontal window lighting. Clothes and face fully visible, no excessive glamour, no text or labels, no watermark, no collage. Square composition. This is the input image only; do not generate any after comparison or simulated editing result.

## Procesamiento

`backend/tools/procesar_retrato_nuevo_demo.py` sube este original a la cuenta DEMO
individual4, crea el álbum «04 · Retrato nuevo paso a paso DEMO» y solicita
humanización real, textura y cambio de fondo, por ese orden. Cada salida se guarda
como imagen nueva mediante la API. No se fabrica el estado completado.

Registro privado de trabajos y parámetros:
`private_data/demo_senati/retrato_nuevo/proceso.json`.

La humanización del nuevo retrato (trabajo 217) se detuvo por memoria insuficiente
y se conserva como fallida. No se presenta como resultado completado. Se continuó
con `--light`: textura (218) y ajustes (219), ambos procesados y guardados realmente.
No se cerraron las aplicaciones de la usuaria ni se redujeron los controles de seguridad.

Original para la web: `frontend/public/demo/retrato_nuevo_antes.webp`.
Resultados de esta ejecución: `retrato_nuevo_textura_piel.webp` y
`retrato_nuevo_ajustes.webp`, en esa misma carpeta. Las salidas de humanización
y fondo solo se publican si sus trabajos se ejecutan y completan en otra ocasión.

## Cómo ver los cambios

Con LUMIA encendido: `http://localhost:5000/demo/comparacion.html`.
También se accede desde el enlace «Ver antes y después juntos en pantalla completa»
de la portada. Tiene selector de ejemplo, vista paralela, deslizador y acercamiento.
Las copias públicas se reducen a 1000 px para visualizar; los originales y las
salidas completas quedan conservados en el almacenamiento privado.

Free Tier en las API permite usar lo que cada proveedor incluya y mientras exista
cuota; no acredita que todos sus modelos de imágenes sean gratuitos. Este ejemplo
no realiza llamadas a dichas API de imágenes.
