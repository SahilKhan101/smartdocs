# GitHub Setup Guide for SmartDocs

## Step 1: Configure Git (First Time Only)

Set your Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Note**: Use the same email as your GitHub account.

---

## Step 2: Create GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `smartdocs`
   - **Description**: "RAG system for technical documentation Q&A"
   - **Visibility**: Public (or Private if you prefer)
   - **DO NOT** initialize with README (we already have one)
4. Click **"Create repository"**

---

## Step 3: Connect Local Repository to GitHub

After creating the repo, GitHub will show you commands. Use these:

```bash
cd /media/sahil/Workbook/VSCode/RAG/smartdocs

# If you haven't committed yet:
git add .
git commit -m "Initial commit: SmartDocs RAG system with dual LLM support"

# Connect to GitHub (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/smartdocs.git

# Rename branch to 'main' (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Example** (if your username is `john-doe`):
```bash
git remote add origin https://github.com/john-doe/smartdocs.git
git branch -M main
git push -u origin main
```

---

## Step 4: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files!
3. The CI/CD pipeline will automatically run (check the "Actions" tab)

---

## Step 5: Understanding the CI/CD Pipeline

I've set up a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

### What It Does:
1. **Backend Test Job**:
   - Installs Python dependencies
   - Verifies all imports work
   - Runs on every push to `main` or `develop`

2. **Frontend Build Job**:
   - Installs Node.js dependencies
   - Builds the production bundle
   - Uploads the build as an artifact

### When It Runs:
- Every push to `main` or `develop` branches
- Every pull request to `main`

### Viewing Results:
1. Go to your repo on GitHub
2. Click the **"Actions"** tab
3. You'll see all workflow runs with ✅ (pass) or ❌ (fail)

---

## Step 6: Working with Git (Daily Workflow)

### Making Changes

```bash
# 1. Check what changed
git status

# 2. Stage changes
git add .                    # Add all files
# OR
git add backend/main.py      # Add specific file

# 3. Commit with a message
git commit -m "Add feature: streaming responses"

# 4. Push to GitHub
git push
```

### Creating Branches (Best Practice)

```bash
# Create a new feature branch
git checkout -b feature/add-pdf-support

# Make your changes, then commit
git add .
git commit -m "Add PDF document loader"

# Push the branch
git push -u origin feature/add-pdf-support
```

Then create a **Pull Request** on GitHub to merge into `main`.

---

## Step 7: Advanced CI/CD (Future Enhancements)

### Add Automated Testing

Create `backend/tests/test_api.py`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Update `.github/workflows/ci.yml` to run tests:
```yaml
- name: Run tests
  run: |
    cd backend
    pytest tests/
```

### Add Deployment

**Option 1: Deploy Backend to Railway/Render**
- Connect your GitHub repo
- Auto-deploys on every push to `main`

**Option 2: Deploy Frontend to Vercel/Netlify**
- Connect your GitHub repo
- Auto-builds and deploys the `frontend/` directory

### Add Code Quality Checks

Add to `.github/workflows/ci.yml`:
```yaml
- name: Lint Python code
  run: |
    pip install flake8
    flake8 backend/ --max-line-length=100

- name: Lint JavaScript code
  run: |
    cd frontend
    npm run lint
```

---

## Step 8: Protecting Your Secrets

### Never Commit `.env` Files!

The `.gitignore` I created already excludes `.env`, but double-check:

```bash
git status
# Should NOT show .env in the list
```

### Using GitHub Secrets (for CI/CD)

If your CI/CD needs API keys:

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add:
   - Name: `GOOGLE_API_KEY`
   - Value: `your_actual_key`

Then use in workflows:
```yaml
env:
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

---

## Step 9: Collaboration Features

### Issues
Track bugs and feature requests:
- Go to **Issues** tab → **New issue**
- Use labels: `bug`, `enhancement`, `documentation`

### Projects
Organize work with Kanban boards:
- Go to **Projects** tab → **New project**
- Add columns: `To Do`, `In Progress`, `Done`

### Wiki
Document your project:
- Go to **Wiki** tab
- Create pages for architecture, deployment, etc.

---

## Common Git Commands Cheat Sheet

```bash
# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard HEAD

# Pull latest changes from GitHub
git pull

# Create and switch to new branch
git checkout -b branch-name

# Switch to existing branch
git checkout main

# Delete a branch
git branch -d branch-name

# View all branches
git branch -a

# See differences
git diff
```

---

## Troubleshooting

### Issue: "Permission denied (publickey)"
**Solution**: Set up SSH keys or use HTTPS with personal access token

**HTTPS Method** (easier):
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/smartdocs.git
```
GitHub will prompt for username/password (use a Personal Access Token as password).

**SSH Method**:
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Use SSH URL: `git remote set-url origin git@github.com:YOUR_USERNAME/smartdocs.git`

### Issue: "fatal: not a git repository"
**Solution**: You're not in the right directory
```bash
cd /media/sahil/Workbook/VSCode/RAG/smartdocs
```

### Issue: Merge conflicts
**Solution**:
```bash
# Pull latest changes
git pull

# Fix conflicts in your editor (look for <<<<<<< markers)
# Then:
git add .
git commit -m "Resolve merge conflicts"
git push
```

---

## Next Steps

1. ✅ Set up your Git identity
2. ✅ Create GitHub repository
3. ✅ Push your code
4. ✅ Verify CI/CD pipeline runs
5. 📚 Add more documentation
6. 🚀 Deploy to production (optional)

Happy coding! 🎉
