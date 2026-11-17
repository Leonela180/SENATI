# Prepara el motor de humanización LIGERO (Stable Diffusion 1.5 con stable-diffusion.cpp, solo procesador).
# Sirve para cualquier laptop con Windows y ~16 GB de RAM, sin necesidad de tarjeta NVIDIA.
# Requisito previo: .\scripts\instalar.ps1 (SIN -SinIA), porque el filtro de seguridad usa PyTorch y Diffusers.
# Descarga en total unos 5 GB y tarda según tu internet. No borra nada existente.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = "$root\backend\.venv\Scripts\python.exe"
$tools = "$root\private_data\tools\stable-diffusion.cpp"
$models = "$root\models"

# Versión fijada: la misma comprobada en la laptop del proyecto (commit 3bad892), con su huella SHA-256 oficial
$SdUrl = "https://github.com/leejet/stable-diffusion.cpp/releases/download/master-1094-3bad892/sd-master-3bad892-bin-win-cpu-x64.zip"
$SdSha = "0f24fa095c05b411843e4c0d73e44f1ed8e3ccfa17fc052857b874dc6e541cd2"

Write-Host "== Motor ligero de LUMIA AI ==" -ForegroundColor Cyan
if (-not (Test-Path $py)) { throw "Falta el entorno de Python. Ejecuta primero .\scripts\instalar.ps1 (sin -SinIA)." }
& $py -c "import torch, diffusers, transformers" 2>$null
if ($LASTEXITCODE -ne 0) { throw "Falta el motor de IA (PyTorch/Diffusers). Ejecuta .\scripts\instalar.ps1 SIN -SinIA y vuelve a intentarlo." }
$free = [math]::Round((Get-PSDrive ((Resolve-Path $root).Drive.Name)).Free / 1GB, 1)
if ($free -lt 12) { throw "Hay $free GB libres; se necesitan al menos 12 GB." }

# 1/4 Programa stable-diffusion.cpp (verificado con SHA-256 antes de usarlo)
Write-Host "1/4 Programa stable-diffusion.cpp" -ForegroundColor Cyan
if (-not (Test-Path "$tools\sd-cli.exe")) {
    New-Item -ItemType Directory -Force $tools | Out-Null
    $zip = "$tools\sd.zip"
    Invoke-WebRequest -Uri $SdUrl -OutFile $zip -UseBasicParsing
    if ((Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $SdSha) {
        Remove-Item $zip -Force
        throw "La descarga no coincide con la huella oficial. No se usará."
    }
    Expand-Archive -LiteralPath $zip -DestinationPath $tools -Force
    Remove-Item $zip -Force
    $exe = Get-ChildItem $tools -Recurse -Filter "sd-cli.exe" | Select-Object -First 1
    if (-not $exe) { throw "El paquete no contiene sd-cli.exe." }
    if ($exe.DirectoryName -ne $tools) { Get-ChildItem $exe.DirectoryName | Move-Item -Destination $tools -Force }
}
Write-Host "   listo: $tools\sd-cli.exe"

# 2/4 Pesos de Stable Diffusion 1.5 (licencia CreativeML OpenRAIL-M) y filtro de seguridad
Write-Host "2/4 Pesos del modelo (~4,3 GB) y filtro de seguridad (~0,6 GB)" -ForegroundColor Cyan
& $py -m pip install -q -U "huggingface_hub[cli]"
$hf = "$root\backend\.venv\Scripts\hf.exe"
if (-not (Test-Path $hf)) { $hf = "$root\backend\.venv\Scripts\huggingface-cli.exe" }
if (-not (Test-Path "$models\v1-5-pruned-emaonly.safetensors")) {
    & $hf download stable-diffusion-v1-5/stable-diffusion-v1-5 v1-5-pruned-emaonly.safetensors --local-dir $models
}
if (-not (Test-Path "$models\stable-diffusion-v1-5\safety_checker\model.fp16.safetensors")) {
    & $hf download stable-diffusion-v1-5/stable-diffusion-v1-5 --include "*.json" "*.txt" "safety_checker/*.fp16.safetensors" `
        --local-dir "$models\stable-diffusion-v1-5"
}

# 3/4 Copia cuantizada Q4_0 (más liviana para la RAM); el archivo original se conserva
Write-Host "3/4 Preparando la copia ligera del modelo (puede tardar varios minutos)" -ForegroundColor Cyan
Push-Location "$root\backend"
& $py tools\preparar_ligero.py --type q4_0
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "No se pudo preparar el modelo ligero. Revisa private_data\cuantizacion_sd15_q4_0.log" }
Pop-Location

# 4/4 Activar el motor en .env (se guarda una copia .env.bak antes de cambiarlo)
Write-Host "4/4 Activando el motor en .env" -ForegroundColor Cyan
$envFile = "$root\.env"
Copy-Item $envFile "$envFile.bak" -Force
$lines = Get-Content $envFile
$wanted = [ordered]@{ AI_ENGINE = "local"; AI_LOCAL_RUNTIME = "cpp"; AI_LITE_WORK_SIDE = "320"; AI_RESULT_BLEND = "0.35"; AI_DETAIL_INTENSITY = "0.65" }
foreach ($key in $wanted.Keys) {
    if ($lines -match "^$key=") { $lines = $lines -replace "^$key=.*$", "$key=$($wanted[$key])" }
    else { $lines += "$key=$($wanted[$key])" }
}
[System.IO.File]::WriteAllLines($envFile, [string[]]$lines, (New-Object System.Text.UTF8Encoding($false)))   # sin BOM: python-dotenv lo lee bien
Write-Host ""
Write-Host "Motor ligero listo. Reinicia LUMIA AI:  .\scripts\detener.ps1  y  .\scripts\iniciar.ps1" -ForegroundColor Green
Write-Host "Cada humanización tarda unos minutos en el procesador. Revisa el resultado antes de usarlo." -ForegroundColor Yellow
