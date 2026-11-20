# Validación de código e instalación — 20/11/2026

Se incorporó `origin/main` hasta `f180c6c` mediante avance directo, manteniendo el
archivo personal `modificar_codigo.py`, las cuentas DEMO, los originales y los resultados.
Antes de actualizar se creó y verificó un respaldo privado de PostgreSQL y 717 archivos.
El informe académico y las diapositivas se dejan para el final, según lo solicitado.

## Correcciones aplicadas

- `scripts/instalar.ps1` comprueba el código de salida de creación del entorno,
  pip, PyTorch, dependencias de IA, migraciones, npm y compilación. Si una de esas etapas
  falla, se detiene y no anuncia «Instalación completa».
- La comprobación de pesos acepta rutas absolutas o relativas y valores entre
  comillas. El modo `-SinIA` no exige pesos de difusión ni falla por una ruta vacía.
- El diagnóstico `validar_gemini.py` prueba texto por defecto. Solo solicita imágenes
  con `--imagenes` y `GEMINI_IMAGE_ENABLED=1`. No imprime claves ni respuestas completas.
- Se añadieron dos pruebas para evitar llamadas de imágenes y exposición de claves
  en ese diagnóstico, y un recorrido reproducible de instalación aislada.

## Comprobaciones realizadas

| Comprobación | Resultado observado |
|---|---|
| Backend, versión final | 121 pruebas aprobadas en 56,86 s |
| Frontend | 6 pruebas aprobadas; TypeScript/Vite compiló |
| Navegador | 14 recorridos aprobados en 58,8 s |
| PostgreSQL de la aplicación | `alembic check` sin diferencias; no se aplicaron migraciones a producción |
| Gemini de texto real | Respuesta de 105 caracteres, recomendación `mejorar_calidad`; sin imágenes |
| Cuentas DEMO | 20 cuentas, 5 equipos, 62 álbumes y 272 imágenes; 20 descargas e aislamiento entre cuentas verificados |
| Acceso público HTTPS | Sesión, galería, comparación, repetición real, asistente, líder y laboratorio aprobados; sin errores JavaScript |

## Instalación aislada en esta laptop

Se extrajo una copia de Git sin entorno Python ni `node_modules`, con la corrección
del instalador que se estaba validando. Se ejecutó `instalar.ps1 -SinIA`:

- Se crearon un entorno Python y dependencias de backend nuevos.
- `npm ci` instaló desde el lockfile y el frontend compiló.
- Se aplicaron las seis migraciones desde cero en un esquema exclusivo dentro de
  `lumia_test`, con variables verificadas para impedir usar la base de producción.
- Se reutilizó la caché del modelo de segmentación ya descargado y la caché de
  Chromium. No se descargó ni instaló el motor de difusión opcional.
- Se iniciaron API y worker aislados en el puerto 5002 y se cerraron solo esos
  procesos al terminar; la instalación habitual siguió separada.
- El navegador registró una cuenta temporal, subió una imagen, ejecutó segmentación
  real de fondo, comparó y descargó un PNG, y consultó el asistente local.

La prueba pasó, sin errores JavaScript. Demuestra instalación limpia y uso básico
en **la misma laptop**; no equivale a validación en otra computadora o Ubuntu.
El modo de humanización de esa copia era `mock`; la edición del Estudio sí ejecutó
su algoritmo real. No se presenta como nueva evaluación de la humanización generativa.

## Evidencia y continuación

- Evidencia pública revisada: `docs/evidencias/codigo_20261120/`.
- Registro completo privado de la instalación y configuración aislada:
  `private_data/validacion_instalacion/`.
- Accesos DEMO: `private_data/demo_senati/ACCESOS-PRIVADOS.md` (fuera de Git).
- Enlace vigente: `tools/enlace.txt`; requiere laptop, API, worker y túnel encendidos.

No se han cambiado las claves de los proveedores ni la contraseña de la base.
La sustitución de credenciales expuestas requiere acceso a las cuentas de sus
propietarios. La aceptación visual y la evaluación académica siguen siendo tareas
distintas de la verificación del código.
