import subprocess
import json
import os
import sys
from modules.log import update_log

def check_file(original_file, final_file, log_file):
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
    ffprobe_name = 'ffprobe.exe' if sys.platform.startswith('win') else 'ffprobe'
    ffprobe_path = os.path.join(ffmpeg_dir, ffprobe_name)
    
    def get_ffprobe_info(file):
        cmd = [ffprobe_path, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", file]
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            return json.loads(process.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"WARNING: ffprobe failed for {file}: {str(e)}")
            return None

    original_info = get_ffprobe_info(original_file)
    final_info = get_ffprobe_info(final_file)

    check_results = {}

    # 1. Size of original file
    original_size_mb = os.path.getsize(original_file) / 1048576
    check_results['original_size_mb'] = round(original_size_mb, 3)

    # 2. Size of final file
    final_size_mb = os.path.getsize(final_file) / 1048576 if os.path.exists(final_file) else 0
    check_results['final_size_mb'] = round(final_size_mb, 3)

    # 3. Compare sizes
    size_ratio = final_size_mb / original_size_mb if original_size_mb > 0 else 0
    if 0.8 <= size_ratio <= 1.1:
        check_results['size_comparison'] = "OK"
    elif size_ratio < 0.8:
        check_results['size_comparison'] = "squeezed"
    else:
        check_results['size_comparison'] = "inflated"

    # 4. Resolution, FPS, bitrate of final file
    if final_info and final_info.get('streams'):
        final_video_stream = next((s for s in final_info['streams'] if s['codec_type'] == 'video'), {})
        check_results['final_resolution'] = f"{final_video_stream.get('width', 0)}x{final_video_stream.get('height', 0)}"
        check_results['final_fps'] = eval(final_video_stream.get('r_frame_rate', '0/1')) if '/' in final_video_stream.get('r_frame_rate', '0/1') else 0
        check_results['final_bitrate'] = int(final_video_stream.get('bit_rate', 0)) // 1000 if final_video_stream.get('bit_rate') else 0
    else:
        check_results['final_resolution'] = "N/A"
        check_results['final_fps'] = 0
        check_results['final_bitrate'] = 0

    # 5. Resolution, FPS, bitrate of original file
    if original_info and original_info.get('streams'):
        original_video_stream = next((s for s in original_info['streams'] if s['codec_type'] == 'video'), {})
        check_results['original_resolution'] = f"{original_video_stream.get('width', 0)}x{original_video_stream.get('height', 0)}"
        check_results['original_fps'] = eval(original_video_stream.get('r_frame_rate', '0/1')) if '/' in original_video_stream.get('r_frame_rate', '0/1') else 0
        check_results['original_bitrate'] = int(original_video_stream.get('bit_rate', 0)) // 1000 if original_video_stream.get('bit_rate') else 0
    else:
        check_results['original_resolution'] = "N/A"
        check_results['original_fps'] = 0
        check_results['original_bitrate'] = 0

    # 6. Compare resolution
    if check_results['original_resolution'] == check_results['final_resolution']:
        check_results['resolution_comparison'] = "OK"
    else:
        original_width, original_height = map(int, check_results['original_resolution'].split('x')) if check_results['original_resolution'] != "N/A" else (0, 0)
        final_width, final_height = map(int, check_results['final_resolution'].split('x')) if check_results['final_resolution'] != "N/A" else (0, 0)
        if original_width and final_width:
            width_diff = abs(original_width - final_width) / original_width
            height_diff = abs(original_height - final_height) / original_height
            check_results['resolution_comparison'] = "OK" if max(width_diff, height_diff) <= 0.01 else "doesn't match"
        else:
            check_results['resolution_comparison'] = "doesn't match"

    # 7. Number of audio streams, subtitles in final file
    if final_info:
        final_audio_streams = len([s for s in final_info.get('streams', []) if s['codec_type'] == 'audio'])
        final_subtitle_streams = len([s for s in final_info.get('streams', []) if s['codec_type'] == 'subtitle'])
        check_results['final_audio_streams'] = final_audio_streams
        check_results['final_subtitles'] = final_subtitle_streams
    else:
        check_results['final_audio_streams'] = 0
        check_results['final_subtitles'] = 0

    # 8. Number of audio streams, audio channels, subtitles in original file
    if original_info:
        original_audio_streams = len([s for s in original_info.get('streams', []) if s['codec_type'] == 'audio'])
        original_audio_channels = max([s.get('channels', 0) for s in original_info.get('streams', []) if s['codec_type'] == 'audio'], default=0)
        original_subtitle_streams = len([s for s in original_info.get('streams', []) if s['codec_type'] == 'subtitle'])
        check_results['original_audio_streams'] = original_audio_streams
        check_results['original_audio_channels'] = original_audio_channels
        check_results['original_subtitles'] = original_subtitle_streams
    else:
        check_results['original_audio_streams'] = 0
        check_results['original_audio_channels'] = 0
        check_results['original_subtitles'] = 0

    # 9. Compare audio/subtitles
    if (check_results['original_audio_streams'] == check_results['final_audio_streams'] and
        check_results['original_subtitles'] == check_results['final_subtitles']):
        check_results['audio_sub_comparison'] = "OK"
    else:
        check_results['audio_sub_comparison'] = "doesn't match"

    # 10. Container and encoding codec of final file
    if final_info:
        check_results['final_container'] = final_info.get('format', {}).get('format_name', 'N/A')
        check_results['final_codec'] = next((s.get('codec_name', 'N/A') for s in final_info.get('streams', []) if s['codec_type'] == 'video'), 'N/A')
    else:
        check_results['final_container'] = "N/A"
        check_results['final_codec'] = "N/A"

    # Update log with check_results
    update_log(log_file, video=original_file, check_results=check_results)

    return check_results