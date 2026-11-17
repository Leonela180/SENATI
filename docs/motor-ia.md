# Motor de IA

Registro del perfil comprobado en esta laptop. Los campos sin medición no se completan con valores supuestos.

## Hardware (salida de `scripts\diagnostico.ps1`)

- Laptop: HP Laptop 15-fc0xxx (identificador informado por Windows).
- Precio real (S/):
- CPU: AMD Ryzen 7 7730U with Radeon Graphics.
- RAM visible para Windows: 15,34 GiB.
- GPU: AMD Radeon (TM) Graphics. VRAM dedicada no medida; la prueba usa CPU.
- Controlador NVIDIA: no utilizado.

## Modelo

- Repositorio: `stable-diffusion-v1-5/stable-diffusion-v1-5`. Pesos originales conservados; copia activa GGUF Q4_0 en `models/sd15-q4_0.gguf`.
- Licencia de los pesos: CreativeML OpenRAIL-M. Fecha de consulta:
- Licencias del código: stable-diffusion.cpp, MIT; Diffusers, Apache 2.0.
- Versiones:
  - torch: 2.6.0+cpu (filtro local).
  - diffusers: 0.31.0 (filtro y alternativa original).
  - transformers: 4.46.3.
  - stable-diffusion.cpp: ejecutable local, commit 3bad892.
  - OpenCV: paquete opencv-python-headless 4.14.0.94.
- Filtro CLIP local activo antes y después, en procesos separados con parte de los pesos en disco. Un fallo del filtro impide publicar el resultado.
- Configuración activa: `AI_ENGINE=local`, `AI_LOCAL_RUNTIME=cpp`, `AI_LITE_WORK_SIDE=320`, `AI_RESULT_BLEND=0.35`, `AI_DETAIL_INTENSITY=0.65`, un worker.

## Parámetros (`backend/app/ai/prompts.py`, Anexo D)

| Preset | Fuerza | Pasos | Guía | Semilla |
|---|---|---|---|---|
| natural | 0,30 | 30 | 6,0 | 1234 |
| fotografico | 0,36 | 32 | 6,5 | 1234 |
| detalle_suave | 0,22 | 28 | 5,5 | 1234 |

En el perfil ligero activo solo se ofrece «natural». El lado máximo de trabajo es de 320 px; se conserva la proporción mediante relleno y recorte. El resultado vuelve al tamaño original y se rotula «editado con IA». La microtextura y los reflejos se ajustan con detección automática; si no se detecta un rostro frontal se informa que ese ajuste no se aplicó. Los otros presets de la tabla se conservan para el motor Diffusers original, que no se ha activado en esta entrega.

La decodificación VAE usa la imagen de trabajo completa: se descartó una prueba con tiles porque producía marcas de unión. La lectura de pesos no mantiene el archivo completo mapeado en memoria. Los procesos se liberan al terminar y se detienen si se alcanza el límite de memoria o tiempo.

## Resultados de la evaluación (Anexo A)

- Tiempo del retrato público de prueba (1254×1254): 156,08 s. No se declara una media de varias imágenes.
- VRAM usada: 0 GB (CPU).
- RAM disponible mínima observada durante la prueba pública: 1,59 GiB; no equivale a RAM consumida exclusivamente por el motor.
- Naturalidad (antes → después):
- Identidad conservada (% «misma persona»):
- Limitaciones observadas: se requiere retrato frontal nítido para el ajuste automático; el trabajo de baja resolución tiene cambios suaves. La calidad no está garantizada para perfiles, ilustraciones o imágenes con varios rostros. Evaluación de naturalidad e identidad por varios revisores pendiente; no se asignan puntuaciones inventadas.
