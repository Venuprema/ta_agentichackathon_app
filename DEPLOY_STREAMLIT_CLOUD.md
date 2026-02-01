# Deploy to Streamlit Community Cloud

Deploy the Wendy's Offer app to [Streamlit Community Cloud](https://share.streamlit.io) (free). Best for sharing with your organization; API keys are optional (add them in the dashboard later if you want to run the workflow).

---

## Step 1: Push the repo to GitHub

1. Create a new repository on [GitHub](https://github.com/new) (or use an existing one).
2. From your project folder, if you haven’t already:
   ```powershell
   cd "d:\AI Experiments\Projects\Agentic Hackathon AI"
   git init
   git add .
   git commit -m "Wendy's Offer app"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```
   Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name.

**Important:** Do **not** commit `.env` or any file with real API keys. The repo’s `.gitignore` already excludes `.env` and `data/*.csv`.

---

## Step 2: Deploy on Streamlit Community Cloud

1. Go to **https://share.streamlit.io**
2. Sign in with **GitHub** (same account that owns the repo).
3. Click **“New app”**.
4. Fill in:
   - **Repository:** `YOUR_USERNAME/YOUR_REPO`
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `streamlit_app.py`
5. Click **“Deploy!”**.

The first build may take a few minutes. When it’s done, you’ll get a URL like `https://your-repo-streamlit-app-xxxxx.streamlit.app`.

---

## Step 3: First use (generate data)

- On first load, the app will say **“Data not found”**. Click **“Generate / regenerate data”** in the sidebar. Wait for it to finish; the app will show the data summary and you can run the workflow (if you’ve set an API key) or explore the UI.
- Data and sessions are **ephemeral**: they are lost when the app restarts or goes to sleep. You can click “Generate data” again anytime.

---

## Optional: API key (for running the workflow)

If you want to **run the workflow** (multi-agent offers) in the deployed app:

1. In [share.streamlit.io](https://share.streamlit.io), open your app.
2. Click the **⋮** menu → **Settings** → **Secrets**.
3. Add secrets (TOML), for example:
   ```toml
   GEMINI_API_KEY = "your_gemini_key_here"
   ```
   If you use an AI gateway, also add:
   ```toml
   GEMINI_BASE_URL = "https://api.ai-gateway.tigeranalytics.com"
   GEMINI_MODEL = "gemini-2.0-flash"
   ```
4. Save. The app will pick these up on the next run.

If you’re only sharing with your organization and don’t need the workflow yet, you can skip this and add secrets later.

---

## Summary

| Step | Action |
|------|--------|
| 1 | Push repo to GitHub (no `.env` committed) |
| 2 | share.streamlit.io → New app → repo, branch `main`, main file `streamlit_app.py` → Deploy |
| 3 | Open app URL → click “Generate / regenerate data” in sidebar |
| Optional | Settings → Secrets → add `GEMINI_API_KEY` (and gateway vars) to run the workflow |
