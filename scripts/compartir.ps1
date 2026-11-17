# Comparte LUMIA AI por internet con un enlace temporal (Cloudflare Tunnel, gratis y sin cuenta).
# Requisitos: LUMIA AI encendido con scripts\iniciar.ps1 y TRUST_PROXY=1 en el archivo .env.
# El enlace funciona mientras esta ventana y la laptop estén encendidas. Para cerrarlo: Ctrl + C.
param([switch]$SegundoPlano)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$tools = Join-Path $root "tools"
$exe = Join-Path $tools "cloudflared.exe"
$log = Join-Path $tools "cloudflared.log"

# 1) LUMIA AI debe estar encendido
try { Invoke-RestMethod http://127.0.0.1:5000/api/v1/health -TimeoutSec 3 | Out-Null }
catch { Write-Error "LUMIA AI no está encendido. Ejecuta primero: .\scripts\iniciar.ps1" }

# 2) Aviso si falta TRUST_PROXY (sin eso, todos los visitantes cuentan como una sola persona en el límite de intentos)
if ($env:TRUST_PROXY -ne '1' -and -not (Select-String -Path (Join-Path $root ".env") -Pattern "^TRUST_PROXY=1" -Quiet)) {
    Write-Warning "Agrega la línea TRUST_PROXY=1 al archivo .env y reinicia LUMIA AI (detener.ps1 e iniciar.ps1) antes de compartir."
    Write-Warning "Sin esa línea, el límite de 10 registros por hora se aplica a todos los visitantes juntos."
}

# 3) Descarga cloudflared una sola vez (programa oficial de Cloudflare)
if (-not (Test-Path $exe)) {
    New-Item -ItemType Directory -Force $tools | Out-Null
    Write-Host "Descargando cloudflared (una sola vez, ~60 MB)..." -ForegroundColor Cyan
    $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/cloudflare/cloudflared/releases/latest'
    $asset = $release.assets | Where-Object { $_.name -eq 'cloudflared-windows-amd64.exe' } | Select-Object -First 1
    if (-not $asset -or $asset.digest -notmatch '^sha256:([a-f0-9]{64})$') { throw 'No se encontró un hash oficial para verificar cloudflared.' }
    $expectedHash = $Matches[1]
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $exe -UseBasicParsing
    if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
        throw 'La descarga no coincide con el hash oficial. No se ejecutará.'
    }
}

# 4) Abre el túnel y muestra el enlace público
$log = Join-Path $tools ("cloudflared_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log')
$proc = Start-Process $exe -ArgumentList "tunnel", "--no-autoupdate", "--url", "http://127.0.0.1:5000" `
        -RedirectStandardError $log -PassThru -WindowStyle Hidden
try {
    $keepRunning = $false
    $link = $null
    for ($i = 0; $i -lt 60 -and -not $link; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Path $log) {
            $m = Select-String -Path $log -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" | Select-Object -First 1
            if ($m) { $link = $m.Matches[0].Value }
        }
        if ($proc.HasExited) { break }
    }
    if (-not $link) { Write-Error "No se pudo abrir el túnel. Revisa tu internet y el archivo $log" }
    try { Set-Clipboard -Value $link } catch { Write-Warning 'No se pudo copiar el enlace al portapapeles.' }
    $proc.Id | Set-Content (Join-Path $tools 'tunnel.pid')
    $link | Set-Content (Join-Path $tools 'enlace.txt')
    Write-Host ""
    Write-Host "  LUMIA AI ya se puede abrir desde cualquier celular o computadora:" -ForegroundColor Green
    Write-Host "  $link" -ForegroundColor Yellow
    Write-Host "  (el enlace ya está copiado: pégalo en WhatsApp o en un correo)"
    Write-Host ""
    Write-Host "  - Funciona mientras tu laptop esté encendida, conectada y el túnel siga activo."
    Write-Host "  - Cada vez que ejecutes este script el enlace cambia."
    Write-Host "  - Las imágenes que suban otras personas se guardan en tu laptop."
    if (-not $SegundoPlano) { Write-Host "  Para dejar de compartir: presiona Ctrl + C o cierra esta ventana." -ForegroundColor Cyan }
    if ($SegundoPlano) {
        $keepRunning = $true
        Write-Host 'El túnel continúa en segundo plano. Para cerrarlo: scripts\detener.ps1'
    } else { Wait-Process -Id $proc.Id }
} finally {
    if (-not $keepRunning) {
        if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
        Write-Host "Enlace cerrado: LUMIA AI ya no es accesible desde internet." -ForegroundColor Green
    }
}
