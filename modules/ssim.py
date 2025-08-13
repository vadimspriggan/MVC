import subprocess
import os
import re
import sys

def calculate_ssim(test_clip, original_clip, temp_dir, crf):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    ssim_file = os.path.join(temp_dir, f"ssim_{crf}.txt")
    ssim_path = f"./temp/ssim_{crf}.txt"
    log_file = os.path.join(os.getcwd(), f"mvc_logs_{os.path.splitext(os.path.basename(original_clip))[0]}_ssim_crf{crf}.log")
    ssim_command = [ffmpeg_path, "-v", "warning", "-i", test_clip, "-i", original_clip, "-lavfi", f"[0:v][1:v]ssim=stats_file={ssim_path}", "-f", "null", "-"]
    print(f"Running ffmpeg command: {' '.join(ssim_command)}")
    with open(log_file, 'w', encoding='utf-8') as log:
        process = subprocess.run(ssim_command, capture_output=True, text=True)
        log.write(f"stdout: {process.stdout}\nstderr: {process.stderr}")
        print(f"SSIM stdout: {process.stdout}")
        print(f"SSIM stderr: {process.stderr}")

    if not os.path.exists(ssim_file):
        print(f"WARNING: SSIM файл ({ssim_file}) не создан. Лог FFmpeg: {process.stderr}")
        return 0.0

    with open(ssim_file, 'r') as f:
        ssim_content = f.read()
    match = re.search(r"All:\s*([0-9\.]+)", ssim_content)
    if match:
        return float(match.group(1))
    print(f"WARNING: SSIM файл ({ssim_file}) пуст или не содержит All: значение.")
    return 0.0