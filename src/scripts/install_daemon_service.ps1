<#
.SYNOPSIS
  Instalador del servicio DevBrain Observer Daemon para Windows (Scheduled Task).
.DESCRIPTION
  Registra devbrain_daemon.py para ejecutarse en segundo plano con inicio automático en el sistema del usuario.
#>

param (
    [string]$VaultDir = "$HOME\ObsidianVault",
    [string]$Action = "install"
)

$TaskName = "DevBrainObserverDaemon"
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
$ScriptPath = Join-Path $PSScriptRoot "devbrain_daemon.py"

if (-not $PythonExe) {
    Write-Host "[ERROR] Python no fue encontrado en el PATH del sistema." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Host "[ERROR] devbrain_daemon.py no se encontro en: $ScriptPath" -ForegroundColor Red
    exit 1
}

if ($Action -eq "uninstall") {
    Write-Host "Desinstalando tarea programada: $TaskName..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "[OK] Daemon desinstalado con exito." -ForegroundColor Green
    exit 0
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🧠 Instalador del Servicio DevBrain Observer Daemon   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Ruta de Python : $PythonExe"
Write-Host "Ruta de Daemon : $ScriptPath"
Write-Host "Vault Dir      : $VaultDir"
Write-Host ""

# Desregistrar previa si existe
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$ActionObj = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`"" -WorkingDirectory (Split-Path $ScriptPath)
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 365) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $ActionObj -Trigger $Trigger -Settings $Settings -Description "DevBrain Daemon: Sincroniza commits y decisiones tecnicas en segundo plano." | Out-Null

Write-Host "[EXITO] Servicio registrado exitosamente como tarea programada ($TaskName)." -ForegroundColor Green
Write-Host "Iniciando daemon en segundo plano ahora..." -ForegroundColor Gray
Start-ScheduledTask -TaskName $TaskName
Write-Host "[OK] Daemon activo y monitoreando en segundo plano." -ForegroundColor Green
