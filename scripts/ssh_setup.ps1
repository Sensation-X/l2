# ============================================================
#  ssh_setup.ps1 — вход на сервер по SSH-ключу без пароля (Windows)
#
#  Запуск:
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ssh_setup.ps1
#  Или с другими реквизитами:
#    ... ssh_setup.ps1 -Ip 31.207.75.248 -User root
#
#  Что делает: создаёт ключ ed25519 (если нет), копирует его на сервер
#  (попросит пароль root ДВА раза), проверяет вход без пароля.
# ============================================================
param(
    [string]$Ip = "31.207.75.248",
    [string]$User = "root"
)
$ErrorActionPreference = "Stop"

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "Нет SSH-клиента. Параметры -> Приложения -> Дополнительные компоненты -> Открытый клиент OpenSSH." -ForegroundColor Red
    exit 1
}

$keyDir = Join-Path $env:USERPROFILE ".ssh"
$key = Join-Path $keyDir "id_ed25519"
if (-not (Test-Path $key)) {
    Write-Host "[1/3] Создаю ключ $key ..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $keyDir | Out-Null
    & ssh-keygen -t ed25519 -N '""' -f $key | Out-Null
    if (-not (Test-Path $key)) { Write-Host "Ключ не создался." -ForegroundColor Red; exit 1 }
} else {
    Write-Host "[1/3] Ключ уже есть: $key" -ForegroundColor Cyan
}

Write-Host "[2/3] Копирую ключ на сервер. Введи пароль root, когда попросят (символы не видны — это нормально)." -ForegroundColor Cyan
$pub = Get-Content "$key.pub" -Raw
$remote = 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && grep -qxF "' + $pub.Trim() + '" ~/.ssh/authorized_keys || echo "' + $pub.Trim() + '" >> ~/.ssh/authorized_keys && echo KEY_INSTALLED'
$pub | & ssh "$User@$Ip" $remote
if ($LASTEXITCODE -ne 0) { Write-Host "Не удалось скопировать ключ. Проверь пароль и доступность сервера." -ForegroundColor Red; exit 1 }

Write-Host "[3/3] Проверяю вход без пароля..." -ForegroundColor Cyan
& ssh -o BatchMode=yes -o ConnectTimeout=10 "$User@$Ip" "echo SSH_OK_$(hostname)"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Готово: вход по ключу работает. Дальше: ssh $User@$Ip" -ForegroundColor Green
} else {
    Write-Host "Вход без пароля не сработал. Повтори шаг 2 или смотри SSH_SETUP.md." -ForegroundColor Yellow
}
