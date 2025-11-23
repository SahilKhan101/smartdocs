# Rate Limiting Feature

## Overview

Rate limiting has been added to protect the SmartDocs API from abuse and manage API quota usage.

## Configuration

**Current Limits:**
- **Chat endpoint:** 10 requests per minute per IP address
- **Health endpoint:** No limit (for monitoring)

## How It Works

The rate limiter tracks requests by **IP address** and enforces limits using a sliding window algorithm.

### Example:
```
User at IP 192.168.1.1:
- Request 1-10: ✅ Allowed
- Request 11: ❌ Blocked (429 Too Many Requests)
- After 1 minute: ✅ Allowed again
```

## Response When Rate Limited

**Status Code:** `429 Too Many Requests`

**Response Body:**
```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

**Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000000
```

## Customizing Limits

Edit `backend/main.py`:

```python
# Change the limit
@limiter.limit("10/minute")  # Current
@limiter.limit("20/minute")  # More permissive
@limiter.limit("5/minute")   # More restrictive
@limiter.limit("100/hour")   # Hourly limit
```

### Limit Formats:
- `"10/minute"` - 10 requests per minute
- `"100/hour"` - 100 requests per hour
- `"1000/day"` - 1000 requests per day
- `"5/second"` - 5 requests per second

## Per-Endpoint Limits

You can set different limits for different endpoints:

```python
@app.post("/chat")
@limiter.limit("10/minute")  # Chat is expensive
async def chat(...):
    pass

@app.get("/search")
@limiter.limit("30/minute")  # Search is cheaper
async def search(...):
    pass
```

## Exempting IPs (Optional)

To allow unlimited requests from specific IPs (e.g., your own):

```python
# backend/main.py
from slowapi import Limiter

def custom_key_func(request: Request):
    # Exempt localhost
    if request.client.host in ["127.0.0.1", "localhost"]:
        return None  # No limit
    return get_remote_address(request)

limiter = Limiter(key_func=custom_key_func)
```

## Testing Rate Limiting

### Test 1: Normal Usage
```bash
# Should work
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is OmegaCore?", "model_type": "gemini"}'
```

### Test 2: Exceed Limit
```bash
# Run this 11 times quickly
for i in {1..11}; do
  echo "Request $i"
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question": "Test", "model_type": "gemini"}'
  echo ""
done
```

**Expected:** First 10 succeed, 11th returns 429

### Test 3: Check Headers
```bash
curl -i -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Test", "model_type": "gemini"}'
```

Look for `X-RateLimit-*` headers in the response.

## Frontend Handling

Update `frontend/src/App.jsx` to show user-friendly messages:

```javascript
const sendMessage = async () => {
  try {
    const response = await fetch(`${API_URL}/api/chat`, {...})
    
    if (response.status === 429) {
      setMessages(prev => [...prev, { 
        text: "⏳ Rate limit exceeded. Please wait a minute and try again.", 
        sender: "bot" 
      }])
      return
    }
    
    // ... rest of code
  } catch (error) {
    // ... error handling
  }
}
```

## Monitoring

### View Rate Limit Stats

Add an admin endpoint (optional):

```python
@app.get("/admin/rate-limits")
async def get_rate_limits():
    # Return current rate limit stats
    # (Requires additional setup)
    pass
```

### Logging

Rate limit violations are automatically logged:

```python
# backend/main.py
import logging

logger = logging.getLogger("slowapi")
logger.setLevel(logging.INFO)

# Logs will show:
# "Rate limit exceeded for 192.168.1.1"
```

## Production Considerations

### 1. **Use Redis for Distributed Systems**

If running multiple backend instances:

```python
from slowapi.util import get_remote_address
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
```

### 2. **Adjust for Production Traffic**

```python
# Development: Strict limits
@limiter.limit("10/minute")

# Production: More generous
@limiter.limit("100/minute")
```

### 3. **Consider User Authentication**

Instead of IP-based limits, use user IDs:

```python
def get_user_id(request: Request):
    # Extract from JWT token
    token = request.headers.get("Authorization")
    user_id = decode_token(token)
    return user_id

limiter = Limiter(key_func=get_user_id)
```

## Benefits

✅ **Protects API Quota** - Prevents one user from exhausting your Gemini API quota
✅ **Prevents Abuse** - Stops malicious actors from spamming
✅ **Fair Usage** - Ensures all users get equal access
✅ **Cost Control** - Limits unexpected API bills
✅ **DDoS Protection** - Basic protection against simple attacks

## Troubleshooting

### Issue: Rate limit too strict
**Solution:** Increase the limit or time window

### Issue: Legitimate users getting blocked
**Solution:** 
- Increase limits
- Use authentication instead of IP
- Implement tiered limits (free vs paid users)

### Issue: Rate limiter not working
**Check:**
1. `slowapi` is installed
2. Limiter is attached to app: `app.state.limiter = limiter`
3. Decorator is on the endpoint: `@limiter.limit(...)`

## Next Steps

1. ✅ Rate limiting implemented
2. ⏳ Add frontend error handling for 429 responses
3. ⏳ Set up monitoring/alerts for rate limit violations
4. ⏳ Consider Redis for production (if scaling)

---

**Rate limiting is now active!** Your API is protected from abuse. 🛡️
