# Google Cloud Platform (GCP) Credentials Integration Strategy (Updated 2025-03-29)

## Overview

This document outlines the finalized strategy for integrating Google Cloud Platform (GCP) credentials, primarily for accessing Vertex AI services, into the Timekeeper project. This strategy supersedes the initial plan focused solely on service account keys.

**Reference:** For full details, rationale, and setup steps, see `docs/reference/gcp-consultant-recommendation.md`.

## Authentication Strategy

A dual authentication approach has been adopted:

1.  **Local Development (VS Code, Jupyter, etc.):**

    - **Method:** Application Default Credentials (ADC) using authenticated **user credentials**.
    - **Setup:** Achieved via `gcloud auth login` followed by `gcloud auth application-default login`. Credentials stored in `~/.config/gcloud/application_default_credentials.json`.
    - **Usage:** Google Cloud client libraries (e.g., Python SDK) automatically detect and use these credentials when the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is _not_ set.
    - **Rationale:** Leverages developer identity, enhances local security (avoids distributing SA keys), aligns with GCP best practices for local development.

2.  **CI/CD & Automated Environments (GitHub Actions):**
    - **Method:** Dedicated Service Account (`happypatterns@timekeeper-455221.iam.gserviceaccount.com`) key file.
    - **Setup:** The path to the key file is sourced from `~/.secrets/google/gcp_env.sh` (variable `GCP_HAPPYPATTERNS_SA_KEY_PATH`) for local _testing_ of this method if needed, but primarily the key file _content_ should be stored securely (e.g., GitHub Secret).
    - **Usage:** The `GOOGLE_APPLICATION_CREDENTIALS` environment variable must be set (pointing to the key file path, or handled by actions like `google-github-actions/auth`) within the CI/CD environment.
    - **Rationale:** Standard secure method for non-interactive environments.

## Service Account IAM Roles

The `happypatterns@...` service account roles have been refined for least privilege:

- `roles/aiplatform.user` (Essential)
- `roles/aiplatform.serviceAgent` (Google-managed)
- `roles/compute.serviceAgent` (Google-managed)

(Removed: `aiplatform.viewer`, `logging.viewer`, `monitoring.viewer`, `storage.objectAdmin`)

## Local `gcloud` CLI Setup

- The `gcloud` CLI was installed locally in the user's home directory (`/home/verlyn13/google-cloud-sdk`) without requiring admin privileges, using the downloadable archive.
- The user's shell (`.zshrc`) was updated by the installer to include `gcloud` in the PATH.

## Scripting (`scripts/setup_env_tokens.sh`)

- The existing logic in `scripts/setup_env_tokens.sh` to source `~/.secrets/google/gcp_env.sh` remains relevant for potentially testing the CI/CD service account key method locally, but it's **not** the primary method for local development authentication (which now uses user ADC).
- No immediate changes are required to this script based on the primary ADC local strategy, but developers should be aware that setting `GOOGLE_APPLICATION_CREDENTIALS` (e.g., via this script) will override the user ADC credentials.

## Security Considerations

- Credentials (user ADC file, service account key file) must be kept secure and out of the repository.
- Ensure appropriate file permissions (`600`) for key files.
- Follow least privilege principles for both user and service account IAM roles.
