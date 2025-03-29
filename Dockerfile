FROM fedora:41

# Install system dependencies
RUN dnf update -y && \
    dnf install -y \
        git \
        gcc \
        g++ \
        make \
        curl \
        wget \
        unzip \
        nodejs \
        npm \
        python3 \
        python3-pip \
        python3-devel \
        R \
        pandoc \
        texlive \
        texlive-latex \
        texlive-xetex \
        texlive-collection-fontsrecommended \
        texlive-collection-latexrecommended \
        zsh \
        fontconfig \
        freetype \
        libpng \
        libjpeg-turbo \
        libwebp \
        && \
    dnf clean all

# Install Quarto
RUN mkdir -p /opt/quarto && \
    curl -L -o quarto.tar.gz https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.537/quarto-1.4.537-linux-amd64.tar.gz && \
    tar -xzf quarto.tar.gz -C /opt/quarto --strip-components=1 && \
    ln -s /opt/quarto/bin/quarto /usr/local/bin/quarto && \
    rm quarto.tar.gz

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install jupyter matplotlib numpy pytest pytest-cov black isort flake8 mypy

# Install Oh My Zsh for better shell experience
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Create zsh config with better defaults for development
RUN echo 'export PATH=$PATH:/app/.local/bin' >> ~/.zshrc && \
    echo 'alias ll="ls -la"' >> ~/.zshrc && \
    echo 'alias py="python3"' >> ~/.zshrc && \
    echo 'alias test="pytest"' >> ~/.zshrc && \
    echo 'alias coverage="pytest --cov=src"' >> ~/.zshrc && \
    echo 'alias lint="black . && isort . && flake8 ."' >> ~/.zshrc && \
    echo 'alias docs="quarto render"' >> ~/.zshrc && \
    echo 'alias serve="quarto preview"' >> ~/.zshrc

# Set up project structure if not present
RUN mkdir -p src/{python,js,R} data/{raw,processed} tests scripts quarto/{articles,presentations,docs,website} notebooks docs/api

# Create a setup script that runs when container starts
RUN echo '#!/bin/zsh\n\
if [ ! -d ".git" ]; then\n\
  echo "Initializing Git repository..."\n\
  git init\n\
  echo "You may want to set your Git configuration:"\n\
  echo "  git config --global user.name \"Your Name\""\n\
  echo "  git config --global user.email \"your.email@example.com\""\n\
fi\n\
\n\
if [ ! -e "pyproject.toml" ]; then\n\
  echo "Installing package in development mode..."\n\
  pip install -e .\n\
fi\n\
\n\
echo ""\n\
echo "Welcome to the Timekeeper development environment!"\n\
echo ""\n\
echo "Quick commands:"\n\
echo "  test       - Run tests"\n\
echo "  coverage   - Run tests with coverage report"\n\
echo "  lint       - Run code quality checks"\n\
echo "  docs       - Build documentation"\n\
echo "  serve      - Preview documentation site"\n\
echo ""\n\
\n\
# Start zsh with the current directory mounted\n\
zsh' > /usr/local/bin/start.sh && chmod +x /usr/local/bin/start.sh

# Set zsh as the default shell
SHELL ["/bin/zsh", "-c"]

# Set the entrypoint to our setup script
ENTRYPOINT ["/usr/local/bin/start.sh"]