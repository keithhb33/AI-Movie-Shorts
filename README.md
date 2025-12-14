# AI-Movie-Shorts

Turn full-length `.mp4` movies into **AI-narrated movie recap videos** (horizontal + vertical), built automatically from subtitles + optional script context.

Example Video: [Citizen Kane (1941)](https://www.youtube.com/watch?v=ej8c0NwKW00&t=5s)

---

## What it does

Given a movie file, AI-Movie-Shorts will:

1. **Fetch subtitles (SRT)** automatically (and convert timestamps to seconds)
2. **Optionally fetch a script** (used only as extra story context)
3. Ask **OpenAI** to generate a **clip plan** (timestamps + narration per clip)
4. Use **ElevenLabs** to generate voiceover audio for each clip
5. Use **FFmpeg** to:
   - cut each clip
   - time-stretch video to match narration length
   - concatenate all clips into one recap video
6. Optionally add **background music** from `backgroundmusic/`
7. Export:
   - `output/<MovieTitle>.mp4` (standard)
   - `tiktok_output/<MovieTitle>_vertical.mp4` (9:16 vertical)

It also **clears generated files in `clips/` each run** (while preserving the `clips/audio/` folder and only removing files inside it).

---

## Folder structure

- `movies/` — input `.mp4` files (filename should be the movie title)
- `output/` — final horizontal recap videos
- `tiktok_output/` — final vertical recap videos
- `backgroundmusic/` — optional `.mp3` / `.m4a` music used as BGM
- `clips/` — temporary working files (auto-cleared each run)
  - `clips/audio/` — generated narration MP3s (files cleared each run; folder preserved)
- `scripts/srt_files/` — downloaded/cached subtitles and optional scripts

---

## Requirements

You need:

- **FFmpeg + ffprobe**
- **curl**
- **unzip** (for subtitle downloads)
- A C toolchain + build system:
  - macOS/Linux: `cmake`, `make` (or Ninja), `pkg-config`
- Libraries:
  - `libcurl`
  - `cJSON`

### macOS (Homebrew) quick install
```bash
brew install ffmpeg curl cjson cmake pkg-config unzip
```

### Linux (example)
Install equivalents via your package manager (names vary by distro):
- `ffmpeg`
- `curl` + dev headers
- `cmake`, `pkg-config`, build essentials
- `cjson` dev package
- `unzip`

---

## Config

Create `config.json` in the project root:

```json
{
  "open_api_key": "YOUR_OPENAI_KEY",
  "elevenlabs_api_key": "YOUR_ELEVENLABS_KEY",
  "eleven_voice_id": "OPTIONAL_VOICE_ID",
  "eleven_model_id": "OPTIONAL_MODEL_ID"
}
```

Notes:
- `eleven_voice_id` defaults if omitted.
- `eleven_model_id` defaults if omitted.

---

## Build

```bash
rm -rf build
cmake -S . -B build
cmake --build build
```

This produces the executable (name depends on your CMake target, e.g. `movie_summary_bot`).

---

## Usage

1. Put movie files in `movies/`:
   - Example: `movies/Sinners.mp4`
2. Run the program (example binary name):
   ```bash
   ./build/movie_summary_bot
   ```

Outputs:
- `output/Sinners.mp4`
- `tiktok_output/Sinners_vertical.mp4`

---

## Background music behavior

If `backgroundmusic/` contains `.mp3` or `.m4a` files, the program will:
- randomly choose tracks,
- trim from ~40s in (to skip intros),
- stitch enough pieces to cover the recap duration,
- mix narration louder + BGM quieter.

If no music files exist, output will be narration-only.

---

## Subtitles / script fetching

- Subtitles (SRT) are auto-downloaded when missing.
- Script fetching is **best effort** and **optional**. If it fails, the program continues with subtitles only.

If auto-fetch fails, you can manually add:
- `scripts/srt_files/<MovieTitle>.srt`

Then rerun.

---

## Vertical output

The vertical render:
- center-crops the movie to a narrower width,
- scales/pads to a 9:16 canvas,
- keeps audio if present.

Saved to `tiktok_output/`.

---

## Notes & troubleshooting

- **Filename matters**: `movies/My Movie.mp4` → treated as title `My Movie`
- If you see “plan count = 0” or missing clips, check:
  - your OpenAI key
  - network connectivity
  - that the SRT conversion output is not empty
- If vertical render fails, confirm:
  - FFmpeg is installed and in PATH
  - the input `output/<MovieTitle>.mp4` exists and is valid

---

## Legal

Only process videos you own or have permission to use. Subtitle/script sources may be unavailable for some titles, and availability can change over time.
