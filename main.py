import argparse
import subprocess
import os
import json
import math
import re
import multiprocessing as mp

def main(args):
    # Сканирование текущей папки на видео
    video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.wmv']
    videos = [f for f in os.listdir('.') if os.path.isfile(f) and os.path.splitext(f)[1].lower() in video_extensions]
    print(f"Найденные видео: {videos}")

    # Создать temp директорию
    temp_dir = './temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Параллельная обработка видео
    with mp.Pool(processes=os.cpu_count()) as pool:
        pool.starmap(process_video, [(video, args.duration, args.codec, temp_dir) for video in videos])

    # Очистка temp
    import shutil
    shutil.rmtree(temp_dir)

def process_video(input_file, clip_duration, codec, temp_dir):
    # Получить параметры видео
    probe_command = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-select_streams", "v", input_file]
    probe_output = subprocess.check_output(probe_command).decode('utf-8')
    probe = json.loads(probe_output)
    video_stream = probe['streams'][0]
    resolution = f"{video_stream['width']}x{video_stream['height']}"
    bit_rate = int(video_stream['bit_rate']) if 'bit_rate' in video_stream else 0
    print(f"Видео {input_file}: Разрешение {resolution}, Битрейт {bit_rate}")

    # Отрезать 30 секунд
    original_clip = os.path.join(temp_dir, "original_clip.mkv")
    clip_command = ["ffmpeg", "-v", "info", "-ss", str(math.floor(float(probe['streams'][0]['duration']) / 2)), "-i", input_file, "-t", str(clip_duration), "-c", "copy", "-an", "-sn", original_clip, "-y"]
    subprocess.run(clip_command, check=True)

    original_size_mb = os.path.getsize(input_file) / 1048576

    # Параметры кодека
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
        encode_command = ["ffmpeg"] + hw_accel_args + ["-v", "error", "-i", original_clip, "-c:v", codec] + preset_args + [crf_param, str(mid), "-an", "-sn", test_clip, "-y"]
        subprocess.run(encode_command, check=True)

        if not os.path.exists(test_clip) or os.path.getsize(test_clip) == 0:
            print(f"WARNING: Клип для CRF {mid} не создан. Пропускаю.")
            results[str(mid)] = {'PredictedSize': 0, 'SSIM': 0.0}
            high = mid - 1
            continue

        test_size_mb = os.path.getsize(test_clip) / 1048576
        predicted_size_mb = test_size_mb * (full_duration / clip_duration)

        # ffprobe for compatibility
        test_probe_command = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", test_clip]
        test_probe_output = subprocess.check_output(test_probe_command).decode('utf-8')
        test_probe = json.loads(test_probe_output)
        orig_probe_command = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", original_clip]
        orig_probe_output = subprocess.check_output(orig_probe_command).decode('utf-8')
        orig_probe = json.loads(orig_probe_output)
        test_video = next((stream for stream in test_probe['streams'] if stream['codec_type'] == "video"), None)
        orig_video = next((stream for stream in orig_probe['streams'] if stream['codec_type'] == "video"), None)

        if not test_video or not orig_video or test_video['width'] != orig_video['width'] or test_video['height'] != orig_video['height'] or test_video['pix_fmt'] != orig_video['pix_fmt'] or test_video['r_frame_rate'] != orig_video['r_frame_rate']:
            print(f"WARNING: Несовместимые параметры видео для CRF {mid}. Пропускаю SSIM.")
            ssim = 0.0
        else:
            ssim_file = os.path.join(temp_dir, f"ssim_{mid}.txt")
            ssim_command = ["ffmpeg", "-v", "warning", "-i", test_clip, "-i", original_clip, "-lavfi", f"[0:v][1:v]ssim=stats_file={ssim_file}", "-f", "null", "-"]
            ssim_output = subprocess.run(ssim_command, capture_output=True, text=True)
            print(f"SSIM stdout: {ssim_output.stdout}")
            print(f"SSIM stderr: {ssim_output.stderr}")
            if os.path.exists(ssim_file):
                with open(ssim_file, 'r') as f:
                    ssim_content = f.read()
                match = re.search(r"All:\s*([0-9\.]+)", ssim_content)
                if match:
                    ssim = float(match.group(1))
                else:
                    print(f"WARNING: SSIM файл ({ssim_file}) пуст или не содержит All: значение.")
                    ssim = 0.0
            else:
                print(f"WARNING: SSIM файл ({ssim_file}) не создан. Лог FFmpeg: {ssim_output.stderr}")
                ssim = 0.0

        print(f"CRF {mid}: clip {round(test_size_mb, 3)} MB | predicted {round(predicted_size_mb, 3)} MB | SSIM {round(ssim, 3)}")
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
        else:
            best_ssim = results[str(best_crf)]['SSIM']
            closest_size = results[str(best_crf)]['PredictedSize']
            print(f"Выбран CRF с минимальным размером: {best_crf} (SSIM: {round(best_ssim, 3)}, Размер: {round(closest_size, 3)} MB)")
    else:
        print(f"Оптимальный CRF: {best_crf} (SSIM: {round(best_ssim, 3)}, Размер: {round(closest_size, 3)} MB)")

    # Конвертация полного видео
    output_file = os.path.splitext(input_file)[0] + '_converted.mp4'
    convert_command = ["ffmpeg"] + hw_accel_args + ["-v", "error", "-i", input_file, "-c:v", codec] + preset_args + [crf_param, str(best_crf), "-an", "-sn", output_file, "-y"]
    subprocess.run(convert_command, check=True)
    print(f"Полное видео конвертировано: {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Magic Video Converter")
    parser.add_argument('--input', default='./Ангел А.mkv', help='Input video file')
    parser.add_argument('--duration', type=int, default=30, help='Clip duration for testing')
    parser.add_argument('--codec', default='av1_nvenc', help='Codec to use')
    args = parser.parse_args()
    main(args)
