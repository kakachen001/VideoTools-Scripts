## Thumbnail Grid Generator (Standalone)

**File:** `thumbnail_grid_standalone.py`
**Version:** 1.0.0

A standalone Python script that scans a folder of video files and generates a 5×5 contact-sheet thumbnail (JPG) for each one, with an accurate HH:MM:SS timestamp burned into the corner of every frame. Uses [PyAV](https://pyav.org/) (FFmpeg bindings) for decoding, so it handles H.265/HEVC reliably — unlike OpenCV's `VideoCapture`, which is slow and inaccurate when seeking H.265 streams.

### Features

- Extracts 25 evenly-spaced frames across the video's duration and tiles them into one 5×5 grid image.
- Labels each frame with the *actual* decoded timestamp (not just the requested seek target), so the on-image clock always matches what's shown.
- Semi-transparent background box behind each timestamp for readability on any footage.
- Automatically creates its own output folders — no manual setup required.
- Supports common video containers: `.mp4`, `.mkv`, `.mov`, `.avi`, `.wmv`, `.flv`, `.webm`, `.m4v`.
- Videos that fail to process (corrupt file, unreadable stream, unknown duration, etc.) are automatically moved to a separate folder instead of silently skipped.

### Requirements

```bash
pip install av pillow numpy
```

A TrueType font (`arial.ttf`) is used for the timestamp text if available on the system; otherwise the script falls back to PIL's default font.

### Usage

Run the script directly:

```bash
python thumbnail_grid_standalone.py
```

You'll be prompted for a single input folder path — for example:

```
Please enter the input folder path: N:\Media Processing\Media\Review\no_match
```

The script then:

1. Validates the folder exists.
2. Auto-creates two folders **in the directory you ran the script from** (its current working directory, not the input folder):
   - `pic_<input_folder_name>/` — where the generated contact-sheet JPGs are saved
   - `no_thumbnail/` — where any video that fails processing gets moved
3. Asks for confirmation before processing.
4. Processes every supported video file in the input folder.
5. Asks if you'd like to process another folder, or exits.

**Example:** running the script from `C:\Scripts` and pointing it at `N:\Media Processing\Media\Review\no_match` produces:

```
C:\Scripts\pic_no_match\      ← thumbnail grids
C:\Scripts\no_thumbnail\      ← videos that failed to process
```

### Output

Each processed video produces one JPG named after the source file (e.g. `myvideo.mp4` → `myvideo.jpg`), containing a 5×5 grid of frames sampled evenly across the video's duration, each stamped with its timestamp.

### Notes

- If a video yields fewer than 25 readable frames, the remaining grid cells are filled with black placeholder frames rather than failing outright.
- Designed to run standalone; a separate module version of this same processing logic exists for integration into a larger automated pipeline.