import subprocess
import json

def get_metadata(video):
    probe_command = ["./ffmpeg/ffmpeg", "-v", "error", "-print_format", "json", "-show_streams", "-select_streams", "v", video]
    probe_output = subprocess.check_output(probe_command).decode('utf-8')
    probe = json.loads(probe_output)
    video_stream = probe['streams'][0]
    return {
        'resolution': f"{video_stream['width']}x{video_stream['height']}",
        'bitrate': int(video_stream.get('bit_rate', 0)),
        'duration': float(video_stream['duration'])
    }
