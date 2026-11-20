# Auditoría y plan de evolución de LUMIA AI

Fecha: 16/11/2026. Revisión local sobre `main`, commit inicial `6c16aa9`.

> **Actualización tras la implementación:** el diagnóstico de abajo conserva la fotografía inicial. Con autorización del usuario se verificó Python 3.12.10 fuera del aislamiento (el error de intérprete también estaba condicionado por permisos), se instalaron las dependencias ausentes y se aplicó la migración `c3e5a7f1b9d2` tras verificar el respaldo. Alembic ya no encuentra diferencias. Pasan 69 pruebas backend, 6 unitarias frontend y los seis recorridos de navegador de la versión final. El enlace HTTPS responde y usa cookie Secure/CSRF. Gemini reconoce el modelo y la clave, pero la generación real devuelve 429 por cuota; Humanizar sigue en mock. Ver [entrega práctica](../entrega-senati.md).

## Alcance y límites

**Cierre posterior de la humanización:** tras reducir la memoria, se activó el motor local CPP y se validó el flujo real por HTTPS con microtextura y reflejos oculares. La prueba duró 156,08 s, los filtros aprobaron entrada y salida, y la descarga quedó rotulada. Pasan 85 pruebas backend, 6 unitarias frontend y 6 recorridos E2E; el ensayo público real es adicional a esos E2E de simulación. La evidencia técnica está en `evidencias/mejoras_20261116/ia_real_cpu.json`. Las secciones de diagnóstico inicial de esta auditoría se conservan como registro histórico y quedan superadas por este cierre y `estado.md`.

Inventario del repositorio, documentación principal y guía de implementación, rutas React, cliente API, componentes compartidos, endpoints Flask, servicios, modelos SQLAlchemy, migraciones, worker, motores, scripts y estructura de pruebas. Consulta autenticada de PostgreSQL mediante una conexión con `default_transaction_read_only=on`. No se consultaron imágenes ni registros personales.

Esta revisión combina inspección estática y comprobaciones locales. No equivale a una certificación completa: pytest, recorridos de navegador, contraste, rendimiento y motores reales requieren validaciones adicionales. Las evidencias de noviembre 13/14 pertenecen a otra ejecución; no demuestran que esta instalación funcione actualmente.

## Resultado principal

La aplicación contiene una base funcional amplia que debe conservarse. El problema inmediato es la diferencia entre código y entorno instalado, antes de abordar un rediseño mayor.

| Área | Documentado / implementado | Comprobación local |
|---|---|---|
| Git | Proyecto versionado | `main`, árbol inicialmente limpio; `.env` no está versionado. No se verificó sincronización remota |
| Frontend | React, TypeScript, Vite, Tailwind, Query; módulos y rutas presentes | 3 pruebas iniciales pasan y compilación correcta |
| Backend | Flask, sesiones, CSRF, Argon2, permisos y auditoría | Entorno virtual inutilizable: su Python base 3.12 ya no existe |
| PostgreSQL | Modelos y tres migraciones en código | Servicio 17.12 activo; rol conectado sin superusuario; revisión instalada `7b1d2e9a4c10` |
| Módulos nuevos | Galería, Gemini, estudio ampliado y horas | Falta aplicar `c3e5a7f1b9d2`; hay ocho tablas de aplicación, faltan cuatro y cambios en `images` / `processing_jobs` |
| IA | Motor local y simulación diferenciados | `.env` mantiene `AI_ENGINE=mock`; no se activó ningún motor ni servicio externo |
| Pruebas backend | Evidencias históricas: 55 pasan, 1 omitida | No ejecutadas: Python roto y fixtures que modifican tablas |
| Navegador | Cinco casos Playwright existentes | No ejecutados: necesitan API/worker y crean datos; configuración apunta a `localhost:5000` |

## Hallazgos por prioridad

### P0 — Recuperar una instalación consistente

1. `backend/.venv/pyvenv.cfg` apunta a un intérprete inexistente. La presencia del archivo `python.exe` no garantiza que el entorno funcione. Requiere reparar Python y dependencias con autorización.
2. La base local no está al día. La tercera migración añade `albums`, `generations`, `work_schedules`, `time_entries`, `images.album_id`, índices, FK y `processing_jobs.tool` con su restricción. Revisar respaldo antes de autorizar `alembic upgrade head`; no se ejecutó.
3. `backend/tests/conftest.py` utiliza `drop_all/create_all` en cada prueba. `TEST_DATABASE_URL` puede apuntar a cualquier base sin protección adicional. Antes de pytest, añadir comprobación de aislamiento respecto de la base real y autorizar una base desechable. Algunos tests de autenticación también crean/eliminan tablas.

### P1 — Fiabilidad y coherencia del producto

4. Había errores de consulta representados como listas vacías en panel, historial y galería. Corregido en esta etapa con recuperación visible.
5. `AppLayout` redirigía al login ante cualquier fallo de `/auth/me`, incluso un 500 o corte de conexión. Corregido para ofrecer reintento; un 401 sigue enviando al login.
6. El cliente API asumía un token CSRF y JSON válido en respuestas exitosas. Corregido para emitir errores legibles; se comprueba el límite de una renovación CSRF y la conservación de idempotencia.
7. `docs/motor-ia.md` asegura filtro de seguridad activo; `local_engine.py` tiene una alternativa con `safety_checker=None` para pesos de archivo único. Resolver esa diferencia y probar el filtro antes de habilitar IA real.
8. README promete procesamiento local; debe distinguir explícitamente Gemini y la descarga inicial de pesos. Gemini envía la descripción a Google con consentimiento; rembg puede descargar pesos ausentes. `AI_ENGINE=mock` controla humanización, no desactiva por sí mismo Gemini ni segmentación.
9. El borrado de imágenes puede coincidir con un worker procesándolas. Revisar coordinación y archivos huérfanos; riesgo por inspección, no reproducido.
10. El renombrado de álbum puede chocar con la restricción de nombre único y terminar en 500. Añadir manejo de conflicto y prueba tras recuperar backend.
11. La recuperación de trabajos obsoletos ocurre al iniciar el worker. Revisar el límite de intentos y concurrencia cuando un trabajo CPU supera 15 minutos. El latido se actualiza entre trabajos: un procesamiento largo puede aparentar worker caído.
12. Validaciones de JSON en varios endpoints presuponen cadenas/diccionarios; entradas con tipos incorrectos pueden generar 500. Añadir casos de contrato y validación consistente.

### P2 — Experiencia premium y entrega

13. Conservar paleta marfil, tinta y cobre, fuentes locales Inter/Fraunces y navegación existente. Extender jerarquía y espacios a todos los módulos con revisión visual móvil/escritorio.
14. Completar estados de carga/error, acciones en lote con resultados parciales, prevención de doble envío y selección coherente al buscar/paginar.
15. El comparador usa un control transparente: añadido indicador de foco en su figura; contraste y manejo por teclado requieren comprobación en navegador.
16. Todos los módulos se importan de forma inmediata. Compilación inicial JS: aproximadamente 488 kB; considerar carga por rutas tras medir navegación y conservar recuperación ante fallos de carga.
17. La documentación de estado conserva secciones de dos migraciones / dos e2e junto a la actualización de tres migraciones / cinco e2e. Separar evidencia histórica y estado actual.
18. No se encontró un flujo CI en el inventario. Incorporar checks reproducibles después de aislar pruebas y fijar un entorno instalable.

## Plan por etapas y criterios de cierre

| Etapa | Trabajo | Comprobación / autorización |
|---|---|---|
| 0. Diagnóstico | Inventario, discrepancias, conexión de solo lectura y línea base | Documentado aquí; validación dinámica backend pendiente |
| 1. Fiabilidad frontend | Errores recuperables, sesión ante caídas, respuestas API, cargas y métricas honestas | Implementado; 6 tests pasan, TypeScript y build correctos |
| 2. Recuperación local | Reparar intérprete y entorno; respaldo; aplicar migración existente; aislar pruebas | Requiere autorización para instalación y cambios de BD. Cerrar con health, Alembic y pytest en base separada |
| 3. Diseño premium | Refinar panel, navegación móvil, estudio y galería; estados compartidos, accesibilidad | Inicio limitado: cabecera de escritorio, carga del panel y foco del comparador. Pendiente revisión visual a 390/768/1440 px y flujos completos |
| 4. Robustez backend | Validación de entradas, conflictos de álbumes, concurrencia de borrado/worker y recuperación | Casos de regresión y PostgreSQL aislado; solicitar autorización si exige migraciones nuevas |
| 5. Entrega SENATI | Actualizar RF, casos de uso, esquema, endpoints, guía y evidencias; automatizar checks | Instalación reproducible y cinco e2e, incluyendo permisos, descarga y móvil |
| 6. IA real | Validar motor, filtro, hardware, tiempos e identidad antes de activar | Mantener mock hasta aprobación y evidencia. Gemini requiere validación independiente y consentimiento |

## Cambios ya realizados

- Cliente API: rechaza respuesta inesperada y fallo CSRF con `ApiError` legible.
- Pruebas: respuesta HTML, fallo de token sin escritura y renovación limitada preservando clave de idempotencia.
- Componente reutilizable de error con botón de reintento.
- Panel, historial y galería distinguen fallos de colecciones vacías.
- Panel distingue carga inicial y total desconocido; etiqueta «Trabajos registrados» evita presentar trabajos fallidos/en cola como terminados.
- Sesión: reintento ante fallos del servicio y redirección ante falta de autenticación.
- Cabecera de escritorio y foco visible del comparador, conservando identidad y módulos.

## Validación actual

`npm test`: 6 pruebas pasan en 2 archivos. `npm run build`: TypeScript y Vite completan sin errores. PostgreSQL: versión, revisión, tablas y privilegio del rol consultados en solo lectura. No se modificó `.env`, no se instalaron paquetes y no se modificó la base de datos.

Pendientes: ejecución de backend, equivalencia detallada del esquema con modelos (`alembic check`), revisión visual y pruebas de integración. No se afirma que el rediseño premium ni la auditoría dinámica estén terminados.
