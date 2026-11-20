# Pendientes para retomar LUMIA AI

**Registro histórico.** Varios puntos se completaron después: consultar
[cierre del 20/11/2026](cierre-2026-11-20.md) antes de retomar tareas.

Este es un respaldo de avance, no una declaración de entrega al 100 %.

## Implementado y comprobado

- Asistente flotante con conversación conservada al navegar; chat de texto Gemini probado con respuesta real.
- Ampliación digital x2/x4, solicitudes de permisos y revisión por el líder del equipo.
- Portada con fotografías sintéticas propias y ejemplos producidos por las herramientas reales.
- Base respaldada y migrada a `f8c0e2a4b6d8`, sin diferencias detectadas por Alembic.
- Última comprobación de la aplicación: 115 pruebas backend aprobadas y 1 omitida; 6 pruebas frontend y 14 recorridos de navegador aprobados; compilación correcta. Estas comprobaciones no aprueban la calidad visual del laboratorio experimental.

## Antes de habilitar ilustración a persona realista

- Corregir y revisar visualmente los ojos: la primera conversión fotográfica fue rechazada por la usuaria por ojos extraños.
- El último ensayo aislado de PyTorch a 512 px terminó en 505,42 s, con mínimo observado de 1,16 GiB de RAM disponible y filtros de entrada/salida aprobados. Su calidad visual sigue pendiente; completar técnicamente no equivale a una imagen aprobada.
- El prototipo tiene un retrato masculino y parámetros fijos para experimentar. Generalizarlo antes de conectarlo a la aplicación.
- Integrar el motor alternativo con límites de memoria, tiempo, limpieza del almacenamiento temporal, bloqueo compartido y filtros antes/después.
- Validar un trabajo real completo: subir, encolar, navegar o recargar, recuperar el estado, guardar y descargar.
- Mantener `AI_REALISTIC_ENABLED=0` hasta cumplir lo anterior. Los ensayos CPP de conversión fueron rechazados; no presentarlos como resultados aprobados.

## Cierre funcional y demostración

1. Revisar la reprogramación de trabajos cuando el motor está ocupado: que la espera no agote los intentos de procesamiento.
2. Incorporar los cambios finales del laboratorio a la rama de entrega y repetir las comprobaciones afectadas.
3. Reiniciar API y worker con la versión final; verificar sesión, consentimiento, chat real, edición, permisos y descargas en el entorno normal.
4. Renovar y comprobar el enlace HTTPS compartible. Un túnel temporal requiere que la computadora y los procesos sigan encendidos; no equivale a alojamiento permanente.
5. Después de terminar la aplicación, crear cuentas individuales y grupos claramente marcados DEMO, con credenciales nuevas guardadas solo en archivos privados.
6. Poblar sus galerías con trabajos realmente ejecutados, no historiales ficticios ni actividad atribuida a cuentas personales. Documentar qué funciones se pudieron demostrar.
7. Revisar los ejemplos de antes/después con la usuaria, incluida textura de piel, ojos y ropa. La humanización actual es sutil y no demuestra reconstrucción de tejidos.
8. Actualizar el informe de SENATI, capturas, evaluación visual, contraste y verificación de instalación en otra computadora.

## Dependencias y límites

- Gemini de texto respondió; generación de imágenes continúa bloqueada por cuota. No se activó facturación.
- Las preferencias de apariencia/avatar son locales al navegador; las invitaciones por correo abren el cliente de correo, sin envío SMTP automático.
- No subir `.env`, claves, contraseñas, bases de datos, fotos privadas, modelos ni directorios de experimentos.
- Conservar el archivo personal `modificar_codigo.py`; está fuera de este respaldo de código.

Véase [detalle de la etapa](etapa-2026-11-19.md) para implementación y evidencia previa.
