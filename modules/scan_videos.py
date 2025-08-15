import os
import sys

def scan_videos(input_file, recursive):
    videos = []
    extensions = ['.mkv', '.avi', '.mp4', '.mov', '.flv', '.wmv', '.vob']

    if input_file:
        if os.path.isfile(input_file):
            videos.append(input_file)
    else:
        work_dir = os.getcwd()
        for root, dirs, files in os.walk(work_dir):
            # Exclude ./converted folder
            if recursive and 'converted' in dirs:
                dirs.remove('converted')
            for file in files:
                if os.path.splitext(file)[1].lower() in extensions:
                    videos.append(os.path.relpath(os.path.join(root, file), work_dir))

    return videos