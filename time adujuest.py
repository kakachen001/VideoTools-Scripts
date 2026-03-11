import subprocess
import json
import os

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def get_video_info(video_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        video_path
    ]
    result = run(cmd)
    return json.loads(result.stdout)

def get_duration(info):
    return float(info["format"]["duration"])

def has_audio(info):
    return any(s["codec_type"] == "audio" for s in info["streams"])

def build_atempo(speed):
    filters = []
    while speed > 2.0:
        filters.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        filters.append("atempo=0.5")
        speed /= 0.5
    filters.append(f"atempo={speed}")
    return ",".join(filters)

def main():
    input_video = input("Enter input video path: ").strip('"')
    output_video = input("Enter output video path: ").strip('"')
    target_duration = float(input("Enter desired final duration (seconds): "))

    if not os.path.exists(input_video):
        print("❌ Input file does not exist.")
        return

    info = get_video_info(input_video)
    original_duration = get_duration(info)
    speed_factor = original_duration / target_duration

    print(f"Original duration: {original_duration:.2f}s")
    print(f"Target duration:   {target_duration:.2f}s")
    print(f"Speed factor:     {speed_factor:.4f}x")

    video_filter = f"setpts={1/speed_factor}*PTS"

    if has_audio(info):
        print("🔊 Audio stream detected")
        audio_filter = build_atempo(speed_factor)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-filter_complex",
            f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
            "-map", "[v]",
            "-map", "[a]",
            output_video
        ]
    else:
        print("🔇 No audio stream detected")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", video_filter,
            output_video
        ]

    subprocess.run(cmd)
    print("✅ Done!")

if __name__ == "__main__":
    main()
