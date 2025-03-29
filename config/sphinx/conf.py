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
    "sphinx.ext.autodoc",  # Auto-documentation from docstrings
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinx.ext.viewcode",  # Link to source code
    "sphinx.ext.mathjax",  # LaTeX support
    "sphinx_autodoc_typehints",  # Type hints support
    "sphinx_copybutton",  # Add copy button to code blocks
    "sphinx.ext.intersphinx",  # Link to other documentation
]

# Theme configuration
html_theme = "furo"  # Modern, responsive theme
html_title = "Timekeeper API Documentation"
html_short_title = "Timekeeper API"
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

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
napoleon_custom_sections = ["References", "Theoretical Foundation"]

# Add cross-references to the theory documentation
intersphinx_mapping = {
    "theory": ("../../_build/theory", None),
}

# Other settings
add_module_names = False
autodoc_member_order = "bysource"
autoclass_content = "both"

# Pygments syntax highlighting
pygments_style = "sphinx"
pygments_dark_style = "monokai"

# HTML output settings
html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#1565c0",  # Primary color
        "color-brand-content": "#1565c0",  # Content links
        "color-api-name": "#0d47a1",  # API names
        "color-api-pre-name": "#0d47a1",  # API prefix
    },
    "dark_css_variables": {
        "color-brand-primary": "#42a5f5",  # Primary color (dark mode)
        "color-brand-content": "#42a5f5",  # Content links (dark mode)
        "color-api-name": "#90caf9",  # API names (dark mode)
        "color-api-pre-name": "#90caf9",  # API prefix (dark mode)
    },
}

# Enable "Edit on GitHub" links
html_context = {
    "display_github": True,
    "github_user": "verlyn13",
    "github_repo": "timekeeper",
    "github_version": "main",
    "conf_py_path": "/config/sphinx/",
}

# Add any paths that contain custom static files
html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]

# Add logo if available
# html_logo = "_static/logo.png"
# html_favicon = "_static/favicon.ico"

# Add extra options for the RTD theme
# html_theme_options.update({
#     "repository_url": "https://github.com/verlyn13/timekeeper",
#     "use_repository_button": True,
# })
