import subprocess
import os
import sys

def convert_full_video(input_file, output_file, codec, crf, upscale=False):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    log_file = os.path.join(os.getcwd(), f"mvc_logs_{os.path.splitext(os.path.basename(input_file))[0]}_convert.log")
    
    if not os.path.isfile(ffmpeg_path):
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"Error: ffmpeg not found at {ffmpeg_path}")
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")

    if not os.path.isfile(input_file):
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"Error: Input file {input_file} does not exist")
        raise FileNotFoundError(f"Input file {input_file} does not exist")

    # Use same name as input file (without extension) for output
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(os.getcwd(), 'converted', f"{base_name}.mp4")

    if codec == "av1_nvenc":
        hw_accel_args = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
        preset_args = ["-preset", "p7"]
        crf_param = "-cq:v"
    elif codec == "libsvtav1":
        hw_accel_args = []
        preset_args = ["-preset", "7"]
        crf_param = "-crf"
    else:
        hw_accel_args = []
        preset_args = ["-preset", "7"]
        crf_param = "-cq"

    # Two-pass encoding
    pass1_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "1", "-map", "0", "-c:a", "copy", "-c:s", "mov_text", "-f", "mp4", os.devnull]
    pass2_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "2", "-map", "0", "-c:a", "copy", "-c:s", "mov_text", output_file, "-y"]
    
    if upscale:
        pass1_command += ["-vf", "scale=4k:-1"]
        pass2_command += ["-vf", "scale=4k:-1"]

    print(f"Running ffmpeg two-pass command (pass 1): {' '.join(pass1_command)}")
    try:
        process = subprocess.run(pass1_command, capture_output=True, text=True, check=True)
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"Pass 1 stdout: {process.stdout}\nPass 1 stderr: {process.stderr}")
    except subprocess.CalledProcessError as e:
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"Pass 1 failed: stdout: {e.stdout}\nstderr: {e.stderr}")
        # Try without subtitles if mov_text fails
        print(f"WARNING: Pass 1 failed: {e.stderr}. Retrying without subtitles.")
        pass1_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "1", "-map", "0:v", "-map", "0:a", "-c:a", "copy", "-sn", "-f", "mp4", os.devnull]
        pass2_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "2", "-map", "0:v", "-map", "0:a", "-c:a", "copy", "-sn", output_file, "-y"]
        if upscale:
            pass1_command += ["-vf", "scale=4k:-1"]
            pass2_command += ["-vf", "scale=4k:-1"]
        print(f"Retrying ffmpeg two-pass command (pass 1, no subtitles): {' '.join(pass1_command)}")
        try:
            process = subprocess.run(pass1_command, capture_output=True, text=True, check=True)
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Retry Pass 1 (no subtitles) stdout: {process.stdout}\nRetry Pass 1 stderr: {process.stderr}")
        except subprocess.CalledProcessError as e:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Retry Pass 1 (no subtitles) failed: stdout: {e.stdout}\nstderr: {e.stderr}")
            raise RuntimeError(f"ffmpeg pass 1 failed for {input_file} even without subtitles: {e.stderr}")

    print(f"Running ffmpeg two-pass command (pass 2): {' '.join(pass2_command)}")
    try:
        process = subprocess.run(pass2_command, capture_output=True, text=True, check=True)
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Pass 2 stdout: {process.stdout}\nPass 2 stderr: {process.stderr}")
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Pass 2 failed: stdout: {e.stdout}\nstderr: {e.stderr}")
        print(f"WARNING: Pass 2 failed: {e.stderr}. Retrying without subtitles.")
        print(f"Retrying ffmpeg two-pass command (pass 2, no subtitles): {' '.join(pass2_command)}")
        try:
            process = subprocess.run(pass2_command, capture_output=True, text=True, check=True)
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Retry Pass 2 (no subtitles) stdout: {process.stdout}\nRetry Pass 2 stderr: {process.stderr}")
        except subprocess.CalledProcessError as e:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Retry Pass 2 (no subtitles) failed: stdout: {e.stdout}\nstderr: {e.stderr}")
            raise RuntimeError(f"ffmpeg pass 2 failed for {input_file} even without subtitles: {e.stderr}")

    print(f"Полное видео конвертировано: {output_file}")