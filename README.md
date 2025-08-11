# MVC
Magic Video Converter | One-Click Video Converter

Автоматизированный инструмент для оптимизации видео: сканирует папку, отрезает фрагменты, тестирует CRF в AV1, выбирает оптимальный по SSIM и размеру, конвертирует полные видео с GPU ускорением. Цель: "1 кнопка — делай хорошо" для больших архивов.

## Установка
1. Скачай репо как zip или git clone.
2. Разархивируй в папку.
3. Для Windows: Запусти install.ps1 (PowerShell).
4. Для Linux/Mac: Запусти install.sh (bash).
5. Скрипт скачает portable Python и FFmpeg (без установки).
6. После установки запусти run.bat (Windows) или ./run.sh (Unix) с параметрами.

## Запуск
- Windows: run.bat --input "./video.mkv" --duration 30 --codec av1_nvenc
- Unix: ./run.sh --input "./video.mkv" --duration 30 --codec av1_nvenc
- Для всех видео в папке: run.bat --all

Параметры:
- --input: Путь к видео (default: all in current dir).
- --duration: Длительность фрагмента для теста (default: 30).
- --codec: Кодек (default: av1_nvenc).
- --all: Обработать все видео в папке.

## Что делает
1. Сканирует папку на видео.
2. Собирает параметры (разрешение, битрейт).
3. Отрезает 30 сек, тестирует CRF (18-30) в AV1.
4. Сравнивает SSIM (>=0.95) и размер (<= оригинал).
5. Конвертирует полное видео в .mp4.
6. Параллельная обработка.

## Будущие фичи
- Upscale и чистка (Hugging Face AI).
- GUI (1 кнопка "делай хорошо").

Лицензия: MIT
