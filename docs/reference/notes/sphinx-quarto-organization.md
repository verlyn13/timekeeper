# File Organization Recommendations for Sphinx-Quarto Integration

## Current Structure and Observations

During the implementation of the Sphinx-Quarto integration, I observed some organizational aspects that could be improved for clarity:

1. **CSS File Duplication**: There's a `styles.css` in the project root that appears to be for Quarto, but the relationship isn't immediately clear. When working in `_site`, another CSS file had to be created/copied.

2. **Build Output Directories**: Both Quarto and Sphinx have their own build output preferences, leading to a merged `_site` directory with varied structure.

3. **Documentation Source Locations**: Documentation sources are spread across multiple directories:
   - `docs/`: Contains architectural documentation and Sphinx sources
   - `quarto/`: Contains Quarto-specific files
   - Project root: Contains some config files like `_quarto.yml`

## Recommendations for Improved Organization

### 1. Clear Directory Structure

```
timekeeper/
├── docs/
│   ├── sphinx/              # Sphinx configuration and source
│   │   └── ...
│   ├── quarto/              # Quarto configuration and source
│   │   └── ...
│   ├── assets/              # Shared assets (images, styles, etc.)
│   │   ├── css/             # All stylesheets
│   │   └── images/          # All documentation images
│   └── architecture/        # Architecture documentation
├── src/
│   └── python/              # Python source code
└── _build/                  # All build outputs
    ├── sphinx/              # Sphinx output
    ├── quarto/              # Quarto output
    └── site/                # Combined site
```

### 2. Configuration File Organization

1. **Move `_quarto.yml` to `docs/quarto/`**: This makes it clear that it's part of the documentation system, not a project-level file.

2. **Create a `docs/config/` directory**: Place all documentation configuration files here, with clear naming:

   - `sphinx_config.py` (instead of conf.py)
   - `quarto_config.yml` (instead of \_quarto.yml)

3. **Add README files**: In each directory, include a README.md that explains what the directory contains and how it relates to other components.

### 3. Build Script Improvements

1. **Add configuration options**: Allow users to specify output directories, enabling different build targets (development, production, etc.).

2. **Add documentation**: Comment the build script better and include a README for the CI/CD process.

3. **Standardize references**: Ensure all paths in configuration files use consistent relative paths, ideally through variables.

### 4. Style Organization

1. **Move all stylesheets to `docs/assets/css/`**: This centralizes styling and makes it clear where to modify appearance.

2. **Use namespacing for styles**: Adopt a convention like `tk-sphinx.css` and `tk-quarto.css` to make the purpose clear.

3. **Create a shared stylesheet**: Extract common styles to `tk-common.css` to maintain consistency.

### 5. Documentation Pointers

1. **Add a top-level documentation README**: At `docs/README.md`, explain the overall documentation system, how it's built, and where to find different components.

2. **Create a documentation map**: Add a simple diagram showing the relationship between documentation components.

3. **Implement cross-references**: Ensure Sphinx and Quarto documents can reference each other clearly.

## Implementation Timeline

While some of these changes may be substantial for the current project state, they could be implemented gradually:

1. **Immediate**: Add clarifying READMEs and create the documentation map
2. **Short-term**: Move stylesheets and standardize naming
3. **Medium-term**: Restructure directories while maintaining backward compatibility
4. **Long-term**: Fully implement the new directory structure with build script enhancements

## Conclusion

These recommendations aim to create a more intuitive project structure where the purpose of each file is immediately clear from its location. This will reduce confusion, minimize duplication, and make the documentation system more maintainable as it grows.
