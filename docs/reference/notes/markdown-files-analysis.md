# Markdown Files Analysis and Recommendations

This document analyzes all markdown files in the project, identifies their purpose, and recommends actions to properly organize them according to the new directory structure.

## Root Level Markdown Files

| File                 | Purpose                                  | Recommendation                                                                     |
| -------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------- |
| README.md            | Main project README                      | **Keep in place** - This is the standard location for the main project README      |
| LICENSE.md           | Project license information              | **Keep in place** - This is the standard location for license information          |
| INTEGRATION_GUIDE.md | Guide for integrating with Timekeeper    | **Move** to `docs/dev-guides/integration-guide.md`                                 |
| forme.md             | Personal notes or draft (needs checking) | **Review and decide** - May need to be moved to `docs/reference/notes/` or removed |
| pyproject.md.orig    | Original version of a modified file      | **Review and remove** if no longer needed (appears to be a backup file)            |

## Docs Directory Files That Need Attention

| File                                               | Purpose                           | Current Status                                   | Recommendation                                                              |
| -------------------------------------------------- | --------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| docs/architecture-specification.md                 | Original architecture spec        | Needs to be moved                                | **Move** to `docs/architecture/system-overview.md`                          |
| docs/updated-architecture-specification.md         | Updated architecture spec         | Already consolidated into system-overview.md     | **Remove** after verifying all content preserved                            |
| docs/implementation-plan.md                        | Implementation plan               | Needs to be moved                                | **Move** to `docs/architecture/development-roadmap.md`                      |
| docs/mvp-development-roadmap.md                    | MVP roadmap                       | Already consolidated into development-roadmap.md | **Remove** after verifying all content preserved                            |
| docs/sphinx-quarto-integration-plan.md             | Integration plan                  | Needs to be moved                                | **Move** to `docs/reference/integration-plans/sphinx-quarto-integration.md` |
| docs/sphinx-quarto-implementation-steps.md         | Implementation steps              | Needs to be moved                                | **Move** to `docs/reference/integration-plans/sphinx-quarto-integration.md` |
| docs/sphinx-quarto-updated-implementation-steps.md | Updated implementation steps      | Needs to be moved                                | **Move** to `docs/reference/integration-plans/sphinx-quarto-integration.md` |
| docs/migration-plan-sphinx-quarto.md               | Migration plan                    | Needs to be moved                                | **Move** to `docs/reference/migration-guides/sphinx-quarto-migration.md`    |
| docs/documentation-organization-plan.md            | Documentation reorganization plan | Active reference during reorganization           | **Move** to `docs/reference/notes/` once reorganization is complete         |
| docs/documentation-reorganization-summary.md       | Summary of reorganization         | Active reference during reorganization           | **Move** to `docs/reference/notes/` once reorganization is complete         |

## Role Definitions Files - COMPLETED

| File                                        | Purpose                        | Status                                                               |
| ------------------------------------------- | ------------------------------ | -------------------------------------------------------------------- |
| docs/role_definitions/architect_role.md     | Architect role definition      | **MOVED** to `docs/reference/role-definitions/architect_role.md`     |
| docs/role_definitions/documentation_role.md | Documentation role definition  | **MOVED** to `docs/reference/role-definitions/documentation_role.md` |
| docs/role_definitions/sample-roo-configs/\* | Sample Roo configuration files | **MOVED** to `docs/reference/role-definitions/sample-roo-configs/`   |

## Notes Files - COMPLETED

| File                                     | Purpose            | Status                                                            |
| ---------------------------------------- | ------------------ | ----------------------------------------------------------------- |
| docs/notes/sphinx-quarto-organization.md | Organization notes | **MOVED** to `docs/reference/notes/sphinx-quarto-organization.md` |

## TODO: Missing Files

Based on the research-oriented architecture, these files should be created:

### Theory Documentation

- docs/theory/temporal_universe.md (convert from current .qmd)
- docs/theory/hierarchical_partition.md (convert from current .qmd)
- docs/theory/timepoint_operations.md (convert from current .qmd)
- docs/theory/morphisms.md (convert from current .qmd)
- docs/theory/lattice_structure.md (convert from current .qmd)

### Implementation Documentation

- docs/implementation/agent_temporal.md (needs to be created)
- docs/implementation/task_scheduler.md (needs to be created)
- docs/implementation/adaptive_system.md (needs to be created)

### Architecture Documentation

- docs/architecture/component-specifications.md (needs to be created)
- docs/architecture/integration-strategy.md (needs to be created)

### Developer Guides

- docs/dev-guides/setup-guide.md (needs to be created)
- docs/dev-guides/contribution-guide.md (needs to be created)

## Updated Action Plan

1. **Next Steps**: Move integration plans to their new location
2. **After That**: Move migration guides to their new location
3. **Then**: Move and merge architecture specification documents
4. **Finally**: Create placeholder files for missing documentation and document the gaps
