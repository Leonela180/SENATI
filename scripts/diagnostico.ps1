# Verifica requisitos de la PC (skill §11). No instala nada.
$ErrorActionPreference = "Continue"
Write-Host "== Diagnóstico LUMIA AI ==" -ForegroundColor Cyan
"Windows : " + (Get-CimInstance Win32_OperatingSystem).Caption + " " + (Get-CimInstance Win32_OperatingSystem).OSArchitecture
"Equipo  : " + (Get-CimInstance Win32_ComputerSystem).Manufacturer + " " + (Get-CimInstance Win32_ComputerSystem).Model
"CPU     : " + (Get-CimInstance Win32_Processor | Select-Object -First 1).Name
"RAM     : {0} GB" -f [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
"Disco C : {0} GB libres" -f [math]::Round((Get-PSDrive C).Free / 1GB, 1)
$faltan = 0
foreach ($cmd in "python", "node", "npm", "psql", "nvidia-smi") {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) { Write-Host ("{0,-11} OK   {1}" -f $cmd, $c.Source) -ForegroundColor Green }
    else { Write-Host ("{0,-11} FALTA" -f $cmd) -ForegroundColor Red; $faltan++ }
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    $v = python --version
    if ($v -notmatch "3\.12") { Write-Warning "Se recomienda Python 3.12 (encontrado: $v)" }
}
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else { Write-Warning "Sin GPU NVIDIA: el motor local funcionará en CPU (muy lento) o solo con AI_ENGINE=mock." }
$svc = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($svc) { "PostgreSQL servicio: " + ($svc | Select-Object -First 1).Status } else { Write-Warning "No se encontró el servicio de PostgreSQL." }
if ($faltan -gt 0) { Write-Host "Faltan $faltan programas. Instálalos antes de continuar." -ForegroundColor Red; exit 1 }
Write-Host "Diagnóstico correcto." -ForegroundColor Green
