# Timekeeper

A Hierarchical Partition-Based Approach to Temporal Optimization in Small-Scale Agent Systems

[![Build Status](https://github.com/verlyn13/timekeeper/workflows/Timekeeper%20CI/CD/badge.svg)](https://github.com/verlyn13/timekeeper/actions)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://verlyn13.github.io/timekeeper/)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)

## Integrated Framework Overview

Timekeeper is a comprehensive framework for optimizing temporal dynamics in small-scale agent systems. The project integrates several key components:

1. **Mathematical Foundation**: Rigorous mathematical definitions of temporal hierarchies, operations, and properties
2. **Python Implementation**: Clean, well-documented code that directly implements the mathematical constructs
3. **Interactive Documentation**: Quarto-based documentation system with integrated code execution
4. **Research Framework**: Structured approach to hypothesis tracking and experimental design

This repository contains both the implementation code and the documentation system, tightly integrated to maintain consistency between theory and practice.

## Key Features

- **Hierarchical Temporal Partitioning**: Organize time into nested uniform partitions
- **Timepoint Operations**: Well-defined addition, subtraction, and comparison
- **Human-Agent Time Mapping**: Bidirectional morphisms between agent time and human time
- **Dynamic Adaptability**: Automatic adjustment of temporal granularity
- **Task Scheduling**: Optimized scheduling for small-scale agent systems

## Installation

```bash
# Clone the repository
git clone https://github.com/verlyn13/timekeeper.git
cd timekeeper

# Install the package
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"

# Install documentation dependencies (optional)
pip install -e ".[docs]"
```

## Quick Start

```python
from src.python.agent_temporal import AgentTemporal

# Create a temporal system
temporal = AgentTemporal()

# Create some timepoints
t1 = temporal.create_timepoint(epoch=1, cycle=12, step=30)
t2 = temporal.create_timepoint(cycle=10, step=45)

# Perform operations
t3 = temporal.add_time(t1, cycle=5, step=25)
comparison = temporal.compare_timepoints(t1, t2)

# Convert to human time
human_time = temporal.to_human_time(t3)
print(human_time)  # {'hours': 1, 'minutes': 17, 'seconds': 55}
```

## Documentation System

Timekeeper uses Quarto for documentation, which enables several advanced features:

1. **Mathematical Integration**: Direct mapping between LaTeX definitions and code implementation
2. **Interactive Examples**: Executable code blocks that demonstrate the framework in action
3. **Visualization**: Dynamic visualizations of temporal structures and operations
4. **Advanced Metadata**: Content categorization, status tracking, and filtered browsing

### Building the Documentation

```bash
# Build the documentation
quarto render

# Preview the documentation site
quarto preview
```

### Documentation Structure

- **Concepts**: Theoretical foundations and mathematical explanations
- **Implementation**: Practical guides and code documentation
- **Examples**: Interactive demos and use cases
- **Research**: Hypotheses, experiments, and results

## Development Workflow

The development workflow is designed to maintain consistency between the mathematical theory and code implementation:

1. **Mathematical Foundation**: Formal definitions and properties in LaTeX
2. **Implementation**: Python code with docstrings referencing the mathematical concepts
3. **Documentation**: Quarto documents that explain and demonstrate the implementation
4. **Integration**: Scripts that ensure consistency across all components

### Integration Scripts

Several scripts help maintain integration:

- `scripts/build_docs.py`: Builds API documentation from docstrings
- `scripts/build_website.sh`: Builds the complete Quarto documentation site
- `scripts/integrate_components.py`: Checks consistency across components

```bash
# Check for integration issues
python scripts/integrate_components.py --check

# Fix integration issues
python scripts/integrate_components.py --fix
```

## Project Structure

```
timekeeper/
├── src/
│   ├── python/           # Python implementation
│   ├── js/               # JavaScript implementation (future)
│   └── R/                # R implementation (future)
├── quarto/               # Documentation source
│   ├── concepts/         # Theoretical concepts
│   ├── docs/             # User documentation
│   ├── examples/         # Interactive examples
│   └── research/         # Research materials
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── latex/                # LaTeX source for formal descriptions
├── _quarto.yml           # Quarto configuration
└── styles.css            # Custom styling
```

## Contributing

We welcome contributions from researchers, developers, and users:

1. **Theoretical Extensions**: Extending the mathematical framework
2. **Implementation Improvements**: Enhancing the code implementation
3. **Documentation**: Improving explanations and examples
4. **Research**: Conducting experiments and sharing results

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

[MIT License](LICENSE.md)

## Acknowledgments

This project builds on research in temporal logic, scheduling theory, and agent systems. We acknowledge the contributions of the research community in these fields.
