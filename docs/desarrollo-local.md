# Desarrollo local

## Tres ventanas (modo desarrollo, con recarga automática del frontend)

```powershell
# 1) API
cd backend; .\.venv\Scripts\Activate.ps1; python -m flask --app wsgi run --port 5000
# 2) Worker
cd backend; .\.venv\Scripts\Activate.ps1; python -m app.workers.image_worker
# 3) Frontend
cd frontend; npm run dev          # http://localhost:5173 (usa la API por el proxy de Vite)
```

## Modo demostración (un solo servidor)

Primero compila el frontend con `npm run build` en `frontend/`. Después basta con la API y el worker, y Flask sirve la web en http://localhost:5000. `scripts\iniciar.ps1` hace todo esto.

## Pruebas

```powershell
cd backend; .\.venv\Scripts\pytest.exe -v        # usa la base lumia_test (nunca la real)
cd frontend; npm test                            # Vitest
cd frontend; npx playwright install chromium; npm run e2e    # con la app levantada en :5000
```

- Para usar otra base de pruebas, define `TEST_DATABASE_URL`.
- El registro está limitado a 10 cuentas por hora desde la misma PC (RNF-01). Si repites mucho los e2e, reinicia la API.

## Migraciones

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\alembic.exe check                # debe decir: No new upgrade operations detected.
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe el cambio"   # tras cambiar un modelo
```
