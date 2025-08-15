import subprocess
import math
import os
import sys
from modules.metadata import get_metadata

def cut_clip(video, duration, output_clip):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")

    metadata = get_metadata(video)
    start_time = math.floor(metadata['duration'] / 2)
    clip_command = [ffmpeg_path, "-v", "info", "-fflags", "+genpts", "-ss", str(start_time), "-i", video, "-t", str(duration), "-c", "copy", "-vsync", "1", "-an", "-sn", output_clip, "-y"]
    print(f"Running ffmpeg clip command: {' '.join(clip_command)}")
    
    try:
        process = subprocess.run(clip_command, capture_output=True, text=True, encoding='utf-8', check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg clip failed for {video}: {e.stderr}")