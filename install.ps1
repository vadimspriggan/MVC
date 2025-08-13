$ErrorActionPreference = "Stop"

$currentDir = Get-Location
$pythonDir = "$currentDir\python"
$ffmpegDir = "$currentDir\ffmpeg"
$tempDir = "$currentDir\ffmpeg_temp"
$modulesDir = "$currentDir\modules"

# Создание директорий
New-Item -ItemType Directory -Path $pythonDir -Force | Out-Null
New-Item -ItemType Directory -Path $ffmpegDir -Force | Out-Null
New-Item -ItemType Directory -Path $modulesDir -Force | Out-Null

# Проверка наличия Python
if (Test-Path "$pythonDir\python.exe") {
    Write-Host "Python уже установлен в $pythonDir"
} else {
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
}

# Проверка наличия FFmpeg и ffprobe
if ((Test-Path "$ffmpegDir\ffmpeg.exe") -and (Test-Path "$ffmpegDir\ffprobe.exe")) {
    Write-Host "FFmpeg и ffprobe уже установлены в $ffmpegDir"
} else {
    $ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    $ffmpegZip = "$currentDir\ffmpeg.zip"
    Write-Host "Скачивание FFmpeg (BtbN GPL build): $ffmpegUrl"
    try {
        # Проверка доступности URL
        $response = Invoke-WebRequest -Uri $ffmpegUrl -Method Head -UseBasicParsing
        if ($response.StatusCode -ne 200) {
            Write-Error "URL $ffmpegUrl недоступен (код: $($response.StatusCode))"
            exit
        }
        Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
        Write-Host "Распаковка FFmpeg в $tempDir"
        Expand-Archive -Path $ffmpegZip -DestinationPath $tempDir -Force
    } catch {
        Write-Error "Ошибка при скачивании/распаковке FFmpeg: $_"
        exit
    }

    try {
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
}

# Проверка наличия ffmpeg.exe и ffprobe.exe
if (!(Test-Path "$ffmpegDir\ffmpeg.exe")) {
    Write-Error "ffmpeg.exe не найден в $ffmpegDir"
    exit
}
if (!(Test-Path "$ffmpegDir\ffprobe.exe")) {
    Write-Error "ffprobe.exe не найден в $ffmpegDir"
    exit
}

# Проверка main.py и модулей
$scriptUrl = "https://raw.githubusercontent.com/your-username/MVC/main/main.py"  # Замени на твой GitHub
$scriptPath = "$currentDir\main.py"
$moduleUrls = @{
    "scan_videos.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/scan_videos.py";
    "metadata.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/metadata.py";
    "clip.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/clip.py";
    "encode.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/encode.py";
    "ssim.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/ssim.py";
    "convert.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/convert.py";
    "compare.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/compare.py";
    "__init__.py" = "https://raw.githubusercontent.com/your-username/MVC/main/modules/__init__.py"
}
Write-Host "Проверка main.py и модулей"
if (!(Test-Path $scriptPath) -or !(Test-Path "$modulesDir\scan_videos.py")) {
    Write-Host "Скачивание main.py и модулей"
    try {
        Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath
        foreach ($module in $moduleUrls.Keys) {
            Invoke-WebRequest -Uri $moduleUrls[$module] -OutFile "$modulesDir\$module"
        }
    } catch {
        Write-Error "Ошибка при скачивании main.py или модулей: $_"
        exit
    }
} else {
    Write-Host "main.py и modules/*.py уже присутствуют в репо"
}

# Создание run.bat
$runBat = "$currentDir\run.bat"
$runContent = @"
@echo off
chcp 65001 >nul
set "work_dir="
set "norecursive="
set "params=%*"

:: Check if --work-dir is in params
echo %* | find "--work-dir" >nul
if %ERRORLEVEL% equ 0 (
    for /f "tokens=1,* delims== " %%a in ('echo %*') do (
        if "%%a"=="--work-dir" set "work_dir=%%b"
    )
) else (
    set /p work_dir="Введите путь к рабочей директории (например, E:\test1, пусто = текущая папка): "
)

:: Use current directory if work_dir is empty
if not defined work_dir (
    set "work_dir=%CD%"
)

:: Validate work-dir
if not exist "%work_dir%" (
    echo Ошибка: Папка %work_dir% не существует
    pause
    exit /b 1
)

:: Ask about non-recursive processing
set /p norecursive="Отключить рекурсивный поиск в подпапках? (y/N): "
if /i "%norecursive%"=="y" (
    set "params=%params% --norecursive"
)

:: Run main.py with explicit work-dir
cd /d "%~dp0"
echo Running: python\python.exe main.py --work-dir "%work_dir%" %params%
python\python.exe main.py --work-dir "%work_dir%" %params%
if %ERRORLEVEL% neq 0 (
    echo Ошибка при выполнении main.py
    pause
    exit /b %ERRORLEVEL%
)
"@
Set-Content -Path $runBat -Value $runContent -Encoding UTF8

Write-Host "Установка завершена. Запускайте run.bat с параметрами, например: run.bat --work-dir E:\test1"