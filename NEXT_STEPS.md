# SmartDocs Deployment - Next Steps

## ✅ What's Been Done

I've completed **Phase 1 & 2** of the deployment plan:

### Code Changes:
- ✅ Updated `frontend/src/App.jsx` - Environment-aware API URLs
- ✅ Updated `backend/main.py` - CORS for HF + enhanced health check
- ✅ Created `Dockerfile` - Production-ready Docker image
- ✅ Created `.dockerignore` - Optimized build
- ✅ Created `.github/workflows/deploy.yml` - Auto-deploy workflow
- ✅ Updated `.github/workflows/ci.yml` - Prevent duplicate runs
- ✅ Created `README_HF.md` - Hugging Face Space README
- ✅ Created `develop` branch
- ✅ Committed and pushed all changes

### Branch Status:
```
main (production)     ← Ready for deployment
  ↑
develop (staging)     ← ✅ Your changes are here
```

---

## 🎯 What You Need to Do Next

### Step 1: Create Hugging Face Space (5 minutes)

1. Go to: https://huggingface.co/new-space
2. Fill in:
   - **Owner:** Your username
   - **Space name:** `smartdocs`
   - **License:** MIT
   - **SDK:** Docker ← IMPORTANT!
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public
3. Click **"Create Space"**

**Result:** You'll get `https://huggingface.co/spaces/YOUR_USERNAME/smartdocs`

---

### Step 2: Add Secrets to HF Space (2 minutes)

1. Go to your Space → **Settings** tab
2. Scroll to **"Repository secrets"**
3. Click **"New secret"**
4. Add:
   - **Name:** `GOOGLE_API_KEY`
   - **Value:** Your actual Gemini API key
5. Click **"Add"**

---

### Step 3: Add GitHub Secrets (3 minutes)

1. Go to: https://github.com/SahilKhan101/smartdocs/settings/secrets/actions
2. Click **"New repository secret"**
3. Add **two** secrets:

**Secret 1:**
- Name: `HF_TOKEN`
- Value: Your HF write token (from earlier)

**Secret 2:**
- Name: `HF_USERNAME`
- Value: `SahilKhan101` (or your actual HF username)

---

### Step 4: Create Pull Request (2 minutes)

1. Go to: https://github.com/SahilKhan101/smartdocs
2. You'll see a banner: **"develop had recent pushes"**
3. Click **"Compare & pull request"**
4. Title: "Deploy to Hugging Face"
5. Description:
   ```
   ## Changes
   - Add Docker support
   - Add Hugging Face deployment pipeline
   - Update frontend for production
   - Configure CORS for HF domains
   
   ## Deployment
   This will auto-deploy to HF Spaces on merge.
   ```
6. Click **"Create pull request"**

---

### Step 5: Wait for CI Tests (2-3 minutes)

GitHub Actions will automatically run tests. You'll see:
- ✅ `backend-test` - Testing Python imports
- ✅ `frontend-build` - Building React app

**Wait for both to pass** (green checkmarks)

---

### Step 6: Merge to Main (1 minute)

Once tests pass:
1. Click **"Merge pull request"**
2. Click **"Confirm merge"**

**This triggers automatic deployment!** 🚀

---

### Step 7: Monitor Deployment (10-15 minutes)

**GitHub Actions:**
1. Go to: https://github.com/SahilKhan101/smartdocs/actions
2. Click on "Deploy to Hugging Face" workflow
3. Watch the logs

**Hugging Face:**
1. Go to: https://huggingface.co/spaces/YOUR_USERNAME/smartdocs
2. Click **"Logs"** tab
3. Watch the Docker build

**Expected build time:** 10-15 minutes (first time)

---

### Step 8: Test Your Deployed App! (5 minutes)

Once HF shows "Running":
1. Visit: `https://YOUR_USERNAME-smartdocs.hf.space`
2. Test:
   - ✅ Frontend loads
   - ✅ Ask: "What is OmegaCore?"
   - ✅ Check response includes sources
   - ✅ Try switching models

**Test health endpoint:**
```bash
curl https://YOUR_USERNAME-smartdocs.hf.space/health
```

---

## 🎉 Success Checklist

- [ ] HF Space created
- [ ] HF secret added (GOOGLE_API_KEY)
- [ ] GitHub secrets added (HF_TOKEN, HF_USERNAME)
- [ ] Pull request created
- [ ] CI tests passed
- [ ] PR merged to main
- [ ] GitHub Actions deployed successfully
- [ ] HF build completed
- [ ] App accessible at HF URL
- [ ] Health check passes
- [ ] Can ask questions and get answers

---

## 🐛 Troubleshooting

### If CI tests fail:
- Check the Actions tab for error messages
- Most common: Linting errors (can be ignored for now)

### If HF build fails:
- Check HF Logs tab
- Common issues:
  - Missing `GOOGLE_API_KEY` secret
  - Dockerfile syntax error (unlikely, I tested it)

### If app loads but API fails:
- Check browser console for errors
- Verify CORS settings
- Check HF Logs for Python errors

---

## 📊 Estimated Timeline

| Step | Time | Status |
|------|------|--------|
| Create HF Space | 5 min | ⏳ TODO |
| Add HF secrets | 2 min | ⏳ TODO |
| Add GitHub secrets | 3 min | ⏳ TODO |
| Create PR | 2 min | ⏳ TODO |
| Wait for CI | 3 min | ⏳ TODO |
| Merge PR | 1 min | ⏳ TODO |
| Wait for deployment | 15 min | ⏳ TODO |
| Test app | 5 min | ⏳ TODO |
| **Total** | **~35 minutes** | |

---

## 🔗 Quick Links

- **GitHub Repo:** https://github.com/SahilKhan101/smartdocs
- **GitHub Actions:** https://github.com/SahilKhan101/smartdocs/actions
- **HF Spaces:** https://huggingface.co/spaces (create space here)
- **HF Tokens:** https://huggingface.co/settings/tokens

---

## 💡 Tips

1. **Keep both tabs open:**
   - GitHub Actions (to watch deploy)
   - HF Space Logs (to watch build)

2. **First deployment is slow:**
   - Downloads ~2GB of dependencies
   - Future deploys are faster (cached)

3. **If something fails:**
   - Don't panic!
   - Check logs
   - You can always re-trigger by pushing to main

---

## 🚀 Ready?

Start with **Step 1: Create Hugging Face Space**

Good luck! 🎉
