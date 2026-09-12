# ============================================================
#  recon.ps1 — разведка сервера одной командой (ничего не меняет)
#  Запуск:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts/recon.ps1
#  Скопирует recon.sh на сервер, выполнит его и напечатает отчёт у тебя.
# ============================================================
param(
    [string]$Ip = "31.207.75.248",
    [string]$User = "root"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "[1/2] Копирую скрипт разведки на сервер..." -ForegroundColor Cyan
& scp "$root/site/recon.sh" "${User}@${Ip}:/root/recon.sh"
if ($LASTEXITCODE -ne 0) { Write-Host "scp не сработал. Проверь, что вошли по ключу: ssh $User@$Ip" -ForegroundColor Red; exit 1 }

Write-Host "[2/2] Запускаю разведку (только чтение)..." -ForegroundColor Cyan
& ssh "${User}@${Ip}" "bash /root/recon.sh"
Write-Host ""
Write-Host "Скопируй ВЕСЬ вывод выше и пришли в чат." -ForegroundColor Green
