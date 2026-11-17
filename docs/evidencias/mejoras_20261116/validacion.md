# Validación de la entrega del 16/11/2026

| Comprobación | Resultado |
|---|---|
| Backend con PostgreSQL separado | 85 pruebas pasan al integrar IA y detalle facial. `pytest.txt` conserva la línea base anterior de 69 |
| Frontend Vitest | 6 pruebas pasan en 2 archivos |
| TypeScript + Vite | Compilación correcta |
| Playwright | 6 recorridos pasan; salida en `playwright.txt` |
| Diseño | Capturas de escritorio 1440 px y móvil 390 px revisadas; consentimiento móvil corregido |
| Migraciones | Revisión `c3e5a7f1b9d2`; Alembic sin diferencias |
| Respaldo previo | Archivo PostgreSQL custom verificado mediante pg_restore --list; conservado fuera de Git |
| Segmentación | U²-Net descargado y cambio de fondo real comprobado en navegador |
| Seguridad | CSRF, permisos, JSON incorrecto, cabeceras, no caché y protección de la base real en pruebas comprobados |
| Enlace externo | Frontend y health responden HTTP 200 por HTTPS; cookie Secure y validación CSRF comprobadas |
| Gemini | Modelo y clave reconocidos por Google; generación real devuelve 429 por cuota |
| Humanizar | IA local CPP activa y prueba pública real completada en 156,08 s; evidencia en `ia_real_cpu.json` |
| Piel y ojos | Ajuste automático de microtextura y dos zonas oculares aplicado; conserva reflejos existentes y rasgos |
| Scripts | Parser PowerShell sin errores; inicio público y túnel utilizados en esta entrega |

Las pruebas no garantizan ausencia absoluta de errores. Gemini sigue pendiente de cuota. La humanización real pasó la comprobación técnica y visual de un retrato; una evaluación de naturalidad con varias imágenes y revisores queda fuera de lo demostrado.

Las capturas del servidor E2E muestran Gemini desconfigurado deliberadamente: ese servidor no usa la clave real ni consume cuota. La instalación pública sí lee la clave existente desde `.env`.

La captura de la prueba real y las imágenes comparativas se conservan en `private_data/validacion_publica/` y `private_data/validacion_detalle/`, fuera de Git. No se copiaron las imágenes privadas al frontend público.
# Ampliacion final

92 pruebas backend, 6 pruebas frontend y 8 recorridos Playwright satisfactorios. Compilacion TypeScript/Vite correcta; migracion d4f6b8a2c0e1 aplicada y alembic check sin diferencias. Los registros anteriores de esta carpeta se conservan como evidencia historica, no como conteos actuales.

`personalizacion.png` muestra el modo oscuro, acento Oceano y avatar de camara. Se captura en el entorno E2E aislado, por eso su aviso de humanizacion en simulacion; el servidor compartido mantiene el motor local real. Se verificaron tambien la restauracion al navegar/recargar, el registro de la persona invitada y la restriccion de correo de la invitacion.
