# LUMIA AI

Entrega SENATI: incluye humanizacion local, Estudio con restauracion conservadora de fotos, guia de edicion sin API, personalizacion de apariencia y avatar, y equipos con invitaciones dirigidas compartibles por correo/WhatsApp. Consulta [la guia de demostracion](docs/entrega-senati.md) para conocer el alcance y los requisitos reales.

Aplicación web para editar y organizar imágenes generadas por IA. Incluye humanización de retratos con un motor local, Estudio de edición, galería, equipos con permisos, control de horas y un chat asistente. Los originales se conservan en la computadora que aloja la aplicación; si accedes desde otro dispositivo, las imágenes se suben a esa computadora. El chat con Gemini envía solo el texto que escribes, y solo con tu consentimiento; la generación de imágenes por API está desactivada (`GEMINI_IMAGE_ENABLED=0`).

**Entrega actual en esta laptop:** humanización real con `AI_ENGINE=local`, motor CPU optimizado, microtextura de piel y realce de reflejos existentes en los ojos. El circuito público de subida, procesamiento, comparación y descarga está comprobado. Consulta la [guía práctica SENATI](docs/entrega-senati.md).

> **¿Buscas dónde está algo?** La **[guía de arquitectura](docs/ARQUITECTURA.md)** tiene el mapa por módulos, cómo se conecta cada parte, cómo funciona el chatbot y una tabla «quiero cambiar… → archivo».

Proyecto de Innovación SENATI «Mejora de piel con IA».

> **¿Primera vez en una computadora nueva?** Sigue **[docs/LAPTOP_PASO_A_PASO.md](docs/LAPTOP_PASO_A_PASO.md)**: desde instalar los programas y clonar este repositorio hasta ver la web funcionando.

## Módulos

Último estado y pendientes: [auditoría](docs/historial/auditoria-2026-11-20.md) y [cierre del 20/11/2026](docs/historial/cierre-2026-11-20.md).
La demostración se prepara con cuentas y grupos identificados como DEMO; las
credenciales permanecen en `private_data/demo_senati/ACCESOS-PRIVADOS.md`, fuera de Git.

| Módulo | Qué hace | ¿Necesita GPU? |
|---|---|---|
| **Humanizar** | Stable Diffusion 1.5 *image-to-image*: piel, ojos, cabello y luz más naturales | Recomendable; en CPU funciona a 512 px y tarda minutos |
| **Estudio de edición** | Restauración conservadora, textura de piel, quitar lunares o manchas, cambiar fondo, desenfoque, ampliación digital ×2/×4 y ajustes de color y rotación | No (CPU) |
| **Generar con IA** | Desactivado por defecto (`GEMINI_IMAGE_ENABLED=0`). El código se conserva; el chat redacta prompts para crear la imagen fuera y subirla | No (servicio externo) |
| **Galería** | Subida múltiple, álbumes, búsqueda, mover, borrar y procesamiento por lotes | No |
| **Historial y detalle** | Comparador antes/después, descarga rotulada y trazabilidad | No |
| **Horario y horas** | Horario semanal, marcar entrada/salida, registros manuales con motivo, horas trabajadas vs. esperadas, horas por recuperar y reporte del equipo en CSV | No |
| **Equipo y administración** | Invitaciones dirigidas de un solo uso, imágenes compartidas, líder que revisa permisos, estadísticas y supervisión técnica | No |
| **Asistente flotante** | Ayuda sin abandonar la pantalla: guía local y conversación Gemini de texto con consentimiento | No; Gemini necesita internet y cuota |
| **Apariencia y perfil** | Tema, colores y avatar guardados en el navegador | No |

La conversión de ilustraciones a personas realistas es un laboratorio experimental:
deshabilitado por defecto y validado con trabajos reales en esta laptop antes de
activarlo localmente. No garantiza identidad ni idéntica calidad con otros personajes.
El código de generación con Gemini
se conserva; su cuota externa debe estar disponible para poder generar imágenes.

## Requisitos

- Windows 10/11 · Python 3.12 · Node.js 20 o superior · PostgreSQL 17
- 16 GB de RAM. Sin GPU NVIDIA funciona todo; la humanización corre en el procesador (más lenta)
- Para el chat con IA: una clave de Gemini en `.env` (`GEMINI_API_KEY`) e internet

## Arranque rápido

```powershell
.\scripts\diagnostico.ps1      # revisa la PC (no instala nada)
.\scripts\instalar.ps1         # entorno de Python, PyTorch, migraciones y frontend
.\scripts\iniciar.ps1          # API + worker y abre http://localhost:5000
.\scripts\verificar.ps1        # salud, migraciones, pruebas e inferencia real
.\scripts\detener.ps1          # cierra solo lo que abrió iniciar.ps1
.\scripts\compartir.ps1        # enlace https temporal para que cualquiera lo abra (Parte H de la guía)
```

Antes de instalar, copia `.env.example` como `.env` y complétalo. **El `.env` nunca se sube a Git.** Para probar sin GPU usa `.\scripts\instalar.ps1 -SinIA` y deja `AI_ENGINE=mock`: la interfaz avisa «Simulación, sin IA real».

## Estructura

```text
backend/       Servidor: Flask + SQLAlchemy + Alembic
  app/api/        rutas /api/v1 (una por módulo: auth, images, jobs, gallery, teams, leave, hours, assistant…)
  app/services/   lógica de cada módulo (trabajos, equipos, horas, Gemini, instrucciones del chat)
  app/models/     tablas de PostgreSQL
  app/ai/         motores: humanización local SD 1.5, Estudio (OpenCV), textura de piel, laboratorio realista
  app/workers/    worker de la cola (FOR UPDATE SKIP LOCKED, reintentos, latido)
  migrations/     cambios de la base de datos (Alembic)
  tests/          pruebas del servidor (pytest)
  tools/          scripts de apoyo: demostración, motor de IA y pruebas (ver tools/README.md)
frontend/      Pantallas: React + TypeScript + Vite + Tailwind + shadcn/ui + TanStack Query
  src/pages/      una pantalla por módulo
  src/features/   hooks que conectan cada pantalla con la API (y la guía local del chat)
  src/components/ piezas reutilizables (chat flotante, comparador, permisos…)
  src/lib/api.ts  conexión con el servidor
  src/styles/     colores y tema
  e2e/            recorridos de navegador (Playwright)
scripts/       instalar, iniciar, detener, verificar y diagnóstico (.ps1)
docs/          ARQUITECTURA.md, guías, evidencias/, historial/ (notas por fecha) y referencia/ (guía y skill originales)
models/        pesos del modelo (fuera de Git)
private_data/  originales, resultados y accesos DEMO (fuera de Git)
```

## Documentación

- [Última validación de código e instalación](docs/VALIDACION-CODIGO-2026-11-20.md): actualización, pruebas, instalación aislada y límites comprobados.

- [Arquitectura y mapa de módulos](docs/ARQUITECTURA.md): dónde está cada cosa y cómo cambiarla.
- [Entrega práctica SENATI](docs/entrega-senati.md): cómo abrir, compartir, demostrar y comprobar el proyecto.
- [docs/LAPTOP_PASO_A_PASO.md](docs/LAPTOP_PASO_A_PASO.md): instalación y prueba de la IA real en la laptop.
- [docs/desarrollo-local.md](docs/desarrollo-local.md): cómo trabajar con tres ventanas (API, worker, frontend).
- [docs/motor-ia.md](docs/motor-ia.md): ficha del modelo.
- [docs/CIERRE_EN_LA_LAPTOP.md](docs/CIERRE_EN_LA_LAPTOP.md): cambiar claves, instalación limpia (CP-14) y evaluación de retratos.
- [docs/RETOMAR-LUMIA.md](docs/RETOMAR-LUMIA.md): punto para retomar el trabajo.
- `docs/historial/`: auditorías, cierres y pendientes de cada fecha (registro histórico).
- `docs/referencia/`: guía de implementación y skill V7 originales.
