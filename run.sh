#!/usr/bin/env bash
#
# Script to launch the AI‑Movie‑Shorts application.
# Assumes that a virtual environment has been created and dependencies
# installed via setup.sh.  This script activates the virtual
# environment before running the main program.

set -e

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

source .venv/bin/activate

python main.py "$@"
