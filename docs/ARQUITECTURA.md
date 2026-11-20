# Arquitectura de LUMIA AI: dónde está cada cosa

Esta guía sirve para encontrar rápido el archivo que hay que tocar.
Las rutas parten de la carpeta del proyecto.

## 1. Cómo viaja una acción

```text
 NAVEGADOR (frontend/, React)                         SERVIDOR (backend/, Flask)                       DATOS
 ─────────────────────────────                        ──────────────────────────                       ─────
 Página  (src/pages/Studio.tsx)                         Ruta  (app/api/jobs.py)                         PostgreSQL
   │ usa un «hook»                                        │ revisa sesión y permisos                      (app/models/*.py
   ▼                                                      │ (app/services/permission_service.py)           = tablas)
 Hook   (src/features/jobs/useJobs.ts)                    ▼                                                  ▲
   │ llama a api("/jobs")                               Servicio (app/services/job_service.py) ──────────────┘
   ▼                                                      │ crea el trabajo en estado «queued»
 Conexión (src/lib/api.ts)  ── /api/v1/jobs ──────────►   ▼
   (agrega la cookie de sesión y el token CSRF)         WORKER (app/workers/image_worker.py)            Archivos privados
                                                          │ toma el trabajo de la cola                    private_data/
                                                          ▼                                               originals/ results/
                                                        Motor de IA / Estudio (app/ai/*.py) ─────────────►
```

- **Conexión navegador ↔ servidor:** `frontend/src/lib/api.ts`. Todas las llamadas pasan por la función `api()`, que añade `/api/v1`.
  En desarrollo, `frontend/vite.config.ts` (línea `proxy`) reenvía `/api` al puerto 5000.
- **Conexión servidor ↔ base de datos:** variable `DATABASE_URL` del archivo `.env`, que lee `backend/app/config.py`.
- **Conexión servidor ↔ Gemini (Google):** `backend/app/services/gemini_service.py`, con la clave `GEMINI_API_KEY` del `.env`.
- **Registro de todas las rutas:** `backend/app/__init__.py`, línea `for module in (auth, users, ...)`.
- **Configuración (`.env`):** se explica en `.env.example`; los valores por defecto están en `backend/app/config.py`.

## 2. Mapa por módulos

Cada fila es un módulo de la aplicación. Para entender o cambiar un módulo, abre sus archivos de izquierda a derecha.

| Módulo | Pantalla (frontend/src/) | Hook / conexión | Rutas del servidor (backend/app/api/) | Lógica (backend/app/) | Tablas (backend/app/models/) |
|---|---|---|---|---|---|
| **Cuenta y sesión** | `pages/Login.tsx`, `Register.tsx`, `Profile.tsx` | `features/auth/useAuth.ts` | `auth.py`, `users.py` | `services/permission_service.py` | `user.py` → `users` |
| **Humanizar** | `pages/Humanize.tsx` | `features/jobs/useJobs.ts`, `features/images/useImages.ts` | `images.py`, `jobs.py` | `services/job_service.py`, `workers/image_worker.py`, `ai/lite_engine.py`, `ai/facial_detail.py` | `image.py`, `job.py` → `images`, `processing_jobs` |
| **Estudio de edición** (7 herramientas) | `pages/Studio.tsx` | `features/jobs/useJobs.ts`, `features/gallery/useGallery.ts` | `jobs.py` | `ai/editing.py`, `ai/skin_texture.py`, `services/job_service.py` (límites de cada herramienta) | `processing_jobs` |
| **Ilustración a realista** (laboratorio) | `pages/Realistic.tsx` | `features/jobs/useJobs.ts` | `jobs.py` | `ai/realistic_engine.py`, `ai/capabilities.py`, `ai/diffusers_probe.py` | `processing_jobs` |
| **Galería y álbumes** | `pages/Gallery.tsx` | `features/gallery/useGallery.ts` | `gallery.py` | `services/image_service.py` | `gallery.py` → `albums` |
| **Historial y detalle** | `pages/History.tsx`, `JobDetail.tsx` | `features/jobs/useJobs.ts` | `jobs.py` (`/compare`, `/download`, `/retry`, `/save`) | `services/job_service.py` | `processing_jobs` |
| **Chatbot (asistente)** | `pages/Assistant.tsx`, `components/FloatingAssistant.tsx` | `features/assistant/guiaLocal.ts` | `assistant.py` | `services/asistente_instrucciones.py`, `services/gemini_service.py` | ninguna (no guarda mensajes) |
| **Generar con IA** (desactivado) | `pages/Generate.tsx` | `features/generations/useGenerations.ts` | `generations.py` | `services/gemini_service.py` | `gallery.py` → `generations` |
| **Horario y horas** | `pages/Hours.tsx` | `features/hours/useHours.ts` | `hours.py` | `services/hours_service.py` | `hours.py` → `work_schedules`, `time_entries` |
| **Equipo e invitaciones** | `pages/Team.tsx`, `Invitation.tsx`, `components/TeamProgress.tsx` | `features/teams/useTeams.ts` | `teams.py` | `services/team_service.py` | `workspace.py` → `workspaces`, `team_memberships`, `team_invitations` |
| **Permisos del equipo** | `components/LeavePanel.tsx` (dentro de Equipo) | `lib/api.ts` | `leave.py` | — | `leave.py` → `leave_requests` |
| **Administración** | `pages/Admin.tsx` | `features/teams/useTeams.ts` | `admin.py` | `services/permission_service.py` (`admin_required`) | `audit.py` → `audit_events`, `service_incidents` |
| **Portada pública** | `pages/Home.tsx`, `app/layouts/PublicLayout.tsx` | `public/demo/ejemplos.json` | `/health` en `__init__.py` | `tools/preparar_ejemplos.py` | — |

Otras piezas comunes:

- **Menú lateral y barra superior:** `frontend/src/app/layouts/AppLayout.tsx` (lista `SECTIONS`).
- **Direcciones de cada página (rutas del navegador):** `frontend/src/app/router.tsx`.
- **Botones, tarjetas y campos reutilizables:** `frontend/src/components/ui/`.
- **Seguridad de archivos subidos:** `backend/app/security/uploads.py`.
- **Dónde se guardan los archivos:** `backend/app/storage/local_private.py`.
- **Cambios de tablas:** `backend/migrations/versions/` (6 migraciones, se aplican con `alembic upgrade head`).
- **Pruebas:** `backend/tests/` (servidor), `frontend/src/tests/` (unitarias) y `frontend/e2e/` (navegador).
- **Scripts de Windows:** `scripts/` (instalar, iniciar, detener, verificar).
- **Scripts de apoyo y demostración:** `backend/tools/` (ver su `README.md`).

## 3. «Quiero cambiar…» → dónde

| Quiero cambiar… | Archivo | Qué buscar dentro |
|---|---|---|
| El color principal (celeste/azul) | `frontend/src/styles/globals.css` | `--g1`, `--g2`, `--g3` dentro del primer `:root` |
| Los colores que se eligen en Perfil | `frontend/src/styles/globals.css` y `frontend/src/lib/appearance.ts` | `data-accent="ocean"`… y `ACCENTS` (nombre que se muestra) |
| Colores del modo oscuro | `frontend/src/styles/globals.css` | bloque `.dark {` |
| Lo que responde el chat **sin** IA | `frontend/src/features/assistant/guiaLocal.ts` | `RECIPES`, `SUGERENCIAS`, `BIENVENIDA` |
| Lo que responde el chat **con** Gemini | `backend/app/services/asistente_instrucciones.py` | `CHAT_SYSTEM` |
| El modelo de Gemini del chat | `.env` | `GEMINI_CHAT_MODEL` |
| Cuántos mensajes por hora permite el chat | `backend/app/api/assistant.py` | `@limiter.limit("40/hour")` |
| Las opciones del menú | `frontend/src/app/layouts/AppLayout.tsx` | `const SECTIONS` |
| Textos de la portada | `frontend/src/pages/Home.tsx` | el texto que quieras cambiar |
| Nombres y valores iniciales de las herramientas del Estudio | `frontend/src/pages/Studio.tsx` | `TOOLS` |
| Límites que acepta el servidor para cada herramienta | `backend/app/services/job_service.py` | `clean_tool_params` |
| Cómo trabaja cada herramienta del Estudio | `backend/app/ai/editing.py` | la función con el nombre de la herramienta (`mejorar_calidad`, `cambiar_fondo`…) |
| La textura de piel | `backend/app/ai/skin_texture.py` | `textura_piel` |
| El motor de humanización (pasos, fuerza) | `backend/app/ai/lite_engine.py` y `backend/app/ai/prompts.py` | `PRESETS` |
| Tamaño máximo de las imágenes subidas | `.env` | `MAX_UPLOAD_MB`, `MAX_IMAGE_PIXELS` |
| Reintentos de un trabajo que falla | `backend/app/config.py` | `AI_MAX_ATTEMPTS` |
| Activar el laboratorio realista | `.env` | `AI_REALISTIC_ENABLED=1` (solo con los pesos instalados) |
| Mensajes de error del chat | `backend/app/api/assistant.py` | `ERRORS` |
| Zona horaria de las horas | `.env` | `APP_TZ_OFFSET_HOURS` |

Después de cambiar algo, comprueba que nada se rompió:

```powershell
cd backend;  .venv\Scripts\python -m pytest -q        # servidor
cd frontend; npm test; npm run build                   # pantallas
```

## 4. Cómo funciona el chatbot

El asistente está en dos lugares: la página **Asistente** y el **botón flotante** que
aparece en todas las pantallas (`FloatingAssistant.tsx` muestra la misma página en
pequeño).

Tiene dos formas de responder:

1. **Guía local (sin IA).** Se usa cuando la persona no marca «Usar IA (Gemini)», cuando
   no hay clave en el `.env` o cuando Gemini falla. El navegador busca palabras clave en
   el mensaje (por ejemplo «antigua», «fondo» o «lunar») y muestra una receta fija con pasos
   y un aviso de límites. No sale nada de la computadora. Las recetas están en `guiaLocal.ts`.
2. **Gemini (con IA).** Si la persona marca el consentimiento y hay clave, el navegador
   envía **solo el texto** de los últimos mensajes a `POST /api/v1/assistant/chat`.
   El servidor:
   - rechaza la solicitud si no hay consentimiento;
   - recorta a 12 mensajes de 1000 caracteres como máximo;
   - permite 40 mensajes por hora por persona;
   - añade las instrucciones de `asistente_instrucciones.py` y llama a Gemini;
   - si la respuesta termina en `HERRAMIENTA: <nombre>`, la quita del texto y el navegador
     muestra el botón «Abrir herramienta»;
   - registra solo que hubo una consulta y si funcionó, **nunca el contenido**.

El chat **no ve las imágenes**, no puede aprobar permisos ni ejecutar acciones: solo
orienta y lleva a la herramienta correcta. Si Gemini falla (sin internet, sin cuota o
clave inválida), responde la guía local con un aviso.
