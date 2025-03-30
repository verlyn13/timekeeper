**Date:** 2025-03-29

**Prepared By:** Roo (Architect Mode)

## 1. Project Context & Goals

### Elevator Pitch

Timekeeper is a Python-based research framework designed to provide a mathematically rigorous approach for optimizing temporal dynamics in small-scale agent systems (typically 1-3 agents). It focuses on hierarchical temporal partitioning, precise timepoint operations, dynamic adaptability of time granularity, and optimized task scheduling. The project emphasizes bidirectional traceability between its formal mathematical foundation and the Python implementation.

Currently, the project has completed its core implementation components (temporal systems, scheduler, basic visualization) and initial integration testing (Task Scheduler). The immediate focus has shifted from further MVP refinement (docstring enhancement, example suite development) to integrating Google Cloud Platform services, primarily Vertex AI, to enhance agent capabilities.

The goal is to automate the framework and publishing aspect of this project as much as possible, in order to focus on the research and development of the agentic capabilities. This includes leveraging advanced generative models for agentic tasks, improving authentication and cost management practices, and exploring potential CI/CD enhancements.

### GCP Objectives

The primary objectives for utilizing Google Cloud at this stage are:

- **Leverage Vertex AI:** Utilize Vertex AI's generative models (specifically targeting Gemini models like gemini-2.5-pro-exp-03-25) for advanced agentic tasks, moving beyond current LLM interaction methods.
- **Secure & Efficient Authentication:** Establish best practices for authenticating to GCP services (Vertex AI) from developer environments (VS Code, potentially Jupyter/Quarto notebooks) and future automated workflows, considering developer permission constraints.
- **Cost Management:** Understand cost implications of using Vertex AI models and effectively utilize the existing $1,000 "Trial credit for GenAI App Builder". Information below.
- **Development Environment (Potential):** Explore Vertex AI Notebooks as a potential platform for interactive development and collaborative research, if suitable and cost-effective.
- **CI/CD (Future):** Gain initial insights into potentially leveraging GCP for future CI/CD enhancements, although the current GitHub Actions setup is functional.

## 2. Technical Architecture Summary (GCP Focus)

### Existing Architecture Document

A detailed overview of the system architecture can be found here:
[Timekeeper System Architecture Overview](../../architecture/system-overview.md)

### Key Interaction Points with GCP

The primary interaction points with GCP services are expected to be:

- **Python Agent Implementations:** Core agent logic within `src/python/` (e.g., potentially within `AdaptiveAgentTemporal` or dedicated agent behavior modules not yet created) will need to make calls to Vertex AI services.
- **Development/Research Environment:** Developers using VS Code, potentially interacting with Quarto notebooks or scripts that require GCP access.
- **Testing Framework (Potential):** Integration tests might eventually need to interact with GCP services if core functionality relies on them.

### LLM Interaction Details

- **Current Method:** LLM interaction currently relies on the integrated "roo code" plugin within the development environment. Limitations include lack of direct control over models, potential quota/cost opacity, and the need for specific models like Gemini 1.5 Pro.
- **Planned Method:** The intention is to move towards direct interaction with Vertex AI using the Python SDK (`google-cloud-aiplatform`). The recent setup of GCP service account credential sourcing ([GCP Credentials Integration Plan](../memory-bank/gcp-credentials-integration.md)) supports this direction.
- **MCP Proxy:** A proxy server (MCP) was previously considered but is not the current primary approach. Direct SDK usage is preferred for now.
- **Target Models:** gemini-2.5-pro-exp-03-25 and the very latest 2.x gemini models are the primary target.
- **Usage Volume:** Expected usage is for research-driven agentic tasks (e.g., planning, reasoning, function calling based on temporal context). Initial volume is likely moderate, but estimates are needed.

### Technology Stack Confirmation

- **Primary Language:** Python (>=3.11)
- **Key Libraries:** NumPy, Matplotlib, pytest, hypothesis, Hatch (for environment/build)
- **Documentation:** Quarto, Sphinx (for API docs), Markdown
- **CI/CD:** GitHub Actions
- **Databases:** None currently defined.

## 3. Current GCP Environment

- Project ID: timekeeper-455221
- Service Account: happypatterns@timekeeper-455221.iam.gserviceaccount.com
- Service Account Name: happypatterns
- Service Account Email: happypatterns@timekeeper-455221.iam.gserviceaccount.com
- Service Account Unique ID: 107074850995679227290
- **Existing Services:**
  - Vertex AI API is enabled (implied by credential setup).
  - Other services may need to be added.
  - A Service Account key file exists and its path is managed via `~/.secrets/google/gcp_env.sh` -> `GCP_HAPPYPATTERNS_SA_KEY_PATH`.
  - Developer user roles and permissions within GCP are TBD. Note the constraint regarding local admin rights (see Section 5).
- **Billing & Credits:**
  - Billing Account is set up.
  - A $1,000 "Trial credit for GenAI App Builder" is available.
    - Credit Name: Trial credit for GenAI App Builder
    - Status: Available
    - Credit ID: 5e13527ddb31d40f0092bd3f291904caacad1961a4d11eb6512bab0eb5de4834
    - End Date: December 18, 2025

## 4. Specific Questions & Challenges

- Authentication Strategy: What is the most secure and practical way to manage Vertex AI authentication (Application Default Credentials vs. Service Account Keys) for:
  - Developers using VS Code / potentially Jupyter/Quarto?
  - Future automated services or CI/CD pipelines?
  - How does the local non-admin constraint impact ADC setup (`gcloud auth application-default login`)?
- IAM Recommendations: Recommend specific, least-privilege IAM roles/permissions for:
  - Developers needing to call Vertex AI models.
  - Developers managing Vertex AI Notebooks (if used).
  - The service account used by the application/agents.
- Credit Utilization: How can the "GenAI App Builder" credit best be utilized, given the primary use case involves direct Vertex AI model calls via SDK rather than App Builder tools? Does it apply to general Vertex AI API usage?
- Vertex AI Notebooks: Best practices for setting up, managing, and collaborating using Vertex AI Notebook environments for this type of research project? Considerations for environment consistency and cost.
- Cost Estimation: Provide guidance on estimating costs for calling Gemini models via Vertex AI API (e.g., cost per X prompts/tokens for Gemini 2.x pro models). Tools or methods for monitoring and alerting?
- Local Setup (`gcloud`/SDK): Guidance on setting up the `gcloud` CLI and Python SDK on developer machines, especially considering potential lack of admin rights for installation.

## 5. Constraints & Developer Environment

- **Budget:** Primary funding is the $1,000 GCP credit. Need clarity on budget constraints beyond this for sustained usage. Cost optimization is important.
- **Security:**
  - Credentials must not be stored in the repository.
  - Service account key files are stored locally with restricted permissions (`600`).
  - There is no sensitive data in the repository, but the project may involve sensitive agent interactions or data processing in the future.
- **Local Environment:**
  - Suggestions welcome for local development setup, especially for GCP SDK and Python libraries.
  - The primary developer is using Linux (Fedora) with VS Code and Hatch for Python environment management.
  - The developer is an admin on their machine, but any other team members are not.
  - For CI/DC, github actions are used.
  - Systemwide installation of `gcloud` and other tools may not be possible due to primary developer permissions.
  - **Developer Permissions:** Developers (except for the primary user) **do not have local administrator rights** on their machines. This impacts the ability to install software requiring elevation (e.g., system-wide `gcloud` installers, Docker Desktop requiring admin rights on some OSs).
  - **Typical Setup:** Linux (Fedora specified in environment details), VS Code, Python environments managed via Hatch.
