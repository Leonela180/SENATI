# Motor de IA

Completa esta ficha en la laptop con los datos **medidos**. No llenes ningún campo con valores supuestos.

## Hardware (salida de `scripts\diagnostico.ps1`)

- Laptop (modelo exacto):
- Precio real (S/):
- CPU:
- RAM:
- GPU y VRAM:
- Controlador NVIDIA:

## Modelo

- Repositorio: `stable-diffusion-v1-5/stable-diffusion-v1-5` (variante fp16)
- Licencia de los pesos: CreativeML OpenRAIL-M. Fecha de consulta:
- Licencia del código: Diffusers, Apache 2.0
- Versiones:
  - torch:
  - diffusers:
  - transformers:
- El filtro de seguridad (safety checker) está activo.

## Parámetros (`backend/app/ai/prompts.py`, Anexo D)

| Preset | Fuerza | Pasos | Guía | Semilla |
|---|---|---|---|---|
| natural | 0,30 | 30 | 6,0 | 1234 |
| fotografico | 0,36 | 32 | 6,5 | 1234 |
| detalle_suave | 0,22 | 28 | 5,5 | 1234 |

El lado menor de trabajo es de 640 px. El resultado vuelve al tamaño original y se rotula «editado con IA».

## Resultados de la evaluación (Anexo A)

- Tiempo medio por imagen (s):
- VRAM máxima (GB):
- Naturalidad (antes → después):
- Identidad conservada (% «misma persona»):
- Limitaciones observadas:
