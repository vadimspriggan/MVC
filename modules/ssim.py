import subprocess
import os
import re

def calculate_ssim(test_clip, original_clip, temp_dir, crf):
    ssim_file = os.path.join(temp_dir, f"ssim_{crf}.txt")
    ssim_command = ["./ffmpeg/ffmpeg", "-v", "warning", "-i", test_clip, "-i", original_clip, "-lavfi", f"[0:v][1:v]ssim=stats_file={ssim_file}", "-f", "null", "-"]
    ssim_output = subprocess.run(ssim_command, capture_output=True, text=True)
    print(f"SSIM stdout: {ssim_output.stdout}")
    print(f"SSIM stderr: {ssim_output.stderr}")

    if not os.path.exists(ssim_file):
        print(f"WARNING: SSIM файл ({ssim_file}) не создан. Лог FFmpeg: {ssim_output.stderr}")
        return 0.0

    with open(ssim_file, 'r') as f:
        ssim_content = f.read()
    match = re.search(r"All:\s*([0-9\.]+)", ssim_content)
    if match:
        return float(match.group(1))
    print(f"WARNING: SSIM файл ({ssim_file}) пуст или не содержит All: значение.")
    return 0.0
