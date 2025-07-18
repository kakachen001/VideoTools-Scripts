import subprocess
import json
import csv
import os
import time
import random

# Path to cookies.txt (optional)
COOKIES_FILE = "C:\\www.youtube.com_cookies.txt"

# Delay range between video fetches (seconds)
DELAY_RANGE = (1, 3)

def fetch_video_info(video_url):
    command = [
        'yt-dlp',
        '--skip-download',
        '--dump-json',
        '--no-warnings',
    ]

    if COOKIES_FILE:
        command += ['--cookies', COOKIES_FILE]

    command.append(video_url)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[!] Error fetching metadata for {video_url}: {result.stderr.strip()}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("[!] Failed to parse JSON.")
        return None

def get_video_urls(channel_url):
    command = [
        'yt-dlp',
        '--flat-playlist',
        '--dump-single-json',
        '--no-warnings',
    ]

    if COOKIES_FILE:
        command += ['--cookies', COOKIES_FILE]

    command.append(channel_url)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[!] Error fetching playlist data: {result.stderr.strip()}")
        return []

    try:
        data = json.loads(result.stdout)
        return [entry['url'] for entry in data.get('entries', [])]
    except Exception as e:
        print(f"[!] Failed to parse playlist JSON: {e}")
        return []

def write_to_csv(videos_data, filename):
    if not videos_data:
        print("[!] No video data to write.")
        return

    keys = ['id', 'title', 'upload_date', 'duration', 'view_count', 'like_count', 'channel', 'channel_id', 'webpage_url']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for video in videos_data:
            row = {key: video.get(key, '') for key in keys}
            writer.writerow(row)

    print(f"[✔] CSV file saved: {filename}")

def main():
    print("YouTube Channel Video Metadata Exporter")
    channel_name = input("Enter a name for the channel (used as CSV filename): ").strip()
    channel_url = input("Enter the YouTube channel or playlist URL: ").strip()

    if not channel_name or not channel_url:
        print("[!] Channel name or URL cannot be empty.")
        return

    output_filename = f"{channel_name}_videos.csv"
    print("[*] Fetching video list...")
    video_urls = get_video_urls(channel_url)

    print(f"[*] Found {len(video_urls)} videos.")
    all_data = []

    for i, vid_url in enumerate(video_urls):
        print(f"[{i+1}/{len(video_urls)}] Processing: {vid_url}")
        info = fetch_video_info(vid_url)
        if info:
            all_data.append(info)
        time.sleep(random.uniform(*DELAY_RANGE))

    write_to_csv(all_data, output_filename)

if __name__ == "__main__":
    main()
