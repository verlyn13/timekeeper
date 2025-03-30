# Vertex AI Workbench Integration Plan

**Date:** 2025-03-30

**Status:** Proposed

**Objective:** Integrate Google Cloud Vertex AI Workbench into the Timekeeper project workflow as a primary environment for interactive research, development, testing, and documentation tasks, ensuring alignment with existing architectural patterns, security practices, and documentation standards.

---

## Prerequisites

- **GCP Project:** An existing Google Cloud project with billing enabled.
- **IAM Permissions:** The user executing this plan requires sufficient IAM permissions in the GCP project (e.g., roles like `roles/owner`, or a combination including `compute.admin`, `iam.serviceAccountAdmin`, `aiplatform.admin`, `serviceusage.serviceUsageAdmin`, `resourcemanager.projectIamAdmin`) to enable APIs, manage IAM policies, and create/manage Vertex AI Workbench instances.
- **Service Account:** The dedicated service account (`happypatterns@...`) must exist.
- **Tools:** `gcloud` CLI installed locally or access via Google Cloud Shell.
- **Repository Access:** Access to clone the Timekeeper Git repository.

---

## Phase 1: GCP Foundation & Security Alignment

**Goal:** Verify and document the GCP environment configuration aligns with Workbench needs and Timekeeper's security patterns.

### Task 1.1: Verify API Enablement

- **Objective:** Confirm necessary GCP APIs are enabled.
- **Actions:**
  - Navigate to GCP Console -> APIs & Services -> Enabled APIs.
  - Verify `Vertex AI API` (aiplatform.googleapis.com) is listed and enabled.
  - Verify `Compute Engine API` (compute.googleapis.com) is listed and enabled.
- **Deliverable:** Confirmation screenshot or note added to this plan's execution log.

### Task 1.2: Review IAM & Service Account Permissions

- **Objective:** Ensure the dedicated Service Account (`happypatterns@...`) has the minimum necessary permissions for Workbench operations.
- **Actions:**
  - Review roles currently assigned (Ref: `docs/reference/gcp-consultant-recommendation.md`, `memory-bank/decisionLog.md [2025-03-29 21:24:00]`). Current roles: `roles/aiplatform.user`, `roles/aiplatform.serviceAgent`, `roles/compute.serviceAgent`.
  - Analyze potential future needs (e.g., specific GCS bucket access for research data, calling specific Vertex AI model endpoints).
  - If additional permissions are needed, grant them following the principle of least privilege via GCP Console IAM or `gcloud projects add-iam-policy-binding`.
  - **Note:** Start with the existing roles. Only add specific permissions (e.g., `roles/storage.objectViewer` for a specific bucket) if a workflow in Phase 3 explicitly fails due to lack of access. Avoid overly broad roles.
- **Deliverable:** Documented confirmation of roles (or justification for changes) in this plan's execution log. Updated `memory-bank/decisionLog.md` if roles are changed.

### Task 1.3: Document Workbench Authentication Strategy

- **Objective:** Clearly document how user and service account authentication works specifically for Workbench within the Timekeeper project.
- **Actions:**
  - Create a new section in an appropriate dev guide (e.g., `docs/dev-guides/gcp-integration.md` or create `docs/dev-guides/vertex-ai-workbench-setup.md`).
  - Explain:
    - Users access the JupyterLab UI via their own GCP identity (User ADC).
    - The Workbench _instance_ runs _as_ the dedicated Service Account (`happypatterns@...`).
    - Code run _within_ the instance authenticates to other GCP services using the Service Account's permissions automatically.
  - Add a cross-reference note to `memory-bank/gcp-credentials-integration.md`.
- **Deliverable:** New/updated section in the developer guide. Note added to `memory-bank/gcp-credentials-integration.md`.

### Task 1.4: Finalize Network Configuration Decision

- **Objective:** Decide and document the networking setup for Workbench instances.
- **Actions:**
  - Evaluate if instances need placement in a specific VPC/subnet or require Private Google Access.
  - Default VPC is the initial assumption unless specific needs arise.
  - Document the decision (e.g., "Default VPC sufficient for initial phase") and rationale.
- **Deliverable:** Documented decision added to `docs/architecture/system-overview.md` or a dedicated networking section/document.

### Task 1.5: Verify Budget Alerts

- **Objective:** Ensure cost monitoring is in place.
- **Actions:**
  - Navigate to GCP Console -> Billing -> Budgets & alerts.
  - Confirm an active budget alert exists for the project encompassing Compute Engine and Vertex AI costs.
- **Deliverable:** Confirmation screenshot or note added to this plan's execution log.

### Task 1.6: Update Memory Bank (Phase 1 Completion)

- **Objective:** Record the completion of Phase 1 foundational work.
- **Actions:**
  - Update `memory-bank/progress.md`: Mark Phase 1 tasks as complete.
  - Update `memory-bank/activeContext.md`: Note completion of foundational setup.
  - Update `memory-bank/decisionLog.md`: Add entries for any specific decisions made (e.g., final network config).
- **Deliverable:** Updated Memory Bank files.

---

## Phase 2: Workbench Instance Provisioning & Environment Replication

**Goal:** Deploy a standardized Workbench instance capable of running the full Timekeeper development workflow.

### Task 2.1: Define Standard Instance Configuration

- **Objective:** Create a template for consistent Workbench instance creation.
- **Actions:**
  - Draft the standard configuration details:
    - **Instance Type:** Vertex AI Managed Notebooks
    - **Region:** `us-central1` (or other preferred region)
    - **Environment:** `Python 3 (with Intel® MKL)` (Image Family: `python-3-notebooks` or similar standard Python 3.11+ environment)
    - **Machine Type:** `e2-standard-4` (4 vCPU, 16 GB RAM - adjust based on typical workload, monitor cost)
    - **GPU:** None (Add if required for specific ML tasks)
    - **Data disk:** 100 GB Standard Persistent Disk (adjust size if large datasets are stored locally)
    - **Service Account:** `happypatterns@...` (Ensure this is selected under 'Permission')
    - **Networking:** Default VPC network (Confirm based on Task 1.4 decision)
    - **Idle Shutdown:** Enabled, 60 minutes timeout (Crucial for cost control)
    - **Example `gcloud` command:**
      ```bash
      gcloud notebooks managed create timekeeper-workbench-std \
        --location=us-central1 \
        --vm-image-family=python-3-notebooks \
        --machine-type=e2-standard-4 \
        --data-disk-size-gb=100 \
        --data-disk-type=PD_STANDARD \
        --service-account="happypatterns@<your-project-id>.iam.gserviceaccount.com" \
        --network=default \
        --metadata=idle-timeout-seconds=3600
      ```
      _(Note: Replace `<your-project-id>` with the actual project ID)_
  - Document this configuration in `docs/dev-guides/vertex-ai-workbench-setup.md` (create file if it doesn't exist).
- **Deliverable:** Documented standard configuration in the setup guide.

### Task 2.2: Develop Environment Setup Script

- **Objective:** Automate the setup of the Timekeeper environment within a Workbench instance.
- **Actions:**

  - Create `scripts/setup_workbench_env.sh`.
  - Script (`scripts/setup_workbench_env.sh`) should perform the following (run from the repository root):

    ```bash
    #!/bin/bash
    set -e # Exit immediately if a command exits with a non-zero status.

    echo "--- Updating package list and installing OS dependencies ---"
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv make pandoc git

    echo "--- Verifying Python version ---"
    python3.11 --version

    echo "--- Creating Python virtual environment '.venv' ---"
    python3.11 -m venv .venv

    echo "--- Activating virtual environment ---"
    source .venv/bin/activate

    echo "--- Upgrading pip ---"
    pip install --upgrade pip

    echo "--- Installing project dependencies (including dev/docs) from pyproject.toml ---"
    # Assuming dev/docs dependencies are specified correctly in pyproject.toml
    # Adjust if using requirements files (e.g., pip install -r requirements.txt -r requirements-dev.txt)
    pip install .[dev,docs] # Or adjust based on actual extras_require keys

    # If docs tools aren't in pyproject.toml extras:
    # echo "--- Installing documentation tools ---"
    # pip install sphinx quartodoc <specific versions if needed>

    echo "--- Verifying gcloud CLI ---"
    gcloud --version

    echo "--- Environment setup complete! ---"
    echo "To activate the environment, run: source .venv/bin/activate"
    ```

    - Ensure the script has execute permissions (`chmod +x scripts/setup_workbench_env.sh`).
    - Add checks for successful command execution (covered by `set -e`).

  - Test the script locally or in a test environment if possible.
  - Commit the script to the repository.

- **Deliverable:** `scripts/setup_workbench_env.sh` script created, tested, and committed.

### Task 2.3: Provision & Setup Test Instance

- **Objective:** Create a functional Workbench instance using the standard configuration and setup script.
- **Actions:**
  - Create a new Managed Notebook instance via GCP Console or `gcloud notebooks managed create timekeeper-workbench-test --location=<region> --vm-image-project=... --vm-image-family=... --machine-type=e2-standard-4 --service-account=happypatterns@...`. (Adjust flags based on chosen image/config).
  - Access the JupyterLab interface.
  - Open a terminal.
  - Clone the `timekeeper` repository: `git clone <repo-url>`.
  - Navigate into the repository directory.
  - Execute the setup script: `bash scripts/setup_workbench_env.sh`.
  - Troubleshoot any errors during setup.
- **Deliverable:** A running Workbench instance (`timekeeper-workbench-test`) with the project cloned and environment successfully configured via the script.

### Task 2.4: Verify GCP Connection (Service Account)

- **Objective:** Confirm code running within the instance uses the attached Service Account for GCP authentication.
- **Actions:**
  - Ensure the virtual environment created by the setup script is active (`source .venv/bin/activate`).
  - Run the test script: `python scripts/test_vertex_connection.py`.
  - Verify the script executes successfully and indicates authentication via the Service Account (it should _not_ require `GOOGLE_APPLICATION_CREDENTIALS` to be set manually within the instance).
- **Deliverable:** Successful execution of `scripts/test_vertex_connection.py` using implicit SA credentials.

### Task 2.5: Update Memory Bank (Phase 2 Completion)

- **Objective:** Record the completion of Phase 2 provisioning.
- **Actions:**
  - Update `memory-bank/progress.md`: Mark Phase 2 tasks as complete, add setup script creation.
  - Update `memory-bank/activeContext.md`: Note availability of test instance and setup script.
- **Deliverable:** Updated Memory Bank files.

---

## Phase 3: Workflow Integration & Validation

**Goal:** Ensure all core Timekeeper workflows function correctly and consistently within the Workbench environment.

### Task 3.1: Validate Interactive Research/Development Workflow

- **Objective:** Confirm core coding and research tasks can be performed in Workbench notebooks.
- **Actions:**
  - Create a new notebook (`.ipynb`) in the test instance (e.g., `docs/examples/workbench_basic_usage.ipynb`).
  - Add cells to:
    - Import modules from `src/python/` (e.g., `from src.python.agent_temporal import AgentTemporal`).
    - Instantiate classes and call methods (core temporal math, scheduling, adaptation).
    - (If applicable) Add example code interacting with Vertex AI APIs (e.g., calling a prediction endpoint) to test SA permissions.
  - Execute cells and verify expected outputs.
  - Save and commit the example notebook.
- **Deliverable:** `docs/examples/workbench_basic_usage.ipynb` created, tested, and committed.

### Task 3.2: Validate Testing Workflow

- **Objective:** Ensure the project's test suite runs successfully within Workbench.
- **Actions:**
  - Open a terminal in the test instance.
  - Activate the virtual environment (`source .venv/bin/activate`).
  - Navigate to the repository root.
  - Run the full test suite: `pytest tests/`.
  - Verify all tests pass, including unit and integration tests. Note any environment-specific failures for investigation (ideally none).
- **Deliverable:** Successful execution of `pytest tests/` with all tests passing.

### Task 3.3: Validate Documentation Workflow

- **Objective:** Confirm Sphinx and Quarto documentation can be built correctly within Workbench.
- **Actions:**
  - Open a terminal in the test instance.
  - Activate the virtual environment (`source .venv/bin/activate`).
  - Navigate to the repository root.
  - Run the Sphinx build command (e.g., `make -C config/sphinx html`). Verify output files are generated in the expected build directory without errors. Check for correct LaTeX rendering.
  - Run the Quarto build command (e.g., `quarto render .`). Verify the site builds successfully in `_site/` without errors. Check that Sphinx API docs are correctly included/iframed and that LaTeX renders correctly.
  - Review the generated documentation for consistency with the style guide (`docs/implementation/latex_style_guide.md`).
- **Deliverable:** Successful builds of both Sphinx API docs and the Quarto site. Verified correct rendering and integration.

### Task 3.4: Perform Workflow Consistency Check

- **Objective:** Ensure development practices remain consistent when using Workbench.
- **Actions:**
  - Perform a small code change + docstring update within the Workbench environment.
  - Verify adherence to type hints, docstring format (including LaTeX and traceability links), and coding style (`.clinerules`).
  - Commit the change.
- **Deliverable:** Confirmation that project standards can be easily maintained within the Workbench workflow.

### Task 3.5: Update Memory Bank (Phase 3 Completion)

- **Objective:** Record the completion of Phase 3 validation.
- **Actions:**
  - Update `memory-bank/progress.md`: Mark Phase 3 tasks as complete.
  - Update `memory-bank/activeContext.md`: Note successful validation of core workflows in Workbench.
- **Deliverable:** Updated Memory Bank files.

---

## Phase 4: Documentation, Best Practices & Team Onboarding

**Goal:** Equip the team to use Vertex AI Workbench effectively and consistently.

### Task 4.1: Create Workbench Developer Guide

- **Objective:** Provide comprehensive documentation for using Workbench with Timekeeper.
- **Actions:**
  - Create/finalize `docs/dev-guides/vertex-ai-workbench-setup.md`.
  - Include sections covering:
    - Introduction/Purpose
    - Standard Instance Configuration (Link/Embed from Task 2.1)
    - Step-by-Step Setup Guide (Cloning, Running `scripts/setup_workbench_env.sh`)
    - Authentication Explained (User vs. SA)
    - Running Tests
    - Building Documentation (Sphinx & Quarto commands)
    - Link to `docs/examples/workbench_basic_usage.ipynb`
- **Deliverable:** Completed `docs/dev-guides/vertex-ai-workbench-setup.md`.

### Task 4.2: Define and Document Best Practices

- **Objective:** Establish clear guidelines for effective and responsible Workbench usage.
- **Actions:**
  - Add a "Best Practices" section to `docs/dev-guides/vertex-ai-workbench-setup.md`.
  - Cover:
    - **Cost Management:** MANDATORY shutdown of idle instances, choosing appropriate machine types, link to budget alerts.
    - **Environment Consistency:** Importance of using the setup script.
    - **Kernel Selection:** When opening notebooks (`.ipynb`), ensure you select the kernel associated with the project's virtual environment (e.g., named 'Python 3 (.venv)' or similar, depending on how Workbench registers it) to use the installed dependencies.
    - **Project Standards:** Reinforce adherence to coding style, docstrings, LaTeX, traceability.
    - **Data Handling:** Guidelines for accessing GCS data (if needed).
    - **Security:** No hardcoded secrets, use GCP Secret Manager if necessary.
- **Deliverable:** Best Practices section added to the setup guide.

### Task 4.3: Update Memory Bank (Final Integration)

- **Objective:** Ensure the Memory Bank fully reflects the adoption of Workbench.
- **Actions:**
  - Review and update `memory-bank/productContext.md`: Mention Workbench as a key development environment.
  - Review and update `memory-bank/systemPatterns.md`: Add Workbench usage to architectural/development patterns.
  - Review and update `memory-bank/decisionLog.md`: Add final decision entry confirming successful integration and rollout.
  - Review and update `memory-bank/activeContext.md`: Reflect Workbench as the current standard interactive environment.
  - Review and update `memory-bank/progress.md`: Mark Phase 4 tasks and overall integration as complete.
- **Deliverable:** Fully updated Memory Bank files reflecting Workbench integration.

### Task 4.4: Prepare Onboarding Materials

- **Objective:** Gather resources for introducing the team to the new workflow.
- **Actions:**
  - Ensure the setup guide (`docs/dev-guides/vertex-ai-workbench-setup.md`) is finalized and accessible.
  - Ensure the example notebook (`docs/examples/workbench_basic_usage.ipynb`) is clean and runnable.
  - Prepare a brief announcement or presentation outlining the change and linking to the resources.
- **Deliverable:** Set of onboarding resources (guide, notebook, announcement draft).

---
