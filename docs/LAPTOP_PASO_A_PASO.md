# LUMIA AI en cualquier laptop, paso a paso

Esta guía sirve para **cualquier laptop con Windows 10 u 11**, tenga tarjeta NVIDIA, AMD Radeon o Intel. Empieza con una laptop sin nada instalado y termina con LUMIA AI funcionando.

**Cómo usar los comandos:**

- Todos se escriben en **PowerShell**: menú Inicio → escribe «PowerShell» → ábrelo.
- Copia cada bloque tal cual y presiona Enter.
- Lo que está en MAYÚSCULAS (por ejemplo `TU_CLAVE`) lo cambias por tus datos.

> ⚠️ Si algo falla, **copia el mensaje de error completo** y envíalo. Si en el mensaje aparece una contraseña o una clave, bórrala antes de enviarlo.

---

## ¿Ya lo tienes instalado? Solo actualiza

Si en esta laptop ya seguiste la guía antes, no repitas nada: trae los cambios nuevos de GitHub con estos comandos.

```powershell
cd C:\proyectos\SENATI
.\scripts\detener.ps1
git pull
.\scripts\instalar.ps1 -SinIA
.\scripts\iniciar.ps1
```

Si ya activaste la IA real (Parte F), usa `.\scripts\instalar.ps1` sin `-SinIA`. `instalar.ps1` actualiza las librerías y la base de datos sin borrar tus datos.

---

## Antes de empezar: ¿qué puede hacer tu laptop?

**Requisitos mínimos:**

- Windows 10 u 11 de 64 bits.
- **8 GB de RAM**; se recomiendan 16 GB.
- **15 GB libres** en el disco.
- Internet durante la instalación.

Busca tu tipo de laptop en esta tabla y fíjate qué opciones te tocan en las partes E y F.

| Tu laptop tiene… | Qué funciona | Cómo instalar |
|---|---|---|
| **Tarjeta NVIDIA** con 6 GB de memoria de video o más | **Todo**, y la humanización con IA tarda segundos | Parte E y luego Parte F, **opción A** |
| **AMD Radeon o Intel** (sin NVIDIA), con 16 GB de RAM | **Todo**. La humanización con IA corre en el procesador y tarda varios minutos por imagen | Parte E y luego Parte F, **opción B** |
| **8 GB de RAM** o un equipo antiguo | **Todo, excepto la humanización con IA real**. Queda el modo simulación, y el Estudio, la Galería, Gemini y las Horas funcionan igual | Solo la Parte E (instalación con `-SinIA`) |

Para no adivinar qué tienes, después de la Parte B ejecuta `.\scripts\diagnostico.ps1`: muestra la tarjeta de video, la RAM y el espacio libre.

---

## PARTE A: Instalar los programas (una sola vez)

Instálalos en este orden. En cada instalador deja las opciones por defecto, salvo lo que se indica.

| # | Programa | Dónde descargarlo | Importante al instalar |
|---|---|---|---|
| 1 | **Git** | https://git-scm.com/download/win | Todo por defecto |
| 2 | **Python 3.12** | https://www.python.org/downloads/ (elige la versión 3.12.x) | ✅ Marca **«Add python.exe to PATH»** en la primera pantalla |
| 3 | **Node.js LTS** | https://nodejs.org | Todo por defecto |
| 4 | **PostgreSQL 17** | https://www.postgresql.org/download/windows/ → «Download the installer» | Te pide una contraseña para el usuario **postgres**: **anótala**. Deja el puerto **5432** |
| 5 | **Controlador de video** | NVIDIA: https://www.nvidia.com/es-la/drivers/ · AMD: https://www.amd.com/es/support · Intel: Windows Update | Recomendado. Con NVIDIA es **obligatorio** para usar la tarjeta |

Cuando termines, **cierra PowerShell y ábrelo de nuevo**. Luego comprueba la instalación:

```powershell
git --version
python --version
node --version
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" --version
```

Cada comando debe mostrar una versión, y `python` debe decir **3.12**.

---

## PARTE B: Descargar el proyecto desde GitHub

```powershell
mkdir C:\proyectos
cd C:\proyectos
git clone https://github.com/Leonela180/SENATI.git
cd SENATI
```

Si el repositorio es privado, se abre una ventana para **iniciar sesión en GitHub**. Inicia sesión y presiona **«Authorize»**.

Ahora permite que Windows ejecute los scripts del proyecto. Se hace una sola vez; si pregunta, responde **S**:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Revisa tu laptop (este comando no instala nada):

```powershell
.\scripts\diagnostico.ps1
```

Si dice que falta `psql` o `nvidia-smi`, no te preocupes:

- `psql`: el proyecto usa la ruta completa de PostgreSQL, así que no hace falta.
- `nvidia-smi`: solo existe en laptops con NVIDIA.

📌 **Guarda lo que imprime**: el modelo de la laptop, el procesador, la RAM y la tarjeta de video van en el informe.

---

## PARTE C: Crear la base de datos (una sola vez)

Entra a PostgreSQL como administrador. Te pide la contraseña de **postgres** que anotaste en la Parte A. Mientras la escribes no se ve nada en pantalla; es normal.

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost
```

Cuando veas `postgres=#`, pega estas 3 líneas. Cambia `TU_CLAVE` por una clave nueva para el proyecto, **sin el símbolo %**, y déjala entre las comillas simples:

```sql
CREATE USER lumia_app WITH PASSWORD 'TU_CLAVE';
CREATE DATABASE lumia OWNER lumia_app ENCODING 'UTF8';
CREATE DATABASE lumia_test OWNER lumia_app ENCODING 'UTF8';
```

Debe responder `CREATE ROLE` y dos veces `CREATE DATABASE`. Para salir, escribe `\q` y presiona Enter.

---

## PARTE D: Crear el archivo `.env` (una sola vez)

El `.env` guarda tus claves. **Nunca se sube a GitHub**; por eso no vino con el proyecto y hay que crearlo.

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

## PARTE E: Instalar y encender LUMIA AI (funciona en cualquier laptop)

```powershell
.\scripts\instalar.ps1 -SinIA
```

Tarda unos minutos. Hace cuatro cosas:

1. crea el entorno de Python e instala las librerías;
2. descarga una sola vez el modelo para recortar fondos, de unos 170 MB;
3. crea las tablas en la base de datos;
4. prepara la web.

Tiene que terminar con **«Instalación completa»**. Luego **enciende LUMIA AI**:

```powershell
.\scripts\iniciar.ps1
```

Se abre el navegador en **http://localhost:5000**. Crea tu cuenta y entra.

**Estos módulos funcionan desde ya en cualquier laptop:**

| Módulo (menú lateral) | Qué puedes hacer |
|---|---|
| **Estudio de edición** | Quitar lunares o manchas, cambiar el fondo, desenfoque gaussiano, mejorar calidad y ajustes de color |
| **Galería** | Subir varias imágenes, organizarlas en álbumes y aplicar herramientas en lote |
| **Horario y horas** | Guardar tu horario, marcar entrada y salida, y ver tus horas por recuperar |
| **Historial, Equipo y Perfil** | Ver resultados, comparar, descargar, trabajar en equipo y editar tu cuenta |
| **Humanizar** | En esta etapa funciona en **modo simulación** (con aviso). La IA real se activa en la Parte F |

**Para ver el panel de administración**, convierte tu cuenta en administradora. Cambia `TU_CORREO` por el correo con el que te registraste:

```powershell
cd backend; .\.venv\Scripts\python.exe -m flask --app wsgi crear-admin TU_CORREO; cd ..
```

Recarga la página y aparecerá **Admin** en el menú.

**Para apagar LUMIA AI:** `.\scripts\detener.ps1`

**Los días siguientes**, no hace falta repetir nada:

```powershell
cd C:\proyectos\SENATI
.\scripts\iniciar.ps1
```

### E1. Activar «Generar con IA» (Gemini), en cualquier laptop con internet

1. Crea tu clave gratis en https://aistudio.google.com/apikey, iniciando sesión con tu cuenta de Google.
2. Abre el `.env` con `notepad .env` y pega la clave en esta línea:
   ```
   GEMINI_API_KEY=PEGA_AQUI_TU_CLAVE
   ```
3. Guarda y reinicia: `.\scripts\detener.ps1` y luego `.\scripts\iniciar.ps1`.

La **misma clave** activa el **Chat asistente** (menú de la izquierda). En el chat marca «Usar IA (Gemini) para conversar». Solo se envía el texto que escribes, nunca tus imágenes. Si Gemini no responde, el chat contesta con la guía local.

**La clave es como una contraseña:** no la pegues en el chat ni la subas a GitHub. El `.env` ya está excluido de Git.

---

## PARTE F: Activar la IA real para humanizar (opcional)

Elige **una** opción según tu laptop (ver la tabla del inicio). Antes de empezar, apaga LUMIA AI con `.\scripts\detener.ps1`.

### F1. Instalar el motor de IA (las dos opciones)

```powershell
.\scripts\instalar.ps1
```

Esta vez va **sin** `-SinIA`. Detecta sola tu laptop: con NVIDIA instala PyTorch con CUDA; sin NVIDIA, PyTorch para el procesador. Comprueba el resultado:

```powershell
backend\.venv\Scripts\python.exe -c "import torch; print('PyTorch', torch.__version__, '| GPU NVIDIA:', torch.cuda.is_available())"
```

`GPU NVIDIA: False` en una laptop con **AMD Radeon o Intel es lo normal**.

### F2-B. Sin NVIDIA (AMD Radeon o Intel, ~16 GB de RAM): motor ligero — RECOMENDADO para tu HP

Un solo comando prepara todo. Descarga unos 5 GB:

1. el programa **stable-diffusion.cpp**, en la misma versión ya probada y **verificada con su huella SHA-256**;
2. los pesos de **Stable Diffusion 1.5** y el **filtro de seguridad**;
3. crea una **copia ligera Q4_0** del modelo, que usa menos RAM;
4. activa el motor en tu `.env` y guarda antes una copia `.env.bak`.

```powershell
.\scripts\preparar_motor_ligero.ps1
```

Antes, abre https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5, lee la licencia (CreativeML OpenRAIL-M) y 📌 **anota la fecha** para el informe.

Cuando termine, enciende LUMIA AI con `.\scripts\iniciar.ps1`. El aviso dirá **«IA local en CPU»**. Cada humanización tarda **unos minutos** (unos 156 s en la prueba con la HP Ryzen 7 de 16 GB). Cierra otros programas pesados mientras procesa.

### F2-A. Con NVIDIA (6 GB de memoria de video o más): motor Diffusers

```powershell
backend\.venv\Scripts\pip.exe install -U "huggingface_hub[cli]"
backend\.venv\Scripts\hf.exe download stable-diffusion-v1-5/stable-diffusion-v1-5 --include "*.json" "*.txt" "*.fp16.safetensors" --local-dir .\models\stable-diffusion-v1-5
```

Si `hf.exe` no existe, usa `huggingface-cli.exe` con los mismos parámetros. Luego abre `notepad .env`, cambia `AI_ENGINE=mock` por **`AI_ENGINE=local`** y enciende con `.\scripts\iniciar.ps1`. Tarda segundos por imagen.

📌 Para el informe, anota las versiones:

```powershell
backend\.venv\Scripts\pip.exe show torch diffusers transformers | Select-String "Name|Version"
```

### F3. Revisar la calidad (importante)

Humaniza 2 o 3 retratos **generados por IA** y compara con el deslizador:

- **Piel, ojos y mandíbula:** sin parches ni cambios de tono. La corrección del «efecto mascarilla» ya está incluida.
- **Si casi no cambia:** sube `AI_RESULT_BLEND` en el `.env`, por ejemplo de 0.35 a 0.45.
- **Si cambia demasiado:** bájalo, por ejemplo a 0.25.
- **La textura de la piel** se regula con `AI_DETAIL_INTENSITY` (entre 0 y 1).
- **Después de cambiar algo**, reinicia con `detener.ps1` e `iniciar.ps1`.

### F4. Verificación final (evidencia para el informe)

Guarda un retrato generado por IA, que tengas permiso de usar, como `docs\muestra_autorizada.png`. Con LUMIA AI encendido, ejecuta:

```powershell
.\scriptserificar.ps1
```

Tiene que terminar con **«VERIFICACIÓN COMPLETA»**. El registro queda en `docs\evidenciaserificar_*.txt` y es la evidencia de CP-10 y CP-14.

### F5. Poner el ejemplo real en la portada

Cuando tengas una humanización **real** que te guste:

1. Ábrela desde el **Historial**. En la dirección del navegador verás su número, por ejemplo `/app/trabajos/12`.
2. Ejecuta:

```powershell
cd backend
.\.venv\Scripts\python.exe tools\preparar_portada.py --job 12
cd ..rontend; npm run build; cd ..
```

La portada mostrará ese antes/después con su procedencia. **Solo acepta resultados de IA real**: los de simulación los rechaza. Usa únicamente retratos **generados por IA**, nunca fotos de personas reales.

---

## PARTE G: Evidencias para el informe

1. **Capturas de pantalla** de: landing, panel, Estudio (cada herramienta), Galería, Generar con IA, Horario y horas, Humanizar, historial, equipo, admin y vista de celular. Para la vista de celular, presiona F12 y elige el modo dispositivo. Guárdalas en `docs\evidencias\capturas\`.
2. **Evaluación del Anexo A**, solo si activaste la IA real. Pon tus retratos de prueba en `C:\lumia_muestras` y ejecuta:

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

📌 **Tráeme:**

- la carpeta `docs\evidencias`;
- el modelo y el precio de la laptop;
- las versiones de torch, diffusers y transformers.

---

## PARTE H: Compartir LUMIA AI con cualquier persona (enlace por internet)

Sirve para que tu profesor, tu equipo o el jurado abran LUMIA AI desde **su celular o su computadora**, sin instalar nada. Usa **Cloudflare Tunnel**, que es gratis y no necesita cuenta: crea un enlace seguro (https) hacia tu laptop.

### H1. Activarlo (una sola vez)

1. Abre el `.env` con `notepad .env` y cambia `TRUST_PROXY=0` por **`TRUST_PROXY=1`**. Si la línea no existe, agrégala al final. Guarda.
2. Reinicia LUMIA AI:
   ```powershell
   .\scripts\detener.ps1
   .\scripts\iniciar.ps1
   ```

### H2. Crear el enlace (cada vez que quieras compartir)

Con LUMIA AI encendido, abre **otra** ventana de PowerShell y ejecuta:

```powershell
cd C:\proyectos\SENATI
.\scripts\compartir.ps1
```

- La primera vez descarga el programa oficial `cloudflared` (unos 60 MB).
- En unos segundos aparece un enlace como **`https://palabras-al-azar.trycloudflare.com`**, que **ya queda copiado**.
- Pégalo en WhatsApp o en un correo. Quien lo abra verá la página de inicio de LUMIA AI, podrá crear su cuenta y usar los módulos.
- Las **invitaciones de equipo** que generes mientras compartes ya usan ese enlace público, así que las puedes enviar a cualquiera.

### H3. Dejar de compartir

En la ventana del enlace, presiona **Ctrl + C** o ciérrala. LUMIA AI sigue funcionando en tu laptop, pero ya no desde internet.

### Ten en cuenta

| | |
|---|---|
| ⏻ **Laptop encendida** | El enlace funciona solo mientras tu laptop, LUMIA AI y la ventana de `compartir.ps1` estén encendidos. Si la laptop se suspende, el enlace deja de responder |
| 🔁 **El enlace cambia** | Cada vez que ejecutas `compartir.ps1` sale un enlace nuevo. Envía el nuevo |
| 🔒 **Privacidad** | Las imágenes que suban otras personas se guardan **en tu laptop**. Comparte el enlace solo con quien lo necesite y ciérralo al terminar |
| 🛡️ **Seguridad** | Siguen activos el inicio de sesión, la protección CSRF y el límite de intentos por persona. Cada visitante solo ve sus propias imágenes |
| 🐢 **Velocidad** | Depende de tu internet. Las herramientas del Estudio responden rápido. La humanización sin NVIDIA puede tardar minutos |
| 🎓 **Para el informe** | LUMIA AI sigue siendo una aplicación local. El enlace es solo para **demostraciones**, no un servidor en la nube |

---

## Si algo sale mal

| Mensaje | Solución |
|---|---|
| `python no se reconoce` | Reinstala Python 3.12 marcando **«Add python.exe to PATH»** y abre PowerShell de nuevo |
| `la ejecución de scripts está deshabilitada` | Ejecuta `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `la autentificación password falló para el usuario lumia_app` | La clave del `.env` no es la misma de la Parte C. Corrígela con `notepad .env` |
| `No existe el rol lumia_app` | Te faltó la Parte C |
| `Falta SECRET_KEY` | Te faltó pegar la clave larga en el `.env` (Parte D) |
| `relation "users" does not exist` | Faltan las tablas. Ejecuta `cd backend; .\.venv\Scripts\alembic.exe upgrade head; cd ..` |
| `LUMIA AI ya parece estar en marcha` | Ejecuta `.\scripts\detener.ps1` y luego `iniciar.ps1` |
| La web no abre en localhost:5000 | Revisa la ventana minimizada de la API: ahí aparece el error. Cópialo |
| «Cambiar fondo» termina en «modelo_no_disponible» | El modelo de recorte no se descargó (sin internet al instalar). Conéctate y vuelve a ejecutar `.\scripts\instalar.ps1 -SinIA` |
| «Falta configurar Gemini» | Pega tu clave en `GEMINI_API_KEY` del `.env` y reinicia (Parte E1) |
| «La clave de Gemini no es válida» | Copia la clave otra vez desde https://aistudio.google.com/apikey, sin espacios |
| `GPU NVIDIA: False` con una laptop NVIDIA | Actualiza el controlador NVIDIA y repite F1 |
| `GPU NVIDIA: False` con AMD Radeon o Intel | **Es lo normal.** La IA corre en el procesador (opción B) |
| `gpu_memoria` o la PC se pone muy lenta al humanizar | Cierra otros programas y usa imágenes más pequeñas. Con 8 GB de RAM, mejor deja `AI_ENGINE=mock` |
| El trabajo termina en «Error · modelo_no_disponible» al humanizar | Faltan los pesos en `models\stable-diffusion-v1-5` (repite F2) |
| Al registrarte: demasiadas solicitudes | Es el límite de seguridad de 10 registros por hora. Espera o reinicia con `detener` e `iniciar` |
| Compartiendo, todos los visitantes reciben «demasiadas solicitudes» | Falta `TRUST_PROXY=1` en el `.env`, o no reiniciaste después de agregarlo (Parte H1) |
| `compartir.ps1`: «LUMIA AI no está encendido» | Primero ejecuta `.\scripts\iniciar.ps1` en otra ventana |
| `compartir.ps1`: «No se pudo abrir el túnel» | Revisa tu internet. Algunas redes de institutos bloquean estos túneles; prueba con los datos del celular |
| Al enviar un formulario por el enlace: «Falta o venció el token de seguridad» | Recarga la página. Si el enlace cambió, abre el nuevo |
