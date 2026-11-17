# LUMIA AI

Entrega SENATI: incluye humanizacion local, Estudio con restauracion conservadora de fotos, guia de edicion sin API, personalizacion de apariencia y avatar, y equipos con invitaciones dirigidas compartibles por correo/WhatsApp. Consulta [la guia de demostracion](docs/entrega-senati.md) para conocer el alcance y los requisitos reales.

Aplicación web para crear, editar y organizar imágenes generadas por IA. Incluye humanización de retratos con un motor local, Estudio de edición, galería, equipos y control de horas. Los originales se conservan en la computadora que aloja la aplicación; si accedes desde otro dispositivo, las imágenes se suben a esa computadora. La generación con Gemini envía tu descripción a Google con consentimiento.

**Entrega actual en esta laptop:** humanización real con `AI_ENGINE=local`, motor CPU optimizado, microtextura de piel y realce de reflejos existentes en los ojos. El circuito público de subida, procesamiento, comparación y descarga está comprobado. Gemini está integrado, pero su generación sigue bloqueada por la cuota de Google. Consulta la [guía práctica SENATI](docs/entrega-senati.md).

Proyecto de Innovación SENATI «Mejora de piel con IA».

> **¿Primera vez en una computadora nueva?** Sigue **[docs/LAPTOP_PASO_A_PASO.md](docs/LAPTOP_PASO_A_PASO.md)**: desde instalar los programas y clonar este repositorio hasta ver la web funcionando.

## Módulos

| Módulo | Qué hace | ¿Necesita GPU? |
|---|---|---|
| **Humanizar** | Stable Diffusion 1.5 *image-to-image*: piel, ojos, cabello y luz más naturales | Recomendable; en CPU funciona a 512 px y tarda minutos |
| **Estudio de edición** | Quitar lunares o manchas, cambiar el fondo (color, desenfocado o transparente), desenfoque gaussiano, mejorar calidad (×2) y ajustes de color y rotación | No (CPU, segundos) |
| **Generar con IA** | Crea imágenes a partir de una descripción con Gemini (Google), con aviso y consentimiento | No (servicio externo) |
| **Galería** | Subida múltiple, álbumes, búsqueda, mover, borrar y procesamiento por lotes | No |
| **Historial y detalle** | Comparador antes/después, descarga rotulada y trazabilidad | No |
| **Horario y horas** | Horario semanal, marcar entrada/salida, registros manuales con motivo, horas trabajadas vs. esperadas, horas por recuperar y reporte del equipo en CSV | No |
| **Equipo y administración** | Invitaciones de un solo uso, compartir imágenes, estadísticas agregadas y supervisión técnica | No |

## Requisitos

- Windows 10/11 · Python 3.12 · Node.js 20 o superior · PostgreSQL 17
- 16 GB de RAM. Sin GPU NVIDIA funciona todo; la humanización corre en el procesador (más lenta)
- Para generar imágenes: una clave de Gemini en `.env` (`GEMINI_API_KEY`) e internet

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
backend/    Flask + SQLAlchemy + Alembic (app/, migrations/, tests/, tools/)
  app/ai/       interfaz HumanizationEngine, MockEngine, motor local SD 1.5 y evaluación (Anexo A)
  app/workers/  worker de la cola (FOR UPDATE SKIP LOCKED, reintentos, latido)
frontend/   React + TypeScript + Vite + Tailwind + shadcn/ui + TanStack Query
scripts/    instalar, iniciar, detener, verificar y diagnóstico (.ps1)
docs/       estado del proyecto, guía para la laptop y evidencias
models/     pesos del modelo (fuera de Git)
private_data/  originales y resultados (fuera de Git)
```

## Documentación

- [Entrega práctica SENATI](docs/entrega-senati.md): cómo abrir, compartir, demostrar y comprobar el proyecto; límites actuales de Gemini y Humanizar.
- [Auditoría local y plan de mejoras (16/11/2026)](docs/auditoria-2026-11-16.md): diferencias verificadas entre código, entorno y PostgreSQL; etapas y comprobaciones pendientes.

- [docs/estado.md](docs/estado.md): qué está implementado, qué está probado y qué falta.
- [docs/LAPTOP_PASO_A_PASO.md](docs/LAPTOP_PASO_A_PASO.md): instalación y prueba de la IA real en la laptop.
- [docs/desarrollo-local.md](docs/desarrollo-local.md): cómo trabajar con tres ventanas (API, worker, frontend).
- [docs/motor-ia.md](docs/motor-ia.md): ficha del modelo (se completa en la laptop).
- `infromacion/`: guía de implementación, skill V7 e informe.
