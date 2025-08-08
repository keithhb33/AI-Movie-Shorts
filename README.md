# AI-Movie-Shorts
Turn full movies or .MP4 Files into AI-generated movie commentaries and summaries.

Example Video: [Citizen Kane (1941)](https://www.youtube.com/watch?v=ej8c0NwKW00&t=5s)

Setup
- macOS/Linux: run ./setup.sh
- Windows: double-click setup.bat
- Provide your API keys in config.json

Usage
- Place .mp4 files in the movies/ folder (file name should be the movie title)
- Launch the app: ./run.sh or python3 main.py
- Click Start Generation in the GUI

Notes
- If a script or subtitles cannot be auto-fetched, the app prompts you to add the file manually under scripts/srt_files/.
- Generated videos appear in output/; the vertical variant is saved to tiktok_output/.

YouTube Upload (optional)
- Create client_secrets.json from Google Cloud Console (YouTube Data API v3)
- Click Upload all to YouTube to upload all files from output/.
