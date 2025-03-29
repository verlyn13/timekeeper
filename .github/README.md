# Timekeeper GitHub Workflows

This directory contains GitHub Actions workflows for the Timekeeper project. The workflows automate testing, code quality checks, documentation building, and releases.

## CI/CD Workflow Overview

The main CI/CD workflow (`ci.yml`) consists of four jobs:

### 1. Testing and Code Quality

Runs on every push and pull request to the `main` branch:

- Tests on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Runs code quality checks:
  - Black (code formatting)
  - isort (import sorting)
  - mypy (type checking)
  - flake8 (linting)
- Executes unit tests with coverage reporting
- Uploads coverage reports to Codecov

### 2. Security Scanning

Runs after successful tests:

- Scans dependencies for vulnerabilities with Safety
- Runs Bandit for security-focused static analysis
- Generates security reports as build artifacts

### 3. Documentation Building

Runs only on pushes to the `main` branch:

- Builds Sphinx API documentation
- Renders Quarto project
- Combines documentation into a single site
- Deploys to GitHub Pages

### 4. Release Publishing

Runs only on pushes to the `main` branch with a commit message starting with `release:`:

- Extracts version number from commit message
- Updates version in `pyproject.toml`
- Builds and validates Python package
- Creates a GitHub Release
- Publishes package to PyPI

## How to Use This Workflow

### Running Tests Locally

Before pushing code, you can run the same checks locally using the project's Makefile targets:

```bash
# Install development dependencies
make install

# Run individual checks
make lint      # Code quality checks (black, isort, mypy, flake8)
make test      # Run unit tests
make coverage  # Run tests with coverage reporting
make security  # Run security checks
make all-docs  # Build all documentation

# Run all checks (equivalent to CI pipeline)
make check-all

# Validate a release build
make validate-release
```

This ensures your code will pass the CI pipeline before you push your changes.

### Creating Releases

To create a new release:

1. Ensure all tests pass on the `main` branch
2. Push a commit to `main` with a message in the format: `release: vX.Y.Z`
   - Example: `release: v0.2.0`
3. The workflow will automatically:
   - Create a GitHub release with the tag `vX.Y.Z`
   - Publish the package to PyPI

### Manual Workflow Triggering

You can manually trigger the workflow from the GitHub Actions tab:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Timekeeper CI/CD" workflow
3. Click "Run workflow" and select the branch to run on

## Troubleshooting

If a workflow fails, check:

1. **Test failures**: Review the test logs to understand what's failing
2. **Code quality issues**: Check formatting, type, and linting errors
3. **Documentation errors**: Verify that Sphinx and Quarto build correctly locally
4. **Release issues**: Ensure your commit message follows the `release: vX.Y.Z` format

For security scan issues, check the uploaded security report artifacts.
