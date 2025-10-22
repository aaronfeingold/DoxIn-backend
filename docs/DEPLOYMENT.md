# Secure Deployment Guide

This guide covers deploying the DoxIn document processing system with secure file storage and user authentication.

## Architecture Overview

### Frontend (Next.js on Vercel)

- **Hosting**: Vercel (doxin.xyz)
- **Authentication**: NextAuth.js with Google OAuth
- **File Upload**: Direct to Vercel Blob Storage
- **Security**: JWT tokens, CSRF protection, file validation

### Backend (GCP Compute Engine VM)

- **Infrastructure**: Single GCP VM (e2-medium) running Docker Compose
- **API**: Flask application (port 8000)
- **Database**: PostgreSQL with pgvector extension (containerized)
- **Cache/Broker**: Redis (containerized)
- **Background Processing**: Celery worker
- **Monitoring**: Prometheus, Grafana, exporters
- **Security**: JWT validation, RBAC (Role-Based Access Control)

### File Storage

- **Primary Storage**: Vercel Blob Storage
- **Access Control**: Vercel Blob API with time-limited access
- **Organization**: User-specific folders with UUID-based file naming

## Prerequisites

1. **GCP Account** with billing enabled
2. **Vercel Account** for frontend deployment and blob storage
3. **Google Cloud Console** account for OAuth setup
4. **Domain name** (optional but recommended)
5. **gcloud CLI** installed locally

## Step 1: GCP Setup

### 1.1 Create GCP Compute Engine VM

Using gcloud CLI:

```bash
gcloud compute instances create doxin-backend-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server \
  --project=YOUR_PROJECT_ID
```

Or use the [GCP Console](https://console.cloud.google.com/compute/instances) web UI.

### 1.2 Configure Firewall Rules

Allow API access on port 8000:

```bash
gcloud compute firewall-rules create allow-doxin-api \
  --allow=tcp:8000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server \
  --description="Allow access to DoxIn API on port 8000" \
  --project=YOUR_PROJECT_ID
```

For production, consider restricting to Vercel IPs only:

```bash
gcloud compute firewall-rules create allow-doxin-api-vercel \
  --allow=tcp:8000 \
  --source-ranges=76.76.21.21,76.76.21.22,76.76.21.93,76.76.21.164,76.76.21.241 \
  --target-tags=http-server \
  --description="Allow DoxIn API access from Vercel only"
```

### 1.3 Get VM Public IP

```bash
gcloud compute instances describe doxin-backend-vm \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Save this IP address for later configuration.

### 1.4 Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
5. Configure OAuth consent screen:
   - **Application name**: DoxIn Document Processor
   - **Authorized domains**: doxin.xyz
6. Create OAuth 2.0 Client ID:
   - **Application type**: Web application
   - **Authorized redirect URIs**: `https://doxin.xyz/api/auth/callback/google`
7. Note down:
   - Client ID
   - Client secret

### 1.5 Set up Vercel Blob Storage

1. Go to Vercel Dashboard → Storage → Blob
2. Create a new Blob store for your project
3. Note down the Blob store URL and access token

## Step 2: Install Docker on VM

SSH into your VM:

```bash
gcloud compute ssh doxin-backend-vm --zone=us-central1-a
```

Install Docker Engine:

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group change to take effect
exit
```

SSH back in and verify Docker installation:

```bash
gcloud compute ssh doxin-backend-vm --zone=us-central1-a
docker --version
docker compose version
```

## Step 3: Transfer Application Files

### Option A: Using Git (Recommended)

```bash
# On the VM
cd ~
git clone https://github.com/aaronfeingold/DoxIn.git --recurse-submodules
cd DoxIn
```

### Option B: Using gcloud SCP

```bash
# From your local machine
cd /path/to/your/DoxIn
gcloud compute scp --recurse backend/ doxin-backend-vm:~/DoxIn/backend/ --zone=us-central1-a
```

## Step 4: Create Production Environment File

SSH into the VM and create the production `.env` file:

```bash
cd ~/DoxIn/backend/docker
nano .env.production
```

Add the following configuration (replace placeholders with your actual values):

```env
# Environment
FLASK_ENV=production
ENVIRONMENT=production
DEBUG=false

# Security - GENERATE NEW SECRETS!
SECRET_KEY=GENERATE_A_SECURE_RANDOM_STRING_HERE
JWT_SECRET_KEY=GENERATE_ANOTHER_SECURE_RANDOM_STRING_HERE
WEBHOOK_SECRET=GENERATE_WEBHOOK_SECRET_HERE

# Database (Docker container)
POSTGRES_DB=doxin
POSTGRES_USER=doxin
POSTGRES_PASSWORD=CHANGE_THIS_TO_SECURE_PASSWORD
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://doxin:CHANGE_THIS_TO_SECURE_PASSWORD@postgres:5432/doxin

# Redis (Docker container)
REDIS_URL=redis://redis:6379/0
REDIS_SESSION_DB=2
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CONTAINER_REDIS_URL=redis://redis:6379/0
CONTAINER_CELERY_BROKER_URL=redis://redis:6379/0
CONTAINER_CELERY_RESULT_BACKEND=redis://redis:6379/1

# AI/LLM Configuration
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
DEFAULT_LLM_MODEL=gpt-4o
CONFIDENCE_THRESHOLD=0.8

# File Storage
BLOB_READ_WRITE_TOKEN=YOUR_VERCEL_BLOB_TOKEN_HERE
UPLOAD_FOLDER=/app/uploads

# Frontend & CORS
FRONTEND_URL=https://doxin.xyz
ALLOWED_ORIGINS=https://doxin.xyz
CORS_ORIGINS=https://doxin.xyz

# WebSocket Configuration
WEBSOCKET_ASYNC_MODE=eventlet
WEBSOCKET_LOGGER=false

# Application Settings
APP_VERSION=1.0.0
MAX_CONTENT_LENGTH=16777216
BATCH_PROCESSING_SIZE=10
WORKER_CONCURRENCY=4
REQUEST_TIMEOUT=300

# Monitoring & Metrics
METRICS_ENABLED=true
PROMETHEUS_METRICS_PATH=/metrics
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
ENABLE_PROFILING=false

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Python Path
PYTHONPATH=/app

# Admin User
INITIAL_ADMIN_EMAIL=your-admin@email.com
INITIAL_ADMIN_NAME=System Administrator
INITIAL_ADMIN_PASSWORD=CHANGE_THIS_SECURE_ADMIN_PASSWORD
```

Generate secure random strings for secrets:

```bash
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 32  # For JWT_SECRET_KEY
openssl rand -base64 32  # For WEBHOOK_SECRET
```

Save and exit (Ctrl+X, Y, Enter).

## Step 5: Deploy with Docker Compose

Create a deployment script:

```bash
cd ~/DoxIn/backend/docker
nano deploy.sh
```

Add the following:

```bash
#!/bin/bash
set -e

echo "Deploying DoxIn Backend..."

# Load production environment
export $(cat .env.production | grep -v '^#' | xargs)

# Pull latest images
echo "Pulling Docker images..."
docker compose pull postgres redis

# Build API and worker images
echo "Building application images..."
docker compose build api worker

# Start all services with full profile
echo "Starting services..."
docker compose --profile full up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo "Service Status:"
docker compose ps

# Show logs
echo "Recent logs:"
docker compose logs --tail=50

echo "Deployment complete!"
echo "API available at: http://$(curl -s ifconfig.me):8000"
echo "Grafana dashboard at: http://$(curl -s ifconfig.me):3001"
```

Make it executable and run:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Step 6: Verify Deployment

Check that all containers are running:

```bash
docker compose ps
```

Test the API health endpoint:

```bash
# Replace VM_PUBLIC_IP with your actual IP
curl http://VM_PUBLIC_IP:8000/api/v1/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T...",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

Check logs for any errors:

```bash
# API logs
docker compose logs api

# Worker logs
docker compose logs worker

# All services
docker compose logs -f
```

## Step 7: Configure Vercel Environment Variables

In your Vercel project settings (doxin.xyz), add/update these environment variables:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings > Environment Variables
4. Add/update:

```env
NEXT_PUBLIC_FLASK_API_URL=http://VM_PUBLIC_IP:8000
NEXT_PUBLIC_BACKEND_URL=http://VM_PUBLIC_IP:8000
FLASK_API_URL=http://VM_PUBLIC_IP:8000
NEXTAUTH_URL=https://doxin.xyz
NEXTAUTH_SECRET=your-nextauth-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

Replace `VM_PUBLIC_IP` with your actual GCP VM IP address.

5. Redeploy your Vercel app to pick up the new environment variables

## Step 8: Access Monitoring

Access Grafana dashboard:

```
http://VM_PUBLIC_IP:3001
```

Default credentials:
- Username: `admin`
- Password: `admin` (or value from GRAFANA_PASSWORD in .env)

Access Prometheus:

```
http://VM_PUBLIC_IP:9090
```

## Step 9: Testing

### 9.1 Test Authentication

1. Visit https://doxin.xyz
2. Click "Sign In with Google"
3. Complete Google OAuth flow
4. Verify user is created in database

### 9.2 Test File Upload

1. Upload a test document file
2. Verify file appears in Vercel Blob Storage
3. Check processing job is created
4. Monitor WebSocket updates
5. Check Celery worker logs for task processing

### 9.3 Test Security

1. Try accessing other users' files
2. Verify file access permissions work correctly
3. Test file type validation
4. Check file size limits

## Maintenance Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f postgres
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart api
docker compose restart worker
```

### Update Application Code

```bash
cd ~/DoxIn
git pull origin main
cd backend/docker
docker compose build api worker
docker compose up -d api worker
```

### Stop Services

```bash
docker compose down
```

### Backup Database

Create a backup script:

```bash
nano ~/backup-db.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR=~/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker compose exec -T postgres pg_dump -U doxin doxin | gzip > $BACKUP_DIR/doxin_backup_$TIMESTAMP.sql.gz

echo "Backup created: $BACKUP_DIR/doxin_backup_$TIMESTAMP.sql.gz"

# Keep only last 7 backups
ls -t $BACKUP_DIR/doxin_backup_*.sql.gz | tail -n +8 | xargs rm -f
```

Make executable:

```bash
chmod +x ~/backup-db.sh
```

Schedule daily backups with cron:

```bash
crontab -e
```

Add:

```
0 2 * * * /home/YOUR_USERNAME/backup-db.sh
```

## Troubleshooting

### Common Issues

#### API Returns 502 Bad Gateway

```bash
# Check API logs
docker compose logs api

# Restart API
docker compose restart api
```

#### Database Connection Errors

```bash
# Check postgres is running
docker compose ps postgres

# Check postgres logs
docker compose logs postgres

# Connect to postgres directly
docker compose exec postgres psql -U doxin -d doxin
```

#### Redis Connection Errors

```bash
# Check redis is running
docker compose ps redis

# Test redis connection
docker compose exec redis redis-cli ping
```

#### Worker Not Processing Tasks

```bash
# Check worker logs
docker compose logs worker

# Restart worker
docker compose restart worker

# Check Celery status
docker compose exec worker poetry run celery -A app.services.async_processor.celery_app inspect active
```

#### Out of Memory

```bash
# Check memory usage
free -h
docker stats

# Restart services to free memory
docker compose restart
```

#### Out of Disk Space

```bash
# Check disk usage
df -h
docker system df

# Clean up Docker resources
docker system prune -a
```

### Logs

- **Frontend**: Check Vercel function logs in Vercel dashboard
- **Backend API**: `docker compose logs api`
- **Worker**: `docker compose logs worker`
- **Database**: `docker compose logs postgres`
- **Redis**: `docker compose logs redis`

## Cost Optimization

Current setup costs approximately **$27/month**:

- e2-medium VM: ~$27/month
- 50GB SSD: ~$8.50/month
- Network egress: Variable based on usage

To reduce costs:

- Downgrade to e2-small if sufficient
- Use standard persistent disk instead of SSD
- Set up VM auto-shutdown during off-hours
- Monitor usage with GCP Cloud Monitoring

## Security Best Practices

1. **Rotate secrets regularly** - Update JWT secrets and API keys periodically
2. **Restrict firewall rules** - Limit port 8000 access to Vercel IPs only
3. **Enable audit logging** - Log all file operations and API calls
4. **Implement rate limiting** - Protect API endpoints from abuse
5. **Use Vercel Blob Storage access controls** - Ensure files are properly secured
6. **Implement proper JWT token validation** - Verify tokens on every API request
7. **Regular backups** - Ensure daily database backups are working
8. **Update dependencies** - Regularly update Docker images and system packages
9. **Monitor resources** - Set up alerts for high CPU/memory/disk usage
10. **Secure secrets** - Never commit `.env.production` to git

## Security Configuration

### Configure CORS

CORS is configured in the Flask app to allow only your Vercel domain:

```python
from flask_cors import CORS

CORS(app, origins=[
    "https://doxin.xyz",
    "http://localhost:3000"  # For development only
])
```

### Configure Vercel Blob Storage Security

```javascript
// Example: Secure file upload with Vercel Blob
import { put } from "@vercel/blob";

const blob = await put(`documents/${userId}/${fileName}`, file, {
  access: "public", // or 'private' for restricted access
  token: process.env.BLOB_READ_WRITE_TOKEN,
});
```

### Firewall Rules

For maximum security, restrict API access to Vercel IPs only:

```bash
gcloud compute firewall-rules delete allow-doxin-api

gcloud compute firewall-rules create allow-doxin-api-vercel \
  --allow=tcp:8000 \
  --source-ranges=76.76.21.21,76.76.21.22,76.76.21.93,76.76.21.164,76.76.21.241 \
  --target-tags=http-server \
  --description="Allow DoxIn API access from Vercel only"
```

## Next Steps (Optional)

1. **Add HTTPS**: Set up SSL with Let's Encrypt and a subdomain (e.g., api.doxin.xyz)
2. **Use Managed Services**: Migrate to Cloud SQL (PostgreSQL) and Memorystore (Redis)
3. **Add Load Balancer**: Set up GCP Load Balancer for high availability
4. **CI/CD**: Set up automated deployments with GitHub Actions
5. **Enhanced Monitoring**: Configure alerting in Prometheus/Grafana
6. **Automated Backups**: Use GCP Cloud Storage for backup storage

## Support

For issues or questions:

- Check logs: `docker compose logs -f`
- Review documentation in `backend/docs/`
- Check monitoring dashboards at `http://VM_IP:3001`
- Refer to GCP_DEPLOYMENT.md for detailed GCP-specific instructions
