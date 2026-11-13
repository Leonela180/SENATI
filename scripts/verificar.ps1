# Health check, BD autenticada, migraciones, pruebas mínimas e inferencia real (skill §11, CP-14).
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = "$root\backend\.venv\Scripts\python.exe"
$muestra = "$root\docs\muestra_autorizada.png"
$log = "$root\docs\evidencias\verificar_$(Get-Date -Format yyyyMMdd_HHmm).txt"
Start-Transcript -Path $log | Out-Null
try {
    Write-Host "1/5 Salud de la API" -ForegroundColor Cyan
    $h = (Invoke-RestMethod http://127.0.0.1:5000/api/v1/health).data
    $h | Format-List
    if ($h.engine -ne "local") { throw "AI_ENGINE no es local: la verificación final exige IA real." }

    Write-Host "2/5 Conexión autenticada y migraciones" -ForegroundColor Cyan
    Push-Location "$root\backend"
    & .\.venv\Scripts\alembic.exe current
    & .\.venv\Scripts\alembic.exe check
    if ($LASTEXITCODE -ne 0) { throw "El esquema no coincide con los modelos." }

    Write-Host "3/5 Pruebas automatizadas mínimas" -ForegroundColor Cyan
    & .\.venv\Scripts\pytest.exe -q
    if ($LASTEXITCODE -ne 0) { throw "Hay pruebas fallidas." }
    Pop-Location

    Write-Host "4/5 Worker activo" -ForegroundColor Cyan
    if ($null -eq $h.worker_seconds_since_beat -or $h.worker_seconds_since_beat -gt 30) { throw "El worker no está en marcha." }
    "Worker: OK"

    Write-Host "5/5 Inferencia real con imagen autorizada" -ForegroundColor Cyan
    if (-not (Test-Path $muestra)) { throw "Falta $muestra (imagen sintética autorizada)." }
    & $py "$root\backend\tools\verificar_circuito.py" $muestra
    if ($LASTEXITCODE -ne 0) { throw "La inferencia real falló." }

    Write-Host "VERIFICACIÓN COMPLETA: todo correcto." -ForegroundColor Green
} catch {
    Write-Host "VERIFICACIÓN FALLIDA: $_" -ForegroundColor Red
    exit 1
} finally {
    Stop-Transcript | Out-Null
    Write-Host "Registro guardado en $log"
}
