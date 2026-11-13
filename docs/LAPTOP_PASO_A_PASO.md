# Probar LUMIA AI en la laptop (IA real)

El código está completo y probado en modo simulación. En la laptop solo falta instalar, encender la IA real y juntar las evidencias. Copia los comandos tal cual; todos se ejecutan en **PowerShell** desde la carpeta del proyecto.

> Si un comando falla, **copia el texto completo del error** (no lo resumas) y anota en qué paso ocurrió. Con eso lo corrijo.

## 0. Programas (una sola vez)

Instala, si no los tienes: Python **3.12**, Node.js 20 o superior, PostgreSQL **17**, Git y el controlador NVIDIA más reciente. Después:

```powershell
cd C:\proyectos\Proyecto_Senati_IA_completo        # o donde descomprimiste el proyecto
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # permite ejecutar los .ps1 (una vez)
.\scripts\diagnostico.ps1
```

📌 **Evidencia:** guarda lo que imprime el diagnóstico (modelo de laptop, CPU, RAM, GPU y VRAM). Junto con el **precio real** de la laptop, va al informe (costos y depreciación).

## 1. Base de datos

Si ya creaste `lumia_app`, `lumia` y `lumia_test` antes, salta este paso. Si no:

```powershell
psql -U postgres
```

```sql
CREATE USER lumia_app WITH PASSWORD 'TU_CLAVE';
CREATE DATABASE lumia OWNER lumia_app ENCODING 'UTF8';
CREATE DATABASE lumia_test OWNER lumia_app ENCODING 'UTF8';
\q
```

## 2. Archivo `.env`

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Completa `SECRET_KEY` (los 64 caracteres que imprimió el comando anterior) y `DATABASE_URL=postgresql+psycopg://lumia_app:TU_CLAVE@localhost:5432/lumia`. Deja por ahora `AI_ENGINE=mock`.

Si ya tenías un `.env` del proyecto anterior, puedes reutilizarlo, pero **agrégale `SECRET_KEY`**: el anterior no la tenía.

## 3. Instalar

```powershell
.\scripts\instalar.ps1
```

Este paso tarda: descarga PyTorch con CUDA (unos 2,5 GB). Al final aplica las migraciones:

- Si tu base `lumia` ya tenía las tablas del proyecto anterior, la migración `7b1d2e9a4c10` las ajusta al diccionario de datos del informe, sin borrar nada.
- Si `alembic upgrade head` dice que una tabla «already exists», tu base se creó sin Alembic. Ejecuta esto y luego vuelve a correr `instalar.ps1`:

```powershell
cd backend; .\.venv\Scripts\alembic.exe stamp 24fc4214b845; cd ..
```

## 4. Primera prueba en modo simulación

```powershell
.\scripts\iniciar.ps1
```

Se abre http://localhost:5000. Regístrate, sube una imagen, marca la casilla de declaración y pulsa **Humanizar imagen**. Debe completarse en segundos, con el aviso **«Simulación, sin IA real»**. Cierra con `.\scripts\detener.ps1`.

Para ver el panel de administración:

```powershell
cd backend; .\.venv\Scripts\python.exe -m flask --app wsgi crear-admin TU_CORREO; cd ..
```

## 5. Comprobar la GPU

```powershell
backend\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
backend\.venv\Scripts\pip.exe show torch diffusers transformers | Select-String "Name|Version"
```

Debe decir `True` y el nombre de tu GPU. 📌 **Anota las versiones**: la de Diffusers va en la referencia APA del informe y en `docs/motor-ia.md`.

## 6. Descargar el modelo

1. Abre https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 y lee la licencia (CreativeML OpenRAIL-M). Anota la fecha de consulta en `docs/motor-ia.md`.
2. Descarga solo los archivos fp16 (unos 2,5 GB):

```powershell
backend\.venv\Scripts\pip.exe install -U "huggingface_hub[cli]"
backend\.venv\Scripts\hf.exe download stable-diffusion-v1-5/stable-diffusion-v1-5 --include "*.json" "*.txt" "*.fp16.safetensors" --local-dir .\models\stable-diffusion-v1-5
```

(Si `hf.exe` no existe, usa `huggingface-cli.exe` con los mismos parámetros.)

## 7. Prueba directa del motor

Usa una imagen sintética **tuya**, de una persona generada por IA, con permiso de uso. Guárdala como `docs\muestra_autorizada.png`.

```powershell
cd backend
.\.venv\Scripts\python.exe -c "from app.ai.local_engine import LocalHumanizationEngine as E; e=E(r'..\models\stable-diffusion-v1-5','stable-diffusion-v1-5'); print(e.humanize(r'..\docs\muestra_autorizada.png', r'..\docs\evidencias\prueba_motor.png', 'natural'))"
cd ..
```

Abre `docs\evidencias\prueba_motor.png` y compárala con el original:

- Si la persona cambia demasiado, baja `strength` en `backend\app\ai\prompts.py`.
- Si casi no cambia, súbela, sin pasar de 0,40 (Anexo D).

## 8. Encender la IA real y verificar todo

En `.env`, cambia `AI_ENGINE=mock` por `AI_ENGINE=local`. Después:

```powershell
.\scripts\iniciar.ps1
.\scripts\verificar.ps1
```

`verificar.ps1` revisa, en este orden:

1. la salud de la API;
2. las migraciones;
3. las pruebas automáticas;
4. el worker;
5. una humanización real.

Su registro queda en `docs\evidencias\verificar_*.txt` (evidencia de CP-10 y CP-14). Tiene que terminar con **«VERIFICACIÓN COMPLETA»**.

## 9. Evaluación del Anexo A

Junta tus muestras autorizadas en `C:\lumia_muestras` y ejecuta:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.ai.evaluation procesar C:\lumia_muestras C:\lumia_eval
.\.venv\Scripts\python.exe -m app.ai.evaluation preparar C:\lumia_eval --preset natural
# los 3 revisores llenan sus fichas_revisor_N.csv en Excel
.\.venv\Scripts\python.exe -m app.ai.evaluation resumir C:\lumia_eval
```

## 10. Capturas para el informe (4.5.13)

Con `AI_ENGINE=local`, toma capturas de estas pantallas: landing, login, panel, estudio con la imagen subida, «Procesando», comparador, historial, detalle, equipo, admin y vista de celular (F12 → modo dispositivo). Guárdalas en `docs\evidencias\capturas\`.

## Qué traerme

- La carpeta `docs\evidencias\` completa.
- El modelo y el precio de la laptop.
- Las versiones de torch, diffusers y transformers.
- Los resultados de la evaluación.
- Si algo falló, el texto completo del error.
