# GitHub Repository Setup for CI/CD

This document provides instructions for setting up the necessary GitHub configurations to make the CI/CD workflows function properly.

## Required Setup

### 1. GitHub Pages Permissions

The workflow deploys documentation to GitHub Pages:

1. Go to your repository's **Settings** > **Pages**
2. Ensure **GitHub Actions** is selected as the build and deployment source
3. Set the workflow permissions:
   - Go to **Settings** > **Actions** > **General** > **Workflow permissions**
   - Select **"Read and write permissions"** to allow workflows to write to the repository (required for GitHub Pages deployment)

### 2. PyPI Token for Package Publishing

For publishing releases to PyPI:

1. Create a PyPI API token:

   - Log in to https://pypi.org/
   - Go to **Account settings** > **API tokens** > **Add API token**
   - Give it a name (e.g., "Timekeeper GitHub Actions")
   - Choose "Entire account (all projects)" or scope it to the "timekeeper" project
   - Click "Create"
   - **Copy the token** (you won't see it again!)

2. Add the token to GitHub secrets:
   - Go to your repository's **Settings** > **Secrets and variables** > **Actions**
   - Click **New repository secret**
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the PyPI token you copied
   - Click **Add secret**

## Optional Setup

### 3. Codecov Integration

For code coverage reporting:

1. Sign up or log in at https://codecov.io/
2. Add your GitHub repository to Codecov
3. If needed, add a Codecov token to GitHub secrets:
   - Name: `CODECOV_TOKEN`
   - Value: The token provided by Codecov

### 4. Branch Protection Rules

To ensure code quality:

1. Go to **Settings** > **Branches** > **Add rule**
2. Branch name pattern: `main`
3. Enable:
   - **Require a pull request before merging**
   - **Require status checks to pass before merging**
   - **Require branches to be up to date before merging**
4. Add required status checks (after they've run at least once):
   - `test (3.10)`
   - `security`
   - `docs` (if you want to require documentation builds to pass)

### 5. GitHub Environments

For better control over deployments:

1. Go to **Settings** > **Environments** > **New environment**
2. Name: `production`
3. Configure environment protection rules as desired
4. Add environment secrets if needed

## Troubleshooting

### Workflow Permissions Issues

If you see errors about permissions:

1. Check that workflow permissions are set to "Read and write"
2. For the first run, you may need to approve the workflow in the Actions tab
3. For GitHub Pages, ensure the gh-pages branch exists or that the workflow is allowed to create it

### PyPI Publishing Issues

If package publishing fails:

1. Check that the `PYPI_API_TOKEN` secret is correctly set
2. Ensure the version number in the commit message matches the pattern: `release: vX.Y.Z`
3. Verify that the package builds correctly locally: `python -m build`
4. Check that the package version doesn't already exist on PyPI

### Codecov Integration Issues

If coverage reporting fails:

1. Verify that tests are generating coverage data correctly
2. Check if the repository needs a `CODECOV_TOKEN` secret
3. Look at the Codecov dashboard for specific errors
