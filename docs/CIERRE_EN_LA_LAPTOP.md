# Tres tareas de cierre que se hacen en la laptop

Hazlas en este orden. Cada una dice qué evidencia guardar para el informe.
Ninguna borra tus cuentas DEMO ni tus imágenes.

---

## 1. Cambiar las claves (10 minutos)

Una captura compartida mostró dos claves. No están en GitHub, pero quien vio la captura
podría usarlas. Se cambian así:

### 1a. Clave de Gemini (`GEMINI_API_KEY`)

1. Entra a <https://aistudio.google.com/apikey> con tu cuenta de Google.
2. En la lista, busca la clave que usa LUMIA y bórrala (ícono de papelera → *Delete*).
   Desde ese momento la clave vieja deja de funcionar para cualquiera.
3. Pulsa **Create API key**, elige el mismo proyecto y copia la clave nueva.
4. Abre el `.env` de la carpeta del proyecto con el Bloc de notas y reemplaza el valor:
   `GEMINI_API_KEY=la_clave_nueva`. Guarda.
5. **No la pegues en ningún chat ni la muestres en capturas.**

### 1b. Clave secreta de la aplicación (`SECRET_KEY`)

Firma las sesiones. Si se cambia, todos deben volver a iniciar sesión (las cuentas no se pierden).

```powershell
cd C:\ruta\del\proyecto\backend
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado en el `.env`: `SECRET_KEY=el_resultado`. Guarda.

### 1c. Contraseña de la base de datos (solo si salió en la captura)

Mira tu `DATABASE_URL`: la contraseña es lo que va entre `lumia_app:` y `@localhost`.
Si esa parte se vio en la captura, cámbiala:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost
```

Dentro escribe (con una contraseña nueva, sin el carácter `%`):

```sql
ALTER USER lumia_app WITH PASSWORD 'NUEVA_CLAVE';
\q
```

Luego cambia la misma contraseña dentro de `DATABASE_URL` en el `.env`.

### 1d. Comprobar

```powershell
.\scripts\detener.ps1
.\scripts\iniciar.ps1
```

Entra con una cuenta DEMO y manda un mensaje al chat con «Usar IA» marcado.
Si responde «Respuesta generada con IA», la clave nueva funciona.

---

## 2. Instalación limpia desde GitHub (CP-14, unos 40 minutos)

El caso de prueba CP-14 pide demostrar que el proyecto se instala siguiendo los scripts.
**Lo ideal es otra computadora.** Si haces la prueba en tu misma laptop, sirve como
«instalación limpia desde GitHub», pero el informe debe decir exactamente eso.

La instalación limpia usa **una carpeta y una base de datos nuevas**, así que tu
instalación de siempre y tus cuentas DEMO no se tocan.

1. Cierra la instalación de siempre (usa el mismo puerto 5000):
   ```powershell
   cd C:\ruta\del\proyecto
   .\scripts\detener.ps1
   ```
2. Descarga el proyecto en una carpeta nueva:
   ```powershell
   cd C:\
   git clone https://github.com/Leonela180/SENATI.git C:\lumia_limpia
   cd C:\lumia_limpia
   ```
3. Crea una base nueva (escribe la contraseña de `postgres` cuando la pida):
   ```powershell
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE lumia_limpia OWNER lumia_app ENCODING 'UTF8';"
   ```
4. Crea el `.env` copiando el ejemplo y complétalo:
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```
   - `SECRET_KEY=` una clave nueva (como en el paso 1b).
   - `DATABASE_URL=postgresql+psycopg://lumia_app:TU_CLAVE@localhost:5432/lumia_limpia`
   - Deja `AI_ENGINE=mock`. Así se prueba la instalación sin descargar el modelo de IA otra vez.
5. Anota la hora de inicio e instala:
   ```powershell
   .\scripts\diagnostico.ps1
   .\scripts\instalar.ps1 -SinIA
   .\scripts\iniciar.ps1
   ```
6. En el navegador (<http://localhost:5000>):
   - registra una cuenta nueva;
   - sube una imagen y ejecuta una herramienta del Estudio (por ejemplo, Cambiar fondo);
   - abre el chat flotante y escribe «quiero un fondo blanco».
7. Guarda la evidencia en una carpeta, por ejemplo `C:\lumia_limpia\evidencia_cp14\`:
   - captura de la terminal al terminar `instalar.ps1` («Instalación completa»);
   - captura de la página funcionando y del resultado del Estudio;
   - hora de inicio y de fin, y el modelo de la computadora.
8. Al terminar, cierra y vuelve a tu instalación de siempre:
   ```powershell
   .\scripts\detener.ps1
   cd C:\ruta\del\proyecto
   .\scripts\iniciar.ps1
   ```

Envíame las capturas y los datos del paso 7, y con eso actualizo CP-14 en el informe.
Si algo falla, copia el mensaje de error completo: también es un resultado válido.

---

## 3. Evaluar la humanización con 3 a 5 retratos (Anexo A, 1 a 2 horas)

Sirve para medir con números el objetivo principal: que la imagen se vea más natural
**sin cambiar a la persona**. Lo ideal es que califiquen **3 revisores** que no sean tú
(compañeros del área), porque no saben cuál es el original.

### 3a. Preparar y procesar

1. Elige de 3 a 5 retratos **generados por IA** (no fotos de personas reales). Ponlos en
   `C:\lumia_muestras` con nombres simples: `r1.png`, `r2.png`, `r3.png`…
2. Inicia LUMIA con la IA real (`AI_ENGINE=local`), entra con tu cuenta y humaniza cada retrato
   en **Humanizar**.
3. En el detalle de cada trabajo, anota los **segundos** que tardó y descarga el resultado.
4. Guarda cada resultado en `C:\lumia_eval\resultados\` con el mismo nombre más `_natural`:
   `r1_natural.png`, `r2_natural.png`…
5. Crea `C:\lumia_eval\resultados.csv` en el Bloc de notas con los tiempos anotados:
   ```text
   muestra,seconds
   r1,141.2
   r2,138.7
   r3,150.3
   ```

### 3b. Revisión a ciegas

```powershell
cd C:\ruta\del\proyecto\backend
.\.venv\Scripts\python.exe -m app.ai.evaluation preparar C:\lumia_eval --muestras C:\lumia_muestras --revisores 3
```

Esto crea:

- `C:\lumia_eval\revision_a_ciegas\`: cada retrato como A y B, en orden al azar;
- `ficha_revisor_1.csv`, `ficha_revisor_2.csv` y `ficha_revisor_3.csv`: una por revisor;
- `clave_NO_ENTREGAR_A_REVISORES.csv`: dice cuál es el original. **No se la muestres a los revisores.**

Da a cada revisor la carpeta `revision_a_ciegas` y su ficha. La llenan en Excel con
notas de 1 a 5:

| Columna | Qué escribe el revisor |
|---|---|
| `naturalidad_A` / `naturalidad_B` | Qué tan real se ve cada imagen (1 = artificial, 5 = muy natural) |
| `misma_persona` | Si A y B parecen la misma persona (1 = otra persona, 5 = idéntica) |
| `conserva_pose_ropa_fondo` | `si` o `no` |
| `artefactos` | `ninguno`, `leves` o `graves` |
| `observaciones` | Lo que quiera comentar |

### 3c. Resultado

Cuando tengas las tres fichas llenas en `C:\lumia_eval\`:

```powershell
.\.venv\Scripts\python.exe -m app.ai.evaluation resumir C:\lumia_eval
```

Toma una captura de lo que aparece (naturalidad media, identidad media, porcentaje que
conserva pose y ropa, artefactos graves y tiempo medio) y envíamela junto con las fichas.
Con esos números reales completo el Capítulo V y el Anexo A del informe.
Si los resultados no salen bien, también se reportan: el informe dice lo que se midió.
