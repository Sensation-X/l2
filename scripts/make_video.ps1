# ============================================================
#  make_video.ps1 — сборка видео без монтажки (голос + клипы + плашка)
#
#  Что нужно один раз:
#    winget install Gyan.FFmpeg            (или скачай ffmpeg и добавь в PATH)
#    pip install edge-tts                  (бесплатная нейрозвучка, русские голоса)
#
#  Использование:
#    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\make_video.ps1 -Ep ep01
#    powershell ... make_video.ps1 -Ep ep01 -Format Vertical
#    powershell ... make_video.ps1 -Ep ep01 -Voice ru-RU-SvetlanaNeural -Title "ХУРМЫЧ"
#
#  Вход:  video\<Ep>\vo.txt     текст озвучки (по строке на фразу)
#         video\<Ep>\clips.txt  список клипов "путь|секунд" (можно закомментировать всё —
#                               тогда видеорядом будет тёмная подложка с титулом)
#  Выход: video\<Ep>\out_horizontal.mp4 / out_vertical.mp4
# ============================================================
param(
    [string]$Ep = "ep01",
    [string]$Format = "Horizontal",
    [string]$Voice = "ru-RU-DmitryNeural",
    [string]$Title = "ХУРМЫЧ"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$epd  = Join-Path $root "video\$Ep"
$vo   = Join-Path $epd "vo.txt"

function Need($cmd, $hint) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "Не найден $cmd. Установи: $hint" -ForegroundColor Red; exit 1
    }
}
Need ffmpeg "winget install Gyan.FFmpeg"
Need python "winget install Python.Python.3.12"

Write-Host "[1/5] Озвучка через edge-tts ($Voice)..." -ForegroundColor Cyan
python -m edge_tts --voice $Voice --file $vo --write-media (Join-Path $epd "vo.mp3")
if (-not (Test-Path (Join-Path $epd "vo.mp3"))) { Write-Host "Озвучка не создалась. pip install edge-tts" -ForegroundColor Red; exit 1 }

$aud = [double](& ffprobe -v error -show_entries format=duration -of csv=p=0 (Join-Path $epd "vo.mp3"))
Write-Host ("      длительность озвучки: {0:N0} сек" -f $aud) -ForegroundColor Gray

# размеры кадра
if ($Format -eq "Vertical") { $W = 1080; $H = 1920; $out = "out_vertical.mp4" }
else                        { $W = 1920; $H = 1080; $out = "out_horizontal.mp4" }
$VF = "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:color=0x14161C,fps=30"

Write-Host "[2/5] Нарезка клипов..." -ForegroundColor Cyan
$tmp = Join-Path $epd "_build"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$list = Join-Path $tmp "list.txt"; Set-Content $list ""
$total = 0.0; $i = 0
if (Test-Path (Join-Path $epd "clips.txt")) {
    foreach ($line in Get-Content (Join-Path $epd "clips.txt") -Encoding UTF8) {
        $line = $line.Trim()
        if (-not $line -or $line.StartsWith("#")) { continue }
        $parts = $line.Split("|"); $clip = $parts[0].Trim()
        if (-not [System.IO.Path]::IsPathRooted($clip)) { $clip = Join-Path $root $clip }
        if (-not (Test-Path $clip)) { Write-Host "      пропуск (нет файла): $clip" -ForegroundColor Yellow; continue }
        $sec = if ($parts.Count -gt 1) { [double]$parts[1] } else { 0 }
        $seg = Join-Path $tmp ("seg{0:D2}.mp4" -f $i)
        $args = @("-y", "-v", "error", "-i", $clip)
        if ($sec -gt 0) { $args += @("-t", $sec) }
        $args += @("-an", "-vf", $VF, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", $seg)
        & ffmpeg @args
        $d = [double](& ffprobe -v error -show_entries format=duration -of csv=p=0 $seg)
        Add-Content $list ("file '" + $seg + "'")
        $total += $d; $i++
        Write-Host ("      сегмент {0}: {1:N0} сек" -f $i, $d) -ForegroundColor Gray
    }
}

Write-Host "[3/5] Добор фона до длительности озвучки..." -ForegroundColor Cyan
if ($total -lt $aud) {
    $gap = [math]::Ceiling($aud - $total) + 1
    $fill = Join-Path $tmp "fill.mp4"
    & ffmpeg -y -v error -f lavfi -i ("color=c=0x14161C:s=${W}x${H}:d={0}:r=30" -f $gap) `
        -vf ("drawtext=fontfile=C\:/Windows/Fonts/arial.ttf:text='{0}':fontcolor=0xEB7A34:fontsize={1}:x=(w-text_w)/2:y=(h-text_h)/2" -f $Title, [int]($H/14)) `
        -c:v libx264 -preset veryfast -crf 23 $fill
    Add-Content $list ("file '" + $fill + "'")
}

Write-Host "[4/5] Склейка + титул + звук..." -ForegroundColor Cyan
$font = "C\:/Windows/Fonts/arial.ttf"
$dt = ("drawtext=fontfile={0}:text='{1}':fontcolor=0xF2E8D5:fontsize={2}:x=(w-text_w)/2:y=h*0.42:enable='lt(t,4)':box=1:boxcolor=0x14161C@0.55:boxborderw=24" -f $font, $Title, [int]($H/12))
& ffmpeg -y -v error -f concat -safe 0 -i $list -i (Join-Path $epd "vo.mp3") `
    -vf $dt -c:v libx264 -preset medium -crf 21 -c:a aac -b:a 160k -shortest (Join-Path $epd $out)

Write-Host "[5/5] Готово:" -ForegroundColor Green
Write-Host ("      " + (Join-Path $epd $out)) -ForegroundColor Green
Write-Host "Дальше: залей файл на YouTube/VK/Rutube, вставь описание и таймкоды из video\$Ep\script.md." -ForegroundColor Gray
Write-Host "Вертикалки: запусти тот же скрипт с -Format Vertical или нарежь в CapCut по блокам раскадровки." -ForegroundColor Gray
