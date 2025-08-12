import os

def scan_videos(input_file=None):
    video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.wmv']
    if input_file:
        return [input_file] if os.path.isfile(input_file) and os.path.splitext(input_file)[1].lower() in video_extensions else []
    return [f for f in os.listdir('.') if os.path.isfile(f) and os.path.splitext(f)[1].lower() in video_extensions]
