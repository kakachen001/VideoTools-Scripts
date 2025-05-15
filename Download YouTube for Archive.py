import subprocess
import json
import os
import datetime
import time

DEFAULT_COOKIES_FILE = "C:\\www.youtube.com_cookies.txt" # ✅ Hardcoded path to your cookies file
ARCHIVE_FILE = "archive.txt" # ✅ Archive file to avoid re-downloading

def prompt_for_cookies():
    print("[!] Cookies file not found or empty.")
    while True:
        path = input("Please enter the full path to your cookies file (or leave blank to skip): ").strip()
        if path == "":
            return None
        elif os.path.isfile(path) and os.path.getsize(path) > 0:
            print(f"[+] Using cookies file: {path}")
            return path
        else:
            print("[!] Invalid file. Try again.")

def run_yt_dlp(url, use_cookies=False, cookies_file=None, fallback=False):
    command = [
        'yt-dlp',
        '--embed-thumbnail',
        '--write-info-json',
        '--download-archive', ARCHIVE_FILE, # ✅ Archive file to avoid re-downloading
        '--print-json',
        '--merge-output-format', 'mp4', # ✅ Merge into MP4 after download
        '-o', '%(title)s [%(id)s].%(ext)s', # ✅ filename with video ID
        '-f', 'bv*+ba/b', # ✅ Best video + best audio
    ]

    if use_cookies and cookies_file:
        command += ['--cookies', cookies_file] # ✅ Use cookies for authentication

    if fallback:
        command += [
            '--no-check-certificate',
            '--force-generic-extractor'
        ]

    print(f"[*] Running yt-dlp {'with cookies' if use_cookies else 'without cookies'}...")
    result = subprocess.run(command + [url], capture_output=True, text=True)

    if result.returncode != 0:
        print("[!] yt-dlp error:", result.stderr.strip())
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("[!] Failed to parse yt-dlp output.")
        return None

def set_file_timestamp(filepath, upload_date):
    try:
        dt = datetime.datetime.strptime(upload_date, '%Y%m%d')
        mod_time = time.mktime(dt.timetuple())
        os.utime(filepath, (mod_time, mod_time))
        print(f"[+] Set modified time to {dt.date()} for: {filepath}")
    except Exception as e:
        print(f"[!] Failed to update timestamp: {e}")

def download_video(url, cookies_file):
    # Try without cookies first
    metadata = run_yt_dlp(url, use_cookies=False)

    # Retry with cookies if failed
    if not metadata and cookies_file:
        print("[*] Retrying with cookies...")
        metadata = run_yt_dlp(url, use_cookies=True, cookies_file=cookies_file)

    # Retry with generic fallback if needed
    if not metadata:
        print("[*] Trying fallback method...")
        metadata = run_yt_dlp(url, use_cookies=True, cookies_file=cookies_file, fallback=True)

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
    print("📁 Archive log file: " + os.path.abspath(ARCHIVE_FILE))

    # Check cookies file at startup
    if os.path.isfile(DEFAULT_COOKIES_FILE) and os.path.getsize(DEFAULT_COOKIES_FILE) > 0:
        cookies_file = DEFAULT_COOKIES_FILE
        print(f"[+] Using default cookies file: {cookies_file}")
    else:
        cookies_file = prompt_for_cookies()

    while True:
        url = input("\nEnter YouTube URL (or type 'exit' to quit): ").strip()
        if url.lower() == 'exit':
            print("Goodbye!")
            break
        elif url:
            download_video(url, cookies_file)
