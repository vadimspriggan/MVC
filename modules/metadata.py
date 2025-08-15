import subprocess
import json
import os
import sys

def get_metadata(video):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffprobe_name = 'ffprobe.exe' if sys.platform.startswith('win') else 'ffprobe'
    ffprobe_path = os.path.join(ffmpeg_dir, ffprobe_name)
    
    if not os.path.isfile(ffprobe_path):
        raise FileNotFoundError(f"ffprobe not found at {ffprobe_path}")

    if not os.path.isfile(video):
        raise FileNotFoundError(f"Video file {video} does not exist")

    video_path = os.path.abspath(video)
    probe_command = [ffprobe_path, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", "-select_streams", "v", video_path]
    print(f"Running ffprobe command: {' '.join(probe_command)}")

    try:
        process = subprocess.run(probe_command, capture_output=True, text=True, encoding='utf-8', check=True)
        probe = json.loads(process.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed for {video}: {e.stderr}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse ffprobe output for {video}: {e}")

    if not probe.get('streams'):
        raise RuntimeError(f"No video streams found in {video}")

    video_stream = probe['streams'][0]
    duration_str = video_stream.get('duration') or probe.get('format', {}).get('duration') or "0"
    try:
        duration_val = float(duration_str)
    except ValueError:
        duration_val = 0.0

    bitrate_str = video_stream.get('bit_rate') or probe.get('format', {}).get('bit_rate') or "0"
    try:
        bitrate_val = int(bitrate_str) // 1000  # Convert to kbps
    except ValueError:
        bitrate_val = 0

    return {
        'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
        'bitrate': bitrate_val,
        'duration': duration_val,
        'codec_name': video_stream.get('codec_name', ''),
        'video_stream_count': len(probe['streams'])
    }