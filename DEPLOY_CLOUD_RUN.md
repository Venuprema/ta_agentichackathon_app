# Deploy Wendy's Offer App to Google Cloud Run — Step by Step

Follow these steps in order. Use **PowerShell** or **Command Prompt** (not Git Bash for `gcloud`).

---

## Step 1: Install Google Cloud SDK (if needed)

1. Download: https://cloud.google.com/sdk/docs/install
2. Run the installer and complete the setup.
3. **Restart your terminal** after install.
4. Check it works:
   ```powershell
   gcloud --version
   ```
   You should see something like `Google Cloud SDK 4xx.x.x`.

**If PowerShell says "gcloud is not recognized":**  
The installer may not have added the SDK to your PATH, or the terminal was opened before install. Do one of the following.

- **Quick fix (current terminal only):** Add the SDK `bin` folder to PATH for this session (typical user install path):
  ```powershell
  $env:Path += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
  gcloud --version
  ```
  If that fails, use the full path to run gcloud:
  ```powershell
  & "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" --version
  ```

- **Permanent fix:** Add the SDK `bin` folder to your user PATH:
  1. Press **Win + R**, type `sysdm.cpl`, Enter → **Advanced** tab → **Environment Variables**.
  2. Under **User variables**, select **Path** → **Edit** → **New**.
  3. Add: `C:\Users\YOUR_USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`  
     (replace YOUR_USERNAME with your Windows username, or use `%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin`).
  4. OK out, **close and reopen** PowerShell (and Cursor if you use its terminal).

---

## Step 2: Log in to Google Cloud

1. Open PowerShell or Command Prompt.
2. Run:
   ```powershell
   gcloud auth login
   ```
3. A browser window opens. Sign in with your Google account and allow access.
4. When it says "You are now logged in", you can close the browser and return to the terminal.

---

## Step 3: Create or select a GCP project

**Option A — Use an existing project**

1. List your projects:
   ```powershell
   gcloud projects list
   ```
2. Pick the **PROJECT_ID** (e.g. `my-project-12345`).
3. Set it as the active project (replace `YOUR_PROJECT_ID` with yours):
   ```powershell
   gcloud config set project YOUR_PROJECT_ID
   ```

**Option B — Create a new project (use the web Console)**

Creating a project from the **Cloud Console (web)** avoids permission errors. Many accounts (especially personal/free) do not have `resourcemanager.projects.create` when using `gcloud projects create`; the Console allows creating projects without that API permission.

1. Go to **https://console.cloud.google.com/**
2. Click the **project dropdown** at the top (next to "Google Cloud") → **New Project**.
3. Enter a **Project name** (e.g. "Wendy's Hackathon"). Note the **Project ID** (e.g. `wendys-hackathon-123456`) — you’ll need it for `gcloud`.
4. Click **Create** and wait for the project to be created.
5. In your terminal, set that project (replace with your Project ID):
   ```powershell
   gcloud config set project YOUR_NEW_PROJECT_ID
   ```

If you prefer the CLI and get *"You do not have the required resourcemanager.projects.create permission"*: create the project in the Console (steps 1–4 above), then use step 5 to select it in gcloud.

---

## Step 4: Enable required APIs

Run this once per project (replace `YOUR_PROJECT_ID` if you didn’t set it in Step 3):

```powershell
gcloud services enable run.googleapis.com artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
```

If you already ran `gcloud config set project YOUR_PROJECT_ID`, you can omit `--project=...`:

```powershell
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

Wait until it says "Operation finished successfully."

---

## Step 5: Go to your app folder

From PowerShell or Command Prompt:

```powershell
cd "d:\AI Experiments\Projects\Agentic Hackathon AI"
```

Confirm you see `streamlit_app.py`, `Dockerfile`, and `requirements.txt` in this folder.

---

## Step 6: Deploy to Cloud Run

**Option A — API key in env (simplest)**

Replace `YOUR_GEMINI_API_KEY` with your real Gemini API key. Use one line (no backslashes in PowerShell):

```powershell
gcloud run deploy wendys-offer-app --source . --region us-central1 --allow-unauthenticated --set-env-vars "GEMINI_API_KEY=YOUR_GEMINI_API_KEY,REQUIRE_GEMINI_KEY=1"
```

If you use the **AI gateway** (e.g. Tiger Analytics), set all vars in one string:

```powershell
gcloud run deploy wendys-offer-app --source . --region us-central1 --allow-unauthenticated --memory 1Gi --set-env-vars "GEMINI_API_KEY=YOUR_KEY,GEMINI_BASE_URL=https://api.ai-gateway.tigeranalytics.com,GEMINI_MODEL=gemini-2.0-flash,REQUIRE_GEMINI_KEY=1"
```

**What happens:**  
- `--source .` uploads the current folder (respecting `.gcloudignore`) and builds the container using the Dockerfile.  
- First run can take several minutes (building image, pushing, deploying).  
- When it finishes, you’ll see a **Service URL** like `https://wendys-offer-app-xxxxx-uc.a.run.app`.

**Option B — API key in Secret Manager (more secure)**

1. Create the secret (one-time; replace `your_actual_key` with your key):

   **PowerShell:**
   ```powershell
   "your_actual_key" | Out-File -FilePath gemini-key.txt -Encoding ascii -NoNewline
   gcloud secrets create gemini-api-key --data-file=gemini-key.txt
   del gemini-key.txt
   ```

2. Deploy and use the secret:
   ```powershell
   gcloud run deploy wendys-offer-app --source . --region us-central1 --allow-unauthenticated --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
   ```

   If Secret Manager isn’t enabled yet:
   ```powershell
   gcloud services enable secretmanager.googleapis.com
   ```

---

## Step 7: Open the app

1. After deploy, copy the **Service URL** from the command output (e.g. `https://wendys-offer-app-xxxxx-uc.a.run.app`).
2. Paste it into your browser and press Enter.
3. You should see the Wendy’s Offer Innovation app. Generate data if needed, then run the workflow with your Gemini key (already set in Cloud Run).

---

## Quick reference

| Step | Command / action |
|------|-------------------|
| 1 | Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) |
| 2 | `gcloud auth login` |
| 3 | `gcloud config set project YOUR_PROJECT_ID` |
| 4 | `gcloud services enable run.googleapis.com artifactregistry.googleapis.com` |
| 5 | `cd "d:\AI Experiments\Projects\Agentic Hackathon AI"` |
| 6 | `gcloud run deploy wendys-offer-app --source . --region us-central1 --allow-unauthenticated --set-env-vars "GEMINI_API_KEY=YOUR_KEY,REQUIRE_GEMINI_KEY=1"` |
| 7 | Open the Service URL in your browser |

---

## Troubleshooting

- **"gcloud: command not found"**  
  Install the Cloud SDK (Step 1) and restart the terminal. Ensure the install path is on your PATH.

- **"Permission denied" or "API not enabled"**  
  Run Step 4 again with the correct project. In Cloud Console, enable **Cloud Run API** and **Artifact Registry API** for that project.

- **Build fails (Dockerfile)**  
  Make sure you’re in the project root (Step 5) and that `Dockerfile`, `requirements.txt`, and `streamlit_app.py` are present.

- **App loads but "API key validation failed"**  
  Set `GEMINI_API_KEY` (and if needed `GEMINI_BASE_URL`, `GEMINI_MODEL`) in Cloud Run:  
  **Cloud Console** → **Cloud Run** → select **wendys-offer-app** → **Edit & deploy new revision** → **Variables & Secrets** → add or edit env vars → **Deploy**.

- **Different region**  
  Use e.g. `--region europe-west1` instead of `us-central1` in the deploy command.
