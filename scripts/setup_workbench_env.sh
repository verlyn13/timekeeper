#!/bin/bash
set -e                                # Exit immediately if a command exits with a non-zero status.
export DEBIAN_FRONTEND=noninteractive # Prevent interactive prompts during apt installs

echo "--- [1/4] Updating package list and installing OS dependencies ---"
sudo apt-get update
# Ensure python3.11, venv, make, pandoc, and git are installed
sudo apt-get install -y --no-install-recommends \
    python3.11 \
    python3-venv \
    make \
    pandoc \
    git

echo "--- [2/4] Verifying Python 3.11 ---"
python3.11 --version

echo "--- [3/4] Creating Python virtual environment '.venv' using Python 3.11 ---"
# Ensure this script is run from the repository root directory
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: This script must be run from the repository root directory (containing pyproject.toml)."
    exit 1
fi
python3.11 -m venv .venv
echo "Created .venv using $(python3.11 --version)"

echo "--- Activating virtual environment ---"
source .venv/bin/activate

echo "--- Upgrading pip ---"
pip install --upgrade pip

echo "--- Installing project dependencies (including dev/docs) from pyproject.toml ---"
# This command assumes it's run from the repo root where pyproject.toml exists
pip install .[dev,docs] # Or adjust based on actual extras_require keys

echo "--- [4/4] Verifying gcloud CLI ---"
gcloud --version

echo "--- Environment setup complete! ---"
echo "To activate the environment in your terminal, run: source .venv/bin/activate"
