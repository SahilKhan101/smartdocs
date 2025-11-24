# Understanding Nginx in SmartDocs

## What is Nginx?

**Nginx** (pronounced "engine-x") is a **web server** and **reverse proxy**. In your deployment, it acts as a traffic director that sits between users and your application.

---

## The Problem Nginx Solves

### Without Nginx (Local Development):

```
User's Browser
    ↓
    ↓ http://localhost:5173 (Frontend - React)
    ↓
Frontend (Vite Dev Server)
    ↓
    ↓ http://localhost:8000/chat (API call)
    ↓
Backend (FastAPI)
```

**Two separate servers:**
- Frontend: Port 5173
- Backend: Port 8000

**This works locally but has problems in production:**
1. ❌ Need to expose 2 ports
2. ❌ CORS issues (cross-origin requests)
3. ❌ Can't use one domain
4. ❌ Harder to manage

---

### With Nginx (Production on Hugging Face):

```
User's Browser
    ↓
    ↓ https://your-app.hf.space
    ↓
Nginx (Port 7860) ← Single entry point
    ↓
    ├─→ Frontend (Static files)
    │   └─→ Serves HTML/CSS/JS
    │
    └─→ Backend (FastAPI on port 8000)
        └─→ Handles /api/* requests
```

**One server, one port, one domain!**

---

## How Nginx Works: Step-by-Step

### Scenario 1: User Loads the Page

```
1. User visits: https://your-app.hf.space/

2. Request arrives at Nginx (port 7860)

3. Nginx checks its config:
   location / {
       root /app/frontend/dist;
       try_files $uri $uri/ /index.html;
   }

4. Nginx serves: /app/frontend/dist/index.html

5. Browser receives HTML, loads React app
```

**Result:** User sees your React interface

---

### Scenario 2: User Asks a Question

```
1. User clicks "Send" in React app

2. Frontend makes request:
   fetch('/api/chat', {...})
   
   Full URL: https://your-app.hf.space/api/chat

3. Request arrives at Nginx (port 7860)

4. Nginx checks its config:
   location /api/ {
       proxy_pass http://localhost:8000/;
   }

5. Nginx forwards to: http://localhost:8000/chat
   (Note: /api/ is removed!)

6. FastAPI handles request, returns answer

7. Nginx forwards response back to browser

8. React displays the answer
```

**Result:** User gets their answer

---

## Your Nginx Configuration

Let's break down your `Dockerfile` nginx config:

```nginx
server {
    listen 7860;                    # HF requires port 7860
    server_name _;                  # Accept any domain
    client_max_body_size 10M;       # Allow 10MB uploads
    
    # Rule 1: Serve Frontend
    location / {
        root /app/frontend/dist;           # Where React build is
        try_files $uri $uri/ /index.html;  # SPA routing
    }
    
    # Rule 2: Proxy API Requests
    location /api/ {
        proxy_pass http://localhost:8000/;  # Forward to FastAPI
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Rule 3: Health Check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

---

## URL Routing Examples

### Example 1: Homepage

```
User requests: https://your-app.hf.space/

Nginx matches: location /
Action: Serve /app/frontend/dist/index.html
Result: React app loads
```

---

### Example 2: Chat Request

```
User requests: https://your-app.hf.space/api/chat

Nginx matches: location /api/
Action: proxy_pass http://localhost:8000/
Result: Forwards to http://localhost:8000/chat
        (removes /api/ prefix)
```

**Why remove `/api/`?**
- Frontend calls: `/api/chat`
- Backend endpoint is: `/chat` (not `/api/chat`)
- Nginx strips `/api/` before forwarding

---

### Example 3: Static Asset

```
User requests: https://your-app.hf.space/assets/index.js

Nginx matches: location /
Action: try_files /assets/index.js
Result: Serve /app/frontend/dist/assets/index.js
```

---

## Why Use `/api/` Prefix?

### Without Prefix (Confusing):

```
Frontend calls: /chat
Nginx: Is this a frontend route or API call? 🤔
```

### With Prefix (Clear):

```
Frontend calls: /api/chat
Nginx: Starts with /api/ → Must be API call! ✅
```

**Benefits:**
1. ✅ Clear separation (frontend vs API)
2. ✅ No route conflicts
3. ✅ Easy to add more API endpoints
4. ✅ Standard practice

---

## Local vs Production Comparison

### Local Development:

```javascript
// Frontend (localhost:5173)
const API_URL = 'http://localhost:8000'
fetch(`${API_URL}/chat`)  // http://localhost:8000/chat

// Backend (localhost:8000)
@app.post("/chat")  // Endpoint: /chat
```

**Two separate servers, direct connection**

---

### Production (Hugging Face):

```javascript
// Frontend (served by nginx)
fetch('/api/chat')  // Relative URL

// Nginx (port 7860)
location /api/ {
    proxy_pass http://localhost:8000/;  // Remove /api/
}

// Backend (localhost:8000)
@app.post("/chat")  // Endpoint: /chat
```

**One server (nginx), proxy to backend**

---

## The Complete Flow (Production)

```
┌─────────────────────────────────────────────────────┐
│  User's Browser                                     │
│  https://your-app.hf.space                          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  Nginx (Port 7860)                                  │
│  ┌─────────────────────────────────────────────┐   │
│  │ Routing Logic:                              │   │
│  │ - /          → Frontend files               │   │
│  │ - /api/*     → Backend (port 8000)          │   │
│  │ - /health    → Backend health check         │   │
│  └─────────────────────────────────────────────┘   │
└─────────┬──────────────────────────┬────────────────┘
          │                          │
          ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Frontend           │    │  Backend            │
│  (Static Files)     │    │  (FastAPI)          │
│                     │    │  Port 8000          │
│  /app/frontend/dist │    │                     │
│  - index.html       │    │  Endpoints:         │
│  - assets/          │    │  - POST /chat       │
│  - *.js, *.css      │    │  - GET /health      │
└─────────────────────┘    └─────────────────────┘
```

---

## Why This Architecture?

### 1. **Single Entry Point**
```
Before: https://app.com:5173 (frontend)
        https://app.com:8000 (backend)

After:  https://app.com (everything)
```

### 2. **No CORS Issues**
```
Same origin: https://app.com/api/chat
No cross-origin request!
```

### 3. **Better Security**
```
Backend not directly exposed
Nginx handles SSL/TLS
Can add rate limiting at nginx level
```

### 4. **Easier Deployment**
```
One container
One port (7860)
One domain
```

---

## Common Nginx Patterns

### Pattern 1: SPA Routing

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

**What it does:**
- Try to find exact file: `/about` → `/about`
- Try as directory: `/about` → `/about/index.html`
- Fall back to: `/index.html` (React Router handles it)

**Example:**
```
User visits: /about
File exists? No
Directory exists? No
Serve: index.html
React Router: Sees /about, shows About page
```

---

### Pattern 2: API Proxy

```nginx
location /api/ {
    proxy_pass http://localhost:8000/;
}
```

**URL transformation:**
```
/api/chat       → http://localhost:8000/chat
/api/users/123  → http://localhost:8000/users/123
/api/health     → http://localhost:8000/health
```

**Note the trailing slash!**
```
proxy_pass http://localhost:8000/;   ← Removes /api/
proxy_pass http://localhost:8000;    ← Keeps /api/
```

---

### Pattern 3: Static Assets

```nginx
location /assets/ {
    root /app/frontend/dist;
    expires 1y;  # Cache for 1 year
}
```

**Optimization:**
- Browser caches JS/CSS files
- Faster page loads
- Less bandwidth

---

## Debugging Nginx

### Check if Nginx is Running:

```bash
# In Docker container
ps aux | grep nginx

# Should see:
# nginx: master process
# nginx: worker process
```

### View Nginx Logs:

```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

### Test Nginx Config:

```bash
nginx -t

# Should output:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## Common Issues & Solutions

### Issue 1: 404 on API Calls

**Symptom:**
```
GET /api/chat → 404 Not Found
```

**Cause:** Nginx config missing or wrong

**Fix:**
```nginx
location /api/ {
    proxy_pass http://localhost:8000/;  # Don't forget trailing /
}
```

---

### Issue 2: CORS Errors

**Symptom:**
```
Access-Control-Allow-Origin error
```

**Cause:** Backend not receiving proxy headers

**Fix:**
```nginx
location /api/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;              # Add this
    proxy_set_header X-Real-IP $remote_addr;  # And this
}
```

---

### Issue 3: React Router 404

**Symptom:**
```
/about works, but refresh → 404
```

**Cause:** Nginx looking for /about file (doesn't exist)

**Fix:**
```nginx
location / {
    try_files $uri $uri/ /index.html;  # Fall back to index.html
}
```

---

## Summary

### What Nginx Does:

1. **Web Server** - Serves your React app (HTML/CSS/JS)
2. **Reverse Proxy** - Forwards API requests to FastAPI
3. **Load Balancer** - Can distribute traffic (not used here)
4. **SSL Termination** - Handles HTTPS (HF does this)

### Why You Need It:

- ✅ One domain for everything
- ✅ No CORS issues
- ✅ Better security
- ✅ Standard production setup
- ✅ Required by Hugging Face (port 7860)

### Your Setup:

```
User → Nginx (7860) → Frontend (static files)
                    → Backend (8000) for /api/*
```

---

## Quick Reference

### Local Development:
```javascript
fetch('http://localhost:8000/chat')  // Direct to backend
```

### Production (with Nginx):
```javascript
fetch('/api/chat')  // Nginx proxies to backend
```

### Nginx Config:
```nginx
location /api/ {
    proxy_pass http://localhost:8000/;  # Remove /api/ prefix
}
```

---

**That's nginx in a nutshell!** It's the glue that makes your frontend and backend work together seamlessly in production. 🚀
