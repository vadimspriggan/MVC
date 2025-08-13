import os
import glob

def scan_videos(input_file=None, recursive=False):
    video_extensions = [
        '.mp4', '.m4v', '.mkv', '.webm', '.mov', '.qt', '.avi', '.flv', '.f4v',
        '.mpg', '.mpeg', '.vob', '.dvd', '.ts', '.m2t', '.m2ts', '.mts', '.ogg',
        '.ogv', '.mxf', '.nut', '.asf', '.wmv', '.wma', '.gxf', '.dv', '.mj2',
        '.3gp', '.3gpp'
    ]
    if input_file:
        return [input_file] if os.path.isfile(input_file) and os.path.splitext(input_file)[1].lower() in video_extensions else []

    videos = []
    if recursive:
        for ext in video_extensions:
            videos.extend(glob.glob(f"**/*{ext}", recursive=True))
    else:
        videos = [f for f in os.listdir('.') if os.path.isfile(f) and os.path.splitext(f)[1].lower() in video_extensions]
    return videos