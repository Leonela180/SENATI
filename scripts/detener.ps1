# Cierra SOLO los procesos que abrió iniciar.ps1 (no toca PostgreSQL ni otros servicios).
param([switch]$ConservarTunel)
$tunnelFile = Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\tunnel.pid'
if (-not $ConservarTunel -and (Test-Path $tunnelFile)) {
    $tunnelProcess = Get-Process -Id (Get-Content $tunnelFile) -ErrorAction SilentlyContinue
    if ($tunnelProcess -and $tunnelProcess.ProcessName -eq 'cloudflared') { Stop-Process -Id $tunnelProcess.Id }
    Remove-Item -LiteralPath $tunnelFile
}
$file = "$PSScriptRoot\.pids"
if (-not (Test-Path $file)) { Write-Host "No hay procesos de LUMIA AI registrados."; exit 0 }
Get-Content $file | ForEach-Object {
    $ownedProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $_" -ErrorAction SilentlyContinue
    $expectedPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'backend\.venv\Scripts\python.exe'
    if ($ownedProcess -and $ownedProcess.ExecutablePath -eq $expectedPath -and $ownedProcess.CommandLine -match 'waitress|app.workers.image_worker') {
        # El lanzador de un venv puede crear un hijo: cerrar también ese hijo evita dejar el puerto ocupado.
        & taskkill.exe /PID $_ /T /F | Out-Null
        "Detenido proceso LUMIA $_ y sus hijos"
    }
}
Remove-Item $file
Write-Host "LUMIA AI detenido." -ForegroundColor Green
