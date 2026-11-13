# Estado de LUMIA AI

Actualizado el 13/11/2026.

Lo marcado como «probado» se ejecutó en la PC de desarrollo, que no tiene GPU NVIDIA, con `AI_ENGINE=mock`, primero en un PostgreSQL 16 temporal y después en el **PostgreSQL 17.12 real** (usuario `lumia_app` sin superusuario). Las salidas están en `docs/evidencias/desarrollo_20261113/`; las de PostgreSQL 17 terminan en `_postgresql17.txt`, incluida la estructura de las 8 tablas.

**Ninguna de estas pruebas comprueba todavía la IA real.** Esa prueba se hace en la laptop; ver `LAPTOP_PASO_A_PASO.md`.

## Criterios de aceptación (skill §14)

| # | Criterio | Implementado | Probado | Evidencia |
|---|---|---|---|---|
| 1 | La landing pública carga sin sesión y explica la humanización | Sí | Sí | capturas_modo_simulacion/01 y 11 |
| 2 | Registro, login, logout y permisos | Sí | Sí | pytest.txt (test_auth) |
| 3 | Una carga válida guarda el original en privado y crea el trabajo; una carga inválida se rechaza | Sí | Sí | pytest.txt (test_imagenes) |
| 4 | El modelo real se comprobó y se evaluó visualmente | El código, sí | **No** | **Pendiente (laptop)** |
| 5 | Estado, historial, comparación y descarga, con autorización | Sí | Sí, en modo simulación | pytest.txt, playwright.txt |
| 6 | Otro usuario no puede ver el original ni el resultado ajeno | Sí | Sí | pytest.txt (CP-11) |
| 7 | Diseño cuidado y accesible en celular y escritorio | Sí | En parte: falta medir el contraste AA | capturas |
| 8 | Migraciones y pruebas ejecutadas, con resultados documentados | Sí | Sí | alembic.txt, pytest.txt, vitest.txt |
| 9 | La instalación se repite en otra PC compatible | Los scripts, sí | **No** | **Pendiente: verificar_*.txt de la laptop** |
| 10 | Este archivo declara con precisión qué está implementado, qué está probado y qué falta | Sí | Sí | este archivo |

## Casos de prueba del informe

| CP | Qué prueba | Dónde | Resultado en la PC de desarrollo |
|---|---|---|---|
| CP-01 | Registro válido | test_cp01_registro_valido | Pasa |
| CP-02 | Correo ya registrado | test_cp02_correo_existente | Pasa |
| CP-03 | Login inválido con mensaje genérico | test_cp03_login_invalido | Pasa |
| CP-04 | Carga de un JPG válido | test_cp04_carga_jpg_valida | Pasa |
| CP-05 | Archivo con extensión falsa | test_cp05_extension_falsa | Pasa |
| CP-06 | Carga sin la declaración de IA | test_cp06_sin_declaracion | Pasa |
| CP-07 | Idempotencia | test_cp07_idempotencia | Pasa |
| CP-08 | Dos workers no toman el mismo trabajo | test_cp08_dos_workers | Pasa (con PostgreSQL) |
| CP-09 | Fallo del motor sin trazas internas | test_cp09_fallo_del_motor | Pasa |
| CP-10 | Humanización real con el modelo | Paso 13 y verificar_circuito.py | **Pendiente (laptop)** |
| CP-11 | Acceso cruzado devuelve 404 | test_cp11_acceso_cruzado | Pasa |
| CP-12 | Descarga autorizada y auditada | test_cp12_descarga_autorizada | Pasa |
| CP-13 | POST sin token CSRF devuelve 403 | test_cp13_csrf | Pasa |
| CP-14 | Instalación en otra PC | verificar.ps1 | **Pendiente (laptop)** |

Además, estas pruebas pasan:

- **pytest:** RF-03 (logout), RF-05 (cambio de clave), RF-06 (megapíxeles), RF-08 (sin ruta pública), RF-18 a RF-21 (equipos y admin), RNF-01 (límite de intentos), RNF-07 y RNF-10.
- **Vitest:** 3 pruebas del frontend.
- **Playwright:** 2 flujos completos en el navegador.

## Diferencias con el informe

- **Endpoints nuevos.** Estos 5 no están en la Tabla E1:
  - `GET /auth/csrf`
  - `GET /health`
  - `PATCH /images/{id}/visibility`
  - `GET /teams/{id}/stats`
  - `PATCH /admin/incidents/{id}`
- **Esquema en dos migraciones.**
  - La migración `24fc4214b845` crea el esquema inicial.
  - La migración `7b1d2e9a4c10` lo ajusta al diccionario de datos: JSONB, NOT NULL y el CHECK «completed ⇒ resultado».
  - `alembic check` no encuentra diferencias con los modelos.
- **Versiones de la PC de desarrollo.** Las pruebas pasaron en PostgreSQL 17.12, como pide el informe, pero con Python 3.11. Python 3.12 se confirma en la laptop.

## Pendientes

1. En la laptop:
   - instalar PyTorch y Diffusers;
   - descargar los pesos del modelo;
   - anotar las versiones en `docs/motor-ia.md`.
2. Ejecutar `verificar.ps1` con `AI_ENGINE=local` (CP-10 y CP-14) y guardar su registro.
3. Hacer la evaluación del Anexo A con `python -m app.ai.evaluation` y los 3 revisores.
4. Tomar capturas con IA real para la sección 4.5.13 del informe. Las capturas actuales son del modo simulación.
5. Medir el contraste AA de la paleta (RNF-04) con las DevTools.
6. Cambiar el recuadro «Antes · Después» de la landing por un ejemplo real cuando exista.
