import subprocess
import os

def convert_full_video(input_file, output_file, codec, crf):
    if codec == "av1_nvenc":
        hw_accel_args = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
        preset_args = ["-preset", "p7"]
        crf_param = "-cq"
    elif codec == "libsvtav1":
        hw_accel_args = []
        preset_args = ["-preset", "4"]
        crf_param = "-crf"
    else:
        hw_accel_args = []
        preset_args = ["-preset", "4"]
        crf_param = "-cq"

    convert_command = ["./ffmpeg/ffmpeg"] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec] + preset_args + [crf_param, str(crf), "-an", "-sn", output_file, "-y"]
    subprocess.run(convert_command, check=True)
    print(f"Полное видео конвертировано: {output_file}")
