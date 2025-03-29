#!/bin/bash
# Script to build the Timekeeper documentation website

set -e # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Timekeeper documentation website...${NC}"

# Check dependencies
if ! command -v quarto &>/dev/null; then
    echo -e "${RED}Quarto not found. Please install Quarto from https://quarto.org/docs/get-started/${NC}"
    exit 1
fi

if ! command -v python &>/dev/null; then
    echo -e "${RED}Python not found. Please install Python 3.7 or higher.${NC}"
    exit 1
fi

# Check for required Python packages
python -c "import yaml, matplotlib, numpy, networkx" 2>/dev/null || {
    echo -e "${YELLOW}Installing required Python packages...${NC}"
    pip install pyyaml matplotlib numpy networkx
}

# Create directories if they don't exist
echo -e "${GREEN}Ensuring directory structure...${NC}"
mkdir -p quarto/concepts quarto/docs quarto/examples quarto/research quarto/browse quarto/_templates

# Generate API documentation
echo -e "${GREEN}Generating API documentation...${NC}"
python scripts/build_docs.py

# Generate browse pages if they don't exist
echo -e "${GREEN}Checking for browse pages...${NC}"
if [ ! -f "quarto/browse/status.qmd" ]; then
    echo -e "${YELLOW}Creating status browse page...${NC}"
    cat >quarto/browse/status.qmd <<'EOF'
---
title: "Browse by Status"
page-layout: full
toc: false
listing:
  contents:
    - "../concepts/*.qmd"
    - "../docs/*.qmd"
    - "../examples/*.qmd"
    - "../research/*.qmd"
  type: grid
  sort: "date desc"
  categories: false
  sort-ui: true
  filter-ui: true
  field-display-names:
    status: "Status"
  fields: [title, description, date, status]
  filter: status
---

Browse content by status. This is useful for tracking the development stage of different documentation components.

```{python}
#| echo: false
#| output: asis

import os
import glob
import yaml
from collections import defaultdict

# Function to extract frontmatter
def extract_frontmatter(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        if content.startswith('---'):
            # Extract YAML frontmatter
            _, frontmatter, _ = content.split('---', 2)
            try:
                metadata = yaml.safe_load(frontmatter)
                return metadata
            except yaml.YAMLError:
                return {}
    return {}

# Find all qmd files
qmd_files = []
for pattern in ['../concepts/*.qmd', '../docs/*.qmd', '../examples/*.qmd', '../research/*.qmd']:
    qmd_files.extend(glob.glob(pattern))

# Group by status
status_groups = defaultdict(list)

for file in qmd_files:
    metadata = extract_frontmatter(file)
    if 'status' in metadata:
        status = metadata.get('status', 'Unknown')
        title = metadata.get('title', os.path.basename(file))
        rel_path = os.path.relpath(file, '..')
        status_groups[status].append((title, f"../{rel_path}"))

# Output status groups
for status, files in sorted(status_groups.items()):
    print(f"## {status}\n")
    print("<ul>")
    for title, path in sorted(files):
        print(f'<li><a href="{path}">{title}</a></li>')
    print("</ul>\n")
```
EOF
fi

if [ ! -f "quarto/browse/recent.qmd" ]; then
    echo -e "${YELLOW}Creating recent updates browse page...${NC}"
    cat >quarto/browse/recent.qmd <<'EOF'
---
title: "Recent Updates"
page-layout: full
toc: false
listing:
  contents:
    - "../concepts/*.qmd"
    - "../docs/*.qmd"
    - "../examples/*.qmd"
    - "../research/*.qmd"
  type: table
  sort: "date desc"
  categories: true
  sort-ui: false
  filter-ui: true
  fields: [title, description, date, status, categories]
  date-format: "YYYY-MM-DD"
---

Browse the most recently updated documentation.
EOF
fi

# Build the website
echo -e "${GREEN}Building Quarto website...${NC}"
quarto render

echo -e "${GREEN}Documentation website built successfully!${NC}"
echo -e "${GREEN}Output is in the _site directory.${NC}"
echo -e "${YELLOW}To preview the site locally, run: quarto preview${NC}"
