import subprocess
import os
import math
from modules.ssim import calculate_ssim
from modules.compare import compare_results, find_best_crf
import sys

def test_crf(original_clip, clip_duration, codec, temp_dir, original_size_mb, original_duration):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")
    if not os.path.isfile(original_clip):
        raise FileNotFoundError(f"Original clip {original_clip} does not exist")

    # Check if av1_nvenc is supported, fallback to libsvtav1 if not
    effective_codec = codec
    if codec == "av1_nvenc":
        try:
            # Test encode a short clip in YUV420P to check av1_nvenc support
            test_command = [ffmpeg_path, "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=30", "-pix_fmt", "yuv420p", "-c:v", "av1_nvenc", "-f", "null", "-"]
            process = subprocess.run(test_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"WARNING: av1_nvenc not supported: {e.stderr}. Falling back to libsvtav1")
            effective_codec = "libsvtav1"

    if effective_codec == "av1_nvenc":
        hw_accel_args = ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
        preset_args = ["-preset", "p7"]
        crf_param = "-cq:v"
    elif effective_codec == "libsvtav1":
        hw_accel_args = []
        preset_args = ["-preset", "7"]
        crf_param = "-crf"
    else:
        hw_accel_args = []
        preset_args = ["-preset", "7"]
        crf_param = "-cq"

    low = 18
    high = 30
    results = {}

    while low <= high:
        mid = math.floor((low + high) / 2)
        if str(mid) in results:
            low = mid + 1
            continue

        test_clip = os.path.join(temp_dir, f"test_clip_crf{mid}.mp4")
        log_file = os.path.join(os.getcwd(), f"mvc_logs_{os.path.splitext(os.path.basename(original_clip))[0]}_encode_crf{mid}.log")
        
        # Two-pass encoding
        pass1_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-fflags", "+genpts", "-i", original_clip, "-c:v", effective_codec, "-vsync", "1"] + preset_args + [crf_param, str(mid), "-pass", "1", "-an", "-sn", "-f", "null", os.devnull]
        pass2_command = [ffmpeg_path] + hw_accel_args + ["-v", "error", "-fflags", "+genpts", "-i", original_clip, "-c:v", effective_codec, "-vsync", "1"] + preset_args + [crf_param, str(mid), "-pass", "2", "-an", "-sn", test_clip, "-y"]
        
        print(f"Running ffmpeg two-pass command (pass 1): {' '.join(pass1_command)}")
        try:
            process = subprocess.run(pass1_command, capture_output=True, text=True, check=True)
            with open(log_file, 'w', encoding='utf-8') as log:
                log.write(f"Pass 1 stdout: {process.stdout}\nPass 1 stderr: {process.stderr}")
        except subprocess.CalledProcessError as e:
            with open(log_file, 'w', encoding='utf-8') as log:
                log.write(f"Pass 1 failed: stdout: {e.stdout}\nstderr: {e.stderr}")
            print(f"WARNING: Pass 1 failed for CRF {mid}: {e.stderr}")
            results[str(mid)] = {'PredictedSize': 0, 'SSIM': 0.0}
            high = mid - 1
            continue

        print(f"Running ffmpeg two-pass command (pass 2): {' '.join(pass2_command)}")
        try:
            process = subprocess.run(pass2_command, capture_output=True, text=True, check=True)
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Pass 2 stdout: {process.stdout}\nPass 2 stderr: {process.stderr}")
        except subprocess.CalledProcessError as e:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Pass 2 failed: stdout: {e.stdout}\nstderr: {e.stderr}")
            print(f"WARNING: Pass 2 failed for CRF {mid}: {e.stderr}")
            results[str(mid)] = {'PredictedSize': 0, 'SSIM': 0.0}
            high = mid - 1
            continue

        if not os.path.exists(test_clip) or os.path.getsize(test_clip) == 0:
            print(f"WARNING: Клип для CRF {mid} не создан. Пропускаю.")
            results[str(mid)] = {'PredictedSize': 0, 'SSIM': 0.0}
            high = mid - 1
            continue

        test_size_mb = os.path.getsize(test_clip) / 1048576
        predicted_size_mb = test_size_mb * (original_duration / clip_duration)
        ssim = calculate_ssim(test_clip, original_clip, temp_dir, mid)

        print(f"CRF {mid}: clip {test_size_mb:.3f} MB | predicted {predicted_size_mb:.3f} MB | SSIM {ssim:.3f}")
        results[str(mid)] = {'PredictedSize': predicted_size_mb, 'SSIM': ssim}

        is_acceptable, _ = compare_results(ssim, predicted_size_mb, original_size_mb)
        if is_acceptable:
            high = mid - 1
        else:
            low = mid + 1

    return find_best_crf(results, original_size_mb)