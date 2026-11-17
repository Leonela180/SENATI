# LUMIA AI — Hoja de pendientes para la entrega SENATI

**Actualizado:** 17 de noviembre de 2026. Esta hoja separa tres cosas: lo que está implementado y comprobado, lo que solo se puede comprobar en la laptop del proyecto y lo que depende de servicios externos.

## ✅ Resuelto en esta etapa

| Pendiente anterior | Qué se hizo | Cómo se comprobó |
|---|---|---|
| Efecto mascarilla en la humanización | Solo se transfiere la textura de la IA, no su tono. La máscara es suave (sin parches), con protecciones graduales de ojos y boca y sin costuras en el borde | Prueba de regresión `test_sin_efecto_mascarilla_aunque_la_ia_cambie_el_tono`, con retrato sintético y cambio de tono |
| Portada con dibujos | Nueva portada «Aurora». Muestra el antes/después **real** solo si existe `/demo/demo.json`; si no, capturas reales de la aplicación | Prueba e2e `inicio.spec.ts`, en escritorio y celular |
| Diseño poco llamativo | Tema «Aurora»: fondo profundo, degradado vibrante, 4 acentos y modo claro u oscuro | Revisión visual a 1440 y 390 px; 9 recorridos e2e |
| Pruebas fallaban sin el motor de IA | `test_pesos.py` se omite si falta `safetensors` | Instalación limpia con `-SinIA`: 91 pruebas recolectadas |
| Motor ligero no reproducible | `scripts/preparar_motor_ligero.ps1`, con versión fijada y SHA-256 | Revisión del script y prueba de la edición del `.env`. La descarga y la ejecución se prueban en la laptop |
| Ejemplo de portada | `tools/preparar_portada.py --job N`, que rechaza resultados de simulación | `test_portada.py` |
| Piel «de plástico» que casi no cambiaba | Nueva herramienta **Textura de piel realista** en el Estudio: poros, grano fino, micro-brillos y pecas opcionales solo en la piel detectada (ojos, boca, cejas, lunares y cabello protegidos). Es una edición digital en CPU (≈0,3 s), no IA generativa. Atajo «Agregar textura de piel» al terminar Humanizar | `test_textura_piel.py` (6 pruebas) y `e2e/textura.spec.ts`; prueba con detección real de rostro en el servidor local |
| Humanización poco notoria | «Modo más notorio» documentado en la guía (Parte F3): `AI_LITE_WORK_SIDE=448`, `AI_RESULT_BLEND=0.5`, `AI_DETAIL_INTENSITY=0.85` | Se prueba en la laptop (tarda unos 4 a 6 minutos por imagen) |
| `modificar_codigo.py` en la raíz | Retirado del proyecto. No tenía relación con LUMIA | — |

## 🔎 Comprobar en la laptop del proyecto (no se puede hacer en otra PC)

| Pendiente | Cómo cerrarlo |
|---|---|
| Validar la corrección de la mascarilla con el retrato real (`lumia_10`) | Volver a humanizar ese retrato y compararlo con el deslizador. Si queda bien, guardar una captura en `docs/evidencias/` |
| Textura de piel con tus retratos | Probar 70–80 % en 3 retratos generados por IA, sola y después de Humanizar; guardar una captura del deslizador en `docs/evidencias/` |
| Naturalidad con varios retratos | Humanizar de 3 a 5 retratos generados por IA, con distintas poses y luz, y revisarlos con el deslizador (Parte F3 de la guía) |
| Ejemplo real en la portada | `preparar_portada.py --job N` con la mejor humanización real y luego `npm run build` (Parte F5) |
| Ejecución de `preparar_motor_ligero.ps1` en una instalación nueva | Seguir la Parte F2-B en la laptop o en otra PC sin NVIDIA |

## ⚪ Dependen de servicios externos (opcionales; se declaran como tales)

| Elemento | Situación |
|---|---|
| Gemini (generar imágenes) | La clave funciona, pero Google responde 429 por falta de cuota. La interfaz ya gestiona el consentimiento y el error |
| Chat asistente con IA | **Implementado:** el chat conversa con Gemini (texto) si hay clave y consentimiento; si no hay cuota o clave, responde la guía local. Probado con respuestas simuladas; falta probarlo con tu clave real en la laptop |
| Enlace permanente | El enlace de Cloudflare es temporal y depende de la laptop encendida. Uno permanente necesitaría alojamiento |
| Correo automático | Las invitaciones se envían a mano, por correo o por WhatsApp. No hay un servidor de correo configurado |
| Personalización entre dispositivos | Se guarda en el navegador |

## 📄 Entrega académica

- Actualizar el informe y las diapositivas con los módulos, el tema, el motor en CPU y las evidencias reales.
- Anotar el **precio real** de la laptop (HP 15-fc0xxx, Ryzen 7 7730U, unos 16 GB) para los costos.
