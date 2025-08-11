$ErrorActionPreference = "Stop"

$currentDir = Get-Location
$pythonDir = "$currentDir\python"
$ffmpegDir = "$currentDir\ffmpeg"

# Скачивание portable Python
$pythonUrl = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-embed-amd64.zip"
$pythonZip = "$currentDir\python.zip"
Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
Expand-Archive $pythonZip -DestinationPath $pythonDir
Remove-Item $pythonZip

# Скачивание portable FFmpeg
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ffmpegZip = "$currentDir\ffmpeg.zip"
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
Expand-Archive $ffmpegZip -DestinationPath "$currentDir\ffmpeg_temp"
Move-Item -Path "$currentDir\ffmpeg_temp\bin\* " -Destination $ffmpegDir -Force
Remove-Item -Path "$currentDir\ffmpeg_temp" -Recurse -Force
Remove-Item $ffmpegZip

# Скачивание main.py (из GitHub или скопировать из репо)
# Для теста: Assume it's in the repo, or download from raw URL
$scriptUrl = "https://raw.githubusercontent.com/your-username/MVC/main/main.py"  # Замени на твой repo
$scriptPath = "$currentDir\main.py"
Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath

# Создание run.bat
$runBat = "$currentDir\run.bat"
$runContent = "@echo off`r`n%~dp0python\python.exe %~dp0main.py %*"
Set-Content -Path $runBat -Value $runContent -Encoding ASCII

Write-Host "Установка завершена. Запускайте run.bat с параметрами, например: run.bat"
