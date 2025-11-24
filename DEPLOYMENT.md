# Deployment & Zero-Downtime Updates

## Overview

This document explains how SmartDocs handles deployments on Hugging Face Spaces and what users experience during updates.

---

## How Hugging Face Deployments Work

### Blue-Green Deployment Strategy

Hugging Face uses a **blue-green deployment** approach to ensure zero downtime:

```
┌─────────────────────────────────────────────────────┐
│          Hugging Face Load Balancer                 │
│          (Routes traffic to containers)             │
└─────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌───────────────┐                 ┌───────────────┐
│  BLUE (OLD)   │                 │  GREEN (NEW)  │
│   Running     │                 │   Building    │
│               │                 │               │
│  Users here   │                 │  Not live yet │
└───────────────┘                 └───────────────┘
```

---

## Deployment Timeline

### Step-by-Step Process

#### **Phase 1: Pre-Deployment (Current State)**
```
Time: 00:00
Status: Normal operation
User Experience: ✅ App working normally

┌─────────────┐
│   OLD v1.0  │ ← All traffic
│   Running   │
└─────────────┘
```

---

#### **Phase 2: Code Push (You Merge PR)**
```
Time: 00:01
Action: Merge PR to main branch
Trigger: GitHub Actions workflow starts

┌─────────────┐
│   OLD v1.0  │ ← All traffic (still running!)
│   Running   │
└─────────────┘

GitHub Actions:
  ✓ Run tests
  ✓ Push code to HF Space
```

**User Experience:** ✅ No change, app still works

---

#### **Phase 3: Docker Build (Background)**
```
Time: 00:02 - 00:12 (10 minutes)
Action: HF builds new Docker image
Status: OLD version still serving traffic

┌─────────────┐         ┌─────────────┐
│   OLD v1.0  │ ← Users │   NEW v1.1  │
│   Running   │         │   Building  │
└─────────────┘         └─────────────┘
                             ↓
                        Docker build:
                        - Install dependencies
                        - Build frontend
                        - Ingest data
                        - Create image
```

**User Experience:** ✅ Still using old version, no interruption

---

#### **Phase 4: Health Checks**
```
Time: 00:12 - 00:13
Action: HF validates new container
Status: Both containers running

┌─────────────┐         ┌─────────────┐
│   OLD v1.0  │ ← Users │   NEW v1.1  │
│   Running   │         │   Starting  │
└─────────────┘         └─────────────┘
                             ↓
                        Health checks:
                        GET /health
                        → {"status": "healthy"}
```

**If health check fails:** Deployment aborted, old version keeps running

---

#### **Phase 5: Traffic Switch (Atomic)**
```
Time: 00:13 (1 second)
Action: Load balancer switches traffic
Status: Instant cutover

┌─────────────┐         ┌─────────────┐
│   OLD v1.0  │         │   NEW v1.1  │ ← Users
│  Draining   │         │   Running   │
└─────────────┘         └─────────────┘
```

**User Experience:** 
- 99.9%: Seamless transition
- 0.1%: One request might fail (retry succeeds)

---

#### **Phase 6: Graceful Shutdown**
```
Time: 00:13 - 00:14 (30 seconds)
Action: Old container finishes existing requests
Status: New version fully live

                        ┌─────────────┐
                        │   NEW v1.1  │ ← All traffic
                        │   Running   │
                        └─────────────┘

Old container:
  - Finishes pending requests
  - Closes connections
  - Shuts down
  - Resources freed
```

---

## What Users Experience

### Scenario 1: User Just Browsing

```
10:00 AM - User opens app (OLD version)
10:05 AM - User asks question (OLD version)
10:10 AM - [DEPLOYMENT HAPPENS]
10:11 AM - User asks another question (NEW version)
10:15 AM - User refreshes page (NEW version UI)
```

**Result:** Seamless, no errors

---

### Scenario 2: User Mid-Request During Switch

```
User clicks "Send" → Request starts
                     ↓
              [Traffic switch happens]
                     ↓
              Request completes on OLD container
                     ↓
              User sees response ✅
```

**OR (rare, <1% chance):**

```
User clicks "Send" → Request starts
                     ↓
              [Traffic switch happens]
                     ↓
              Connection reset
                     ↓
              Frontend shows error
                     ↓
              User retries → NEW container handles it ✅
```

---

### Scenario 3: User Has Page Open for Hours

```
9:00 AM  - User opens page (OLD frontend cached in browser)
10:00 AM - [DEPLOYMENT]
11:00 AM - User still using page

Frontend: OLD version (cached JavaScript)
Backend:  NEW version (API calls)

Potential issue: Version mismatch
Solution: User refreshes → Gets NEW frontend
```

---

## Edge Cases & Handling

### Case 1: Build Fails

```
Docker build error
    ↓
HF shows error in logs
    ↓
OLD version keeps running ✅
    ↓
Users unaffected ✅
    ↓
Fix code → Retry deployment
```

**User Impact:** None

---

### Case 2: New Version Crashes

```
NEW container starts
    ↓
Application crashes
    ↓
Health check fails
    ↓
HF automatically rolls back to OLD version ✅
    ↓
Users see OLD version (working)
```

**User Impact:** None (automatic rollback)

---

### Case 3: Database Migration Required

```
NEW version needs schema change
    ↓
OLD version can't read new schema
    ↓
Problem: Incompatible versions
```

**Solution:**
1. Deploy backward-compatible migration first
2. Deploy new code second
3. Remove old code support third

**For SmartDocs:** Not applicable (no database, only vector store)

---

## Minimizing User Impact

### 1. Add Version Endpoint

```python
# backend/main.py
import os
from datetime import datetime

VERSION = "1.1.0"
DEPLOYED_AT = datetime.now().isoformat()

@app.get("/version")
async def version():
    return {
        "version": VERSION,
        "deployed_at": DEPLOYED_AT,
        "environment": os.getenv("HF_SPACE", "development")
    }
```

---

### 2. Frontend Version Check

```javascript
// frontend/src/App.jsx
import { useState, useEffect } from 'react'

const CURRENT_VERSION = "1.1.0"

function App() {
  const [newVersionAvailable, setNewVersionAvailable] = useState(false)

  useEffect(() => {
    const checkVersion = async () => {
      try {
        const response = await fetch('/api/version')
        const data = await response.json()
        
        if (data.version !== CURRENT_VERSION) {
          setNewVersionAvailable(true)
        }
      } catch (error) {
        console.error('Version check failed:', error)
      }
    }

    // Check every minute
    const interval = setInterval(checkVersion, 60000)
    checkVersion() // Check immediately

    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      {newVersionAvailable && (
        <div className="update-banner">
          🎉 New version available! 
          <button onClick={() => window.location.reload()}>
            Refresh to update
          </button>
        </div>
      )}
      {/* Rest of app */}
    </div>
  )
}
```

---

### 3. Add Request Retry Logic

```javascript
// frontend/src/App.jsx
const sendMessage = async (retries = 3) => {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, model_type: model })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    if (retries > 0) {
      console.log(`Retrying... (${retries} attempts left)`)
      await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1s
      return sendMessage(retries - 1)
    }
    
    throw error // All retries exhausted
  }
}
```

---

### 4. Add Loading States

```javascript
// frontend/src/App.jsx
const [connectionStatus, setConnectionStatus] = useState('connected')

const sendMessage = async () => {
  setConnectionStatus('sending')
  
  try {
    const response = await fetch(...)
    setConnectionStatus('connected')
    // ... handle response
  } catch (error) {
    setConnectionStatus('error')
    // ... show error
  }
}

// In UI
{connectionStatus === 'error' && (
  <div className="connection-error">
    ⚠️ Connection lost. Retrying...
  </div>
)}
```

---

## Platform Comparison

### Deployment Strategies

| Platform | Strategy | Downtime | Switch Time | Rollback |
|----------|----------|----------|-------------|----------|
| **Hugging Face** | Blue-Green | ~1s | Instant | Automatic |
| **Vercel** | Atomic | 0s | Instant | Manual |
| **Railway** | Rolling | ~5s | Gradual | Manual |
| **Render** | Blue-Green | ~10s | Instant | Automatic |
| **Heroku** | Rolling | ~30s | Gradual | Manual |
| **AWS ECS** | Blue-Green | 0s | Instant | Automatic |
| **Kubernetes** | Rolling | 0s | Gradual | Manual |

---

## Best Practices

### For Development

1. **Test locally first**
   ```bash
   docker build -t smartdocs:test .
   docker run -p 7860:7860 smartdocs:test
   # Test thoroughly before deploying
   ```

2. **Use staging environment**
   - Create a separate HF Space for testing
   - Deploy to staging first
   - Verify everything works
   - Then deploy to production

3. **Monitor deployments**
   - Watch HF build logs
   - Check health endpoint after deployment
   - Test critical features

---

### For Production

1. **Deploy during low-traffic hours**
   - Check analytics for quiet periods
   - Typically: Late night or early morning
   - Minimize impact on users

2. **Communicate with users**
   ```javascript
   // Show maintenance banner before deployment
   <div className="maintenance-notice">
     🔧 Scheduled update in 5 minutes. 
     You may experience brief interruption.
   </div>
   ```

3. **Have rollback plan**
   - Keep previous version tagged in Git
   - Know how to revert quickly
   - HF does this automatically, but good to know

4. **Monitor after deployment**
   - Check error rates
   - Watch response times
   - Verify user reports

---

## Monitoring Deployments

### 1. Check HF Build Logs

```
HF Space → Logs tab

Look for:
✓ "Building..."
✓ "Build succeeded"
✓ "Starting container..."
✓ "Application startup complete"
```

### 2. Check Health Endpoint

```bash
# After deployment
curl https://YOUR_USERNAME-smartdocs.hf.space/health

# Should return:
{
  "status": "healthy",
  "timestamp": "2025-11-23T...",
  "vector_db": "connected",
  "environment": "production"
}
```

### 3. Test Critical Paths

```bash
# Test chat endpoint
curl -X POST https://YOUR_USERNAME-smartdocs.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is OmegaCore?", "model_type": "gemini"}'

# Should return answer with sources
```

---

## Troubleshooting

### Issue: Users Report "Old Version"

**Cause:** Browser cached old frontend

**Solution:**
```javascript
// Add cache busting to index.html
<script src="/main.js?v=1.1.0"></script>

// Or force reload
if (newVersionAvailable) {
  window.location.reload(true) // Hard reload
}
```

---

### Issue: Deployment Takes Too Long

**Cause:** Large Docker image, slow build

**Solutions:**
1. Optimize `.dockerignore`
2. Use smaller base images
3. Cache dependencies
4. Remove unused packages

---

### Issue: Health Check Fails

**Cause:** App not starting properly

**Debug:**
1. Check HF logs for errors
2. Test locally with Docker
3. Verify environment variables
4. Check port configuration (must be 7860)

---

## Summary

### Key Takeaways

✅ **Zero downtime** - Users don't experience interruptions

✅ **Automatic rollback** - Failed deployments don't affect users

✅ **Gradual transition** - Old version finishes requests gracefully

✅ **Health checks** - New version validated before going live

✅ **Simple for users** - At most, they need to refresh the page

---

### Deployment Checklist

Before deploying:
- [ ] Test locally with Docker
- [ ] Review code changes
- [ ] Check environment variables
- [ ] Verify health endpoint works
- [ ] Update version number

After deploying:
- [ ] Check HF build logs
- [ ] Test health endpoint
- [ ] Verify critical features
- [ ] Monitor error rates
- [ ] Check user feedback

---

### For SmartDocs Specifically

**What happens when you deploy:**
1. GitHub Actions pushes code to HF
2. HF builds Docker image (10-15 min)
3. Old version keeps running
4. New version starts
5. Traffic switches (1 second)
6. Old version shuts down

**User experience:**
- 99.9% seamless
- Might need to refresh for UI changes
- One request might fail (very rare)

**Your app is production-ready!** 🚀

---

## Additional Resources

- **Hugging Face Docs:** https://huggingface.co/docs/hub/spaces
- **Blue-Green Deployments:** https://martinfowler.com/bliki/BlueGreenDeployment.html
- **Zero-Downtime Guide:** https://cloud.google.com/architecture/application-deployment-and-testing-strategies

---

**Last Updated:** 2025-11-23
**Version:** 1.0
