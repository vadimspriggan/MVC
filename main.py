import argparse
import os
import sys
import json
import datetime
from concurrent.futures import ThreadPoolExecutor
import shutil

# Ensure parent directory (containing modules) is in sys.path before any imports
program_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(program_dir, 'modules')
print(f"Current working directory: {os.getcwd()}")
print(f"Program directory: {program_dir}")
print(f"Modules directory: {modules_dir}")
print(f"sys.path before: {sys.path}")
if not os.path.isdir(modules_dir):
    raise FileNotFoundError(f"Modules directory {modules_dir} does not exist")
if not os.path.isfile(os.path.join(modules_dir, '__init__.py')):
    raise FileNotFoundError(f"__init__.py not found in {modules_dir}")
if not os.path.isfile(os.path.join(modules_dir, 'scan_videos.py')):
    raise FileNotFoundError(f"scan_videos.py not found in {modules_dir}")

# List contents of modules directory
print(f"Contents of {modules_dir}:")
for item in os.listdir(modules_dir):
    print(f"  - {item} (is_file: {os.path.isfile(os.path.join(modules_dir, item))})")

sys.path.insert(0, program_dir)
print(f"sys.path after: {sys.path}")

# Clear Python cache
def clear_cache():
    cache_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '__pycache__'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules', '__pycache__')
    ]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
            print(f"Cleared cache: {cache_dir}")

clear_cache()

# Import modules after setting sys.path
try:
    from modules.scan_videos import scan_videos
    from modules.metadata import get_metadata
    from modules.remux import remux_video
    from modules.clip import cut_clip
    from modules.encode import test_crf
    from modules.convert import convert_full_video
    from modules.check import check_file
    from modules.log import update_log
except ImportError as e:
    raise ImportError(f"Failed to import modules: {e}")

def main(args):
    print(f"Arguments: work_dir={args.work_dir}, input={args.input}, duration={args.duration}, codec={args.codec}, norecursive={args.norecursive}")

    work_dir = args.work_dir if args.work_dir else os.getcwd()
    if not os.path.isdir(work_dir):
        raise ValueError(f"Working directory {work_dir} does not exist or is not a directory")

    original_dir = os.getcwd()
    os.chdir(work_dir)
    print(f"Changed to working directory: {os.getcwd()}")

    # Scan videos, excluding ./converted
    videos = scan_videos(args.input, not args.norecursive)
    print(f"Найденные видео в {work_dir}: {videos}")

    temp_dir = './temp'
    converted_dir = './converted'
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)

    # Initialize converted_log.json with all videos
    log_file = os.path.join(converted_dir, 'converted_log.json')
    converted_log = {"files": [{"file": v, "status": "pending", "date": datetime.datetime.now().isoformat(), "warnings": [], "errors": [], "check_results": {}} for v in videos]}
    update_log(log_file, converted_log)

    # Filter videos to process (skip done and warning)
    processed_files = {entry['file'] for entry in converted_log['files'] if entry.get('status') in ['done', 'warning']}
    videos_to_process = [v for v in videos if v not in processed_files]
    for v in videos:
        if v in processed_files:
            print(f"Пропуск {v}: Уже обработан (status: done или warning в converted_log.json)")

    # Process videos with 2 workers
    with ThreadPoolExecutor(max_workers=2) as executor:
        for v in videos_to_process:
            executor.submit(process_video, v, args.duration, args.codec, temp_dir, converted_dir, log_file)

    # Cleanup temp
    shutil.rmtree(temp_dir)
    os.chdir(original_dir)

def process_video(video, duration, codec, temp_dir, converted_dir, log_file):
    try:
        update_log(log_file, video=video, status="inprogress", warnings=[], errors=[])

        metadata = get_metadata(video)
        extension = os.path.splitext(video)[1].lower()
        codec_name = metadata.get('codec_name', '').lower()
        if extension == '.mp4' and codec_name in ['av1', 'hevc']:
            print(f"Пропуск {video}: Уже оптимальный формат (.mp4, {codec_name})")
            update_log(log_file, video=video, status="done", warnings=["Already in optimal format"], errors=[])
            return

        print(f"Обработка {video}: Разрешение {metadata['resolution']}, Битрейт {metadata['bitrate']} кбит/с")

        remuxed_file = remux_video(video, temp_dir)
        original_clip = os.path.join(temp_dir, f"original_clip_{os.path.splitext(os.path.basename(video))[0]}.mkv")
        cut_clip(remuxed_file, duration, original_clip)

        original_size_mb = os.path.getsize(video) / 1048576
        warnings = []
        best_crf, best_ssim, closest_size = test_crf(original_clip, duration, codec, temp_dir, original_size_mb, metadata['duration'], warnings)

        output_file = os.path.join(converted_dir, f"{os.path.splitext(os.path.basename(video))[0]}.mp4")
        convert_full_video(remuxed_file, output_file, codec, best_crf)

        # Check the output file
        check_results = check_file(video, output_file, log_file)

        status = "done" if not warnings else "warning"
        update_log(log_file, video=video, status=status, warnings=warnings, errors=[], check_results=check_results)
        print(f"Оптимальный CRF для {video}: {best_crf} (SSIM: {best_ssim:.3f}, Размер: {closest_size:.3f} MB)")

    except Exception as e:
        print(f"Error processing {video}: {str(e)}")
        update_log(log_file, video=video, status="error", warnings=[], errors=[str(e)])
    finally:
        if os.path.exists(remuxed_file) and remuxed_file != video:
            os.remove(remuxed_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Magic Video Converter")
    parser.add_argument('--work-dir', help='Working directory with videos (default: current directory)')
    parser.add_argument('--input', help='Input video file (default: all in work-dir)')
    parser.add_argument('--duration', type=int, default=30, help='Clip duration for testing')
    parser.add_argument('--codec', default='av1_nvenc', help='Codec to use (av1_nvenc, libsvtav1)')
    parser.add_argument('--norecursive', action='store_true', help='Disable recursive subdirectory scan')
    args = parser.parse_args()
    main(args)