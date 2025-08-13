import subprocess
import math
from modules.metadata import get_metadata
import os
import sys

def cut_clip(video, duration, output_clip):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    log_file = os.path.join(os.getcwd(), f"mvc_logs_{os.path.splitext(os.path.basename(video))[0]}_clip.log")
    
    if not os.path.isfile(ffmpeg_path):
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"Error: ffmpeg not found at {ffmpeg_path}")
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")

    metadata = get_metadata(video)
    start_time = math.floor(metadata['duration'] / 2)
    clip_command = [ffmpeg_path, "-v", "info", "-fflags", "+genpts", "-ss", str(start_time), "-i", video, "-t", str(duration), "-c", "copy", "-vsync", "1", "-an", "-sn", output_clip, "-y"]
    print(f"Running ffmpeg command: {' '.join(clip_command)}")
    
    with open(log_file, 'w', encoding='utf-8') as log:
        process = subprocess.run(clip_command, capture_output=True, text=True, check=True)
        log.write(f"stdout: {process.stdout}\nstderr: {process.stderr}")