import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import av  # PyAV library for FFmpeg-based decoding (install using: pip install av)
import shutil

VERSION = "1.0.0"

def seconds_to_hhmmss(seconds):
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"

def create_beautiful_timestamp(frame, timestamp_text, position=(20, 20), font_size=72):
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Ensure correct font
    except IOError:
        print("Font not found, using default.")
        font = ImageFont.load_default()

    # Base image, kept in RGBA so we can composite the semi-transparent box onto it
    pil_image = Image.fromarray(frame).convert("RGBA")

    bbox = font.getbbox(timestamp_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = 10
    x, y = position
    background_coords = [x, y, x + text_width + 2 * padding, y + text_height + 2 * padding]

    overlay = Image.new("RGBA", pil_image.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(background_coords, fill=(0, 0, 0, 180))

    # Composite the dark background box onto the base image
    pil_image = Image.alpha_composite(pil_image, overlay)

    # Draw on the SAME image object we just composited, then convert to RGB at the end
    draw = ImageDraw.Draw(pil_image)

    # font.getbbox() ink often has an offset from (0,0) — subtract it so the
    # glyphs land centered in the padded box instead of drifting down/right.
    text_x = x + padding - bbox[0]
    text_y = y + padding - bbox[1]
    shadow_offset = 2

    draw.text((text_x + shadow_offset, text_y + shadow_offset), timestamp_text, font=font, fill=(0, 0, 0))
    draw.text((text_x, text_y), timestamp_text, font=font, fill=(255, 255, 255))

    pil_image = pil_image.convert("RGB")

    return np.array(pil_image)

def move_to_no_thumbnail(video_path, no_thumbnail_folder):
    """Move the video file to the 'no_thumbnail' folder, renaming if necessary."""
    os.makedirs(no_thumbnail_folder, exist_ok=True)
    base_name = os.path.basename(video_path)
    destination_file = os.path.join(no_thumbnail_folder, base_name)

    # Handle filename conflicts
    if os.path.exists(destination_file):
        name, ext = os.path.splitext(base_name)
        counter = 0
        while os.path.exists(os.path.join(no_thumbnail_folder, f"{name}({counter}){ext}")):
            counter += 1
        destination_file = os.path.join(no_thumbnail_folder, f"{name}({counter}){ext}")

    shutil.move(video_path, destination_file)
    print(f"Moved {video_path} to {destination_file}")

def process_video(video_path, output_folder, no_thumbnail_folder):
    output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(video_path))[0] + ".jpg")

    try:
        container = av.open(video_path)
    except av.AVError as e:
        print(f"Error: Cannot open video file {video_path}: {e}")
        move_to_no_thumbnail(video_path, no_thumbnail_folder)
        return

    stream = container.streams.video[0]
    # Use the stream's own time_base (not the container-level av.time_base) to
    # convert stream.duration ticks into seconds. Fall back to container.duration
    # (which IS in AV_TIME_BASE / microsecond units) if the stream doesn't report one.
    if stream.duration:
        duration = float(stream.duration * stream.time_base)
    elif container.duration:
        duration = container.duration / 1_000_000
    else:
        duration = None
    fps = stream.average_rate if stream.average_rate else 30  # Default to 30 FPS if unavailable

    if not duration:
        print(f"Error: Unable to determine duration for {video_path}.")
        move_to_no_thumbnail(video_path, no_thumbnail_folder)
        return

    print(f"Video duration: {seconds_to_hhmmss(duration)} for {video_path}")

    timestamps = [duration * i / 26 for i in range(1, 27)]
    frames = []
    for timestamp in timestamps:
        # container.seek() with a stream= argument expects the offset expressed
        # in THAT STREAM's time_base ticks, not av.time_base (which is only
        # valid for whole-container seeks with no stream specified).
        seek_target = int(timestamp / stream.time_base)
        container.seek(seek_target, stream=stream)
        for frame in container.decode(video=0):
            frame_array = np.array(frame.to_ndarray(format="rgb24"))
            # Seeking only lands on the nearest keyframe, so label the image
            # with the frame's ACTUAL decoded timestamp rather than the
            # timestamp we originally asked for — otherwise the on-image
            # clock and the pixels it's labeling can disagree.
            actual_time = float(frame.pts * stream.time_base) if frame.pts is not None else timestamp
            timestamp_text = seconds_to_hhmmss(actual_time)
            frame_with_text = create_beautiful_timestamp(frame_array, timestamp_text)
            frames.append(Image.fromarray(frame_with_text))
            break

    container.close()

    if len(frames) == 0:
        print(f"Error: No frames could be read from {video_path}. Moving to 'no_thumbnail'.")
        move_to_no_thumbnail(video_path, no_thumbnail_folder)
        return

    if len(frames) < 25:
        print(f"Warning: Only {len(frames)} frames were extracted. Filling with black frames.")
        missing_frames = 25 - len(frames)
        placeholder_frame = Image.new("RGB", (frames[0].width, frames[0].height), (0, 0, 0))
        frames.extend([placeholder_frame] * missing_frames)

    frames = frames[:25]
    grid_width = max(frame.width for frame in frames)
    grid_height = max(frame.height for frame in frames)
    grid = Image.new("RGB", (grid_width * 5, grid_height * 5))

    for i, frame in enumerate(frames):
        x = (i % 5) * grid_width
        y = (i // 5) * grid_height
        grid.paste(frame, (x, y))

    grid.save(output_path)
    print(f"5x5 grid screenshot saved to {output_path}")

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v")

def process_folder(input_folder, output_folder, no_thumbnail_folder):
    """Process all common video files in a folder."""
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(VIDEO_EXTENSIONS):
            video_path = os.path.join(input_folder, file_name)
            process_video(video_path, output_folder, no_thumbnail_folder)

def run_process(input_folder, output_folder, no_thumbnail_folder):
    """Run the process with specified folders."""
    print(f"Checking input folder: {input_folder}")
    print(f"Checking output folder: {output_folder}")
    print(f"Checking 'no_thumbnail' folder: {no_thumbnail_folder}")

    if os.path.isdir(input_folder) and os.path.isdir(output_folder):
        process_folder(input_folder, output_folder, no_thumbnail_folder)
    else:
        print(f"Invalid folder path(s). Please ensure the folder(s) exist.")
        print(f"Input folder: {input_folder}")
        print(f"Output folder: {output_folder}")

def user_prompt():
    """Ask the user for an input folder only. Output and no_thumbnail folders
    are created automatically next to the input folder — no more hardcoded paths."""
    while True:
        input_folder = input("Please enter the input folder path: ").strip().strip('"')

        if not os.path.isdir(input_folder):
            print(f"'{input_folder}' is not a valid folder. Please try again.\n")
            continue

        # Self-create output folders in the current working directory (i.e.
        # wherever this script was launched from), not next to the input
        # folder. E.g. if you run this from C:\Scripts and point it at
        # N:\Media Processing\Media\Review\no_match, you'll get:
        #   C:\Scripts\pic_no_match         (output, auto-created)
        #   C:\Scripts\no_thumbnail         (failed extractions, auto-created)
        run_dir = os.getcwd()
        folder_name = os.path.basename(os.path.normpath(input_folder))
        output_folder = os.path.join(run_dir, f"pic_{folder_name}")
        no_thumbnail_folder = os.path.join(run_dir, "no_thumbnail")

        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(no_thumbnail_folder, exist_ok=True)

        print(f"\nInput folder: {input_folder}")
        print(f"Output folder (auto-created): {output_folder}")
        print(f"'No thumbnail' folder (auto-created): {no_thumbnail_folder}")

        confirm = input("Do you want to proceed with these settings? (yes/no): ").strip().lower()
        if confirm == "yes":
            run_process(input_folder, output_folder, no_thumbnail_folder)
        elif confirm == "no":
            print("Re-enter the folder path.")
            continue
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
            continue

        repeat = input("Do you want to process another folder? (yes/no): ").strip().lower()
        if repeat != "yes":
            print("Exiting the program.")
            break

if __name__ == "__main__":
    print(f"thumbnail_grid_standalone.py version {VERSION}")
    user_prompt()