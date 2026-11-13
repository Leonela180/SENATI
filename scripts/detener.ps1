# Cierra SOLO los procesos que abrió iniciar.ps1 (no toca PostgreSQL ni otros servicios).
$file = "$PSScriptRoot\.pids"
if (-not (Test-Path $file)) { Write-Host "No hay procesos de LUMIA AI registrados."; exit 0 }
Get-Content $file | ForEach-Object {
    $p = Get-Process -Id $_ -ErrorAction SilentlyContinue
    if ($p -and $p.ProcessName -like "python*") { Stop-Process -Id $_ -Force; "Detenido proceso $_" }
}
Remove-Item $file
Write-Host "LUMIA AI detenido." -ForegroundColor Green
