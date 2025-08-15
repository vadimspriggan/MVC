import json
import os
import datetime

def update_log(log_file, converted_log=None, video=None, status=None, warnings=None, errors=None, check_results=None):
    if converted_log is not None:
        # Initialize or overwrite log
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(converted_log, f, indent=4, ensure_ascii=False)
    elif video is not None:
        try:
            # Update existing log
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                log_data = {"files": []}

            # Find or create entry for video
            entry_found = False
            for entry in log_data['files']:
                if entry['file'] == video:
                    entry_found = True
                    if status is not None:
                        entry['status'] = status
                    entry['date'] = datetime.datetime.now().isoformat()
                    if warnings is not None:
                        entry['warnings'] = warnings
                    if errors is not None:
                        entry['errors'] = errors
                    if check_results is not None:
                        entry['check_results'] = check_results
                    break
            if not entry_found:
                log_data['files'].append({
                    'file': video,
                    'status': status,
                    'date': datetime.datetime.now().isoformat(),
                    'warnings': warnings or [],
                    'errors': errors or [],
                    'check_results': check_results or {}
                })

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error updating log for {video}: {str(e)}")