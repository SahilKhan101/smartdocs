FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs npm \
    nginx \
    python3-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Build React frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci --only=production
COPY frontend .
RUN npm run build

# Install Python backend
WORKDIR /app
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application files
COPY backend ./backend
COPY data ./data

# Configure nginx to serve React + proxy API
RUN echo 'server { \
    listen 7860; \
    server_name _; \
    client_max_body_size 10M; \
    \
    location / { \
        root /app/frontend/dist; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /api/ { \
        proxy_pass http://localhost:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_read_timeout 300s; \
    } \
    \
    location /health { \
        proxy_pass http://localhost:8000/health; \
    } \
}' > /etc/nginx/sites-available/default

# Ingest documentation into ChromaDB
WORKDIR /app/backend
RUN python ingest.py

# Expose Hugging Face port (must be 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Start nginx and FastAPI
CMD service nginx start && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info
