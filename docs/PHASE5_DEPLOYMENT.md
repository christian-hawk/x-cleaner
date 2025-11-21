# Phase 5 Deployment Guide - Streamlit Dashboard

This document provides deployment instructions for the X-Cleaner Streamlit Dashboard (Phase 5).

## Local Deployment

### Prerequisites

- Python 3.11+
- All dependencies installed (`pip install -r requirements.txt`)
- Database populated (via scan or sample data)

### Running Locally

#### Basic Usage

```bash
streamlit run streamlit_app/app.py
```

The dashboard will be available at `http://localhost:8501`

#### Custom Port

```bash
streamlit run streamlit_app/app.py --server.port 8080
```

#### Headless Mode (Background)

```bash
streamlit run streamlit_app/app.py --server.headless true
```

#### With Custom Config

```bash
streamlit run streamlit_app/app.py --server.port 8080 --theme.base dark
```

## Development Mode

### Hot Reload

Streamlit automatically reloads when you edit files. Enable development mode:

```bash
streamlit run streamlit_app/app.py --server.runOnSave true
```

### Debug Mode

```bash
streamlit run streamlit_app/app.py --logger.level debug
```

## Production Deployment

### Option 1: Streamlit Cloud (Recommended)

**Pros:**
- Free tier available
- Automatic HTTPS
- Built-in authentication
- Easy deployment from GitHub
- Automatic updates

**Steps:**

1. **Push code to GitHub** (if not already done)

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Connect your GitHub account**

4. **Deploy app:**
   - Repository: `christian-hawk/x-cleaner`
   - Branch: `main`
   - Main file path: `streamlit_app/app.py`

5. **Add secrets** (Settings → Secrets):
   ```toml
   X_API_BEARER_TOKEN = "your_token"
   X_USER_ID = "your_user_id"
   XAI_API_KEY = "your_key"
   ```

6. **Configure resources:**
   - Python version: 3.11
   - Add `requirements.txt` to root

7. **Deploy!**

Your app will be available at: `https://your-app-name.streamlit.app`

### Option 2: Docker Container

**Create Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
ENTRYPOINT ["streamlit", "run", "streamlit_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Create docker-compose.yml:**

```yaml
version: '3.8'

services:
  x-cleaner-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - X_API_BEARER_TOKEN=${X_API_BEARER_TOKEN}
      - X_USER_ID=${X_USER_ID}
      - XAI_API_KEY=${XAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

**Deploy:**

```bash
docker-compose up -d
```

### Option 3: Cloud VPS (AWS, DigitalOcean, etc.)

#### Example: Ubuntu 22.04 Server

**1. Install dependencies:**

```bash
sudo apt update
sudo apt install -y python3.11 python3-pip nginx
```

**2. Clone and setup:**

```bash
git clone https://github.com/christian-hawk/x-cleaner.git
cd x-cleaner
pip install -r requirements.txt
```

**3. Create systemd service:**

```bash
sudo nano /etc/systemd/system/x-cleaner.service
```

```ini
[Unit]
Description=X-Cleaner Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/x-cleaner
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/streamlit run streamlit_app/app.py --server.port 8501 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

**4. Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable x-cleaner
sudo systemctl start x-cleaner
```

**5. Configure Nginx as reverse proxy:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**6. Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/x-cleaner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 4: Railway

**1. Install Railway CLI:**

```bash
npm install -g @railway/cli
```

**2. Login:**

```bash
railway login
```

**3. Initialize project:**

```bash
railway init
```

**4. Add start command to `Procfile`:**

```
web: streamlit run streamlit_app/app.py --server.port $PORT --server.headless true
```

**5. Deploy:**

```bash
railway up
```

### Option 5: Heroku

**1. Create `Procfile`:**

```
web: streamlit run streamlit_app/app.py --server.port $PORT --server.headless true
```

**2. Create `setup.sh`:**

```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**3. Deploy:**

```bash
heroku create your-app-name
git push heroku main
heroku open
```

## Security Considerations

### 1. Environment Variables

**Never commit sensitive data!**

Use environment variables for:
- API keys
- Tokens
- Passwords
- Connection strings

**Best practices:**
- Use `.env` files locally (add to `.gitignore`)
- Use secrets management in production
- Rotate credentials regularly

### 2. Authentication

**Streamlit Cloud:**
- Use GitHub authentication
- Restrict to specific email domains

**Self-hosted:**
- Use nginx basic auth
- Implement custom auth with Streamlit
- Use VPN or firewall rules

### 3. HTTPS

**Always use HTTPS in production:**

- Streamlit Cloud: Automatic
- Docker: Use nginx or Caddy as reverse proxy
- VPS: Use Let's Encrypt (certbot)

### 4. Rate Limiting

Configure rate limiting to prevent abuse:

```python
# In streamlit_app/app.py
import streamlit as st

@st.cache_resource
def rate_limiter():
    # Implement rate limiting logic
    pass
```

### 5. Data Privacy

- Don't expose sensitive account data
- Implement access controls
- Regular security audits
- GDPR compliance if needed

## Performance Optimization

### 1. Caching

Already implemented in `utils.py`:

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_all_accounts():
    # ...
```

**Adjust TTL based on update frequency:**

```python
# For frequently updated data
@st.cache_data(ttl=60)  # 1 minute

# For static data
@st.cache_data(ttl=3600)  # 1 hour
```

### 2. Database Optimization

- Add indexes for frequently queried fields
- Use pagination for large result sets
- Implement connection pooling

### 3. Frontend Optimization

- Lazy load images
- Limit initial data rendering
- Use progressive loading
- Minimize chart complexity

### 4. Resource Limits

Configure Streamlit resource limits:

```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
```

## Monitoring

### 1. Application Logs

**View Streamlit logs:**

```bash
# Development
streamlit run streamlit_app/app.py --logger.level debug

# Production (systemd)
sudo journalctl -u x-cleaner -f
```

### 2. Performance Monitoring

**Using Streamlit built-in profiler:**

```python
import streamlit as st

with st.spinner("Loading data..."):
    # Your code
    pass
```

### 3. Error Tracking

**Integrate Sentry:**

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

### 4. Analytics

**Track usage with Google Analytics:**

Add to `.streamlit/config.toml`:

```toml
[browser]
gatherUsageStats = true
```

## Backup and Recovery

### 1. Database Backup

**Automated backup script:**

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/x-cleaner"
DB_PATH="data/accounts.db"

mkdir -p $BACKUP_DIR
cp $DB_PATH "$BACKUP_DIR/accounts_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "accounts_*.db" -mtime +30 -delete
```

**Add to crontab:**

```bash
0 2 * * * /path/to/backup_db.sh
```

### 2. Configuration Backup

Backup `.env` and configuration files:

```bash
tar -czf config_backup.tar.gz .env .streamlit/
```

### 3. Disaster Recovery

**Recovery procedure:**

1. Restore database from backup
2. Restore configuration files
3. Redeploy application
4. Verify functionality

## Scaling

### Horizontal Scaling

**Load balancing multiple instances:**

```nginx
upstream streamlit_backend {
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
}

server {
    location / {
        proxy_pass http://streamlit_backend;
        # ... other proxy settings
    }
}
```

### Vertical Scaling

**Increase resources:**

- CPU: 2+ cores recommended
- RAM: 2GB minimum, 4GB+ recommended
- Storage: SSD for database

### Database Scaling

**For very large datasets:**

- Consider PostgreSQL instead of SQLite
- Implement read replicas
- Use Redis for caching

## Maintenance

### Regular Tasks

**Weekly:**
- Review logs for errors
- Check disk space
- Monitor performance

**Monthly:**
- Update dependencies
- Security patches
- Backup verification

**Quarterly:**
- Performance review
- Security audit
- Feature updates

### Updates

**Update Streamlit:**

```bash
pip install --upgrade streamlit
```

**Update all dependencies:**

```bash
pip install --upgrade -r requirements.txt
```

**Test after updates:**

```bash
pytest tests/
streamlit run streamlit_app/app.py
```

## Troubleshooting

### Common Issues

**Port already in use:**

```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>
```

**Memory issues:**

```bash
# Increase memory limit
streamlit run streamlit_app/app.py --server.maxMessageSize 500
```

**WebSocket errors:**

Check proxy configuration for WebSocket support.

**Database locked:**

```python
# Add timeout in database.py
conn = sqlite3.connect(self.db_path, timeout=10.0)
```

## Conclusion

The Streamlit dashboard is now ready for production deployment. Choose the deployment option that best fits your needs:

- **Quick prototype**: Local deployment
- **Public sharing**: Streamlit Cloud
- **Full control**: Docker or VPS
- **Enterprise**: Kubernetes cluster

For questions or issues, refer to:
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Project README](../README.md)
- [GitHub Issues](https://github.com/christian-hawk/x-cleaner/issues)
