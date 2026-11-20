# Herramientas de apoyo (`backend/tools/`)

Son scripts que se ejecutan a mano. **La aplicación no los usa para funcionar.**
Se ejecutan desde `backend/` con el Python del entorno, por ejemplo:
`.venv\Scripts\python tools\verificar_cuentas_demo.py`.

## Demostración SENATI (cuentas y grupos DEMO)

Las cuentas DEMO se guardan en el PostgreSQL de la laptop. Sus claves están en
`private_data/demo_senati/ACCESOS-PRIVADOS.md`, que no se sube a GitHub.

| Script | Para qué sirve |
|---|---|
| `preparar_cuentas_demo.py` | Crea las 5 cuentas individuales y los 5 grupos (líder + 2 integrantes), con sus álbumes, trabajos reales, horarios y permisos |
| `verificar_cuentas_demo.py` | Comprueba que las cuentas y los permisos DEMO funcionan, sin mostrar las claves |
| `cerrar_trabajos_demo.py` | Guarda los resultados terminados y avisa cuáles siguen en cola |
| `encolar_humanizaciones_demo.py` | Pone en cola dos humanizaciones reales en cuentas DEMO |
| `validar_conversion_demo.py` | Hace una conversión «ilustración a realista» de prueba en una cuenta DEMO |
| `habilitar_laboratorio_validado.py` | Activa el laboratorio realista solo en esta laptop, después de validarlo |
| `procesar_retrato_nuevo_demo.py` | Sube un retrato propio y guarda cada etapa procesada |
| `corregir_ejemplos_calidad.py` | Rehace los ejemplos de ampliación con el método natural |
| `exportar_demo_senati.py` | Copia a la portada ejemplos propios ya procesados |

## Portada y ejemplos

| Script | Para qué sirve |
|---|---|
| `preparar_ejemplos.py` | Crea la galería «Ejemplos reales» de la portada con las herramientas reales del Estudio |
| `preparar_portada.py` | Publica en la portada un antes/después real de humanización |
| `preparar_demostracion.py` | Genera ejemplos reproducibles del Estudio a partir de un retrato sintético autorizado |

## Motor de IA

| Script | Para qué sirve |
|---|---|
| `preparar_ligero.py` | Cuantiza los pesos de Stable Diffusion para el motor ligero (lo llama `scripts/preparar_motor_ligero.ps1`) |
| `compactar_pesos.py` | Crea `models/sd15-compact.safetensors`, el archivo que usa el laboratorio realista |
| `validar_ligero.py` | Prueba real del motor ligero |
| `validar_humanizacion.py` | Prueba real de humanización sin tocar la configuración |
| `verificar_circuito.py` | Ejecuta un trabajo real de punta a punta (lo llama `scripts/verificar.ps1`) |

## Pruebas y mediciones

| Script | Para qué sirve |
|---|---|
| `servidor_pruebas.py` | Levanta la API y el worker contra la base `lumia_test`, sin Gemini, para Playwright |
| `probar_navegador.py` | Inicia el servidor de pruebas, corre Playwright y lo cierra |
| `medir_api.py` | Mide los tiempos de respuesta de la API (RNF-03) |
| `validar_gemini.py` | Prueba texto por defecto, sin mostrar clave ni respuesta. Imágenes solo con `--imagenes` y `GEMINI_IMAGE_ENABLED=1` |

Los ensayos antiguos (prototipos de ojos y piel y las pruebas de SD 1.5 en CPU)
se retiraron el 20/11/2026. Si se necesitan, siguen en el historial de Git.
