# Auditoría y cierre de LUMIA AI — 20/11/2026

Esta auditoría conserva el diagnóstico inicial. Los fallos y pendientes resueltos
durante la implementación posterior están en el [cierre funcional](cierre-2026-11-20.md).

## Versión revisada

GitHub `origin/main`, commit `5bee905`. Se sincronizó la copia local mediante avance directo, conservando `modificar_codigo.py` como archivo personal no versionado. No se instalaron dependencias ni se aplicaron migraciones.

Desde el respaldo `0012f52` se agregaron dos commits:

- `f10d21d`: el motor ocupado reencola sin gastar intentos ni crear incidentes; el laboratorio realista se oculta del menú y panel cuando no está disponible. La tarjeta experimental se retiró de la portada.
- `5bee905`: 17 capturas y registros de pruebas del 19/11 para el informe.

## Comprobaciones de esta revisión

- Backend: **117 pruebas aprobadas**, sin omisiones en esta computadora. La evidencia anterior era 116 aprobadas y 1 omitida; la diferencia no implica que se haya agregado otro caso.
- Frontend: **6 pruebas aprobadas** y compilación TypeScript/Vite correcta. Advertencia de rendimiento: paquete JavaScript principal de 530,14 kB sin comprimir; conviene dividir rutas, pero no bloquea la compilación.
- PostgreSQL: revisión `f8c0e2a4b6d8`, coincidente con head; `alembic check` no detecta cambios pendientes. Consulta sin modificar datos reales.
- Los recorridos de navegador se ejecutan por separado en `lumia_test`; la humanización usa simulación y Gemini externo queda desactivado. No prueban naturalidad ni cuota del proveedor.
- Resultado actual de navegador: **13 aprobados y 1 fallido**. En `e2e/modulos.spec.ts:25`, al guardar el resultado de fondo y aplicar desenfoque, no apareció el comparador en 60 segundos. El worker completó trabajos, pero la interfaz volvió a mostrar la imagen editable sin comparador. Revisar la sincronización entre guardar resultado, cambio de imagen/herramienta y reinicio del estado de Studio; todavía no se confirma la causa. Evidencia local en `frontend/test-results/` y `private_data/e2e/`.
- No se repitieron inferencias reales ni llamadas de pago a proveedores en esta auditoría. La cuota y calidad se describen según la última evidencia, no como comprobación nueva.

## Funciones y límites reales

| Área | Situación |
|---|---|
| Registro, sesión y acceso privado | Implementados, con pruebas de permisos y protección CSRF |
| Estudio | Fondo, lunares/manchas, desenfoque, restauración conservadora, ajustes, textura y ampliación digital x2/x4 |
| Galería e historial | Álbumes, lotes, comparación, guardado y descarga |
| Asistente | Flotante y movible; guía local y Gemini de texto con consentimiento. Respuesta real registrada en la etapa anterior |
| Equipos | Invitaciones dirigidas; el creador es líder dentro de LUMIA y revisa permisos. No acredita un cargo empresarial ni verifica RUC |
| Horas | Horario, marcación, registros manuales y reporte CSV |
| Apariencia | Tema, acentos y avatar guardados en el navegador, sin sincronización entre dispositivos |
| Humanización | Motor local existente y ejemplos reales; efecto sutil. Falta aceptación con varias imágenes; no garantiza reconstruir ropa ni corregir cualquier rostro |
| Ilustración a realista | Incompleto y deshabilitado. Ojos rechazados por la usuaria; prototipo alternativo aislado aún no integrado |
| Generación Gemini | Integrada, última prueba real bloqueada por cuota. Una suscripción de chat no demuestra cuota de API |
| Correo/WhatsApp | Preparan una invitación para compartir; no existe envío automático por SMTP |
| Acceso público | Túnel temporal dependiente de la computadora encendida. No se verificó un enlace activo en esta revisión |

## Orden para terminar

### 1. Cierre de seguridad y alcance

- Revocar y reemplazar las dos claves mostradas en la captura compartida; escribir las nuevas solo en `.env`. No basta con que ese archivo esté ignorado por Git.
- Mantener `AI_REALISTIC_ENABLED=0` hasta tener resultado visual aceptado y flujo real validado.
- Presentar generación de imágenes como no disponible mientras no exista cuota comprobada; conservar el código y las demás funciones.

### 2. Calidad de imagen (principal pendiente del producto)

- Antes de nuevas funciones, resolver o aislar el fallo de edición encadenada detectado hoy y repetir ese recorrido con navegación lenta; no ampliar el timeout para ocultarlo.

- Comparar humanización y textura con 3–5 retratos propios o autorizados: ojos, poros, bordes de máscara, cabello y ropa. Registrar aceptación y rechazo, tiempos y RAM.
- Corregir los ojos del laboratorio; generalizar el prototipo que hoy tiene personaje masculino y parámetros fijos.
- Integrar el motor alternativo con filtros antes/después, límites de RAM/tiempo y limpieza de temporales. Una ejecución técnica completa no equivale a calidad aprobada.
- Comprobar conversión real mediante cola, navegación/recarga, guardado y descarga antes de habilitarla.

### 3. Demostración completa y presentación

- Reiniciar API y worker con esta versión y comprobar el flujo normal con imágenes reales. Cerrar el navegador no debe cancelar el trabajo; apagar el servidor sí interrumpe su ejecución.
- Crear cuentas y grupos DEMO identificados como tales, con contraseñas nuevas en un archivo privado; llenar galerías con trabajos realmente procesados.
- Revisar portada en móvil y escritorio: ejemplos comparables, leyendas precisas y funciones disponibles. La base visual ya existe; no hace falta rediseñar todo desde cero.
- Renovar el enlace HTTPS y comprobarlo desde otro dispositivo. Para acceso continuo hace falta una computadora siempre encendida o alojamiento.

### 4. Documentación y entrega SENATI

- Usar esta hoja como lista actual; mantener documentos anteriores como registros históricos.
- Actualizar README: aún enumera siete módulos antiguos y ampliación x2; omite el asistente flotante, x4 y permisos del líder.
- Actualizar el informe y diapositivas con las capturas nuevas, funciones actuales y límites de IA; separar evidencia mock de inferencias reales.
- Medir contraste, revisar teclado/móvil y repetir instalación en otra computadora. Los scripts actuales son PowerShell de Windows: la instalación y los ejecutables de IA no están validados en Ubuntu.

## Criterio de finalización

La plataforma no está al 100 % del alcance solicitado: faltan calidad visual aprobada, conversión realista funcional, demostración poblada y cierre operativo. El núcleo de edición y colaboración está implementado y comprobable. No asignar un porcentaje global sin una lista acordada de entregables y sus criterios de aceptación.
