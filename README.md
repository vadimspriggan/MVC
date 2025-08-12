# MVC - Magic Video Converter

Automates video conversion by optimizing CRF (Constant Rate Factor) for AV1 encoding, ensuring quality (SSIM >= 0.95) and size (<= original). Goal: "One button to make it great" for large video archives.

## Features
- Scans current directory for videos (.mkv, .mp4, .avi, etc.).
- Extracts metadata (resolution, bitrate).
- Cuts 30-second clips, tests CRF (18-30) in AV1.
- Compares SSIM and size to choose optimal CRF.
- Converts full videos in parallel (GPU-accelerated with av1_nvenc).
- Future: AI upscale and noise reduction for VHS-quality videos.

## Installation
1. Clone or download this repository: `git clone https://github.com/your-username/MVC.git`
2. Windows: Run `install.ps1` in PowerShell.
3. Linux/Mac: Run `install.sh` in bash.
4. The script downloads portable Python and FFmpeg, creating a self-contained folder.

## Usage
- Windows: `run.bat --all` or `run.bat --input "./video.mkv" --duration 30 --codec av1_nvenc`
- Linux/Mac: `./run.sh --all` or `./run.sh --input "./video.mkv" --duration 30 --codec av1_nvenc`

Parameters:
- `--input`: Specific video file (default: all videos in current directory).
- `--duration`: Clip duration for testing (default: 30).
- `--codec`: Codec (default: av1_nvenc).
- `--all`: Process all videos in the directory.

## Output
- Converted videos in `./converted`.
- Temporary files in `./temp` (auto-deleted).

## Future Plans
- AI upscale with Hugging Face.
- GUI for "one-button" operation.

## License
MIT
