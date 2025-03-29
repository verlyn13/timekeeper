# Sphinx-Quarto Integration for Research-Oriented Architecture

## Overview

This document provides a comprehensive plan for integrating Sphinx API documentation with Quarto-based conceptual documentation within the research-oriented architecture of the Timekeeper project. The integration is designed to maintain bidirectional traceability between mathematical theory and implementation.

## 1. Integration Architecture

### 1.1 Component Roles

| Component  | Primary Role                                   | Secondary Roles                                 |
| ---------- | ---------------------------------------------- | ----------------------------------------------- |
| **Python** | Core implementation of temporal mathematics    | Mathematical validation, visualization          |
| **Quarto** | Conceptual documentation, interactive examples | Research framework, visual demonstrations       |
| **Sphinx** | API documentation from docstrings              | Code structure visualization, cross-referencing |

### 1.2 Integration Flow

```
┌──────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│                  │     │                   │     │                  │
│  Python Code     │────▶│  Sphinx           │────▶│  API Docs        │
│  with Docstrings │     │  Documentation    │     │                  │
│                  │     │                   │     │                  │
└──────────────────┘     └───────────────────┘     └────────┬─────────┘
        │                                                    │
        │                                                    │
        │                                                    ▼
        │                ┌───────────────────┐     ┌──────────────────┐
        │                │                   │     │                  │
        └───────────────▶│  Quarto          │────▶│  Complete        │
                         │  Documentation    │     │  Documentation   │
                         │                   │     │                  │
                         └───────────────────┘     └──────────────────┘
```

## 2. Directory Structure

The directory structure follows the research-oriented architecture:

```
timekeeper/
├── theory/                  # Mathematical foundation
│   ├── formal/              # Formal mathematical theory
│   ├── mappings/            # Theory-to-implementation mappings
│   └── visualization/       # Theoretical visualizations
├── src/                     # Source code
│   ├── core/                # Core implementation
│   │   ├── temporal/        # Temporal universe implementation
│   │   ├── morphisms/       # Temporal morphisms
│   │   └── lattice/         # Lattice operations
│   ├── adaptive/            # Adaptive temporal system
│   ├── scheduler/           # Task scheduling
│   └── viz/                 # Visualization components
├── docs/                    # Documentation
│   ├── theory/              # Theory documentation
│   ├── implementation/      # Implementation documentation
│   │   └── api/             # API documentation (placeholder for Sphinx output)
│   ├── research/            # Research documentation
│   └── examples/            # Example usage
├── config/                  # Configuration files
│   ├── sphinx/              # Sphinx configuration
│   │   ├── conf.py          # Sphinx config
│   │   ├── index.rst        # API index
│   │   ├── modules/         # Module documentation
│   │   ├── _static/         # Static files
│   │   └── _templates/      # Custom templates
│   └── quarto/              # Quarto configuration
│       └── _quarto.yml      # Quarto config
├── scripts/                 # Build scripts
│   └── build/               # Documentation build scripts
│       ├── api_build.py     # API documentation build
│       ├── theory_build.py  # Theory documentation build
│       └── research_build.py # Research documentation build
├── _build/                  # Build outputs
│   ├── api/                 # Sphinx API documentation output
│   ├── theory/              # Theory documentation output
│   └── site/                # Combined site output
├── quarto.yml               # Top-level Quarto configuration
└── scripts/build_docs.py    # Main documentation build script
```

## 3. Configuration Files

### 3.1 Sphinx Configuration (`config/sphinx/conf.py`)

```python
"""
Sphinx configuration for Timekeeper API documentation.
"""

import os
import sys
from datetime import datetime

# Add the source directory to the path so Sphinx can find the modules
sys.path.insert(0, os.path.abspath("../../src"))

# Project information
project = "Timekeeper"
copyright = f"{datetime.now().year}, Timekeeper Contributors"
author = "Timekeeper Contributors"
version = "0.1.0"
release = "0.1.0"

# Extensions
extensions = [
    'sphinx.ext.autodoc',         # Auto-documentation from docstrings
    'sphinx.ext.napoleon',        # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',        # Link to source code
    'sphinx.ext.mathjax',         # LaTeX support
    'sphinx_autodoc_typehints',   # Type hints support
    'sphinx_copybutton',          # Add copy button to code blocks
    'sphinx.ext.intersphinx',     # Link to other documentation
    'sphinx.ext.imgmath',         # Enhanced math support
]

# Theme configuration
html_theme = 'furo'             # Modern, responsive theme
html_title = 'Timekeeper API Documentation'
html_short_title = 'Timekeeper API'
html_static_path = ['_static']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Napoleon settings for docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# Custom sections for theory references
napoleon_custom_sections = [
    'References',
    'Theoretical Foundation'
]

# Add cross-references to the theory documentation
intersphinx_mapping = {
    'theory': ('../../_build/theory', None),
}

# Other settings
add_module_names = False
autodoc_member_order = 'bysource'
autoclass_content = 'both'
```

### 3.2 Quarto Configuration (`config/quarto/_quarto.yml`)

```yaml
website:
  title: "Timekeeper"
  description: "A Mathematical Framework for Temporal Dynamics in Agent Systems"
  navbar:
    background: primary
    search: true
    left:
      - text: "Home"
        file: index.qmd
      - text: "Theory"
        file: docs/theory/index.qmd
      - text: "Implementation"
        menu:
          - text: "Overview"
            file: docs/implementation/index.qmd
          - text: "API Reference"
            href: docs/implementation/api/index.html
      - text: "Research"
        file: docs/research/index.qmd

  sidebar:
    - title: "Theory"
      contents:
        - docs/theory/index.qmd
        - docs/theory/temporal_universe.qmd
        - docs/theory/hierarchical_partition.qmd
        - docs/theory/timepoint_operations.qmd
        - docs/theory/morphisms.qmd
        - docs/theory/lattice_structure.qmd

    - title: "Implementation"
      contents:
        - docs/implementation/index.qmd
        - docs/implementation/agent_temporal.qmd
        - docs/implementation/task_scheduler.qmd
        - docs/implementation/adaptive_system.qmd
        - section: "API Reference"
          contents:
            - href: docs/implementation/api/index.html
            - href: docs/implementation/api/modules/temporal.html
            - href: docs/implementation/api/modules/morphisms.html
            - href: docs/implementation/api/modules/scheduler.html
            - href: docs/implementation/api/modules/adaptive.html

    - title: "Research"
      contents:
        - docs/research/index.qmd
        - section: "Hypotheses"
          contents:
            - docs/research/hypotheses/coordination_efficiency.qmd
            - docs/research/hypotheses/temporal_density.qmd
            - docs/research/hypotheses/scheduler_optimization.qmd
        - section: "Experiments"
          contents:
            - docs/research/experiments/index.qmd

format:
  html:
    theme: cosmo
    css: docs/assets/css/styles.css
    toc: true
    toc-depth: 3
    include-in-header:
      text: |
        <link rel="stylesheet" href="config/sphinx/_static/custom.css">
```

### 3.3 Top-Level Quarto Configuration (`quarto.yml`)

```yaml
project:
  type: website
  output-dir: _build/site

render:
  - docs/**/*.qmd

include-in-project:
  - config/quarto/_quarto.yml
```

## 4. Build Scripts

### 4.1 API Documentation Build Script (`scripts/build/api_build.py`)

```python
#!/usr/bin/env python3
"""
Build API documentation using Sphinx.

This script builds the API documentation from Python docstrings,
integrating references to the mathematical theory.
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

# Project directories
CONFIG_DIR = "config/sphinx"
OUTPUT_DIR = "_build/api"
SITE_DIR = "_build/site/docs/implementation/api"

def ensure_directory(dir_path):
    """Ensure a directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def run_command(cmd, cwd=None):
    """Run a shell command and print its output."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True, text=True, capture_output=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(e.stderr)
        return False

def build_api_docs():
    """Build API documentation using Sphinx."""
    print("Building API documentation...")

    # Ensure the build directory exists
    ensure_directory(OUTPUT_DIR)

    # Run Sphinx build
    sphinx_cmd = [
        "sphinx-build",
        "-b", "html",
        "-c", CONFIG_DIR,  # Use the config directory
        "src",            # Source directory (look at Python code here)
        OUTPUT_DIR        # Output directory
    ]

    if not run_command(sphinx_cmd):
        return False

    # Ensure the site API directory exists
    ensure_directory(SITE_DIR)

    # Copy Sphinx output to site directory
    print("Copying Sphinx output to site directory...")
    for item in os.listdir(OUTPUT_DIR):
        src_path = os.path.join(OUTPUT_DIR, item)
        dst_path = os.path.join(SITE_DIR, item)

        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

    print("API documentation built successfully.")
    return True

if __name__ == "__main__":
    build_api_docs()
```

### 4.2 Main Build Script (`scripts/build_docs.py`)

```python
#!/usr/bin/env python3
"""
Main documentation build script.

This script coordinates the building of all documentation components:
- Theory documentation
- API documentation (Sphinx)
- Research documentation
- Combined site (Quarto)
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def ensure_directory(dir_path):
    """Ensure a directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def run_script(script):
    """Run a Python script and check for errors."""
    print(f"Running {script}...")
    result = subprocess.run([sys.executable, script], check=False)
    if result.returncode != 0:
        print(f"Error running {script}. Continuing...")
    return result.returncode == 0

def run_command(cmd, cwd=None, check=True):
    """Run a shell command and print its output."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=check, text=True, capture_output=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(e.stderr)
        return False
    except FileNotFoundError as e:
        print(f"Command not found: {e}")
        return False

def main():
    """Build all documentation components."""
    # Create output directories
    ensure_directory("_build/site")

    # Build theory documentation
    print("Building theory documentation...")
    run_script("scripts/build/theory_build.py")

    # Build API documentation
    print("Building API documentation...")
    run_script("scripts/build/api_build.py")

    # Build combined site with Quarto
    print("Building combined site...")
    quarto_success = run_command(["quarto", "render"], check=False)

    if not quarto_success:
        print("Quarto not found or failed. Building without Quarto...")
        print("API documentation is available at _build/api/")
        # Create a simple index page for accessing the API docs directly
        index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Timekeeper Documentation</title>
    <meta http-equiv="refresh" content="0; url=docs/implementation/api/index.html">
</head>
<body>
    <p>Redirecting to <a href="docs/implementation/api/index.html">API documentation</a>...</p>
</body>
</html>"""
        with open("_build/site/index.html", "w") as f:
            f.write(index_html)
    else:
        print("Documentation built successfully!")

    print("You can find the output in the _build directory:")
    print("  - API documentation: _build/api/")
    print("  - Combined site: _build/site/")

    # Serve instructions
    print("\nTo view the documentation, run:")
    print("  python -m http.server -d _build/site 8080")
    print("  Then open http://localhost:8080 in your browser")

if __name__ == "__main__":
    main()
```

## 5. Docstring Format for Theory-Implementation Mapping

Docstrings should follow the Google-style format with additional sections for theoretical references:

```python
def normalize(self, timepoint):
    """
    Normalize a timepoint to its canonical form.

    Implements the normalization procedure from Definition 7 (Canonical Timepoint Representation)
    in the formal theory. Ensures each component a_i satisfies 0 <= a_i < k_i.

    Args:
        timepoint (dict): A dictionary representation of a timepoint

    Returns:
        dict: The normalized timepoint in canonical form

    References:
        - Definition 7: Canonical Timepoint Representation
        - Used in: Axiom 2 (Temporal Addition), Axiom 3 (Temporal Subtraction)

    Theoretical Foundation:
        See theory/formal/definitions.tex, lines 42-50
    """
    # Implementation follows algorithm in Definition 7
    result = timepoint.copy()
    carry = 0

    # Process from finest unit to coarsest, applying normalization
    for i in range(len(self.units) - 1, 0, -1):
        # Rest of the implementation...
```

## 6. Implementation Steps

### 6.1 Setup Phase

1. Create directory structure:

   ```bash
   mkdir -p theory/{formal,mappings,visualization} \
            src/{core/{temporal,morphisms,lattice},adaptive,scheduler,viz} \
            research/{hypotheses,experiments,validation,papers} \
            docs/{theory,implementation/api,research,examples} \
            config/{sphinx,quarto} \
            scripts/build \
            _build/{api,theory,site}
   ```

2. Move existing Sphinx files to the new structure:

   ```bash
   mkdir -p config/sphinx/{modules,_static,_templates}
   mv docs/sphinx/conf.py config/sphinx/
   mv docs/sphinx/index.rst config/sphinx/
   mv docs/sphinx/modules/* config/sphinx/modules/
   mv docs/sphinx/_static/* config/sphinx/_static/
   ```

3. Move Quarto configuration to the new structure:
   ```bash
   mv _quarto.yml config/quarto/
   ```

### 6.2 Configuration Phase

1. Update Sphinx configuration (`config/sphinx/conf.py`)
2. Create or update module RST files (`config/sphinx/modules/*.rst`)
3. Create top-level Quarto configuration (`quarto.yml`)
4. Update Quarto configuration (`config/quarto/_quarto.yml`)

### 6.3 Build Scripts Phase

1. Create API build script (`scripts/build/api_build.py`)
2. Create theory build script (`scripts/build/theory_build.py`)
3. Create research build script (`scripts/build/research_build.py`) if needed
4. Update main build script (`scripts/build_docs.py`)

### 6.4 Content Phase

1. Create basic documentation structure:

   - Theory documentation (`docs/theory/*.qmd`)
   - Implementation documentation (`docs/implementation/*.qmd`)
   - Research documentation (`docs/research/*.qmd`)
   - Example documentation (`docs/examples/*.qmd`)

2. Update Python docstrings with theoretical references

### 6.5 Integration Phase

1. Test build process for all components
2. Verify cross-references between theory and implementation
3. Validate integration through CI/CD pipeline

## 7. CI/CD Integration

Integrate the documentation build into the CI/CD pipeline with GitHub Actions:

```yaml
docs:
  name: Documentation
  needs: test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
        cache: "pip"
    - name: Install Quarto
      uses: quarto-dev/quarto-actions/setup@v2
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install sphinx furo sphinx-autodoc-typehints sphinx-copybutton
        pip install -e .
    - name: Build documentation
      run: python scripts/build_docs.py
    - name: Upload documentation artifact
      uses: actions/upload-artifact@v3
      with:
        name: documentation
        path: _build/site/
    - name: Deploy to GitHub Pages
      if: github.event_name != 'pull_request'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./_build/site
```

## 8. Technical Requirements

- Python 3.8+
- Sphinx 7.0+
- Furo theme (for Sphinx)
- Sphinx extensions:
  - sphinx-autodoc-typehints
  - sphinx-copybutton
  - sphinx-rtd-theme (alternative theme)
- Quarto CLI 1.4+ (optional, build works without it)

## 9. Implementation Timeline

| Phase                | Tasks                                           | Timeline |
| -------------------- | ----------------------------------------------- | -------- |
| **1. Setup**         | Create directory structure, move existing files | Week 1   |
| **2. Configuration** | Update Sphinx/Quarto configurations             | Week 1   |
| **3. Build Scripts** | Create and test build scripts                   | Week 2   |
| **4. Content**       | Create initial documentation structure          | Week 2   |
| **5. Integration**   | Test and validate integration                   | Week 3   |

## 10. Success Criteria

The Sphinx-Quarto integration will be considered successful when:

1. All Python docstrings are properly parsed and displayed in the API documentation
2. The API documentation is seamlessly integrated with the Quarto documentation
3. Cross-references work in both directions (code to concepts, concepts to code)
4. Theory-implementation mappings are clearly documented
5. Documentation builds automatically on code changes
6. All mathematical formulas render correctly in both systems
7. The build process works with and without Quarto
8. The directory structure follows the research-oriented architecture

## 11. Future Enhancements

After implementing the basic integration, consider these enhancements:

1. Automated validation of theory-implementation mappings
2. Interactive visualizations of temporal concepts
3. Automated LaTeX processing for mathematical theory
4. Enhanced search functionality across theory and implementation
5. Version-based documentation with navigation between versions
6. Documentation impact analysis for code changes
