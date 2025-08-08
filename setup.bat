@echo off
REM
REM Setup script for AI‑Movie‑Shorts on Windows.
REM
REM This script creates a Python virtual environment, installs
REM dependencies and prepares the directory structure. Run this script
REM from the root of the project directory by double clicking it or
REM executing `setup.bat` from a command prompt.

SETLOCAL

echo [AI-Movie-Shorts] Creating virtual environment...

REM Use python if available in PATH
WHERE python >NUL 2>NUL
IF ERRORLEVEL 1 (
    echo Python is not installed or not found in PATH. Please install Python 3.7 or newer.
    EXIT /B 1
)

IF NOT EXIST .venv (
    python -m venv .venv
)

echo [AI-Movie-Shorts] Activating virtual environment...
CALL .venv\Scripts\activate

echo [AI-Movie-Shorts] Upgrading pip...
python -m pip install --upgrade pip

echo [AI-Movie-Shorts] Installing requirements...
python -m pip install -r requirements.txt

echo [AI-Movie-Shorts] Removing .placeholder files...
for /r %%i in (*.placeholder) do del "%%i"

echo [AI-Movie-Shorts] Creating required folders...
python - <<PYEOF
import os
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

echo [AI-Movie-Shorts] Setup complete.
echo Please edit config.json to provide your OpenAI and ElevenLabs API keys before running the application.

ENDLOCAL
