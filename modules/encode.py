import subprocess
import os
import math
from modules.ssim import calculate_ssim

def test_crf(original_clip, clip_duration, codec, temp_dir, original_size_mb):
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

    low = 18
    high = 30
    best_crf = None
    best_ssim = 0.0
    closest_size = 0.0
    results = {}

    while low <= high:
        mid = math.floor((low + high) / 2)
        if str(mid) in results:
            low = mid + 1
            continue

        test_clip = os.path.join(temp_dir, f"test_clip_crf{mid}.mp4")
        encode_command = ["./ffmpeg/ffmpeg"] + hw_accel_args + ["-v", "error", "-i", original_clip, "-c:v", codec] + preset_args + [crf_param, str(mid), "-an", "-sn", test_clip, "-y"]
        subprocess.run(encode_command, check=True)

        if not os.path.exists(test_clip) or os.path.getsize(test_clip) == 0:
            print(f"WARNING: Клип для CRF {mid} не создан. Пропускаю.")
            results[str(mid)] = {'PredictedSize': 0, 'SSIM': 0.0}
            high = mid - 1
            continue

        test_size_mb = os.path.getsize(test_clip) / 1048576
        predicted_size_mb = test_size_mb * (metadata['duration'] / clip_duration)
        ssim = calculate_ssim(test_clip, original_clip, temp_dir, mid)

        print(f"CRF {mid}: clip {test_size_mb:.3f} MB | predicted {predicted_size_mb:.3f} MB | SSIM {ssim:.3f}")
        results[str(mid)] = {'PredictedSize': predicted_size_mb, 'SSIM': ssim}

        if ssim >= 0.95 and predicted_size_mb <= original_size_mb:
            best_crf = mid
            best_ssim = ssim
            closest_size = predicted_size_mb
            high = mid - 1
        else:
            low = mid + 1

    if best_crf is None:
        best_crf = min((k for k, v in results.items() if v['PredictedSize'] > 0), key=lambda k: results[k]['PredictedSize'], default=30)
        if best_crf == 30:
            print("WARNING: Нет подходящего CRF. Fallback на CRF=30.")
        best_ssim = results[str(best_crf)]['SSIM']
        closest_size = results[str(best_crf)]['PredictedSize']
    return best_crf, best_ssim, closest_size
