# API Documentation

> **Note**: This is a placeholder directory for Sphinx-generated API documentation.

## Overview

This directory contains the API documentation automatically generated from Python docstrings using Sphinx. When the documentation is built, Sphinx processes the Python source code, extracts docstrings, and generates HTML documentation that is placed in this directory.

## Generation Process

The API documentation is generated through the following process:

1. Python source code in the `src/` directory is processed by Sphinx
2. Docstrings are extracted and converted to HTML documentation
3. The generated documentation is placed in this directory
4. Cross-references to the theory documentation are resolved

## Documentation Structure

The API documentation is organized by module:

- **core.temporal**: Documentation for the core temporal system
- **core.morphisms**: Documentation for temporal morphisms
- **core.lattice**: Documentation for lattice operations
- **adaptive**: Documentation for the adaptive temporal system
- **scheduler**: Documentation for the task scheduler
- **viz**: Documentation for visualization components

## Theory-Implementation Mapping

Each class and function in the API documentation includes references to the mathematical definitions, axioms, and theorems it implements. These references are maintained through special docstring sections:

```python
"""
...

References:
    - Definition 1: Temporal Universe
    - Axiom 2: Temporal Addition

Theoretical Foundation:
    See theory/formal/definitions.tex, lines 5-10
"""
```

## Usage

To view the API documentation:

1. Build the documentation using `python scripts/build_docs.py`
2. Open `_build/site/index.html` in a web browser
3. Navigate to the API Reference section

## Implementation Notes

The Sphinx configuration for generating API documentation is located in `config/sphinx/conf.py`. The configuration includes:

- Extensions for processing type hints, mathematical notation, and cross-references
- Theme and styling configuration
- Custom docstring section processing

## Related Documentation

- [Agent Temporal System](../agent_temporal.md): Overview of the core temporal system
- [Task Scheduler](../task_scheduler.md): Overview of the task scheduler
- [Adaptive System](../adaptive_system.md): Overview of the adaptive temporal system
