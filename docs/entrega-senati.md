# LUMIA AI — entrega práctica SENATI

## Abrir y compartir

La aplicación completa funciona con Flask, PostgreSQL y un worker en esta computadora. El enlace HTTPS de Cloudflare permite acceder desde otro celular o PC, crear una cuenta y utilizar los módulos respetando sus permisos.

Para generar un enlace nuevo desde la raíz del proyecto:

```powershell
.\scripts\publicar_demo.ps1
```

El comando inicia API y worker en segundo plano y abre el enlace público. El enlace actual se guarda localmente en `tools/enlace.txt`, fuera de Git. Si la aplicación ya estaba iniciada, ciérrala primero con `scripts/detener.ps1`.

El enlace es temporal: cambia al volver a crear el túnel y requiere esta computadora encendida, sin suspensión y con internet. No es un alojamiento permanente. Para cerrar la aplicación y el enlace:

```powershell
.\scripts\detener.ps1
```

Para usar solo en esta PC: `scripts/iniciar.ps1`, y abrir `http://localhost:5000`.

## Recorrido de demostración

Actualizacion de entrega: el panel destaca el **Asistente de edicion**, una guia local de recorridos preparados que no se presenta como un modelo de chat. Gemini conserva su ruta `/app/generar` para una futura activacion con cuota; no es requisito para restaurar ni editar.

En **Perfil** se puede elegir avatar de iniciales o iconos, cuatro acentos, modo claro/oscuro/sistema y navegacion compacta. Se guardan en este navegador, sin sincronizacion entre dispositivos.

En **Estudio > Restaurar foto**, subir una fotografia propia con permiso, ajustar recuperacion de tonos y marcar pequenas rayas o manchas. El algoritmo combina reduccion de ruido, correccion de luminancia e inpainting; no genera rostros ni colorea automaticamente. Conservar la comparacion y descargar la copia.

En **Equipo**, indicar nombre y correo para una invitacion dirigida. El enlace permite precargar ambos datos; la persona elige su contrasena. Solo la cuenta con el correo indicado puede aceptar. Los botones **Preparar correo** y **WhatsApp** abren sus aplicaciones para que el propietario revise y envie; no se configuro un servicio SMTP ni envio automatico. El enlace sirve una vez y vence a las 72 horas.

Los trabajos de imagen se ejecutan en el worker independientemente de la pestaña. Se pueden recuperar desde **Historial**, incluyendo al recargar la pagina. Una desconexion al consultar no cancela el trabajo. El servidor debe seguir encendido; los errores reales de memoria, archivo o motor se siguen informando.

1. Registrarse y entrar al panel.
2. Subir imágenes generadas por IA a la galería, confirmando el permiso de uso.
3. Crear un álbum y organizar las imágenes.
4. Abrir una imagen en el Estudio: cambiar el fondo o aplicar ajustes.
5. Comparar el original con el resultado, descargarlo y guardar una copia para seguir editando.
6. Mostrar el historial y la trazabilidad.
7. Crear un equipo e invitar a otra cuenta mediante enlace de un solo uso.
8. Configurar el horario y registrar entrada/salida; mostrar resumen y CSV del equipo.
9. Mostrar los prompts de ejemplo de Gemini, su consentimiento y su tratamiento de errores.
10. Mostrar Humanizar con el modo local real, la microtextura, el realce de reflejos y sus parámetros de trazabilidad.

## Estado de las funciones de IA

Comprobación adicional: el modelo de texto `gemini-2.5-flash` usado por `modificar_codigo.py` también se probó directamente con la clave configurada. Google respondió 404 e indicó que ya no estaba disponible para nuevos usuarios. Es independiente del 429 por cuota recibido al generar imágenes; ejecutar desde la terminal no elimina esas restricciones del proveedor.

- **Estudio:** edición real con OpenCV/Pillow y segmentación U²-Net en CPU. El cambio de fondo se comprueba en el recorrido de navegador.
- **Humanizar:** activado en esta laptop con `AI_ENGINE=local` y `AI_LOCAL_RUNTIME=cpp`. SD 1.5 usa pesos GGUF en disco, trabajo de 320 px y una imagen por vez. El ajuste posterior conserva detalle de piel y realza reflejos existentes en los ojos con OpenCV; no añade lunares ni cambia la forma de los ojos. El resultado final pasa el filtro de seguridad antes de publicarse. Prueba pública completada en 156,08 s.
- **Gemini:** clave leída desde `.env`, modelo accesible y llamada real realizada. Google respondió `429` por cuota. La interfaz permite prompts, consentimiento y gestión del error, pero la generación real no puede darse por validada hasta disponer de cuota en el proyecto de Google. No se habilitó facturación ni se cambió de modelo automáticamente.

### Validar el modo ligero

El perfil utilizado está comprobado en Windows con Ryzen 7 7730U y 15,34 GiB visibles para el sistema. La prueba completa mantuvo al menos 1,59 GiB disponibles, con un límite preventivo de parada de 0,8 GiB. Esos valores son observaciones de esta ejecución, no una garantía de consumo fijo. Conviene evitar ejecutar simultáneamente otro modelo local de IA que ocupe la RAM.

```powershell
cd backend
.\.venv\Scripts\python.exe tools/validar_ligero.py --side 320 --input ../imagenes_prueba/rostro_original.png
```

El archivo de muestra es privado y no está en Git; en otra computadora hay que proporcionar un retrato sintético propio. Esta validación no modifica `.env`. Antes de activar el perfil en otra máquina hay que revisar su resultado visual.

La prueba por la web real se puede repetir desde `frontend/` con `node tools/verificar_ia_publica.mjs`: crea una cuenta de validación, usa la muestra privada y conserva las evidencias dentro de `private_data/validacion_publica/`. Requiere el navegador de Playwright instalado y el enlace activo en `tools/enlace.txt`.

### Motor original Diffusers (alternativa, sin activar)

El motor original de Diffusers sigue disponible, con una comprobación más conservadora de memoria antes de cargarlo:

```powershell
cd backend
.\.venv\Scripts\python.exe tools/validar_humanizacion.py --input ../imagenes_prueba/rostro_original.png
```

La validación requiere al menos 6 GiB disponibles al iniciar como margen preventivo; no garantiza que todas las imágenes o modelos quepan. Detiene exclusivamente su proceso si la memoria disponible baja de 1,5 GiB o supera 15 minutos. Guarda el diagnóstico en `private_data/validacion_ia/` y no modifica `.env`. Si pasa, hay que revisar visualmente el resultado antes de activar el motor.

La configuración VAE que faltaba se descargó del repositorio oficial del modelo. Esta alternativa pesada no es el motor activo; el perfil CPP ligero ya está validado y activado.

## Seguridad aplicada

Sesiones con cookies HttpOnly, protección CSRF, contraseñas con Argon2, permisos de propietario/equipo/admin y archivos privados. En modo compartir, cookies Secure y cabeceras de proxy limitadas al túnel local. Cabeceras contra incrustación y tipos de contenido incorrectos; las respuestas API no se guardan en caché.

La clave de Gemini solo se usa en el backend. Los originales se conservan y las descargas se rotulan. Los mensajes y registros de errores generales no imprimen contraseñas ni respuestas externas completas.

## Pruebas reproducibles

Las pruebas usan una base que debe ser distinta de la real y terminar en `_test`. Nunca configurar `TEST_DATABASE_URL` con la base que contiene datos de usuarios. La suite backend borra y recrea exclusivamente las tablas de la base de pruebas.

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools\servidor_pruebas.py inicializar
.\.venv\Scripts\python.exe tools\probar_navegador.py
```

El último comando inicia API/worker de pruebas en el puerto 5001 y los cierra al terminar. Gemini está desactivado en ese servidor para evitar cargos en pruebas automáticas. Las pruebas de navegador deben ejecutarse después de pytest, ya que comparten la base desechable.

En `frontend/`: `npm test` y `npm run build`. Para instalar el navegador de pruebas por primera vez: `npx playwright install chromium --no-shell`.

Las evidencias de esta entrega se guardan en `docs/evidencias/mejoras_20261116/`. El respaldo previo a la migración está en `private_data/backups/`, fuera de Git.
