# ============================================================
#  publish.ps1 — паблишер Хурмыч для Telegram
#  Читает очередь queue/queue.json и публикует посты через Bot API.
#
#  Использование (из папки проекта):
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\publish.ps1 -List
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\publish.ps1 -DryRun
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\publish.ps1 -Apply
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\publish.ps1 -Apply -All
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\publish.ps1 -Undo p001
#
#  Ключи:
#    -List    показать очередь и статусы, ничего не отправлять
#    -DryRun  показать, ЧТО уйдёт и КОГДА, без отправки (по умолчанию)
#    -Apply   реально отправить посты, у которых наступило время
#    -All     игнорировать расписание и отправить все pending
#    -Undo id отозвать отправленный пост по его id
#
#  Токен бота лежит ТОЛЬКО у тебя: config/secrets.json (в архив не попадает).
# ============================================================
param(
    [switch]$List,
    [switch]$DryRun,
    [switch]$Apply,
    [switch]$All,
    [string]$Undo = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$queuePath = Join-Path $root "queue\queue.json"
$secretPath = Join-Path $root "config\secrets.json"

function Write-Step($m) { Write-Host "[GTV] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "  OK  $m" -ForegroundColor Green }
function Write-Warn2($m){ Write-Host "  !!  $m" -ForegroundColor Yellow }
function Write-Err2($m) { Write-Host "  XX  $m" -ForegroundColor Red }

if (-not (Test-Path $queuePath)) { Write-Err2 "Не найден $queuePath"; exit 1 }

$raw = [System.IO.File]::ReadAllText($queuePath, [System.Text.Encoding]::UTF8)
$queue = $raw | ConvertFrom-Json
$chat = $queue.channel

function Save-Queue {
    $json = $queue | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($queuePath, $json, (New-Object System.Text.UTF8Encoding($false)))
}

if ($List) {
    Write-Step "Очередь: $($queue.items.Count) элемент(ов), канал $chat"
    foreach ($it in $queue.items) {
        $t = if ($it.text) { $it.text.Substring(0, [Math]::Min(60, $it.text.Length)) -replace "`n", " " } else { $it.file }
        Write-Host ("  {0}  {1,-8} {2,-16} {3}  msg={4}" -f $it.id, $it.status, $it.schedule, $t, $it.message_id)
    }
    exit 0
}

$token = $null
if ($Apply -or $Undo) {
    if (-not (Test-Path $secretPath)) {
        Write-Err2 "Нет $secretPath. Скопируй config\secrets.template.json в config\secrets.json и впиши токен бота."
        exit 1
    }
    $sec = ([System.IO.File]::ReadAllText($secretPath, [System.Text.Encoding]::UTF8)) | ConvertFrom-Json
    $token = $sec.telegram_bot_token
    if (-not $token -or $token -like "*СЮДА*") { Write-Err2 "Токен не заполнен в secrets.json"; exit 1 }
}
$api = "https://api.telegram.org/bot$token/"

function Tg-Text($text) {
    $body = @{ chat_id = $chat; text = $text; disable_web_page_preview = $true } | ConvertTo-Json -Depth 5
    $r = Invoke-RestMethod -Uri ($api + "sendMessage") -Method Post -Body $body -ContentType "application/json; charset=utf-8"
    return $r
}
function Tg-File($method, $fileRel, $caption) {
    $file = Join-Path $root $fileRel
    if (-not (Test-Path $file)) { throw "Файл не найден: $file" }
    $args = @("-s", "-X", "POST", $api + $method, "-F", "chat_id=$chat")
    if ($caption) { $args += @("-F", "caption=$caption") }
    $args += @("-F", "photo=@$file")
    if ($method -eq "sendVideo") { $args[$args.Count - 1] = "video=@$file" }
    $out = & curl.exe @args | ConvertFrom-Json
    if (-not $out.ok) { throw "Telegram error: $($out.description)" }
    return $out
}

if ($Undo) {
    $it = $queue.items | Where-Object { $_.id -eq $Undo }
    if (-not $it -or -not $it.message_id) { Write-Err2 "Нет отправленного поста с id=$Undo"; exit 1 }
    $body = @{ chat_id = $chat; message_id = [int]$it.message_id } | ConvertTo-Json
    $r = Invoke-RestMethod -Uri ($api + "deleteMessage") -Method Post -Body $body -ContentType "application/json; charset=utf-8"
    if ($r.ok) { $it.status = "undone"; Save-Queue; Write-Ok "Пост $Undo удалён из канала" } else { Write-Err2 "Не удалось удалить" }
    exit 0
}

$now = Get-Date
$sent = 0
foreach ($it in $queue.items) {
    if ($it.status -ne "pending") { continue }
    $due = $true
    if (-not $All -and $it.schedule) {
        $t = [DateTime]::ParseExact($it.schedule, "yyyy-MM-dd HH:mm", $null)
        $due = $now -ge $t
    }
    $label = if ($it.text) { ($it.text -split "`n" | Select-Object -First 1) } else { $it.file }
    if (-not $Apply) {
        Write-Host ("  [{0}] {1}  {2}  ->  {3}" -f $(if ($due -and $Apply) {"ГОТОВ"} else {"план"}), $it.id, $it.schedule, $label) -ForegroundColor $(if ($due) {"Green"} else {"DarkGray"})
        continue
    }
    if (-not $due) { continue }
    try {
        if ($it.type -eq "text") { $r = Tg-Text $it.text }
        elseif ($it.type -eq "photo") { $r = Tg-File "sendPhoto" $it.file $it.text }
        elseif ($it.type -eq "video") { $r = Tg-File "sendVideo" $it.file $it.text }
        else { throw "Неизвестный тип: $($it.type)" }
        if ($r.ok) {
            $it.status = "sent"
            $it.message_id = $r.result.message_id
            $it.sent_at = $now.ToString("yyyy-MM-dd HH:mm")
            $sent++
            Write-Ok "$($it.id) опубликован (msg $($r.result.message_id))"
        } else { Write-Err2 "$($it.id): $($r.description)" }
    } catch {
        Write-Err2 "$($it.id): $($_.Exception.Message)"
    }
    Start-Sleep -Milliseconds 700   # не долбить API
}

if ($Apply) { Save-Queue; Write-Step "Отправлено: $sent. Статусы записаны в queue.json" }
else { Write-Step "Это был DryRun. Запусти с -Apply, чтобы опубликовать." }
