import subprocess
import os

def download_with_ffmpeg(url, output_filename):
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

    # Print output line by line in real time
    for line in process.stdout:
        print(line, end='')

    process.wait()

    if process.returncode == 0:
        print(f"\n✅ Download completed: {output_filename}")
    else:
        print(f"\n❌ ffmpeg exited with code {process.returncode}")

def main():
    print("🎥 FFmpeg Video Downloader")

    while True:
        url = input("Enter the direct video URL (e.g., m3u8/mp4): ").strip()
        if not url:
            print("❌ No URL provided. Exiting.")
            break

        filename = input("Enter output file name (e.g., myvideo.mp4): ").strip()
        if not filename:
            print("❌ No filename provided. Exiting.")
            break

        if not filename.lower().endswith(('.mp4', '.mkv', '.ts')):
            filename += '.mp4'

        download_with_ffmpeg(url, filename)

        again = input("\n🔁 Do you want to download another video? (y/n): ").strip().lower()
        if again != 'y':
            print("👋 Exiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
