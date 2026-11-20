# Estado de LUMIA AI

## Cierre funcional del 20/11/2026

Estado vigente: [cierre y demostración](cierre-2026-11-20.md).
Se corrigieron la edición encadenada y el reintento de herramientas, se prepararon
20 cuentas DEMO en 5 grupos y 5 perfiles individuales y se integró la conversión
experimental con resultados reales. Las secciones inferiores son registros anteriores.

## Revisión del 20/11/2026

Lista actual y orden de cierre: [auditoría del 20 de noviembre](auditoria-2026-11-20.md).
GitHub revisado hasta `5bee905`: espera del motor sin consumir intentos y laboratorio
oculto cuando está deshabilitado. Backend: 117 pruebas aprobadas; frontend: 6;
compilación correcta y PostgreSQL sin migraciones pendientes. La calidad visual
de la conversión sigue pendiente; no se declara el proyecto completo.
Navegador en esta revisión: 13 recorridos aprobados y 1 fallido al encadenar
quitar fondo y desenfoque; detalle y evidencia en la auditoría enlazada.

## Etapa del 19/11/2026

**Respaldo de avance:** consultar [pendientes para retomar](PENDIENTES-2026-11-19.md).
Las secciones fechadas anteriores son registros históricos, no comprobaciones de la versión actual.

- Chat flotante, ampliacion x2/x4, liderazgo y solicitudes de permiso implementados.
- Chat de texto con Gemini validado con `gemini-3.5-flash-lite`; generacion de
  imagenes sigue sin cuota disponible.
- 115 pruebas backend aprobadas, 1 omitida; 6 pruebas frontend aprobadas;
  los 14 recorridos de navegador completaron sin fallos.
- Portada con fotografias sinteticas propias y resultados reales del editor.
  La muestra de humanizacion local tardo 133,19 s; el cambio es sutil.
- Base respaldada y migrada a `f8c0e2a4b6d8`; `alembic check` sin diferencias.
- La conversion de personajes permanece deshabilitada hasta superar revision
  visual. Los experimentos se documentan en [etapa-2026-11-19.md](etapa-2026-11-19.md).
- Faltan la integracion y puesta en marcha finales y las cuentas de demostracion.

## Cierre de comprobacion de entrega

- Nueva etapa: restauracion conservadora de fotos deterioradas, guia local de edicion, preferencias de apariencia/avatar y enlaces de invitacion dirigidos con correo/WhatsApp preparados.
- 92 pruebas backend y 6 pruebas frontend pasan. TypeScript/Vite compila. Migracion `d4f6b8a2c0e1` aplicada con respaldo verificado; `alembic check` sin diferencias.
- Ocho recorridos Playwright pasan en 31,5 s en base aislada: incluye preferencias persistentes, restauracion al cambiar de pantalla/recargar e invitacion dirigida con registro y aceptacion. El entorno E2E simula solo la humanizacion; las herramientas de edicion ejecutan sus algoritmos reales.
- Las preferencias se guardan en el navegador. El asistente usa recorridos preparados, no un modelo de chat. El correo abre el cliente del propietario: no hay envio SMTP automatico.
- Seguimiento de trabajos: consulta automatica del historial, tiempo desde la creacion del trabajo y recuperacion tras navegar/recargar. Una falla de consulta no se muestra como falla de procesamiento.

- El enlace HTTPS responde con `status=ok`, motor `local`, runtime `cpp` y latido del worker de 3 segundos en la ultima consulta.
- Se repitio la solicitud real de imagen a Gemini con la configuracion existente: sigue devolviendo `gemini_limite`. No se cambio de proveedor ni se activo facturacion.
- El script `scripts/verificar.ps1` comprueba ahora el latido despues de las pruebas, detecta errores al consultar la revision y restaura la carpeta inicial incluso cuando falla.
- La entrega completa con Gemini sigue pendiente de cuota disponible y de una generacion real satisfactoria; el porcentaje comunicado es una estimacion, no una garantia de ausencia de errores.

## Comprobación local del 16/11/2026

- Python 3.12.10 accesible fuera del aislamiento de ejecución y dependencias del editor instaladas.
- PostgreSQL 17.12 actualizado a `c3e5a7f1b9d2`, con respaldo previo verificado y sin diferencias en `alembic check`.
- 85 pruebas backend y 6 pruebas unitarias frontend pasan; compilación TypeScript/Vite correcta.
- Seis recorridos de navegador en base separada pasan: equipos, circuito de humanización mock, edición real de fondo, horas, consentimiento Gemini y vistas móvil/escritorio.
- Enlace HTTPS temporal activo; cookie Secure y protección CSRF comprobadas.
- Gemini: modelo accesible con la clave configurada. Generación real bloqueada por cuota de Google (429); no se puede dar por validada.
- Humanización real activada tras validación: `AI_ENGINE=local`, `AI_LOCAL_RUNTIME=cpp`, perfil natural, lado máximo de trabajo de 320 px y mezcla de IA 0,35. Los filtros locales se ejecutan antes y después en procesos separados.
- Prueba pública real: 156,08 s, original intacto, microtextura aplicada y dos zonas oculares realzadas, descarga rotulada y ningún error JavaScript. El latido del worker no superó 5 s de antigüedad durante el trabajo. Mínimo observado de RAM disponible: 1,59 GiB.
- Los prototipos privados de piel/ojos sirvieron de referencia para un ajuste genérico con detección automática. Las máscaras calibradas a una sola foto no se reutilizan indiscriminadamente.
- La validación técnica y visual de un retrato no sustituye una evaluación con varios retratos/revisores ni garantiza idéntica calidad con cualquier imagen.
- Guía breve: [entrega-senati.md](entrega-senati.md). Evidencias: `docs/evidencias/mejoras_20261116/`.

Los apartados siguientes conservan las evidencias históricas de desarrollo y no sustituyen esta comprobación local.

> **Actualización del 14/11/2026: módulos nuevos.**
> - **Estudio de edición:** quitar lunar, cambiar fondo, desenfoque gaussiano, mejorar calidad y ajustes.
> - **Galería:** álbumes, subida múltiple y procesamiento por lotes.
> - **Generar con IA:** con Gemini, aviso y consentimiento.
> - **Horario y horas:** horario, marcación, registros manuales, horas por recuperar y CSV del equipo.
>
> Evidencias, ejecutadas en la PC de desarrollo con PostgreSQL y el motor en modo simulación, en `docs/evidencias/desarrollo_20261114/`:
> - pytest: 55 pasan y 1 se omite (la prueba de ojos, porque falta su imagen privada);
> - Vitest: 3 pasan;
> - Playwright: 5 pasan;
> - `alembic check`: sin diferencias.
>
> La segmentación real (U²-Net) se probó con imágenes: unos 0,3 s por imagen en CPU.
> **No se probó todavía:** la generación real con Gemini (falta tu clave) y la humanización en la laptop HP con Radeon.

Actualizado el 13/11/2026.

Lo marcado como «probado» se ejecutó en la PC de desarrollo, que no tiene GPU NVIDIA, con `AI_ENGINE=mock`, primero en un PostgreSQL 16 temporal y después en el **PostgreSQL 17.12 real** (usuario `lumia_app` sin superusuario). Las salidas están en `docs/evidencias/desarrollo_20261113/`; las de PostgreSQL 17 terminan en `_postgresql17.txt`, incluida la estructura de las 8 tablas.

**Ninguna de estas pruebas comprueba todavía la IA real.** Esa prueba se hace en la laptop; ver `LAPTOP_PASO_A_PASO.md`.

## Criterios de aceptación (skill §14)

| # | Criterio | Implementado | Probado | Evidencia |
|---|---|---|---|---|
| 1 | La landing pública carga sin sesión y explica la humanización | Sí | Sí | capturas_modo_simulacion/01 y 11 |
| 2 | Registro, login, logout y permisos | Sí | Sí | pytest.txt (test_auth) |
| 3 | Una carga válida guarda el original en privado y crea el trabajo; una carga inválida se rechaza | Sí | Sí | pytest.txt (test_imagenes) |
| 4 | El modelo real se comprobó y se evaluó visualmente | El código, sí | **No** | **Pendiente (laptop)** |
| 5 | Estado, historial, comparación y descarga, con autorización | Sí | Sí, en modo simulación | pytest.txt, playwright.txt |
| 6 | Otro usuario no puede ver el original ni el resultado ajeno | Sí | Sí | pytest.txt (CP-11) |
| 7 | Diseño cuidado y accesible en celular y escritorio | Sí | En parte: falta medir el contraste AA | capturas |
| 8 | Migraciones y pruebas ejecutadas, con resultados documentados | Sí | Sí | alembic.txt, pytest.txt, vitest.txt |
| 9 | La instalación se repite en otra PC compatible | Los scripts, sí | **No** | **Pendiente: verificar_*.txt de la laptop** |
| 10 | Este archivo declara con precisión qué está implementado, qué está probado y qué falta | Sí | Sí | este archivo |

## Casos de prueba del informe

| CP | Qué prueba | Dónde | Resultado en la PC de desarrollo |
|---|---|---|---|
| CP-01 | Registro válido | test_cp01_registro_valido | Pasa |
| CP-02 | Correo ya registrado | test_cp02_correo_existente | Pasa |
| CP-03 | Login inválido con mensaje genérico | test_cp03_login_invalido | Pasa |
| CP-04 | Carga de un JPG válido | test_cp04_carga_jpg_valida | Pasa |
| CP-05 | Archivo con extensión falsa | test_cp05_extension_falsa | Pasa |
| CP-06 | Carga sin la declaración de IA | test_cp06_sin_declaracion | Pasa |
| CP-07 | Idempotencia | test_cp07_idempotencia | Pasa |
| CP-08 | Dos workers no toman el mismo trabajo | test_cp08_dos_workers | Pasa (con PostgreSQL) |
| CP-09 | Fallo del motor sin trazas internas | test_cp09_fallo_del_motor | Pasa |
| CP-10 | Humanización real con el modelo | Paso 13 y verificar_circuito.py | **Pendiente (laptop)** |
| CP-11 | Acceso cruzado devuelve 404 | test_cp11_acceso_cruzado | Pasa |
| CP-12 | Descarga autorizada y auditada | test_cp12_descarga_autorizada | Pasa |
| CP-13 | POST sin token CSRF devuelve 403 | test_cp13_csrf | Pasa |
| CP-14 | Instalación en otra PC | verificar.ps1 | **Pendiente (laptop)** |

Además, estas pruebas pasan:

- **pytest:** RF-03 (logout), RF-05 (cambio de clave), RF-06 (megapíxeles), RF-08 (sin ruta pública), RF-18 a RF-21 (equipos y admin), RNF-01 (límite de intentos), RNF-07 y RNF-10.
- **Vitest:** 3 pruebas del frontend.
- **Playwright:** 2 flujos completos en el navegador.

## Diferencias con el informe

- **Módulos nuevos que el informe aún no describe:**
  - Estudio de edición (5 herramientas);
  - Galería con álbumes;
  - Generación con Gemini (servicio externo con consentimiento);
  - Horario y horas.

  Hay que agregar sus RF, casos de uso, tablas (`albums`, `generations`, `work_schedules`, `time_entries` y la columna `processing_jobs.tool`) y endpoints.
- **Laptop real:** es una HP con Radeon y unos 16 GB de RAM, sin NVIDIA. Hay que actualizar los costos, los requisitos y el motor en CPU.

- **Endpoints nuevos.** Estos 5 no están en la Tabla E1:
  - `GET /auth/csrf`
  - `GET /health`
  - `PATCH /images/{id}/visibility`
  - `GET /teams/{id}/stats`
  - `PATCH /admin/incidents/{id}`
- **Esquema en dos migraciones.**
  - La migración `24fc4214b845` crea el esquema inicial.
  - La migración `7b1d2e9a4c10` lo ajusta al diccionario de datos: JSONB, NOT NULL y el CHECK «completed ⇒ resultado».
  - `alembic check` no encuentra diferencias con los modelos.
- **Versiones de la PC de desarrollo.** Las pruebas pasaron en PostgreSQL 17.12, como pide el informe, pero con Python 3.11. Python 3.12 se confirma en la laptop.

## Pendientes

1. En la laptop:
   - instalar PyTorch y Diffusers;
   - descargar los pesos del modelo;
   - anotar las versiones en `docs/motor-ia.md`.
2. Ejecutar `verificar.ps1` con `AI_ENGINE=local` (CP-10 y CP-14) y guardar su registro.
3. Hacer la evaluación del Anexo A con `python -m app.ai.evaluation` y los 3 revisores.
4. Tomar capturas con IA real para la sección 4.5.13 del informe. Las capturas actuales son del modo simulación.
5. Medir el contraste AA de la paleta (RNF-04) con las DevTools.
6. Cambiar el recuadro «Antes · Después» de la landing por un ejemplo real cuando exista.
