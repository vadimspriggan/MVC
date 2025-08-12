import subprocess
import math

def cut_clip(video, duration, output_clip):
    metadata = get_metadata(video)  # From metadata module
    start_time = math.floor(metadata['duration'] / 2)
    clip_command = ["./ffmpeg/ffmpeg", "-v", "info", "-ss", str(start_time), "-i", video, "-t", str(duration), "-c", "copy", "-an", "-sn", output_clip, "-y"]
    subprocess.run(clip_command, check=True)
