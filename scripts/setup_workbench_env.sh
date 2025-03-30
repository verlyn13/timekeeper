#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Updating package list and installing OS dependencies ---"
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv make pandoc git

echo "--- Verifying Python version ---"
python3.11 --version
echo "--- Creating Python virtual environment '.venv' ---"
python3.11 -m venv .venv

echo "--- Activating virtual environment ---"
# Note: Activation within the script only affects the script's execution context.
# The user needs to run 'source .venv/bin/activate' manually in their terminal.
source .venv/bin/activate

echo "--- Upgrading pip ---"
pip install --upgrade pip

echo "--- Installing project dependencies (including dev/docs) from pyproject.toml ---"
# Assuming dev/docs dependencies are specified correctly in pyproject.toml
# Adjust if using requirements files (e.g., pip install -r requirements.txt -r requirements-dev.txt)
pip install .[dev,docs] # Or adjust based on actual extras_require keys

# If docs tools aren't in pyproject.toml extras:
# echo "--- Installing documentation tools ---"
# pip install sphinx quartodoc <specific versions if needed>

echo "--- Verifying gcloud CLI ---"
# This assumes gcloud is pre-installed on the Vertex AI Workbench image
gcloud --version

echo "--- Environment setup complete! ---"
echo "To activate the environment in your terminal, run: source .venv/bin/activate"
