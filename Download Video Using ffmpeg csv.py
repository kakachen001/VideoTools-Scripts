import subprocess
import os
import csv

CSV_FILE = "downloads.csv"

def create_csv_if_missing():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "link"])
        print(f"📄 Created new CSV file: {CSV_FILE}")
        print("➡ Add entries to it in the format: title,link")
        return False
    return True

def read_csv_entries():
    entries = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["title"].strip()
            link = row["link"].strip()
            if title and link:
                entries.append((title, link))
    return entries

def download_with_ffmpeg(url, output_filename):
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    command = [
        'ffmpeg',
        '-i', url,
        '-c', 'copy',
        output_filename
    ]

    print(f"\n[*] Starting download to '{output_filename}'...\n")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end='')

    process.wait()

    if process.returncode == 0:
        print(f"\n✅ Download completed: {output_filename}")
    else:
        print(f"\n❌ ffmpeg exited with code {process.returncode}")

def main():
    print("🎥 FFmpeg CSV Video Downloader")

    if not create_csv_if_missing():
        return

    entries = read_csv_entries()
    if not entries:
        print(f"❌ No entries found in {CSV_FILE}. Add some and run again.")
        return

    for title, link in entries:
        folder_name = title.split("_")[0]
        ext = os.path.splitext(title)[1]
        if not ext:
            filename = title + ".mp4"
        else:
            filename = title

        output_path = os.path.join(folder_name, filename)
        download_with_ffmpeg(link, output_path)

    print("\n🎉 All downloads completed.")

if __name__ == "__main__":
    main()
