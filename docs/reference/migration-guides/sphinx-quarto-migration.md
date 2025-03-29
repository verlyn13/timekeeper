# Migration Plan: Sphinx-Quarto Integration to Research-Oriented Architecture

## Overview

This document outlines the step-by-step process to migrate from the current Sphinx-Quarto implementation to the new research-oriented architecture described in the [Updated Architecture Specification](../../architecture/system-overview.md). This plan ensures a smooth transition while preserving existing work and minimizing disruption.

## Current vs. Target State

### Current State

- Sphinx configuration in `docs/sphinx/`
- Quarto configuration in project root (`_quarto.yml`)
- Build script in `scripts/build_docs.py`
- Documentation outputs to `_site/`

### Target State

- Theory-implementation-research based structure
- Configuration files in `config/{sphinx,quarto}/`
- Build scripts in `scripts/build/`
- Enhanced docstrings with theoretical references
- Comprehensive build system for all documentation types
- Output to `_build/{theory,api,site}/`

## Migration Steps

### Phase 1: Preparation (Day 1)

1. **Create Backup**

   ```bash
   # Create a backup branch
   git checkout -b pre-migration-backup
   git add .
   git commit -m "Backup before migration to research-oriented architecture"
   git checkout main
   ```

2. **Create New Directory Structure**
   ```bash
   # Create new directories
   mkdir -p theory/{formal,mappings,visualization} \
            config/{sphinx,quarto} \
            scripts/build \
            _build/{api,theory,site} \
            docs/{theory,implementation/api,research/{hypotheses,experiments,results},examples}
   ```

### Phase 2: Migration of Configuration Files (Day 1)

1. **Migrate Sphinx Configuration**

   ```bash
   # Move and adapt Sphinx configuration
   cp -r docs/sphinx/conf.py config/sphinx/
   cp -r docs/sphinx/index.rst config/sphinx/
   cp -r docs/sphinx/modules/ config/sphinx/
   cp -r docs/sphinx/_static/ config/sphinx/
   cp -r docs/sphinx/_templates/ config/sphinx/
   ```

   Then edit `config/sphinx/conf.py` to:

   - Update import paths
   - Add theory-specific extensions
   - Configure cross-references
   - Add custom sections for theoretical references

2. **Migrate Quarto Configuration**

   ```bash
   # Move Quarto configuration
   cp _quarto.yml config/quarto/
   ```

   Create a simplified top-level `quarto.yml`:

   ```yaml
   project:
     type: website
     output-dir: _build/site

   render:
     - docs/**/*.qmd

   include-in-project:
     - config/quarto/_quarto.yml
   ```

   Update `config/quarto/_quarto.yml` to:

   - Reference the new directory structure
   - Include theory, implementation, and research sections
   - Update paths for API references

### Phase 3: Migration of Build Scripts (Day 2)

1. **Create New Build Scripts**
   Create `scripts/build/api_build.py`, `scripts/build/theory_build.py`, and update `scripts/build_docs.py` according to the implementation steps.

2. **Test Build Process**

   ```bash
   # Test API documentation build
   python scripts/build/api_build.py

   # Test main build script
   python scripts/build_docs.py
   ```

3. **Validate Outputs**
   - Check `_build/api/` for API documentation
   - Check `_build/site/` for the combined site

### Phase 4: Content Migration (Day 2-3)

1. **Create Basic Documentation Structure**
   Create initial Quarto files for theory, implementation, and research sections as outlined in the implementation steps.

2. **Migrate Existing Content**
   For each existing documentation file:

   - Determine the appropriate location in the new structure
   - Update internal references to match new paths
   - Enhance with theory references where appropriate

3. **Create Placeholder Files**
   For theoretical components not yet documented, create placeholder files with basic structure.

### Phase 5: Source Code Updates (Day 3-4)

1. **Update Docstrings**
   Progressively update Python docstrings to include references to theoretical components, starting with the most important classes and functions.

2. **Create Theory-Implementation Mappings**
   Create initial YAML mapping files in `theory/mappings/` to document the relationships between theoretical definitions and their implementations.

### Phase 6: Testing and Refinement (Day 4-5)

1. **Test Full Documentation Build**

   ```bash
   python scripts/build_docs.py
   ```

2. **Fix Issues and Refine**

   - Address any issues discovered during testing
   - Refine cross-references and navigation
   - Improve styling and consistency

3. **Update CI/CD Pipeline**
   If using CI/CD, update workflow files to use the new build process.

## Parallel Development Strategy

During the migration, you may need to maintain both old and new structures temporarily. Consider:

1. **Feature Flags**
   Add a command-line flag to build scripts to toggle between old and new structures:

   ```bash
   python scripts/build_docs.py --use-new-architecture
   ```

2. **Gradual Transition**
   Move components one at a time, validating each step:

   - Start with configuration files
   - Then build scripts
   - Then content
   - Finally, update source code

3. **Documentation**
   Keep the team informed about the migration status and any temporary workarounds needed during the transition.

## Post-Migration Cleanup

After successful migration and verification:

1. **Remove Deprecated Files**

   ```bash
   # Remove old directories after ensuring they've been migrated
   rm -rf docs/sphinx
   rm -f _quarto.yml # if replaced by quarto.yml and config/quarto/_quarto.yml
   ```

2. **Update Documentation**
   Update the main README.md and other guides to reflect the new structure and build process.

3. **Team Training**
   Conduct a brief session to familiarize the team with the new structure and workflow.

## Rollback Plan

If serious issues arise during migration:

1. **Git Rollback**

   ```bash
   git checkout pre-migration-backup
   git checkout -b migration-retry
   ```

2. **Partial Rollback**
   If only specific components are problematic, consider rolling back just those components while keeping successfully migrated parts.

## Timeline

| Day | Tasks                                                                  |
| --- | ---------------------------------------------------------------------- |
| 1   | Create backup, set up directory structure, migrate configuration files |
| 2   | Migrate and test build scripts, start content migration                |
| 3   | Continue content migration, start updating docstrings                  |
| 4   | Complete docstring updates, test full build, start refinement          |
| 5   | Complete refinement, update CI/CD, clean up, team training             |

## Success Criteria

The migration will be considered successful when:

1. All documentation builds successfully using the new structure
2. Theory-implementation cross-references work correctly
3. The build process is more robust and maintainable
4. The directory structure clearly separates concerns
5. Mathematical theory and implementation are explicitly connected

## Additional Considerations

1. **Documentation Map**
   Create a visual map of how documentation components relate to each other in the new structure.

2. **Navigation Guide**
   Provide a guide for users to navigate between different types of documentation.

3. **Search Integration**
   Ensure search functionality works across all documentation types.

4. **Performance**
   Monitor build time and optimize if necessary for larger documentation sets.

## Related Documents

- [Sphinx-Quarto Integration Plan](../integration-plans/sphinx-quarto-integration.md)
- [System Architecture Overview](../../architecture/system-overview.md)
- [Development Roadmap](../../architecture/development-roadmap.md)
