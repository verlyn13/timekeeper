#!/usr/bin/env python3
"""
Script to integrate all components of the Timekeeper project.

This script:
1. Updates Python modules with consistent cross-referencing
2. Ensures documentation files have proper metadata
3. Verifies that mathematical definitions are consistent across code and docs
4. Generates metadata-based navigation
5. Checks for missing links or references

Usage:
    python scripts/integrate_components.py

Options:
    --fix       Automatically fix issues where possible
    --check     Only check for issues without fixing
"""

import argparse
import os
import re
import sys
import glob
import yaml
from pathlib import Path


def ensure_directory(dir_path):
    """Ensure a directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def extract_definitions_from_latex(file_path):
    """Extract definitions, theorems, etc. from a LaTeX file."""
    if not os.path.exists(file_path):
        return {}

    definitions = {}
    with open(file_path, "r") as f:
        content = f.read()

    # Find all definitions, theorems, etc.
    pattern = r"\\begin{(definition|theorem|axiom|property)}\[(.*?)\](.*?)\\end{\1}"
    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        def_type = match[0]
        def_name = match[1]
        def_content = match[2].strip()
        definitions[f"{def_type}:{def_name}"] = def_content

    return definitions


def extract_docstrings_from_python(file_path):
    """Extract docstrings from Python files."""
    if not os.path.exists(file_path):
        return {}

    docstrings = {}
    with open(file_path, "r") as f:
        content = f.read()

    # Find class and method docstrings
    class_pattern = r'class\s+(\w+).*?:\s*"""(.*?)"""'
    method_pattern = r'def\s+(\w+).*?:\s*"""(.*?)"""'

    for pattern, prefix in [(class_pattern, "class"), (method_pattern, "method")]:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            name = match[0]
            docstring = match[1].strip()
            docstrings[f"{prefix}:{name}"] = docstring

    return docstrings


def extract_metadata_from_qmd(file_path):
    """Extract YAML metadata from a Quarto document."""
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        content = f.read()

    if content.startswith("---"):
        # Extract YAML frontmatter
        _, frontmatter, _ = content.split("---", 2)
        try:
            metadata = yaml.safe_load(frontmatter)
            return metadata
        except yaml.YAMLError:
            return {}

    return {}


def check_metadata_consistency():
    """Check for consistent metadata across Quarto documents."""
    print("Checking metadata consistency...")

    qmd_files = glob.glob("quarto/**/*.qmd", recursive=True)

    # Required metadata fields
    required_fields = ["title", "description", "date", "status"]
    status_values = ["Draft", "Review", "Stable", "Experimental", "Deprecated"]

    issues = []

    for file_path in qmd_files:
        metadata = extract_metadata_from_qmd(file_path)

        # Check for required fields
        for field in required_fields:
            if field not in metadata:
                issues.append(f"Missing '{field}' in {file_path}")

        # Check status values
        if "status" in metadata and metadata["status"] not in status_values:
            issues.append(
                f"Invalid status '{metadata['status']}' in {file_path}. Valid values: {', '.join(status_values)}"
            )

    return issues


def check_math_consistency():
    """Check for consistent mathematical definitions across code and documentation."""
    print("Checking mathematical consistency...")

    # Extract definitions from LaTeX
    latex_definitions = extract_definitions_from_latex("latex/formal-description.tex")

    # Extract docstrings from Python
    python_docstrings = {}
    for py_file in glob.glob("src/python/*.py"):
        python_docstrings.update(extract_docstrings_from_python(py_file))

    # Extract math references from Quarto docs
    qmd_files = glob.glob("quarto/concepts/*.qmd")
    qmd_math_references = {}
    for qmd_file in qmd_files:
        with open(qmd_file, "r") as f:
            content = f.read()

        # Look for definition references
        pattern = r":::\s*\.callout-note\s*## Definition \d+: (.*?)\s+"
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            def_name = match.strip()
            qmd_math_references[f"definition:{def_name}"] = qmd_file

    # Check for definitions in LaTeX not referenced in QMD
    issues = []
    for def_key, def_content in latex_definitions.items():
        def_type, def_name = def_key.split(":")
        if f"{def_type}:{def_name}" not in qmd_math_references:
            issues.append(
                f"LaTeX definition '{def_name}' not referenced in Quarto docs"
            )

    # Check for Python classes/methods not documenting their mathematical basis
    for docstring_key, docstring in python_docstrings.items():
        prefix, name = docstring_key.split(":")
        if (
            prefix == "class"
            and "Definition" not in docstring
            and "Definitions" not in docstring
        ):
            issues.append(
                f"Python class '{name}' is missing mathematical definition references in docstring"
            )

    return issues


def check_cross_references():
    """Check for broken links and cross-references."""
    print("Checking cross-references...")

    issues = []

    # Get all existing files
    qmd_files = [
        os.path.normpath(f) for f in glob.glob("quarto/**/*.qmd", recursive=True)
    ]
    qmd_files = [f.replace("\\", "/") for f in qmd_files]  # Normalize paths

    # Check links in QMD files
    for file_path in qmd_files:
        with open(file_path, "r") as f:
            content = f.read()

        # Find all links
        link_pattern = r"\[.*?\]\((.*?)\.qmd\)"
        matches = re.findall(link_pattern, content)

        for match in matches:
            target = match.strip()
            target_file = f"{target}.qmd"

            # Make relative links absolute for checking
            if not target.startswith("/"):
                base_dir = os.path.dirname(file_path)
                target_file = os.path.normpath(os.path.join(base_dir, target_file))
                target_file = target_file.replace("\\", "/")  # Normalize path

            if target_file not in qmd_files:
                issues.append(f"Broken link in {file_path}: {target}.qmd")

    return issues


def check_documentation_coverage():
    """Check if all Python modules, classes, and methods are documented."""
    print("Checking documentation coverage...")

    issues = []

    # Get all Python modules
    py_files = glob.glob("src/python/*.py")

    for py_file in py_files:
        module_name = os.path.basename(py_file).replace(".py", "")

        # Check if module has corresponding documentation
        qmd_file = f"quarto/docs/api/{module_name}.qmd"
        if not os.path.exists(qmd_file):
            issues.append(f"Missing API documentation for module {module_name}")

        # Extract classes from Python file
        with open(py_file, "r") as f:
            content = f.read()

        class_pattern = r"class\s+(\w+)"
        classes = re.findall(class_pattern, content)

        for class_name in classes:
            # Check if class is mentioned in documentation
            if os.path.exists(qmd_file):
                with open(qmd_file, "r") as f:
                    doc_content = f.read()

                if class_name not in doc_content:
                    issues.append(f"Class {class_name} not documented in {qmd_file}")

    return issues


def generate_concept_index():
    """Generate an index of concepts based on Quarto documents."""
    print("Generating concept index...")

    # Get all concept documents
    concept_files = glob.glob("quarto/concepts/*.qmd")

    # Extract metadata
    concepts = []
    for file_path in concept_files:
        metadata = extract_metadata_from_qmd(file_path)
        if "title" in metadata:
            concepts.append(
                {
                    "title": metadata["title"],
                    "description": metadata.get("description", ""),
                    "status": metadata.get("status", "Unknown"),
                    "path": os.path.basename(file_path),
                    "tags": metadata.get("tags", []),
                }
            )

    # Sort by title
    concepts.sort(key=lambda x: x["title"])

    # Create index document
    output_path = "quarto/concepts/index.qmd"

    with open(output_path, "w") as f:
        f.write("---\n")
        f.write('title: "Core Concepts"\n')
        f.write('description: "Foundational concepts of the Timekeeper framework"\n')
        f.write('date: "2025-03-28"\n')
        f.write("categories: [Concept]\n")
        f.write('status: "Stable"\n')
        f.write("---\n\n")

        f.write("# Core Concepts of the Timekeeper Framework\n\n")
        f.write(
            "This section outlines the core theoretical concepts that form the foundation of the Timekeeper framework.\n\n"
        )

        f.write("## Concept Map\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")

        # Add nodes
        for i, concept in enumerate(concepts):
            f.write(f'  C{i}["{concept["title"]}"]\n')

        # Add simple relationships based on tags
        for i, concept_i in enumerate(concepts):
            for j, concept_j in enumerate(concepts):
                if i != j:
                    # Look for overlapping tags
                    common_tags = set(concept_i.get("tags", [])) & set(
                        concept_j.get("tags", [])
                    )
                    if common_tags and j > i:  # Only connect in one direction
                        tag = next(iter(common_tags))
                        f.write(f"  C{i} --> C{j}\n")

        f.write("```\n\n")

        f.write("## Overview of Concepts\n\n")

        # Write concept list
        for concept in concepts:
            f.write(f"### [{concept['title']}]({concept['path']})\n\n")
            f.write(f"{concept['description']}\n\n")
            f.write(
                f'<span class="status-{concept["status"].lower()}">{concept["status"]}</span>\n\n'
            )

    print(f"Generated concept index at {output_path}")


def fix_issues(issues, args):
    """Fix identified issues where possible."""
    if not args.fix:
        return

    print("Fixing issues...")

    # Example fixes (would need to be expanded for each issue type)
    for issue in issues:
        if "Missing 'title' in" in issue:
            file_path = issue.split("Missing 'title' in ")[1]
            print(f"  Adding title to {file_path}")

            with open(file_path, "r") as f:
                content = f.read()

            # Add basic title
            title = (
                os.path.basename(file_path)
                .replace(".qmd", "")
                .replace("-", " ")
                .title()
            )
            if content.startswith("---"):
                _, frontmatter, remainder = content.split("---", 2)
                frontmatter += f'title: "{title}"\n'
                content = f"---\n{frontmatter}---\n{remainder}"
            else:
                content = f'---\ntitle: "{title}"\n---\n\n{content}'

            with open(file_path, "w") as f:
                f.write(content)

        # More issue types could be handled here

    print("Fixed issues where possible.")


def main():
    parser = argparse.ArgumentParser(
        description="Integrate components of the Timekeeper project"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Automatically fix issues where possible"
    )
    parser.add_argument(
        "--check", action="store_true", help="Only check for issues without fixing"
    )
    args = parser.parse_args()

    # Collect all issues
    all_issues = []
    all_issues.extend(check_metadata_consistency())
    all_issues.extend(check_math_consistency())
    all_issues.extend(check_cross_references())
    all_issues.extend(check_documentation_coverage())

    # Report issues
    if all_issues:
        print("\nIssues found:")
        for issue in all_issues:
            print(f"  - {issue}")

        # Fix issues if requested
        if args.fix:
            fix_issues(all_issues, args)

        if args.check:
            sys.exit(1)
    else:
        print("\nNo issues found.")

    # Generate indices
    generate_concept_index()

    print("\nIntegration completed successfully.")


if __name__ == "__main__":
    main()
