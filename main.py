import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from modules.scan_videos import scan_videos
from modules.metadata import get_metadata
from modules.clip import cut_clip
from modules.encode import test_crf
from modules.ssim import calculate_ssim
from modules.convert import convert_full_video

def main(args):
    # Scan videos
    videos = scan_videos(args.input)
    print(f"Найденные видео: {videos}")

    # Create temp and converted directories
    temp_dir = './temp'
    converted_dir = './converted'
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)

    # Parallel processing
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(lambda v: process_video(v, args.duration, args.codec, temp_dir, converted_dir), videos)

    # Cleanup temp
    import shutil
    shutil.rmtree(temp_dir)

def process_video(video, duration, codec, temp_dir, converted_dir):
    # Get metadata
    metadata = get_metadata(video)
    print(f"Видео {video}: Разрешение {metadata['resolution']}, Битрейт {metadata['bitrate']}")

    # Cut clip
    original_clip = os.path.join(temp_dir, "original_clip.mkv")
    cut_clip(video, duration, original_clip)

    # Test CRF values
    original_size_mb = os.path.getsize(video) / 1048576
    best_crf, best_ssim, closest_size = test_crf(original_clip, duration, codec, temp_dir, original_size_mb)

    # Convert full video
    output_file = os.path.join(converted_dir, os.path.splitext(os.path.basename(video))[0] + '_converted.mp4')
    convert_full_video(video, output_file, codec, best_crf)

    print(f"Оптимальный CRF для {video}: {best_crf} (SSIM: {best_ssim:.3f}, Размер: {closest_size:.3f} MB)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Magic Video Converter")
    parser.add_argument('--input', help='Input video file (default: all in directory)')
    parser.add_argument('--duration', type=int, default=30, help='Clip duration for testing')
    parser.add_argument('--codec', default='av1_nvenc', help='Codec to use (av1_nvenc, libsvtav1)')
    args = parser.parse_args()
    main(args)
