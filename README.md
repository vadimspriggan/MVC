# Magic Video Converter (MVC) ![Project Cover](./MVC.png)

Automates video conversion by optimizing CRF (Constant Rate Factor) for AV1 encoding, ensuring quality (SSIM >= 0.95) and size (<= original). Goal: "One button to make it great" for large video archives.

Magic Video Converter (MVC) is a Python-based tool for converting videos to AV1 format using FFmpeg, optimizing for quality (SSIM >= 0.95) and size (≤ original size * 1.05). It supports NVIDIA GPU acceleration (av1_nvenc) with fallback to libsvtav1, two-pass encoding, and preserves all audio tracks and subtitles.

## Features
- Converts videos to `.mp4` with AV1 codec (`av1_nvenc` or `libsvtav1`).
- Optimizes CRF (Constant Rate Factor) based on SSIM and file size.
- Supports two-pass encoding for better quality.
- Preserves all audio tracks and subtitles from the source.
- Skips already optimized `.mp4` files with AV1 or HEVC codecs.
- Recursive video scanning by default (optional `--norecursive` flag).
- Handles Cyrillic filenames and paths.

## Requirements
- **Python 3.12**: Embedded Python is automatically downloaded and installed.
- **FFmpeg**: Uses BtbN builds (`ffmpeg-master-latest-win64-gpl.zip`) with `libvmaf` for SSIM, `av1_nvenc`, and `libsvtav1`.
- **Windows**: Tested on Windows (x86_64). Linux/Mac support possible with minor adjustments.
- **NVIDIA GPU**: Optional for `av1_nvenc` acceleration.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/vadimspriggan/MVC.git
   cd MVC

## Output
- Converted videos in `./converted`.
- Temporary files in `./temp` (auto-deleted).

## Future Plans
- AI upscale with Hugging Face.
- GUI for "one-button" operation.

## License
GNU GPL v3

