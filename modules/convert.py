import subprocess
import os
import sys
import glob

def convert_full_video(input_file, output_file, codec, crf, upscale=False):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")

    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist")

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(os.getcwd(), 'converted', f"{base_name}.mp4")
    passlog_prefix = os.path.join(os.getcwd(), 'temp', f"ffmpeg2pass_convert_{base_name}")

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

    pass1_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "1", "-passlogfile", passlog_prefix, "-map", "0", "-c:a", "copy", "-c:s", "mov_text", "-f", "mp4", os.devnull]
    pass2_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "2", "-passlogfile", passlog_prefix, "-map", "0", "-c:a", "copy", "-c:s", "mov_text", output_file, "-y"]
    
    if upscale:
        pass1_command += ["-vf", "scale=4k:-1"]
        pass2_command += ["-vf", "scale=4k:-1"]

    print(f"Running ffmpeg two-pass command (pass 1): {' '.join(pass1_command)}")
    try:
        process = subprocess.run(pass1_command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Pass 1 failed: {e.stderr}. Retrying without subtitles.")
        pass1_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "1", "-passlogfile", passlog_prefix, "-map", "0:v", "-map", "0:a", "-c:a", "copy", "-sn", "-f", "mp4", os.devnull]
        pass2_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec, "-vsync", "1"] + preset_args + [crf_param, str(crf), "-pass", "2", "-passlogfile", passlog_prefix, "-map", "0:v", "-map", "0:a", "-c:a", "copy", "-sn", output_file, "-y"]
        if upscale:
            pass1_command += ["-vf", "scale=4k:-1"]
            pass2_command += ["-vf", "scale=4k:-1"]
        print(f"Retrying ffmpeg two-pass command (pass 1, no subtitles): {' '.join(pass1_command)}")
        try:
            process = subprocess.run(pass1_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg pass 1 failed for {input_file} even without subtitles: {e.stderr}")

    print(f"Running ffmpeg two-pass command (pass 2): {' '.join(pass2_command)}")
    try:
        process = subprocess.run(pass2_command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Pass 2 failed: {e.stderr}. Retrying without subtitles.")
        print(f"Retrying ffmpeg two-pass command (pass 2, no subtitles): {' '.join(pass2_command)}")
        try:
            process = subprocess.run(pass2_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg pass 2 failed for {input_file} even without subtitles: {e.stderr}")
    finally:
        # Clean up ffmpeg2pass logs
        for log_file in glob.glob(f"{passlog_prefix}*.log"):
            try:
                os.remove(log_file)
            except OSError:
                pass

    print(f"Полное видео конвертировано: {output_file}")