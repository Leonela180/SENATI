# LUMIA AI en tu laptop, paso a paso

Esta guía empieza con una laptop sin nada instalado y termina con la web de LUMIA AI funcionando. Primero la verás en **modo simulación**, que es rápido. Después encenderás la **IA real**.

**Cómo usar los comandos:**

- Todos los comandos se escriben en **PowerShell**: menú Inicio → escribe «PowerShell» → ábrelo.
- Copia cada bloque tal cual y presiona Enter.
- Lo que está en MAYÚSCULAS (por ejemplo `TU_CLAVE`) lo cambias por tus datos.

> ⚠️ Si algo falla, **copia el mensaje de error completo** y envíamelo. Si en el mensaje aparece tu contraseña, bórrala antes de enviarlo.

---

## PARTE A: Instalar los programas (una sola vez)

Instálalos en este orden. En cada instalador deja las opciones por defecto, salvo lo que se indica.

| # | Programa | Dónde descargarlo | Importante al instalar |
|---|---|---|---|
| 1 | **Git** | https://git-scm.com/download/win | Todo por defecto |
| 2 | **Python 3.12** | https://www.python.org/downloads/ (elige la versión 3.12.x) | ✅ Marca **«Add python.exe to PATH»** en la primera pantalla |
| 3 | **Node.js LTS** | https://nodejs.org | Todo por defecto |
| 4 | **PostgreSQL 17** | https://www.postgresql.org/download/windows/ → «Download the installer» | Te pedirá una contraseña para el usuario **postgres**: **anótala**. El puerto se queda en **5432** |
| 5 | **Controlador NVIDIA** | https://www.nvidia.com/es-la/drivers/ (o la app NVIDIA) | Solo si tu laptop tiene tarjeta NVIDIA |

Cuando termines, **cierra PowerShell y ábrelo de nuevo**. Después comprueba que todo quedó instalado:

```powershell
git --version
python --version
node --version
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" --version
nvidia-smi
```

Cada comando debe mostrar una versión. `python` debe decir **3.12**. `nvidia-smi` debe mostrar tu tarjeta; si dice que no se reconoce, tu laptop no tiene NVIDIA o falta el controlador. Así igual puedes usar el modo simulación.

---

## PARTE B: Descargar el proyecto desde GitHub

```powershell
mkdir C:\proyectos
cd C:\proyectos
git clone https://github.com/Leonela180/SENATI.git
cd SENATI
```

- Si el repositorio es privado, se abrirá una ventana para **iniciar sesión en GitHub**. Inicia sesión y presiona **«Authorize»**.
- Al terminar tendrás la carpeta `C:\proyectos\SENATI` con todo el proyecto.

Permite que Windows ejecute los scripts del proyecto. Esto se hace una sola vez; si pregunta, responde **S**:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Revisa la laptop con el diagnóstico (no instala nada):

```powershell
.\scripts\diagnostico.ps1
```

📌 **Guarda lo que imprime**: el modelo de la laptop, el procesador, la RAM y la tarjeta de video van en el informe.

---

## PARTE C: Crear la base de datos (una sola vez)

Entra a PostgreSQL como administrador. Te pedirá la contraseña de **postgres** que anotaste en la Parte A. Mientras la escribes no se ve nada en pantalla; es normal.

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost
```

Cuando veas `postgres=#`, pega estas 3 líneas. Cambia `TU_CLAVE` por una clave nueva para el proyecto: **no uses el símbolo %** y déjala entre las comillas simples.

```sql
CREATE USER lumia_app WITH PASSWORD 'TU_CLAVE';
CREATE DATABASE lumia OWNER lumia_app ENCODING 'UTF8';
CREATE DATABASE lumia_test OWNER lumia_app ENCODING 'UTF8';
```

Debe responder `CREATE ROLE` y dos veces `CREATE DATABASE`. Para salir, escribe `\q` y presiona Enter.

---

## PARTE D: Crear el archivo `.env` (una sola vez)

El `.env` guarda tus claves. **Nunca se sube a GitHub**: por eso no vino con el proyecto y hay que crearlo.

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

El segundo comando imprime una clave larga de 64 caracteres. En el Bloc de notas cambia estas 2 líneas:

```
SECRET_KEY=PEGA_AQUI_LA_CLAVE_LARGA_QUE_SALIO
DATABASE_URL=postgresql+psycopg://lumia_app:TU_CLAVE@localhost:5432/lumia
```

`TU_CLAVE` es la misma que pusiste en la Parte C. Deja `AI_ENGINE=mock` por ahora. Guarda con **Ctrl + G** y cierra.

---

## PARTE E: Instalar y ver la web (modo simulación)

```powershell
.\scripts\instalar.ps1 -SinIA
```

Tarda unos minutos. Hace cuatro cosas:

1. crea el entorno de Python;
2. instala las librerías;
3. crea las tablas en la base de datos;
4. prepara la web.

Tiene que terminar con **«Instalación completa»**.

Ahora **enciende LUMIA AI**:

```powershell
.\scripts\iniciar.ps1
```

Se abre el navegador en **http://localhost:5000**. 🎉 Esa es la web:

1. **Crea tu cuenta** y entra.
2. En **Humanizar**, sube una imagen, marca la confirmación y pulsa **Humanizar imagen**.
3. Verás el procesamiento y luego el comparador antes/después.

En este modo aparece el aviso **«Modo simulación»**: todavía no es IA real.

**Para ver el panel de administración**, convierte tu cuenta en administradora. Cambia `TU_CORREO` por el correo con el que te registraste:

```powershell
cd backend; .\.venv\Scripts\python.exe -m flask --app wsgi crear-admin TU_CORREO; cd ..
```

Después recarga la página: aparecerá **Admin** en el menú.

**Para apagar LUMIA AI:**

```powershell
.\scripts\detener.ps1
```

### Para los días siguientes

No hace falta repetir nada. Solo abre PowerShell y escribe:

```powershell
cd C:\proyectos\SENATI
.\scripts\iniciar.ps1
```

Para apagar, usa `.\scripts\detener.ps1`.

---

## PARTE F: Encender la IA real (necesita NVIDIA)

### F1. Instalar el motor de IA

Primero apaga LUMIA AI con `.\scripts\detener.ps1`. Después:

```powershell
.\scripts\instalar.ps1
```

Esta vez es sin `-SinIA`: descarga PyTorch con CUDA, unos 2,5 GB, y tarda. Al terminar, comprueba la tarjeta:

```powershell
backend\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
backend\.venv\Scripts\pip.exe show torch diffusers transformers | Select-String "Name|Version"
```

Debe decir **True** y el nombre de tu tarjeta. 📌 **Anota las versiones**: van en el informe y en `docs/motor-ia.md`.

### F2. Descargar el modelo (unos 2,5 GB)

1. Abre https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 y lee la licencia (CreativeML OpenRAIL-M). 📌 Anota la fecha en que la leíste.
2. Descarga el modelo:

```powershell
backend\.venv\Scripts\pip.exe install -U "huggingface_hub[cli]"
backend\.venv\Scripts\hf.exe download stable-diffusion-v1-5/stable-diffusion-v1-5 --include "*.json" "*.txt" "*.fp16.safetensors" --local-dir .\models\stable-diffusion-v1-5
```

Si dice que `hf.exe` no existe, usa `huggingface-cli.exe` con los mismos parámetros.

### F3. Cambiar a IA real

```powershell
notepad .env
```

Cambia `AI_ENGINE=mock` por `AI_ENGINE=local`, guarda y cierra. Después:

```powershell
.\scripts\iniciar.ps1
```

Ahora el aviso de simulación ya no aparece, y el panel dice **Motor: Local (GPU)**. Sube un retrato generado por IA y humanízalo: esta vez es **IA real**.

### F4. Verificación final (evidencia para el informe)

Guarda un retrato generado por IA, que tengas permiso de usar, como `docs\muestra_autorizada.png`. Después ejecuta:

```powershell
.\scripts\verificar.ps1
```

Tiene que terminar con **«VERIFICACIÓN COMPLETA»**. El registro queda en `docs\evidencias\verificar_*.txt` y es la evidencia de CP-10 y CP-14.

### F5. Ajustar la intensidad (opcional)

- Si la persona cambia demasiado, baja `strength` en `backend\app\ai\prompts.py`.
- Si casi no cambia, súbela, sin pasar de 0,40.
- Después reinicia con `detener.ps1` e `iniciar.ps1`.

---

## PARTE G: Evidencias para el informe

1. **Capturas de pantalla con IA real:** landing, login, panel, estudio, procesando, resultado, historial, detalle, equipo, admin y vista de celular. Para la vista de celular, presiona F12 y elige el modo dispositivo. Guárdalas en `docs\evidencias\capturas\`.
2. **Evaluación del Anexo A.** Pon tus retratos de prueba en `C:\lumia_muestras` y ejecuta:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.ai.evaluation procesar C:\lumia_muestras C:\lumia_eval
.\.venv\Scripts\python.exe -m app.ai.evaluation preparar C:\lumia_eval --preset natural
# los 3 revisores llenan sus fichas_revisor_N.csv en Excel
.\.venv\Scripts\python.exe -m app.ai.evaluation resumir C:\lumia_eval
cd ..
```

3. **Sube tus evidencias a GitHub:**

```powershell
git add docs
git commit -m "Evidencias de la laptop"
git push
```

📌 **Tráeme:** la carpeta `docs\evidencias`, el modelo y el precio de la laptop, y las versiones de torch, diffusers y transformers. Con eso actualizo el informe.

---

## Si algo sale mal

| Mensaje | Solución |
|---|---|
| `python no se reconoce` | Reinstala Python 3.12 marcando **«Add python.exe to PATH»** y abre PowerShell de nuevo |
| `la ejecución de scripts está deshabilitada` | Ejecuta `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `la autentificación password falló para el usuario lumia_app` | La clave del `.env` no es la misma de la Parte C. Corrígela en `notepad .env` |
| `No existe el rol lumia_app` | Te faltó la Parte C |
| `Falta SECRET_KEY` | Te faltó pegar la clave larga en el `.env` (Parte D) |
| `relation "users" does not exist` | Faltan las tablas. Ejecuta `cd backend; .\.venv\Scripts\alembic.exe upgrade head; cd ..` |
| `LUMIA AI ya parece estar en marcha` | Ejecuta `.\scripts\detener.ps1` y luego `iniciar.ps1` |
| La web no abre en localhost:5000 | Revisa la ventana minimizada de la API: ahí aparece el error. Cópialo |
| `torch.cuda.is_available()` dice False | Actualiza el controlador NVIDIA y repite F1 |
| `CUDA out of memory` / `gpu_memoria` | Prueba con una imagen más pequeña o cierra otros programas pesados |
| El trabajo termina en «Error · modelo_no_disponible» | Faltan los pesos en `models\stable-diffusion-v1-5` (repite F2) |
| Al registrarte: demasiadas solicitudes | Es el límite de seguridad de 10 registros por hora. Espera o reinicia con `detener` e `iniciar` |

### Traer cambios nuevos desde GitHub

Si actualizo el proyecto, en la laptop haz esto:

```powershell
cd C:\proyectos\SENATI
.\scripts\detener.ps1
git pull
.\scripts\instalar.ps1
.\scripts\iniciar.ps1
```
