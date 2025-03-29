# Timekeeper Documentation System

This directory contains all documentation for the Timekeeper project, organized according to the research-oriented architecture.

## Documentation Structure

The Timekeeper documentation is organized into the following categories:

```
docs/
├── theory/              # Theory documentation
│   ├── temporal_universe.md
│   ├── hierarchical_partition.md
│   ├── timepoint_operations.md
│   ├── morphisms.md
│   └── lattice_structure.md
├── implementation/      # Implementation documentation
│   ├── agent_temporal.md
│   ├── task_scheduler.md
│   ├── adaptive_system.md
│   └── api/                    # API documentation
├── research/            # Research documentation
│   ├── hypotheses/
│   ├── experiments/
│   └── results/
├── architecture/        # Architecture documentation
│   ├── system-overview.md
│   ├── component-specifications.md
│   ├── integration-strategy.md
│   └── development-roadmap.md
├── dev-guides/          # Developer guides
│   ├── setup-guide.md
│   ├── contribution-guide.md
│   └── rooguide.md
├── examples/            # Example usage
│   ├── basic/
│   └── advanced/
└── reference/           # Reference materials
    ├── migration-guides/
    ├── integration-plans/
    ├── role-definitions/
    └── notes/
```

## Documentation Categories

### Theory Documentation

The `theory/` directory contains documentation on the mathematical foundations of the Timekeeper project, including temporal universe concepts, hierarchical partitions, timepoint operations, morphisms, and lattice structures.

### Implementation Documentation

The `implementation/` directory contains documentation on the implementation of the theoretical concepts, including the AgentTemporal class, task scheduler, adaptive system, and API documentation.

### Research Documentation

The `research/` directory contains documentation related to research activities, including hypotheses, experiments, and results.

### Architecture Documentation

The `architecture/` directory contains high-level architecture documentation, including system overview, component specifications, integration strategy, and development roadmap.

### Developer Guides

The `dev-guides/` directory contains guides for developers, including setup instructions, contribution guidelines, and tool-specific guides.

### Examples

The `examples/` directory contains example usage of the Timekeeper system, ranging from basic to advanced scenarios.

### Reference Materials

The `reference/` directory contains reference materials, including migration guides, integration plans, role definitions, and development notes.

## Documentation Integration

The documentation system is designed to maintain bidirectional traceability between the mathematical theory and its implementation:

1. **Theory-Implementation Mapping**: Clear mapping between theoretical concepts and their implementations
2. **Research Validation**: Experiments and hypotheses explicitly linked to theoretical foundations
3. **API Documentation**: API documentation includes references to theoretical concepts
4. **Examples**: Example usage demonstrates the practical application of theoretical concepts

## Building Documentation

The documentation uses a hybrid approach combining Sphinx for API documentation and Quarto for conceptual documentation and interactive examples.

### Build Process

```bash
# Activate virtual environment (if used)
source .venv/bin/activate

# Build documentation
python scripts/build_docs.py

# Serve documentation locally
python -m http.server -d _build/site 8080
```

## Contributing to Documentation

When adding or modifying documentation:

1. **Place Files Appropriately**: Add files to the appropriate category directory
2. **Maintain Cross-References**: Ensure cross-references between related documents
3. **Theory-Implementation Links**: Maintain links between theoretical concepts and their implementations
4. **Build and Test**: Always build and test the documentation locally before committing
5. **Update READMEs**: Update category README files as needed
