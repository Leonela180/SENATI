# Instala dependencias del proyecto, compila el frontend y aplica migraciones.
# No instala PostgreSQL ni controladores (skill §11).
# Uso: .\scripts\instalar.ps1          (todo, con PyTorch y Diffusers)
#      .\scripts\instalar.ps1 -SinIA    (sin el motor de IA: solo para probar con AI_ENGINE=mock)
param([switch]$SinIA)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Warning "Se creó .env. Completa SECRET_KEY, DATABASE_URL, AI_MODEL_ID y AI_MODEL_PATH y vuelve a ejecutar."
    exit 1
}
if (-not (Select-String -Path ".env" -Pattern "^SECRET_KEY=.+")) { Write-Error "SECRET_KEY está vacío en .env" }
New-Item -ItemType Directory -Force "private_data\originals", "private_data\results", "docs\evidencias" | Out-Null

Write-Host "1/4 Entorno de Python" -ForegroundColor Cyan
Set-Location "$root\backend"
if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = "$root\backend\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -e ".[dev]"

Write-Host "2/4 PyTorch y motor de IA" -ForegroundColor Cyan
if ($SinIA) {
    Write-Warning "Se omite el motor de IA (-SinIA). Solo funcionará AI_ENGINE=mock (simulación, sin IA real)."
} elseif (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    & $py -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
} else {
    Write-Warning "Sin GPU NVIDIA: se instala PyTorch para CPU."
    & $py -m pip install torch torchvision
}
if (-not $SinIA) { & $py -m pip install -e ".[ia]" }

Write-Host "2b/4 Modelo para recortar el fondo (Estudio de edición, ~170 MB, una sola vez)" -ForegroundColor Cyan
Push-Location "$root\backend"
& $py -c "from app.ai import editing; from rembg import new_session; new_session(editing.SEGMENT_MODEL); print('Modelo de segmentación listo:', editing.SEGMENT_MODEL)"
if ($LASTEXITCODE -ne 0) { Write-Warning "No se pudo descargar el modelo de segmentación. Se reintentará la primera vez que uses «Cambiar fondo»." }
Pop-Location

Write-Host "3/4 Migraciones de PostgreSQL" -ForegroundColor Cyan
& "$root\backend\.venv\Scripts\alembic.exe" upgrade head

Write-Host "4/4 Frontend" -ForegroundColor Cyan
Set-Location "$root\frontend"
npm ci
npm run build

$model = (Select-String -Path "$root\.env" -Pattern "^AI_MODEL_PATH=(.+)$").Matches.Groups[1].Value
if (-not $model -or -not (Test-Path (Join-Path $root $model))) {
    Write-Warning "No se encuentran los pesos del modelo en '$model'. Cópialos antes de usar AI_ENGINE=local."
}
Write-Host "Instalación completa. Ejecuta scripts\iniciar.ps1" -ForegroundColor Green
