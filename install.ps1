$ErrorActionPreference = "Stop"

$currentDir = Get-Location
$pythonDir = "$currentDir\python"
$ffmpegDir = "$currentDir\ffmpeg"
$tempDir = "$currentDir\ffmpeg_temp"

# Создание директорий
New-Item -ItemType Directory -Path $pythonDir -Force | Out-Null
New-Item -ItemType Directory -Path $ffmpegDir -Force | Out-Null

# Скачивание portable Python
$pythonUrl = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-embed-amd64.zip"
$pythonZip = "$currentDir\python.zip"
Write-Host "Скачивание Python: $pythonUrl"
try {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
    Write-Host "Распаковка Python в $pythonDir"
    Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
    Remove-Item $pythonZip -Force
} catch {
    Write-Error "Ошибка при скачивании/распаковке Python: $_"
    exit
}

# Скачивание portable FFmpeg
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ffmpegZip = "$currentDir\ffmpeg.zip"
Write-Host "Скачивание FFmpeg: $ffmpegUrl"
try {
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
    Write-Host "Распаковка FFmpeg в $tempDir"
    Expand-Archive -Path $ffmpegZip -DestinationPath $tempDir -Force
} catch {
    Write-Error "Ошибка при скачивании/распаковке FFmpeg: $_"
    exit
}

# Поиск и перемещение файлов FFmpeg
try {
    # Найти папку с бинарниками (например, ffmpeg-7.0-essentials_build\bin)
    $ffmpegBinDir = Get-ChildItem -Path $tempDir -Directory -Recurse | Where-Object { $_.Name -eq "bin" } | Select-Object -First 1
    if (-not $ffmpegBinDir) {
        Write-Error "Папка bin не найдена в $tempDir"
        exit
    }
    Write-Host "Перемещение FFmpeg из $($ffmpegBinDir.FullName) в $ffmpegDir"
    Move-Item -Path "$($ffmpegBinDir.FullName)\*" -Destination $ffmpegDir -Force
    Remove-Item -Path $tempDir -Recurse -Force
    Remove-Item $ffmpegZip -Force
} catch {
    Write-Error "Ошибка при перемещении/удалении FFmpeg файлов: $_"
    exit
}

# Проверка наличия ffmpeg.exe
if (!(Test-Path "$ffmpegDir\ffmpeg.exe")) {
    Write-Error "ffmpeg.exe не найден в $ffmpegDir"
    exit
}

# Создание run.bat
$runBat = "$currentDir\run.bat"
$runContent = "@echo off`r`n%~dp0python\python.exe %~dp0main.py %*"
Set-Content -Path $runBat -Value $runContent -Encoding ASCII

Write-Host "Установка завершена. Запускайте run.bat с параметрами, например: run.bat --all"
