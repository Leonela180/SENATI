# Levanta la API (waitress) y el worker, y abre el navegador (modo demostración).
param([switch]$NoAbrir, [switch]$Compartir)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = "$root\backend\.venv\Scripts\python.exe"
if (-not (Test-Path "$root\.env")) { Write-Error "Falta .env: copia .env.example y complétalo." }
if (-not (Test-Path $py)) { Write-Error "Falta el entorno de Python: ejecuta scripts\instalar.ps1" }

$envs = @{}
Get-Content "$root\.env" | Where-Object { $_ -match "^\s*([A-Z_]+)=(.*)$" } | ForEach-Object {
    $settingName = $Matches[1]
    $settingValue = $Matches[2].Trim()
    if ($settingValue.Length -ge 2 -and (($settingValue.StartsWith("'") -and $settingValue.EndsWith("'")) -or ($settingValue.StartsWith('"') -and $settingValue.EndsWith('"')))) {
        $settingValue = $settingValue.Substring(1, $settingValue.Length - 2)
    }
    $envs[$settingName] = $settingValue
}
foreach ($k in "SECRET_KEY", "DATABASE_URL") { if (-not $envs[$k]) { Write-Error "Falta $k en .env" } }
if ($Compartir) {
    $env:TRUST_PROXY = '1'
    $env:APP_ENV = 'production'
    $envs['TRUST_PROXY'] = '1'
}
$configuredModelPath = $envs["AI_MODEL_PATH"]
if ($configuredModelPath -and -not [System.IO.Path]::IsPathRooted($configuredModelPath)) { $configuredModelPath = Join-Path $root $configuredModelPath }
if ($envs["AI_ENGINE"] -eq "local" -and (-not $configuredModelPath -or -not (Test-Path -LiteralPath $configuredModelPath))) {
    Write-Error "AI_ENGINE=local pero no están los pesos en $($envs['AI_MODEL_PATH'])"
}
if ($envs["AI_ENGINE"] -ne "local") { Write-Warning "AI_ENGINE=$($envs['AI_ENGINE']): SIMULACIÓN, SIN IA REAL" }
if (-not (Test-Path "$root\frontend\dist\index.html")) { Write-Error "Falta compilar el frontend: ejecuta scripts\instalar.ps1" }
if (Test-Path "$PSScriptRoot\.pids") { Write-Error "LUMIA AI ya parece estar en marcha. Ejecuta scripts\detener.ps1 primero." }

& $py -c "import sys; sys.path.insert(0, r'$root\backend'); from app import create_app; from app.extensions import db; a=create_app(); a.app_context().push(); db.session.execute(db.text('SELECT 1')); print('Base de datos: OK')"
if ($LASTEXITCODE -ne 0) { Write-Error "No se pudo conectar con PostgreSQL. Revisa el servicio y DATABASE_URL." }

$pids = @()
$logs = Join-Path $root 'private_data\logs'
New-Item -ItemType Directory -Force $logs | Out-Null
$waitressArgs = @("-m", "waitress", "--listen=127.0.0.1:5000")
if ($envs["TRUST_PROXY"] -eq "1") {
    # Modo compartir (scripts\compartir.ps1): Waitress acepta las cabeceras del túnel local de Cloudflare
    $waitressArgs += @("--trusted-proxy=127.0.0.1", '--trusted-proxy-headers="x-forwarded-for x-forwarded-proto x-forwarded-host"')
}
$waitressArgs += "wsgi:app"
$api = Start-Process $py -ArgumentList $waitressArgs `
       -WorkingDirectory "$root\backend" -PassThru -WindowStyle Hidden `
       -RedirectStandardOutput "$logs\api.out.log" -RedirectStandardError "$logs\api.err.log"
$pids += $api.Id
$n = [int]($envs["AI_WORKER_CONCURRENCY"]); if ($n -lt 1) { $n = 1 }
for ($i = 1; $i -le $n; $i++) {
    $w = Start-Process $py -ArgumentList "-m", "app.workers.image_worker" -WorkingDirectory "$root\backend" -PassThru -WindowStyle Hidden `
         -RedirectStandardOutput "$logs\worker_$i.out.log" -RedirectStandardError "$logs\worker_$i.err.log"
    $pids += $w.Id
}
$pids | Set-Content "$PSScriptRoot\.pids"

$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    try { Invoke-RestMethod http://127.0.0.1:5000/api/v1/health -TimeoutSec 2 | Out-Null; $ok = $true; break } catch { Start-Sleep 1 }
}
if (-not $ok) { Write-Error "La API no respondió en 30 s. Revisa private_data\logs." }
if (-not $NoAbrir -and -not $Compartir) { Start-Process "http://localhost:5000" }
Write-Host "LUMIA AI en marcha (procesos: $($pids -join ', ')). Para cerrar: scripts\detener.ps1" -ForegroundColor Green
