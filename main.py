import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor

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

# Import modules after setting sys.path
try:
    from modules.scan_videos import scan_videos
    from modules.metadata import get_metadata
    from modules.clip import cut_clip
    from modules.encode import test_crf
    from modules.convert import convert_full_video
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

    videos = scan_videos(args.input, not args.norecursive)
    print(f"Найденные видео в {work_dir}: {videos}")

    temp_dir = './temp'
    converted_dir = './converted'
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(lambda v: process_video(v, args.duration, args.codec, temp_dir, converted_dir), videos)

    import shutil
    shutil.rmtree(temp_dir)
    os.chdir(original_dir)

def process_video(video, duration, codec, temp_dir, converted_dir):
    metadata = get_metadata(video)
    extension = os.path.splitext(video)[1].lower()
    codec_name = metadata.get('codec_name', '').lower()
    if extension == '.mp4' and codec_name in ['av1', 'hevc']:
        print(f"Пропуск {video}: Уже оптимальный формат (.mp4, {codec_name})")
        return

    print(f"Обработка {video}: Разрешение {metadata['resolution']}, Битрейт {metadata['bitrate']} кбит/с")

    original_clip = os.path.join(temp_dir, "original_clip.mkv")
    cut_clip(video, duration, original_clip)

    original_size_mb = os.path.getsize(video) / 1048576
    best_crf, best_ssim, closest_size = test_crf(original_clip, duration, codec, temp_dir, original_size_mb, metadata['duration'])

    output_file = os.path.join(converted_dir, f"{os.path.splitext(os.path.basename(video))[0]}.mp4")
    convert_full_video(video, output_file, codec, best_crf)

    print(f"Оптимальный CRF для {video}: {best_crf} (SSIM: {best_ssim:.3f}, Размер: {closest_size:.3f} MB)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Magic Video Converter")
    parser.add_argument('--work-dir', help='Working directory with videos (default: current directory)')
    parser.add_argument('--input', help='Input video file (default: all in work-dir)')
    parser.add_argument('--duration', type=int, default=30, help='Clip duration for testing')
    parser.add_argument('--codec', default='av1_nvenc', help='Codec to use (av1_nvenc, libsvtav1)')
    parser.add_argument('--norecursive', action='store_true', help='Disable recursive subdirectory scan')
    args = parser.parse_args()
    main(args)