# ============================================================
#  install_scheduler.ps1 — автопубликация по расписанию (Windows)
#  Создаёт задачу в Планировщике заданий: каждые 30 минут запускает
#  publish.ps1 -Apply, и посты из очереди уходят сами, без тебя.
#
#  Запуск от обычного пользователя (админ не нужен):
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_scheduler.ps1
#  Удалить задачу:
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_scheduler.ps1 -Remove
# ============================================================
param([switch]$Remove)

$taskName = "GTV_Publish"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$script = Join-Path $root "scripts\publish.ps1"

if ($Remove) {
    schtasks /Delete /TN $taskName /F
    Write-Host "Задача $taskName удалена." -ForegroundColor Yellow
    exit 0
}

$tr = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`" -Apply"
schtasks /Create /TN $taskName /TR $tr /SC MINUTE /MO 30 /F | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Готово: задача $taskName создана, publish.ps1 -Apply будет запускаться каждые 30 минут." -ForegroundColor Green
    Write-Host "Посты уходят, когда наступает их время в queue/queue.json. Компьютер должен быть включён." -ForegroundColor Gray
    Write-Host "Проверить: schtasks /Query /TN $taskName" -ForegroundColor Gray
} else {
    Write-Host "Не удалось создать задачу. Открой Планировщик заданий вручную и создай её сам." -ForegroundColor Red
}
