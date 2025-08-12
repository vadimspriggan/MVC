$ErrorActionPreference = "Stop"

$currentDir = Get-Location
$pythonDir = "$currentDir\python"
$ffmpegDir = "$currentDir\ffmpeg"

# Download portable Python
$pythonUrl = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-embed-amd64.zip"
$pythonZip = "$currentDir\python.zip"
Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
Expand-Archive $pythonZip -DestinationPath $pythonDir
Remove-Item $pythonZip

# Download portable FFmpeg
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ffmpegZip = "$currentDir\ffmpeg.zip"
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
Expand-Archive $ffmpegZip -DestinationPath "$currentDir\ffmpeg_temp"
Move-Item -Path "$currentDir\ffmpeg_temp\bin\* " -Destination $ffmpegDir -Force
Remove-Item -Path "$currentDir\ffmpeg_temp" -Recurse -Force
Remove-Item $ffmpegZip

# Create run.bat
$runBat = "$currentDir\run.bat"
$runContent = "@echo off`r`n%~dp0python\python.exe %~dp0main.py %*"
Set-Content -Path $runBat -Value $runContent -Encoding ASCII

Write-Host "Installation complete. Run run.bat with parameters, e.g.: run.bat --all"
