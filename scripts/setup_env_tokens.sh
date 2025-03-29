#!/bin/bash
# Setup environment tokens for Timekeeper project

# Check if the secrets directory exists
SECRETS_DIR="$HOME/.secrets/timekeeper"
if [ ! -d "$SECRETS_DIR" ]; then
    echo "Creating $SECRETS_DIR..."
    mkdir -p "$SECRETS_DIR"
fi

# Create the tokens.env file if it doesn't exist
TOKENS_FILE="$SECRETS_DIR/tokens.env"
if [ ! -f "$TOKENS_FILE" ]; then
    echo "Creating $TOKENS_FILE..."
    cat >"$TOKENS_FILE" <<EOF
# Timekeeper project tokens
# Created: $(date)

# PyPI API Token for package publishing
export PYPI_API_TOKEN="your_pypi_token_here"

# Codecov Token for coverage reporting
export CODECOV_TOKEN="your_codecov_token_here"
EOF
    chmod 600 "$TOKENS_FILE"
    echo "Token file created with placeholder values. Please edit $TOKENS_FILE to add your actual tokens."
else
    echo "Token file already exists at $TOKENS_FILE"
fi

# Add the function to .zshrc if it doesn't already exist
ZSHRC="$HOME/.zshrc"
if grep -q "function timekeeper-env()" "$ZSHRC"; then
    echo "The timekeeper-env function already exists in $ZSHRC"
else
    echo "Adding timekeeper-env function to $ZSHRC..."
    cat >>"$ZSHRC" <<EOF

# Timekeeper environment variables function
function timekeeper-env() {
  if [ -f ~/.secrets/timekeeper/tokens.env ]; then
    source ~/.secrets/timekeeper/tokens.env
    echo "Timekeeper environment variables loaded (PYPI_API_TOKEN, CODECOV_TOKEN)."
  else
    echo "Error: Timekeeper token file not found at ~/.secrets/timekeeper/tokens.env"
  fi
}
EOF
    echo "Function added to $ZSHRC"
fi

echo "Setup complete! To load Timekeeper environment variables, run: timekeeper-env"
