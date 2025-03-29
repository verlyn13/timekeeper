"""
Sphinx configuration for Timekeeper API documentation.
"""

import os
import sys
from datetime import datetime

# Add the source directory to the path so Sphinx can find the modules
sys.path.insert(0, os.path.abspath("../../src/python"))

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
napoleon_custom_sections = None

# Other settings
add_module_names = False
autodoc_member_order = "bysource"
autoclass_content = "both"
