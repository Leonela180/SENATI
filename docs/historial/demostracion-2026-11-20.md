# Demostración SENATI — 20/11/2026

Los nombres, grupos y jornadas están marcados como **DEMO**. No representan clientes,
empleados ni asistencia laboral reales. Las ediciones sí se ejecutan mediante los
algoritmos de la aplicación; no se insertan trabajos completados ficticios.

## Accesos y organización

- Cinco cuentas individuales: Valeria, Mateo, Camila, Diego y Luciana.
- Cinco equipos: Aurora Retratos, Andes Creativo, Prisma Digital, Raíces Visuales y Luz de Estudio.
- Cada equipo tiene un líder y dos integrantes: quince cuentas de grupo; veinte cuentas en total.
- Tres álbumes por persona: originales, retoque/versiones y entregables.
- Las claves son diferentes y aleatorias. Archivo privado local: `private_data/demo_senati/ACCESOS-PRIVADOS.md`. No copiar sus contenidos a GitHub ni a la portada.

## Datos creados

Se creó un respaldo PostgreSQL antes de la carga, en `private_data/demo_senati/`.
La primera carga completó 120 trabajos reales: fondo, textura, ajustes y ampliación
x2; guardó sus versiones por separado. Son 60 álbumes y 160 imágenes de galería,
además de los archivos de resultado de los trabajos. Las fotos son sintéticas
propias; los mismos originales se reutilizan con diferentes parámetros para
demostrar los flujos y no fingir clientes o identidades distintas.

La ampliación posterior agregó un tercer retrato propio y una cadena de restauración,
retoque localizado, desenfoque de fondo y calidad: **200 trabajos del Estudio**.
La comprobación verificó 262 imágenes de galería contando la primera conversión
experimental, veinte descargas y aislamiento entre cuentas. Se agregan por separado
las siguientes conversiones y humanizaciones reales; la cifra final se registra en
`docs/evidencias/cierre_20261120/demo-verificada.json`.

Incluye veinte jornadas manuales con nota DEMO y diez solicitudes de permisos:
cinco pendientes y cinco revisadas por sus líderes (aprobación o rechazo).

## Recorrido sugerido para exponer

1. Abrir la portada, explicar funciones y mover los comparadores.
2. Entrar con una cuenta individual; mostrar originales, versiones y entregables.
3. Abrir el historial: fecha, herramienta, parámetros, comparación y descarga real.
4. Editar una foto, guardar el resultado y continuar con otra herramienta.
5. Salir a otra sección durante el procesamiento y recuperar el trabajo por historial.
6. Abrir el asistente flotante y una recomendación de la guía local. Usar Gemini de texto solo con consentimiento y respuesta real disponible.
7. Entrar con un integrante y luego con su líder: imágenes compartidas, solicitudes de permiso y revisión.
8. Mostrar tema/avatar, horario y reporte; aclarar que las jornadas de esta exposición son manuales DEMO.

## Herramientas de preparación

- `backend/tools/preparar_cuentas_demo.py`: sin argumentos muestra el plan; `--apply` crea/resume datos y realiza respaldo antes de modificar la base.
- `backend/tools/exportar_demo_senati.py`: exporta a la portada solo ejemplos propios de trabajos reales completados.
- `backend/tools/validar_conversion_demo.py`: valida una conversión real en una cuenta DEMO sin habilitar el laboratorio para visitantes.

Los overrides de CSRF y límites de intentos en estos scripts solo se aplican al
cliente local de carga; no alteran la configuración de la API pública.
