import subprocess
import os
import sys

def remux_video(video, temp_dir):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffmpeg_name = 'ffmpeg.exe' if sys.platform.startswith('win') else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_name)
    
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg not found at {ffmpeg_path}")

    temp_remuxed = os.path.join(temp_dir, f"remuxed_{os.path.splitext(os.path.basename(video))[0]}.mkv")
    os.makedirs(os.path.dirname(temp_remuxed), exist_ok=True)
    remux_command = [ffmpeg_path, "-v", "error", "-i", video, "-c", "copy", "-y", temp_remuxed]
    print(f"Running ffmpeg remux command: {' '.join(remux_command)}")
    
    try:
        process = subprocess.run(remux_command, capture_output=True, text=True, encoding='utf-8', check=True)
        return temp_remuxed
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Remux failed for {video}: {e.stderr}. Proceeding with original file.")
        return video