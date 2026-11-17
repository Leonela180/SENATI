# LUMIA AI — Hoja de pendientes para la entrega SENATI

**Corte:** 16 de noviembre de 2026. **Nivel:** proyecto final de instituto.

Esta hoja distingue implementación, funcionamiento técnico y calidad visual. Los porcentajes comunicados son estimaciones; no sustituyen los criterios de aceptación de abajo.

## Pendientes de la entrega

**Inicio — referencia visual del usuario:** la captura `Captura de pantalla 2026-11-16 230840.png` muestra el rostro dibujado con los rótulos «Antes · piel plástica» y «Después · textura natural». Se debe reemplazar esa ilustración por un retrato de aspecto fotográfico. La comparación mostrará el mismo retrato generado con IA y su resultado real procesado por LUMIA, sin simular la mejora con dibujos ni usar dos personas diferentes. También deben sustituirse las muestras ilustradas de piel, ojos, cabello y luz. El resultado debe superar la revisión visual antes de publicarse; la portada incluirá todas las funciones actuales y se comprobará en celular y escritorio.

| Prioridad | Pendiente | Situación actual | Se considera terminado cuando… |
|---|---|---|---|
| Alta | Corregir el efecto de mascarilla | El resultado `lumia_10_editado_IA.png` presenta parches visibles en el rostro. Se revisó junto al original; aún no se corrigió. | El antes/después no muestra bordes, parches ni cambios de tono artificiales en piel, ojos y mandíbula. |
| Alta | Validar naturalidad de piel y ojos | Hay un ajuste de microtextura y reflejos, pero ejecutar el algoritmo no demuestra calidad. | Se comparan varios retratos propios o autorizados, con distintas poses e iluminación, y se aprueba visualmente el resultado sin cambiar los rasgos. |
| Alta | Revisar ropa, cabello y resto de la imagen | El ajuste específico actual se concentra en el rostro; no existe una mejora validada de textura de ropa. | Se conserva el detalle y no se deterioran prendas ni cabello. Cualquier mejora adicional se demuestra; no se promete recuperar información inexistente. |
| Alta | Completar las fotografías del inicio | Existe un retrato sintético nuevo y una ejecución real del motor sobre él. Faltan preparar y comprobar los recursos públicos definitivos. | La portada carga ambos archivos y muestra el mismo retrato antes/después de LUMIA, con procedencia clara y calidad visual aprobada. No se usan fotos privadas del usuario. |
| Alta | Publicar la portada actualizada | El texto de las funciones y el comparador están editados localmente; aún no están compilados, comprobados ni subidos en esta última versión. | Se ven las funciones actuales, las imágenes cargan y el comparador funciona con toque y teclado, en celular y escritorio. |
| Alta | Incorporar chatbot conversacional | Existe **Asistente de edición**, una guía de recorridos preparados. No es un chatbot generativo. | Se integra y prueba un motor real, con respuestas útiles sobre LUMIA, identificación del proveedor y errores claros. Si se usa Ollama, se coordina con la humanización para no agotar la RAM. |
| Alta | Ejecutar las comprobaciones finales | La etapa anterior pasó sus pruebas; los cambios posteriores del inicio y la corrección visual pendiente necesitan nueva validación. | Pasan las pruebas afectadas, la compilación, el recorrido nuevo del inicio y la revisión visual de las imágenes finales. |
| Alta | Subir los cambios finales a GitHub | La etapa anterior está publicada en `main`, commit `935832d`. Hay cambios locales posteriores pendientes. | El commit final está en GitHub y se verifica que no contiene claves, fotos privadas, modelos ni respaldos. |
| Media | Actualizar documentación y evidencia | Existe documentación de entrega, pero debe reflejar las correcciones y pruebas finales. | La guía coincide con la versión publicada y distingue funciones reales, guía preparada e integraciones bloqueadas. |
| Media | Comprobar continuidad en uso real | Navegar y recargar durante una restauración pasó una prueba de navegador. Falta repetir el cierre/reapertura con una humanización real tras corregirla. | Un trabajo real sigue en el servidor y se recupera desde Historial al volver. Una falla de conexión no aparece como fallo del procesamiento. |

## Dependencias externas y ampliaciones

| Elemento | Qué falta | Alcance de la entrega |
|---|---|---|
| Gemini | Cuota disponible y generación real satisfactoria. La última prueba devolvió límite de cuota. | Integración opcional bloqueada; no anunciar generación disponible hasta validarla. |
| OpenAI | Saldo de API y una respuesta real satisfactoria. La última prueba devolvió saldo agotado. | No está integrado al chat. La suscripción de la aplicación no resuelve el error observado de API. |
| Enlace permanente | Alojamiento y configuración de dominio/servicios si se quiere independencia de esta laptop. | El enlace actual es temporal y necesita servidor encendido e internet. GitHub guarda el código; no aloja automáticamente Flask, PostgreSQL y el worker. |
| Correo automático | Configurar proveedor de correo, credenciales y comprobar entrega. | Actualmente se prepara el mensaje en la aplicación del propietario. WhatsApp también requiere que la persona revise y envíe. No presentarlo como envío automático. |
| Personalización sincronizada | Guardar preferencias por usuario en el servidor, si se necesita compartirlas entre dispositivos. | Actualmente avatar, tema, acento y densidad se guardan en este navegador. No bloquea la entrega con ese alcance declarado. |

## Ya comprobado en la etapa anterior

- 92 pruebas backend, 6 pruebas frontend y 8 recorridos Playwright satisfactorios; compilación TypeScript/Vite correcta.
- Restauración conservadora, reparación de daños pequeños marcados, comparación, descarga y conservación del original.
- Invitaciones de un solo uso y 72 horas, correo destinatario restringido, datos precargados y contraseña elegida por la persona invitada.
- Galería, álbumes, Estudio, historial, equipos, horario/horas y personalización de navegador conservados.
- Migración `d4f6b8a2c0e1` aplicada con respaldo verificado; esquema sin diferencias en la comprobación realizada.

**Criterio de cierre:** completar y comprobar los pendientes de la entrega. Las funciones externas bloqueadas deben quedar claramente identificadas como opcionales. No declarar calidad aprobada, chatbot real ni servicio permanente sin evidencia.
