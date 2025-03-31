
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.abspath("/home/verlyn13/Projects/timekeeper/src"))

# Project information
project = "Timekeeper"
copyright = "2025, Timekeeper Contributors"
author = "Timekeeper Contributors"
version = "0.1.0"
release = "0.1.0"

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
]

# Theme configuration
html_theme = 'furo'
html_title = 'Timekeeper API Documentation'
html_short_title = 'Timekeeper API'
html_static_path = ['_static']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_custom_sections = [
    'References',
    'Theoretical Foundation'
]

# Other settings
add_module_names = False
autodoc_member_order = 'bysource'
autoclass_content = 'both'
