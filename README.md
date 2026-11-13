# LUMIA AI

Aplicación web local que aumenta el **realismo visual** de retratos de personas generados por IA (piel, ojos, cabello y luz) con un modelo image-to-image que corre en la propia computadora. El original nunca se modifica, el resultado se rotula «editado con IA» y las imágenes no salen de la PC.

Proyecto de Innovación SENATI «Mejora de piel con IA».

## Requisitos

- Windows 10/11 · Python 3.12 · Node.js 20 o superior · PostgreSQL 17
- Para la IA real: GPU NVIDIA con 6 GB de VRAM o más y unos 4 GB libres para los pesos del modelo

## Arranque rápido

```powershell
.\scripts\diagnostico.ps1      # revisa la PC (no instala nada)
.\scripts\instalar.ps1         # entorno de Python, PyTorch, migraciones y frontend
.\scripts\iniciar.ps1          # API + worker y abre http://localhost:5000
.\scripts\verificar.ps1        # salud, migraciones, pruebas e inferencia real
.\scripts\detener.ps1          # cierra solo lo que abrió iniciar.ps1
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

- [docs/estado.md](docs/estado.md): qué está implementado, qué está probado y qué falta.
- [docs/LAPTOP_PASO_A_PASO.md](docs/LAPTOP_PASO_A_PASO.md): instalación y prueba de la IA real en la laptop.
- [docs/desarrollo-local.md](docs/desarrollo-local.md): cómo trabajar con tres ventanas (API, worker, frontend).
- [docs/motor-ia.md](docs/motor-ia.md): ficha del modelo (se completa en la laptop).
- `infromacion/`: guía de implementación, skill V7 e informe.
