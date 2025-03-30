# GCP Consultation: Recommendations & Actions Taken

Based on the briefing, initial consultation, and subsequent actions performed on 2025-03-29, here are the updated recommendations and the current configuration state:

## 1. Authentication Strategy (Questions 78-81)

### Recommendation & Status:

Application Default Credentials (ADC) using **user credentials** is the recommended and **configured** method for developers working locally (VS Code, Jupyter, Quarto).

ADC provides a standard way for applications to find credentials without hardcoding them. The lookup order is:

1.  `GOOGLE_APPLICATION_CREDENTIALS` environment variable (pointing to a service account key file) - _Use this for CI/CD_.
2.  Credentials established via `gcloud auth application-default login` - _This is now configured for local development_.
3.  Credentials from the environment (e.g., Compute Engine metadata server).

#### Developers (VS Code/Jupyter/Quarto):

- **Status:** `gcloud auth login` was used successfully to authenticate the CLI with the user `jeffreyverlynjohnson@gmail.com`.
- **Status:** `gcloud auth application-default login` was used successfully to store user credentials at `/home/verlyn13/.config/gcloud/application_default_credentials.json`. Python SDKs and other client libraries will automatically use these credentials when run locally by this user, provided `GOOGLE_APPLICATION_CREDENTIALS` is not set.
- **Non-Admin Constraint**: The `gcloud` CLI was successfully installed without admin rights using the archive download method (see Section 6). Running `gcloud auth login` and `gcloud auth application-default login` also does not require admin rights.

#### Automated Services / CI/CD (GitHub Actions):

- **Recommendation:** Continue using the Service Account key (`happypatterns@...`) stored securely (e.g., as a GitHub Secret) and referenced via the `GOOGLE_APPLICATION_CREDENTIALS` environment variable in the workflow. Use actions like `google-github-actions/auth` for secure handling.

## 2. IAM Recommendations (Questions 82-85)

Following the principle of least privilege:

### Developers Calling Vertex AI Models:

- **Recommended Role**: `roles/aiplatform.user`
- **Rationale**: Allows users to make predictions, view resources, and manage their own jobs/notebooks, but restricts modification of broader AI Platform resources. (Grant this role to developer Google accounts as needed).

### Developers Managing Vertex AI Notebooks (If Used):

- **Recommendation**: Start with `roles/aiplatform.user`. Only add Notebook-specific roles (`roles/notebooks.runner` or `roles/notebooks.admin`) if and when Vertex AI Notebooks are adopted.

### Service Account (`happypatterns@...`):

- **Initial Roles Found:** `roles/aiplatform.serviceAgent`, `roles/aiplatform.user`, `roles/aiplatform.viewer`, `roles/compute.serviceAgent`, `roles/logging.viewer`, `roles/monitoring.viewer`, `roles/storage.objectAdmin`.
- **Actions Taken:** Removed `roles/aiplatform.viewer`, `roles/logging.viewer`, `roles/monitoring.viewer`, and `roles/storage.objectAdmin` as they were redundant or overly permissive for the stated goal of calling Vertex AI APIs.
- **Final Configured Roles (Least Privilege):**
  - `roles/aiplatform.user` (Essential for calling Vertex AI APIs)
  - `roles/aiplatform.serviceAgent` (Google-managed role, kept for service functionality)
  - `roles/compute.serviceAgent` (Google-managed role, kept for potential underlying dependencies)
- **Rationale**: This configuration provides the necessary permissions for the agent to call Vertex AI models while minimizing unnecessary access.

### Granting Roles (Example `gcloud` commands):

(Requires appropriate permissions like `roles/resourcemanager.projectIamAdmin`)

```bash
# Grant Vertex AI User role to a developer's Google account
gcloud projects add-iam-policy-binding timekeeper-455221 \
    --member="user:developer-email@example.com" \
    --role="roles/aiplatform.user"

# Grant Vertex AI User role to the service account (if needed again)
# gcloud projects add-iam-policy-binding timekeeper-455221 \
#     --member="serviceAccount:happypatterns@timekeeper-455221.iam.gserviceaccount.com" \
#     --role="roles/aiplatform.user"
```

## 3. Credit Utilization (Question 86)

- The "Trial credit for GenAI App Builder" ($1,000) likely applies broadly to Vertex AI services, including direct API/SDK calls to Gemini models.
- **Verification**: Confirm applicable SKUs via the GCP Billing console ('Billing' -> 'Credits').

## 4. Vertex AI Notebooks (Question 87)

- **Recommendation**: Stick with the local VS Code + Hatch setup for now due to cost-effectiveness and team familiarity. Re-evaluate Vertex AI Notebooks if specific needs arise (GPUs, shared managed environment, deep GCP data service integration).
- **If Used**: Start with standard machine types, shut down instances when inactive, use IAM for access control.

## 5. Cost Estimation & Monitoring (Question 88)

- **Estimation**: Refer to the official [Vertex AI Pricing page](https://cloud.google.com/vertex-ai/pricing), specifically for "Generative AI" / "Gemini Models". Note experimental model pricing may vary.
- **Monitoring & Alerting**:
  - **GCP Budgets**: Set up budgets in the Billing console for project `timekeeper-455221` with alert thresholds (e.g., 50%, 90%, 100% of credit or desired spend). Filter by service (`Vertex AI`) if needed.
  - **Billing Reports**: Regularly check reports for cost trends.
  - **Labels**: Use labels for granular tracking if needed.

## 6. Local Setup (`gcloud`/SDK) without Admin Rights (Question 89)

### `gcloud` CLI:

- **Recommended Method & Status**: The `gcloud` CLI was **successfully installed** without admin rights by downloading the versioned archive (`.tar.gz`), extracting it to `/home/verlyn13/google-cloud-sdk`, and running the `./google-cloud-sdk/install.sh` script. The script updated `/home/verlyn13/.zshrc` to include the SDK in the PATH.
- **Alternative**: Google Cloud Shell remains an option if local installation is problematic for other users.

### Python SDK (`google-cloud-aiplatform` etc.):

- **Recommendation & Status**: Installation via `pip` (or `hatch add`) into the Hatch-managed environment **does not require admin rights** and is the standard procedure.

---

**Summary:** The `gcloud` CLI is installed and authenticated. Application Default Credentials are configured to use your user identity for local development via the Python SDK. The primary service account's IAM permissions have been adjusted for least privilege based on the current requirements.
