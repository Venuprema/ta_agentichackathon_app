# Push This Project to GitLab — Step by Step

Use **PowerShell** or **Command Prompt** from the project folder:  
`d:\AI Experiments\Projects\Agentic Hackathon AI`

---

## Step 1: Create a GitLab project (if you don’t have one)

1. Go to **https://gitlab.com** and sign in (or create an account).
2. Click **“New project”** → **“Create blank project”**.
3. Fill in:
   - **Project name:** e.g. `wendys-offer-app` or `agentic-hackathon-ai`
   - **Project URL:** choose your namespace (your username or a group).
   - **Visibility:** Private (recommended) or Internal if you have a group.
4. **Do not** initialize with a README (you already have one).
5. Click **“Create project”**.

GitLab will show the project page. Note the **clone URL** (HTTPS or SSH). It looks like:
- **HTTPS:** `https://gitlab.com/YOUR_USERNAME/wendys-offer-app.git`
- **SSH:** `git@gitlab.com:YOUR_USERNAME/wendys-offer-app.git`

You’ll need this URL in Step 5.

---

## Step 2: Open a terminal in the project folder

```powershell
cd "d:\AI Experiments\Projects\Agentic Hackathon AI"
```

---

## Step 3: Initialize Git (if this folder is not yet a repo)

Check if Git is already initialized:

```powershell
git status
```

- If you see **“not a git repository”**, run:
  ```powershell
  git init
  ```
- If you see a list of files or “nothing to commit”, Git is already initialized; go to Step 4.

---

## Step 4: Add files and commit

**4a. Add all files (respecting .gitignore)**

```powershell
git add .
```

**4b. See what will be committed**

```powershell
git status
```

You should **not** see `.env` in the list (it’s in `.gitignore`). If `.env` appears, do **not** commit it; remove it from staging:

```powershell
git reset HEAD .env
```

**4c. Commit**

```powershell
git commit -m "Wendy's Offer app: Streamlit multi-agent workflow"
```

---

## Step 5: Add the GitLab remote and push

**5a. Add GitLab as the remote**

Replace `YOUR_GITLAB_USERNAME` and `YOUR_PROJECT_NAME` with your GitLab username and project name (or use the full clone URL from Step 1):

```powershell
git remote add origin https://gitlab.com/YOUR_GITLAB_USERNAME/YOUR_PROJECT_NAME.git
```

Example:

```powershell
git remote add origin https://gitlab.com/jsmith/wendys-offer-app.git
```

If you already had a remote named `origin` (e.g. from GitHub), either use a different name or update the URL:

```powershell
git remote set-url origin https://gitlab.com/YOUR_GITLAB_USERNAME/YOUR_PROJECT_NAME.git
```

**5b. Rename branch to main (if needed)**

```powershell
git branch -M main
```

**5c. Push to GitLab**

```powershell
git push -u origin main
```

- GitLab may ask for your **username** and **password**.  
- For **password**, use a **Personal Access Token** (not your account password):  
  GitLab → **Settings** → **Access Tokens** → create a token with `write_repository` → use that token as the password when `git push` asks for it.
- If you use **SSH**, add the SSH remote instead and push:
  ```powershell
  git remote add origin git@gitlab.com:YOUR_USERNAME/YOUR_PROJECT_NAME.git
  git push -u origin main
  ```

---

## Step 6: Confirm on GitLab

1. Open your project on **https://gitlab.com**.
2. You should see the latest files and commits.
3. You can now clone, share, or set up CI/CD from this repo.

---

## Quick reference

| Step | Command |
|------|--------|
| 1 | Create blank project on gitlab.com (no README). Copy clone URL. |
| 2 | `cd "d:\AI Experiments\Projects\Agentic Hackathon AI"` |
| 3 | `git status` → if needed: `git init` |
| 4 | `git add .` → `git status` → `git commit -m "Wendy's Offer app"` |
| 5 | `git remote add origin https://gitlab.com/USER/PROJECT.git` → `git branch -M main` → `git push -u origin main` |
| 6 | Check the project on GitLab in the browser. |

---

## Troubleshooting

- **“remote origin already exists”**  
  Either use another name: `git remote add gitlab https://gitlab.com/...` and then `git push -u gitlab main`, or change the URL: `git remote set-url origin https://gitlab.com/...`.

- **“Authentication failed” or “Support for password authentication was removed”**  
  Use a **Personal Access Token**: GitLab → Settings → Access Tokens → create token with `write_repository` → use it as the password when pushing. Or set up SSH keys and use the SSH clone URL.

- **“.env” is in the list of files to commit**  
  Do **not** commit it. Run `git reset HEAD .env` and ensure `.env` is in `.gitignore` (this repo’s `.gitignore` already excludes `.env`).
