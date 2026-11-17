# Comparte Flask + PostgreSQL + worker conservando los datos en esta PC.
param([switch]$NoAbrir)
$ErrorActionPreference = 'Stop'
& "$PSScriptRoot\iniciar.ps1" -Compartir -NoAbrir
& "$PSScriptRoot\compartir.ps1" -SegundoPlano
if (-not $NoAbrir) {
    $root = Split-Path $PSScriptRoot -Parent
    Start-Process (Get-Content (Join-Path $root 'tools\enlace.txt'))
}
