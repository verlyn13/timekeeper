# Timekeeper Documentation Reorganization Plan

## Current Documentation Issues

1. **Scattered Documentation**: Documents are spread across various locations without clear organization
2. **Redundant Content**: Multiple versions of similar documents (e.g., Sphinx-Quarto integration plans)
3. **Inconsistent Structure**: Actual directory structure doesn't match the one described in docs/README.md
4. **Outdated References**: Some documents reference an older architecture that has been updated
5. **Missing Implementation-Theory Mappings**: The research-oriented architecture requires explicit mappings

## Target Documentation Structure

Based on the updated architecture specification, we will reorganize all documentation to follow this structure:

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
    └── integration-plans/
```

## Reorganization Steps

1. **Create Directory Structure**: Ensure all required directories exist
2. **Categorize Existing Documents**: Review and categorize all existing documentation
3. **Consolidate Redundant Documents**: Merge multiple versions of similar documents
4. **Move Documents**: Place documents in their appropriate directories
5. **Update References**: Update cross-references between documents
6. **Update README**: Update docs/README.md to reflect the new structure

## Document Mapping

| Current Location                                   | New Location                                                     | Action                   |
| -------------------------------------------------- | ---------------------------------------------------------------- | ------------------------ |
| docs/architecture-specification.md                 | docs/architecture/system-overview.md                             | Move and rename          |
| docs/updated-architecture-specification.md         | docs/architecture/system-overview.md                             | Merge with above         |
| docs/implementation-plan.md                        | docs/architecture/development-roadmap.md                         | Move and rename          |
| docs/mvp-development-roadmap.md                    | docs/architecture/development-roadmap.md                         | Merge with above         |
| docs/sphinx-quarto-integration-plan.md             | docs/reference/integration-plans/sphinx-quarto-integration.md    | Move and rename          |
| docs/sphinx-quarto-implementation-steps.md         | docs/reference/integration-plans/sphinx-quarto-implementation.md | Move and rename          |
| docs/sphinx-quarto-updated-implementation-steps.md | docs/reference/integration-plans/sphinx-quarto-implementation.md | Merge with above         |
| docs/migration-plan-sphinx-quarto.md               | docs/reference/migration-guides/sphinx-quarto-migration.md       | Move and rename          |
| docs/theory/\*.qmd                                 | docs/theory/\*.md                                                | Convert format if needed |
| docs/role_definitions/\*                           | docs/reference/role-definitions/                                 | Move                     |
| docs/dev-guides/\*                                 | docs/dev-guides/                                                 | Keep in place            |
| docs/notes/\*                                      | docs/reference/notes/                                            | Move                     |

## Implementation Plan

The reorganization will be implemented in phases:

1. **Phase 1: Create Directory Structure**

   - Create all required directories
   - Update docs/README.md

2. **Phase 2: Move and Consolidate Core Documents**

   - Move architecture and implementation documents
   - Consolidate redundant documents

3. **Phase 3: Organize Specialized Documents**

   - Organize theory, research, and reference documents
   - Update cross-references

4. **Phase 4: Final Validation**
   - Verify all documents are correctly placed
   - Ensure all links and references work
   - Update any remaining references to old locations

## Success Criteria

The reorganization will be considered successful when:

1. All documents are placed in appropriate directories according to the new structure
2. The docs/README.md accurately reflects the new organization
3. All cross-references between documents are updated
4. No redundant or obsolete documents remain
5. The structure aligns with the research-oriented architecture described in the updated architecture specification
