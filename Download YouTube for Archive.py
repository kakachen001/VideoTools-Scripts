import subprocess
import json
import os
import datetime
import time

# ✅ Hardcoded path to your cookies file
COOKIES_FILE = "C:\\www.youtube.com_cookies.txt"

def run_yt_dlp(url, fallback=False):
    command = [
        'yt-dlp',
        '--embed-thumbnail',
        '--write-info-json',
        '--cookies', COOKIES_FILE,
        '--print-json',
        '--merge-output-format', 'mp4',       # ✅ Merge into MP4 after download
        '-o', '%(title)s [%(id)s].%(ext)s',   # ✅ filename with video ID
        '-f', 'bv*+ba/b',                     # ✅ Best video + best audio fallback
        url
    ]

    if fallback:
        command += [
            '--no-check-certificate',
            '--force-generic-extractor'
        ]

    print("Running yt-dlp...")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print("Error downloading video:", result.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Error parsing yt-dlp output.")
        return None

def set_file_timestamp(filepath, upload_date):
    try:
        dt = datetime.datetime.strptime(upload_date, '%Y%m%d')
        mod_time = time.mktime(dt.timetuple())
        os.utime(filepath, (mod_time, mod_time))
        print(f"Set modified time to {dt.date()} for: {filepath}")
    except Exception as e:
        print(f"Failed to update timestamp: {e}")

def download_video(url):
    metadata = run_yt_dlp(url)
    if not metadata:
        print("Trying fallback method...")
        metadata = run_yt_dlp(url, fallback=True)

    if not metadata:
        print("❌ Failed to download the video.")
        return

    filepath = metadata.get('_filename')
    upload_date = metadata.get('upload_date')

    if filepath and upload_date:
        set_file_timestamp(filepath, upload_date)
    else:
        print("❌ Could not extract necessary metadata.")

if __name__ == "__main__":
    while True:
        url = input("Enter YouTube URL (or type 'exit' to quit): ").strip()
        if url.lower() == 'exit':
            print("Goodbye!")
            break
        elif url:
            download_video(url)
