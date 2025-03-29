#!/bin/bash
# Script to set up the development environment for the Timekeeper project

set -e # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Timekeeper development environment...${NC}"

# Check for Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
    echo -e "${GREEN}Found Python: ${NC}$(python3 --version)"
else
    echo -e "${RED}Python 3 not found. Please install Python 3.7 or higher.${NC}"
    exit 1
fi

# Check for pip
if ! command -v pip &>/dev/null; then
    echo -e "${RED}pip not found. Please install pip.${NC}"
    exit 1
fi

# Check for virtualenv
if ! command -v virtualenv &>/dev/null; then
    echo -e "${YELLOW}virtualenv not found. Installing...${NC}"
    pip install virtualenv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    virtualenv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install the package in development mode
echo -e "${GREEN}Installing package and dependencies...${NC}"
pip install -e ".[dev,docs]"

# Check for Quarto
if command -v quarto &>/dev/null; then
    echo -e "${GREEN}Found Quarto: ${NC}$(quarto --version)"
else
    echo -e "${YELLOW}Quarto not found. Please install Quarto from https://quarto.org/docs/get-started/${NC}"
    echo -e "${YELLOW}This is required for building documentation.${NC}"
fi

# Setup git hooks if git is available
if command -v git &>/dev/null; then
    if [ -d ".git" ]; then
        echo -e "${GREEN}Setting up git hooks...${NC}"

        # Create pre-commit hook
        mkdir -p .git/hooks
        cat >.git/hooks/pre-commit <<'EOF'
#!/bin/bash
# Pre-commit hook to run tests and linting

echo "Running tests..."
python -m pytest || exit 1

echo "Running linting..."
python -m flake8 --count --select=E9,F63,F7,F82 --show-source --statistics src/ || exit 1

echo "All checks passed!"
EOF
        chmod +x .git/hooks/pre-commit

        echo -e "${GREEN}Git hooks installed.${NC}"
    else
        echo -e "${YELLOW}Not a git repository. Skipping git hooks setup.${NC}"
    fi
else
    echo -e "${YELLOW}Git not found. Skipping git hooks setup.${NC}"
fi

# Create initial directories if they don't exist
echo -e "${GREEN}Ensuring project directories exist...${NC}"
for dir in data/raw data/processed tests src/python src/js notebooks; do
    mkdir -p "$dir"
done

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${GREEN}Activate the environment with: ${YELLOW}source venv/bin/activate${NC}"
echo -e "${GREEN}Run tests with: ${YELLOW}pytest${NC}"
echo -e "${GREEN}Build docs with: ${YELLOW}python scripts/build_docs.py${NC}"
