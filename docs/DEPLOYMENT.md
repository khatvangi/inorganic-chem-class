# Deployment Guide

**Deploying CHEM 361 to chem361.thebeakers.com**

---

## Deployment Options

| Option | Complexity | Best For |
|--------|------------|----------|
| Static Export | Low | HTML/JS only, no API |
| Full Stack | Medium | API + Visualizations |
| Docker Compose | Medium | Reproducible deployment |

---

## Option 1: Static Export (Simplest)

Deploy only the interactive games and visualizations without the dynamic API.

### What Gets Deployed

```
Static files only:
├── index.html              # Main games hub
├── coordination.html       # Interactive games
├── bonding.html
├── isomerism.html
├── reactions.html
├── solids.html
├── visualizations/         # Pre-built visualizations
├── lectures/*.html         # Interactive lectures
├── libs/                   # ChemDoodle
├── js/                     # Utilities
└── data/                   # JSON quizzes
```

### Deployment Steps

```bash
# 1. Build static bundle
cd /storage/inorganic-chem-class

# 2. Copy to web server
rsync -avz --exclude='infrastructure' \
           --exclude='experiments' \
           --exclude='.git' \
           --exclude='*.py' \
           --exclude='__pycache__' \
           ./ user@server:/var/www/chem361/

# 3. Configure nginx
# See nginx config below
```

### Nginx Configuration (Static)

```nginx
server {
    listen 80;
    server_name chem361.thebeakers.com;

    root /var/www/chem361;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # CORS for fonts
    location ~* \.(woff|woff2|ttf|otf|eot)$ {
        add_header Access-Control-Allow-Origin "*";
    }
}
```

### Limitations

- No dynamic prerequisite tracing (`/api/trace` won't work)
- Knowledge Funnel shows static data only
- No lecture generation

---

## Option 2: Full Stack Deployment

Deploy the complete system with API server, Qdrant, and Ollama.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                     │
│                   chem361.thebeakers.com                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │  Static   │   │    API    │   │  Ollama   │
    │  Files    │   │  Server   │   │  (LLM)    │
    │  (nginx)  │   │  (:8361)  │   │  (:11434) │
    └───────────┘   └─────┬─────┘   └───────────┘
                          │
                          ▼
                    ┌───────────┐
                    │  Qdrant   │
                    │  (:6333)  │
                    └───────────┘
```

### Server Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 20 GB | 50 GB (for models) |
| GPU | Optional | Recommended for Ollama |

### Step 1: Install Dependencies

```bash
# On Ubuntu/Debian server
sudo apt update
sudo apt install -y python3.10 python3.10-venv nginx

# Install Docker (for Qdrant)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Set Up Qdrant

```bash
# Create data directory
mkdir -p /opt/chem361/qdrant_storage

# Run Qdrant container
docker run -d \
    --name qdrant \
    --restart unless-stopped \
    -p 6333:6333 \
    -v /opt/chem361/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# Verify
curl http://localhost:6333/collections
```

### Step 3: Set Up Ollama

```bash
# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull required models
ollama pull nomic-embed-text:latest
ollama pull qwen3:latest

# Verify
curl http://localhost:11434/api/tags
```

### Step 4: Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/chem361/app
sudo chown $USER:$USER /opt/chem361/app

# Clone repository
cd /opt/chem361/app
git clone https://github.com/khatvangi/inorganic-chem-class.git .

# Set up Python environment
python3.10 -m venv .venv
source .venv/bin/activate
pip install qdrant-client networkx

# Copy Qdrant data (from development machine)
rsync -avz /storage/inorganic-chem-class/experiments/results/ \
    server:/opt/chem361/app/experiments/results/
```

### Step 5: Import Qdrant Data

```bash
# On development machine, export Qdrant snapshot
curl -X POST "http://localhost:6333/collections/textbooks_chunks/snapshots"

# Copy snapshot to server
scp /path/to/snapshot.snapshot server:/tmp/

# On server, restore snapshot
curl -X PUT "http://localhost:6333/collections/textbooks_chunks/snapshots/recover" \
    -H "Content-Type: application/json" \
    -d '{"location": "file:///tmp/snapshot.snapshot"}'
```

### Step 6: Create Systemd Service

```bash
# /etc/systemd/system/chem361-api.service
sudo tee /etc/systemd/system/chem361-api.service << 'EOF'
[Unit]
Description=CHEM 361 API Server
After=network.target qdrant.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/chem361/app/infrastructure
Environment="QDRANT_URL=http://localhost:6333"
Environment="OLLAMA_URL=http://localhost:11434"
ExecStart=/opt/chem361/app/.venv/bin/python api_server.py --port 8361
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable chem361-api
sudo systemctl start chem361-api

# Check status
sudo systemctl status chem361-api
```

### Step 7: Configure Nginx

```bash
# /etc/nginx/sites-available/chem361
sudo tee /etc/nginx/sites-available/chem361 << 'EOF'
server {
    listen 80;
    server_name chem361.thebeakers.com;

    # Static files
    root /opt/chem361/app;
    index index.html;

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8361;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type" always;
    }

    # Static file caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/chem361 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: SSL Certificate (HTTPS)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d chem361.thebeakers.com

# Auto-renewal is configured automatically
```

---

## Option 3: Docker Compose

Single command deployment with all services.

### docker-compose.yml

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8361:8361"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - qdrant
      - ollama
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - .:/var/www/chem361:ro
      - ./certbot/conf:/etc/letsencrypt:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  qdrant_storage:
  ollama_models:
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY infrastructure/ ./infrastructure/
COPY experiments/results/ ./experiments/results/
COPY data/ ./data/

WORKDIR /app/infrastructure
CMD ["python", "api_server.py", "--port", "8361"]
```

### Deploy with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

## Post-Deployment Checklist

### Verify Services

```bash
# Check API
curl https://chem361.thebeakers.com/api/health

# Check visualization
curl -I https://chem361.thebeakers.com/visualizations/

# Check trace endpoint
curl "https://chem361.thebeakers.com/api/trace?q=crystal+field"
```

### Monitor

```bash
# API logs
sudo journalctl -u chem361-api -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log

# Qdrant logs
docker logs qdrant -f
```

### Backup

```bash
# Backup Qdrant data
curl -X POST "http://localhost:6333/collections/textbooks_chunks/snapshots"

# Backup application
tar -czvf chem361-backup-$(date +%Y%m%d).tar.gz /opt/chem361/app
```

---

## DNS Configuration

Add these records to your DNS provider:

| Type | Name | Value |
|------|------|-------|
| A | chem361 | <server_ip> |
| AAAA | chem361 | <server_ipv6> (optional) |

---

## Security Considerations

### Firewall

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# Block direct access to internal services
sudo ufw deny 6333/tcp  # Qdrant
sudo ufw deny 11434/tcp # Ollama
sudo ufw deny 8361/tcp  # API (accessed via nginx)
```

### API Rate Limiting

Add to nginx config:

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    # ... rest of proxy config
}
```

### Secrets

Never commit these to git:
- API keys
- Database passwords
- SSL certificates

Use environment variables or secrets manager.

---

## Troubleshooting

### API returns 502 Bad Gateway

```bash
# Check if API server is running
sudo systemctl status chem361-api

# Check API logs
sudo journalctl -u chem361-api -n 50

# Restart API
sudo systemctl restart chem361-api
```

### Qdrant connection failed

```bash
# Check Qdrant status
docker ps | grep qdrant
curl http://localhost:6333/collections

# Restart Qdrant
docker restart qdrant
```

### Ollama model not loading

```bash
# Check Ollama status
sudo systemctl status ollama

# Check available models
ollama list

# Pull missing model
ollama pull nomic-embed-text:latest
```

### SSL certificate issues

```bash
# Renew certificate manually
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## Updating

```bash
# Pull latest code
cd /opt/chem361/app
git pull origin main

# Restart API
sudo systemctl restart chem361-api

# Clear nginx cache (if using)
sudo rm -rf /var/cache/nginx/*
sudo systemctl reload nginx
```

---

## Cost Estimates (Cloud Deployment)

| Provider | Instance | Monthly Cost |
|----------|----------|--------------|
| DigitalOcean | 4GB RAM, 2 vCPU | ~$24 |
| AWS EC2 | t3.medium | ~$30 |
| Google Cloud | e2-medium | ~$25 |
| Self-hosted | - | Electricity only |

**Note:** GPU instances for faster Ollama inference are significantly more expensive (~$100-500/month).

---

*Deployment guide for CHEM 361 Knowledge Funnel System*
