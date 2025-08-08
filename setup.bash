#!/usr/bin/env bash
#
# Setup script for AI‑Movie‑Shorts on macOS or Linux.
#
# This script creates a Python virtual environment, installs all
# required dependencies and prepares the directory structure. It
# should be run from the root of the project directory.  If you
# encounter permission errors you may need to run this script with
# `bash setup.sh` instead of relying on file associations.

set -e

echo "[AI-Movie-Shorts] Creating virtual environment..."

# Use python3 if available, otherwise fallback to python
PYTHON_BIN="$(command -v python3 || command -v python)"

if [ -z "$PYTHON_BIN" ]; then
    echo "Python is not installed or not found in PATH. Please install Python 3.7 or newer."
    exit 1
fi

# Create a virtual environment in the .venv directory if it does not already exist
if [ ! -d ".venv" ]; then
    "$PYTHON_BIN" -m venv .venv
fi

echo "[AI-Movie-Shorts] Activating virtual environment..."
source .venv/bin/activate

echo "[AI-Movie-Shorts] Upgrading pip..."
python -m pip install --upgrade pip

echo "[AI-Movie-Shorts] Installing requirements..."
python -m pip install -r requirements.txt

echo "[AI-Movie-Shorts] Removing .placeholder files..."
find . -name "*.placeholder" -type f -delete

echo "[AI-Movie-Shorts] Creating required folders..."
python - <<'PYEOF'
import os
# Create directories that the application expects.  These checks are
# idempotent, so running the script multiple times is safe.
directories = [
    "clips",
    "movies",
    "output",
    "backgroundmusic",
    "scripts",
    "output_audio",
    "tiktok_output",
    os.path.join("scripts", "srt_files")
]
for path in directories:
    os.makedirs(path, exist_ok=True)
print("Created directories: {}".format(", ".join(directories)))
PYEOF

echo "[AI-Movie-Shorts] Setup complete."
echo "Please edit config.json to provide your OpenAI and ElevenLabs API keys before running the application."