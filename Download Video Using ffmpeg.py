import subprocess
import re

def get_best_program(url):
    probe_cmd = [
        "ffmpeg",
        "-allowed_extensions", "ALL",
        "-i", url
    ]

    result = subprocess.run(
        probe_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    programs = re.findall(r"Program (\d+)", result.stdout)
    programs = sorted(set(int(p) for p in programs))

    if not programs:
        return None

    return programs[-1]


def download_with_ffmpeg(url, output_filename):
    best_program = get_best_program(url)

    if best_program is not None:
        print(f"🎯 Selected HLS Program {best_program} (highest bitrate)")
        map_args = [
            "-map", f"p:{best_program}",
        ]
    else:
        print("🎯 No programs detected, using safe fallback mapping")
        map_args = [
            "-map", "0?",
        ]

    command = [
        "ffmpeg",
        "-y",
        "-loglevel", "info",

        # 🔥 REQUIRED for broken HLS playlists with JPEG refs
        "-allowed_extensions", "ALL",

        "-i", url,
        *map_args,

        "-c", "copy",
        "-movflags", "+faststart",
        output_filename
    ]

    print("\n[*] Starting download...\n")
    print("Command:")
    print(" ".join(command))
    print()

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()

    if process.returncode == 0:
        print(f"\n✅ Download completed: {output_filename}")
    else:
        if process.returncode > 2**31:
            real_code = process.returncode - 2**32
            print(f"\n❌ ffmpeg exited with code {real_code} (invalid argument)")
        else:
            print(f"\n❌ ffmpeg exited with code {process.returncode}")


def main():
    print("🎥 FFmpeg Video Downloader (HLS Hardened)")

    while True:
        url = input("\nEnter the direct video URL (m3u8/mp4): ").strip()
        if not url:
            print("❌ No URL provided. Exiting.")
            break

        filename = input("Enter output file name (e.g., video.mp4): ").strip()
        if not filename:
            print("❌ No filename provided. Exiting.")
            break

        if not filename.lower().endswith((".mp4", ".mkv", ".ts")):
            filename += ".mp4"

        download_with_ffmpeg(url, filename)

        again = input("\n🔁 Download another? (y/n): ").strip().lower()
        if again != "y":
            print("👋 Exiting. Goodbye!")
            break


if __name__ == "__main__":
    main()
