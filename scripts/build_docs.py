#!/usr/bin/env python3
"""
Main documentation build script.

This script coordinates the building of all documentation components:
- Theory documentation from LaTeX sources
- API documentation from Python docstrings using Sphinx
- Research documentation
- Combined site using Quarto (if available)

Usage:
    python scripts/build_docs.py [--serve] [--skip-quarto]

Options:
    --serve       After building, serve the documentation for preview
    --skip-quarto Skip Quarto rendering (useful if Quarto is not installed)
"""
import argparse
import os
import subprocess
import sys
import http.server
import socketserver
from pathlib import Path
import importlib.util


def ensure_directory(dir_path):
    """Ensure a directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


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


def run_script(script_path):
    """Run a Python script and check for errors."""
    print(f"Running {script_path}...")

    # Check if the script exists
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return False

    # Import the script as a module and run its main function
    module_name = Path(script_path).stem
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        # If the module has a main function, call it
        if hasattr(module, "main"):
            module.main()
            return True
        # Otherwise, call its primary function if available
        elif hasattr(module, "build_theory_docs"):
            return module.build_theory_docs()
        elif hasattr(module, "build_api_docs"):
            return module.build_api_docs()
        else:
            print(f"No entry point found in {script_path}")
            return False
    except Exception as e:
        print(f"Error running {script_path}: {e}")
        return False


def build_theory_docs():
    """Build theory documentation."""
    return run_script("scripts/build/theory_build.py")


def build_api_docs():
    """Build API documentation."""
    return run_script("scripts/build/api_build.py")


def build_quarto_docs(skip_quarto=False, serve=False):
    """Build Quarto documentation."""
    if skip_quarto:
        print("Skipping Quarto build as requested.")
        return True

    print("Building Quarto documentation...")

    # Check if Quarto is installed
    quarto_available = run_command(["which", "quarto"], check=False)

    if not quarto_available:
        print("Quarto not found. Skipping Quarto build.")
        return False

    # Build Quarto documentation
    if serve:
        return run_command(["quarto", "preview"])
    else:
        return run_command(["quarto", "render"])


def create_fallback_index():
    """Create a fallback index page if Quarto is not available."""
    print("Creating fallback index page...")

    # Ensure the site directory exists
    site_dir = Path("_build/site")
    ensure_directory(site_dir)

    # Create a simple index.html file
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timekeeper Documentation</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #1565c0;
        }
        a {
            color: #0d6efd;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .card {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .warning {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <h1>Timekeeper Documentation</h1>
    
    <div class="warning">
        <strong>Note:</strong> This is a simplified documentation site. The full Quarto-based
        documentation is not available in this build.
    </div>
    
    <h2>Documentation Sections</h2>
    
    <div class="card">
        <h3>Theory Documentation</h3>
        <p>Mathematical foundation of the Timekeeper framework.</p>
        <a href="docs/theory/index.html">Browse Theory Documentation</a>
    </div>
    
    <div class="card">
        <h3>API Reference</h3>
        <p>Detailed API documentation generated from source code.</p>
        <a href="docs/implementation/api/index.html">Browse API Reference</a>
    </div>
    
    <div class="card">
        <h3>Research Components</h3>
        <p>Research hypotheses, experiments, and results.</p>
        <a href="docs/research/index.html">Browse Research Documentation</a>
    </div>
</body>
</html>"""

    with open(site_dir / "index.html", "w") as f:
        f.write(index_html)

    return True


def serve_documentation(directory="_build/site", port=8080):
    """Serve the documentation from the specified directory."""
    print(f"Serving documentation from {directory} on port {port}...")

    # Change to the directory containing the built documentation
    os.chdir(directory)

    # Create an HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server started at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")


def main():
    parser = argparse.ArgumentParser(description="Build Timekeeper documentation")
    parser.add_argument(
        "--serve", action="store_true", help="Serve documentation after building"
    )
    parser.add_argument(
        "--skip-quarto", action="store_true", help="Skip Quarto rendering"
    )
    args = parser.parse_args()

    # Ensure the build directory exists
    ensure_directory("_build/site")

    # Build theory documentation
    theory_success = build_theory_docs()
    if not theory_success:
        print("Warning: Theory documentation build had issues.")

    # Build API documentation
    api_success = build_api_docs()
    if not api_success:
        print("Warning: API documentation build had issues.")

    # Build Quarto documentation
    quarto_success = build_quarto_docs(skip_quarto=args.skip_quarto, serve=False)

    # If Quarto build failed or was skipped, create a fallback index page
    if not quarto_success:
        create_fallback_index()

    # Summary
    print("\nBuild Summary:")
    print(f"- Theory documentation: {'Success' if theory_success else 'Issues'}")
    print(f"- API documentation: {'Success' if api_success else 'Issues'}")
    print(
        f"- Quarto documentation: {'Success' if quarto_success else 'Skipped/Failed'}"
    )

    # If requested to serve the documentation
    if args.serve:
        serve_documentation()
    else:
        print("\nDocumentation built successfully!")
        print("You can find the output in the _build directory:")
        print("  - API documentation: _build/api/")
        print("  - Theory documentation: _build/theory/")
        print("  - Combined site: _build/site/")
        print("\nTo view the documentation, run:")
        print("  python -m http.server -d _build/site 8080")
        print("  Then open http://localhost:8080 in your browser")


if __name__ == "__main__":
    main()
