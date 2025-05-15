# 🎬 YouTube Downloader with Timestamp & Cookie Support

A powerful Python script using [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) to download YouTube videos with smart features:
- ✅ Embed thumbnail into the video
- ✅ Save metadata as JSON
- ✅ Skip already-downloaded videos with an archive log
- ✅ Modify file timestamp to match the video’s original upload date
- ✅ Automatically retry with cookies if authentication is required
- ✅ Interactive loop for downloading multiple videos

---

## 🔧 Features

- Downloads best available quality (video + audio merged into MP4)
- Automatically retries with cookies if video is age-restricted or private
- Prompts for cookies path if missing or expired
- Sets the file's "modified date" to the video's upload date
- Skips re-downloading videos using an archive log
- Safe fallback logic for generic extraction if needed

---

## 📦 Requirements

- Python 3.7+
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) (Install via pip)
- `ffmpeg` in your system PATH
- A valid `cookies.txt` file (e.g. exported using [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/)

### 🛠 Install Dependencies

```bash
pip install yt-dlp
