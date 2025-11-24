FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Ollama requirements
RUN apt-get update && apt-get install -y \
    nodejs npm \
    nginx \
    python3-dev \
    build-essential \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Build React frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci
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

# Pre-download Ollama model (this will take time but only happens once during build)
# We'll use a smaller model to fit in HF's limits
RUN ollama serve & \
    OLLAMA_PID=$! && \
    sleep 10 && \
    ollama pull gemma:2b && \
    kill $OLLAMA_PID

# Expose Hugging Face port (must be 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
    # Start Ollama in background\n\
    ollama serve &\n\
    OLLAMA_PID=$!\n\
    \n\
    # Wait for Ollama to be ready\n\
    echo "Waiting for Ollama to start..."\n\
    for i in {1..30}; do\n\
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then\n\
    echo "Ollama is ready!"\n\
    break\n\
    fi\n\
    echo "Waiting... ($i/30)"\n\
    sleep 2\n\
    done\n\
    \n\
    # Start nginx\n\
    service nginx start\n\
    \n\
    # Start FastAPI\n\
    cd /app/backend\n\
    uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Start all services
CMD ["/app/start.sh"]
