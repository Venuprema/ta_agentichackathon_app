# Wendy's Hackathon: Agentic AI for Offer Innovation

Multi-agent system that collaborates to propose **3 innovative promotional offers** for Wendy's, grounded in market trends, customer insights, and competitor intelligence.

## What this repo contains

- **Data generation:** Local script that produces synthetic market trends, customer transactions, customer feedback, and competitor intel (no GCP).
- **Four agents + orchestrator:** Market Research ? Customer Insights ? Competitor Intelligence ? Offer Design, run in sequence.
- **Streamlit app:** Natural-language query ? 4-step trace (input/output/hand-off per agent) ? Top 3 offer concepts. Sessions persisted to disk; empty-state "Generate data" button.

## Push to GitLab

**Step-by-step:** See **[PUSH_TO_?ITLAB.md](PUSH_TO_?ITLAB.md)** for creating a GitLab project, adding the remote, and pushing. Summary: create a blank project on GitLab ? `git add .` ? `git commit -m "..."` ? `git remote add origin https://gitlab.com/USER/PROJECT.git` ? `git push -u origin main`. Use a Personal Access Token if GitLab asks for a password.

## Quick start (local)

### 1. Clone and install

```bash
git clone <your-repo-url>
cd "Agentic Hackathon AI"
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Generate data

```bash
python scripts/generate_data.py --output-dir data
```

This creates `data/market_trends.csv`, `data/customer_transactions.csv`, `data/customer_feedback.csv`, `data/competitor_intel.csv`.

### 3. API key and base URL (from .env)

The app loads **GEMINI_API_KEY** and **GEMINI_BASE_URL** from a **`.env`** file in the **project root** (same folder as `streamlit_app.py`). Create or edit `.env` there:

```
GEMINI_API_KEY=your_key
GEMINI_BASE_URL=https://api.ai-gateway.tigeranalytics.com
```

On startup the app **validates the API key** with a minimal call and shows in the sidebar: **"API key validated. Ready to run workflow."** or **"API key validation failed."** with the error. If validation fails, fix `.env` and refresh the app. Run workflow is disabled until validation succeeds.

### 4. Run the app

**Option A (Windows):** Double-click `run_app.bat` or in Command Prompt:
```cmd
run_app.bat
```

**Option B (any OS):** Use the Python launcher or your venv:
```cmd
py -m streamlit run streamlit_app.py
```
Or, if you use a venv: activate it first, then:
```bash
python -m streamlit run streamlit_app.py
```

If `python` opens the Windows Store instead of running Python, use `py` or the batch file.

Open the URL shown (e.g. http://localhost:8501). Enter a request (e.g. *??Develop three innovative offers to increase traffic for discount hunters??*) and click **Run workflow**. View the 4-step trace and top 3 offers in the Offer Design step. Past sessions appear in the sidebar.

**Scoping (breakfast, quarter, etc.):** If your request mentions a **daypart** (e.g. breakfast, lunch, late-night) or **time horizon** (e.g. Q1, next quarter, 6 weeks), the app parses these and injects them into every agent's context (e.g. "Parsed scope: daypart=breakfast, time_horizon=Q1"). All four agents are instructed to scope their analysis and recommendations to that context, so you can ask for "breakfast offers only" or "offers for next quarter" and get focused results.

### 5. Empty state

If you haven?t run the data generator, the app shows ??Data not found?? and a **Generate data** button. Click it to run the generator and reload.

## Deployment

### Option A: Streamlit Community Cloud (free)

**Step-by-step:** See **[DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md)** for a short walkthrough (push to GitHub ? connect at share.streamlit.io ? set main file to `streamlit_app.py` ? deploy). API keys are optional; add them in the app?s **Settings ? Secrets** later if you want to run the workflow.

1. Push this repo to GitHub (do not commit `.env`).
2. ?o to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, click **New app**, choose your repo, set **Main file path** to `streamlit_app.py`.
3. Deploy. On first load, click **Generate / regenerate data** in the sidebar.
4. Optional: **Settings ? Secrets** ? add `GEMINI_API_KEY` (and `GEMINI_BASE_URL`, `GEMINI_MODEL` if using a gateway) to run the workflow.

### Option B: GCP Cloud Run (free tier)

Cloud Run has a [free tier](https://cloud.google.com/run/pricing) (e.g. 2 million requests/month). The repo includes a **Dockerfile** and **.gcloudignore** for deploy-from-source.

**Step-by-step guide:** See **[DEPLOY_CLOUD_RUN.md](DEPLOY_CLOUD_RUN.md)** for a numbered walkthrough (install gcloud, login, project, enable APIs, deploy). On Windows you can also edit and run **`deploy_cloudrun.ps1`** after setting your project ID and API key.

#### Prerequisites

- [?oogle Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed and logged in.
- A GCP project with Cloud Run and Container Registry (Artifact Registry) enabled.

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

#### Deploy from source (recommended)

From the project root (same folder as `streamlit_app.py` and `Dockerfile`):

```bash
cd "Agentic Hackathon AI"

gcloud run deploy wendys-offer-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=your_gemini_key_here" \
  --set-env-vars "REQUIRE_GEMINI_KEY=1"
```

- **`--source .`** builds the container from the current directory using the Dockerfile (and uploads files according to `.gcloudignore`).
- **`--allow-unauthenticated`** makes the app publicly reachable (optional; omit for auth-only).
- **Env vars:** The app reads `GEMINI_API_KEY` (required for workflow). If you use an AI gateway, also set:
  - `GEMINI_BASE_URL=https://api.ai-gateway.tigeranalytics.com`
  - `GEMINI_MODEL=gemini-2.0-flash` (or your model name)

Example with gateway and optional memory limit:

```bash
gcloud run deploy wendys-offer-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1?i \
  --set-env-vars "GEMINI_API_KEY=your_key,GEMINI_BASE_URL=https://api.ai-gateway.tigeranalytics.com,GEMINI_MODEL=gemini-2.0-flash,REQUIRE_GEMINI_KEY=1"
```

#### Using Secret Manager for the API key

```bash
# Create secret (one-time)
echo -n "your_gemini_key" | gcloud secrets create gemini-api-key --data-file=-

# Deploy with secret
gcloud run deploy wendys-offer-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

#### What the Dockerfile does

- Uses `python:3.11-slim`.
- Installs dependencies from `requirements.txt`.
- Copies the app and runs `scripts/generate_data.py --output-dir /app/data` at **build time** so the image includes synthetic data (no GCP data needed).
- Runs Streamlit on `PORT` (default 8080) with `--server.address=0.0.0.0` and `--server.headless=true`.

After deploy, Cloud Run prints the service URL (e.g. `https://wendys-offer-app-xxxxx-uc.a.run.app`). Open it in a browser to use the app.

### Other deployment options

| Option | Notes |
|--------|--------|
| **Streamlit Community Cloud** | Easiest: push to GitHub, connect at [share.streamlit.io](https://share.streamlit.io), set app file to `streamlit_app.py`, add `GEMINI_API_KEY` as a secret. No Docker; free tier available. |
| **AWS App Runner** | Run a container from ECR. Build the image with the repo?s Dockerfile, push to ECR, create an App Runner service pointing at that image. Set env vars in the service. [Docs](https://docs.aws.amazon.com/apprunner/) |
| **AWS ECS (Fargate)** | Run the same Docker image as a Fargate task behind a load balancer. ?ood if you already use ECS. |
| **Azure Container Apps** | Deploy the Docker image to Container Apps from Azure Container Registry. Set `GEMINI_API_KEY` (and gateway vars if needed) in the app?s environment. [Docs](https://learn.microsoft.com/en-us/azure/container-apps/) |
| **Railway** | Connect GitHub, deploy from repo. Use ??Dockerfile?? as build; set env vars in the dashboard. [railway.app](https://railway.app) |
| **Render** | Connect repo, create a ??Web Service??, use Docker; set env vars. Free tier for small services. [render.com](https://render.com) |
| **Fly.io** | `fly launch` from the app folder (with a `Dockerfile`), then `fly deploy`. Set secrets with `fly secrets set GEMINI_API_KEY=...`. [fly.io](https://fly.io) |
| **VPS (DigitalOcean, Linode, etc.)** | Rent a small VM, install Docker, clone the repo, run `docker build -t wendys-app .` and `docker run -p 8080:8080 -e GEMINI_API_KEY=... wendys-app`. Put a reverse proxy (e.g. Caddy, nginx) in front if you want HTTPS. |

For any **container-based** option (AWS, Azure, Railway, Render, Fly, VPS), use the repo?s **Dockerfile** as-is. Ensure the app listens on the port the platform expects (often **8080** or the value of `PORT`); the Dockerfile already does that. Set **GEMINI_API_KEY** (and **GEMINI_BASE_URL**, **GEMINI_MODEL** if you use the gateway) in the platform?s environment or secrets.

## Repo structure

```
Agentic Hackathon AI/
??? README.md
??? requirements.txt
??? streamlit_app.py          # Streamlit entry
??? data/                     # Generated CSVs (gitignored)
??? scripts/
?   ??? generate_data.py     # Local data generation (no GCP)
??? src/
?   ??? llm.py                # Gemini client
?   ??? data_loaders.py       # Load CSVs, summarize for LLM
?   ??? orchestrator.py       # Run 4 agents in sequence
?   ??? agents/
?       ??? market_research.py
?       ??? customer_insights.py
?       ??? competitor_intel.py
?       ??? offer_design.py
??? sessions/                 # Persisted sessions (gitignored)
```

## Example prompts

- *??Develop three innovative offers to increase traffic for discount hunters.??*
- *??What are the new offers that could be provided based on recent trends? Provide the top 3 and which customer profile is most relevant.??*
- *??How are quick-service restaurants innovating morning offers for loyal customers?*

## API key: local vs deployment

- **Local run:** GEMINI_API_KEY is **optional** to open the app. You can view sessions and use "Generate data" without it. The key is required only when you click **Run workflow**.
- **Deployment:** Set `REQUIRE_GEMINI_KEY=1` in the deployment environment so the app requires GEMINI_API_KEY on load (e.g. Streamlit Cloud Secrets or Cloud Run env). If the key is missing, the app shows an error and does not allow running the workflow.

## Running tests

```bash
pip install -r requirements.txt
py -m pytest tests/ -v
```

Tests cover: data generation (CSV output, schemas, row counts), data loaders (`data_available`, `load_*`, `summarize_for_llm`), agents (mocked LLM), orchestrator (4-step structure), app helpers (save/load/list sessions), and LLM key handling.

## Requirements

- Python 3.10+
- Gemini API key (one key for all agents; optional for local until you run the workflow)
- No GCP project needed for local run or Streamlit Community Cloud
