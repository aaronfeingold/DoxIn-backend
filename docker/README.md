# DoxIn - Docker Setup

This directory contains the Docker Compose configuration for the DoxIn invoice processing system.

## Overview

DoxIn supports multiple deployment modes to fit different stages of your project:

| Deployment Mode | Database | Cache | Compute | Use Case |
|----------------|----------|-------|---------|----------|
| **Local Development** | Containerized PostgreSQL | Containerized Redis | Docker Compose | Rapid development, testing |
| **Initial Production** | Containerized PostgreSQL | Containerized Redis | GCP VM/GKE | Quick production deployment, proof-of-concept |
| **Scaled Production** | Neon (Serverless) | Upstash (Serverless) | GCP Cloud Run | Ultimate scalability, global distribution |

### Key Differences

**Local Development**:
- All services run in containers on your machine
- Data persisted in Docker volumes
- Full monitoring stack included
- Ideal for development and debugging

**Initial Production (GCP)**:
- All services containerized for easy distribution
- Can deploy to a single VM or multiple nodes
- Simple `docker-compose up` on GCP Compute Engine
- Database and Redis still containerized
- Demonstrates solid deployment principles
- Ready for horizontal scaling when needed
- Good for 100-1000 concurrent users

**Scaled Production (Neon + Upstash)**:
- Managed PostgreSQL (Neon) with auto-scaling and serverless architecture
- Managed Redis (Upstash) with global edge caching
- API and Worker containers deploy independently
- True horizontal scalability (scale to thousands of concurrent users)
- Pay-per-use pricing model
- No database container dependencies
- Optimal for production at scale

## Services

### Core Services

- **postgres**: PostgreSQL database with pgvector support
- **redis**: Redis for message brokering and caching
- **api**: Flask API with WebSocket support (local development)
- **api-production**: Flask API configured for external managed databases
- **worker**: Celery background worker for processing (local development)
- **worker-production**: Celery worker configured for external managed databases
- **flower**: Celery monitoring dashboard (optional)

### Monitoring Services

- **prometheus**: Metrics collection and storage
- **grafana**: Monitoring dashboards and visualization
- **node-exporter**: System and container metrics
- **postgres-exporter**: Database metrics
- **redis-exporter**: Redis metrics
- **alertmanager**: Alert handling and notifications

## Deployment Strategies

### Strategy 1: Local Development
**Use Case**: Local development with hot reload, full monitoring stack

**Services**: Containerized PostgreSQL + Redis + API + Worker + Monitoring

**Command**:
```bash
cd backend/docker
docker-compose --profile full up -d
```

**Characteristics**:
- All services run locally in containers
- Database and Redis data persisted in Docker volumes
- Full monitoring stack (Prometheus, Grafana, Flower)
- Ideal for development and testing

---

### Strategy 2: Initial Production (GCP Container Deployment)
**Use Case**: Quick production deployment to GCP with containerized infrastructure

**Target Platform**: Google Cloud Platform (Compute Engine, GKE, or Cloud Run)

**Services**: Containerized PostgreSQL + Redis + API + Worker (all in containers)

**Command**:
```bash
cd backend/docker
docker-compose --profile full up -d
```

**Deployment Options**:

1. **GCP Compute Engine (VM)**:
   - Deploy Docker Compose stack to a single VM or multiple VMs
   - Simple `docker-compose up` on the VM
   - Good for initial production release and proof-of-concept

2. **GCP Kubernetes Engine (GKE)**:
   - Convert docker-compose.yml to Kubernetes manifests
   - Deploy as pods with persistent volumes
   - Better for production with automatic restarts and health checks

3. **GCP Cloud Run** (individual services):
   - Build and deploy each service separately
   - Use Cloud SQL for PostgreSQL and Memorystore for Redis
   - Most scalable but requires more setup

**Characteristics**:
- All services containerized for easy distribution
- Can run on a single server or distributed across nodes
- Database and Redis can scale independently
- Demonstrates solid deployment principles
- Ready for horizontal scaling when needed

---

### Strategy 3: Scaled Production (Managed External Services)
**Use Case**: Horizontally scalable production with managed databases

**Target Architecture**: 
- **Database**: Neon PostgreSQL (serverless, auto-scaling)
- **Cache**: Upstash Redis (serverless, globally distributed)
- **Compute**: GCP Cloud Run or multiple container instances

**Services**: API + Worker containers connected to external managed services

**Command**:
```bash
cd backend/docker
# Configure .env.production with Neon and Upstash URLs
docker-compose --profile production up -d
```

**Production Profiles**:
```bash
# API only (connects to Neon + Upstash)
docker-compose --profile production-api up -d

# Worker only (connects to Neon + Upstash)
docker-compose --profile production-worker up -d

# Full production stack (API + Worker + Monitoring)
docker-compose --profile production up -d
```

**Characteristics**:
- Managed PostgreSQL (Neon) with auto-scaling and serverless architecture
- Managed Redis (Upstash) with global edge caching
- API and Worker services can scale horizontally independently
- No database container dependencies
- Optimal for high-scale production workloads
- Pay-per-use pricing model

---

## Quick Start Commands

### Local Development
```bash
cd backend/docker
docker-compose --profile full up -d
```

### Initial GCP Production (All Containerized)
```bash
# On GCP VM or locally before deploying
cd backend/docker
docker-compose --profile full up -d
```

### Scaled Production (External Managed DBs)
```bash
cd backend/docker
# Ensure .env.production has NEON_DATABASE_URL and PRODUCTION_REDIS_URL
docker-compose --profile production up -d
```

### Individual Services
```bash
# Database only (PostgreSQL + Redis)
docker-compose --profile local-db up -d

# API only (local development)
docker-compose --profile api up -d

# Worker only (local development)
docker-compose --profile worker up -d

# Production API only (external Neon + Upstash)
docker-compose --profile production-api up -d

# Production Worker only (external Neon + Upstash)
docker-compose --profile production-worker up -d

# Monitoring stack only
docker-compose --profile monitoring up -d
```

## Service URLs

### Core Services
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6379

### Monitoring UIs
- **Flower** (Celery monitoring): http://localhost:5555
- **Grafana** (Dashboards and visualization): http://localhost:3001 (default credentials: admin/admin)
- **Prometheus** (Metrics): http://localhost:9090
- **AlertManager** (Alert management): http://localhost:9093

## Environment Configuration

### Local Development (.env)
Create a `.env` file in the backend directory with:

```bash
# Database (Local Docker)
POSTGRES_DB=doxin
POSTGRES_USER=doxin
POSTGRES_PASSWORD=password

# Redis (Local Docker)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# AI/LLM
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# File Storage
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

### Initial Production on GCP (.env)
For initial production deployment with containerized services on GCP:

```bash
# Database (Containerized PostgreSQL)
POSTGRES_DB=doxin
POSTGRES_USER=doxin
POSTGRES_PASSWORD=strong-production-password

# Redis (Containerized Redis)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Flask Production
FLASK_ENV=production
ENVIRONMENT=production
SECRET_KEY=your-production-secret
DEBUG=false

# AI/LLM Production Keys
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-anthropic-key

# Production File Storage
BLOB_READ_WRITE_TOKEN=your-production-blob-token
FRONTEND_URL=https://your-app.vercel.app

# Security
WEBHOOK_SECRET=your-webhook-secret
JWT_SECRET_KEY=your-jwt-secret
```

### Scaled Production with Neon + Upstash (.env.production)
For horizontally scaled production with managed external services:

```bash
# Neon Database (Serverless PostgreSQL)
NEON_DATABASE_URL=postgresql://user:pass@ep-name-123.us-east-1.aws.neon.tech/doxin?sslmode=require

# Upstash Redis (Serverless Redis)
PRODUCTION_REDIS_URL=rediss://default:your-password@us1-flowing-mantis-12345.upstash.io:6379

# Flask Production
FLASK_ENV=production
ENVIRONMENT=production
SECRET_KEY=your-production-secret
DEBUG=false

# AI/LLM Production Keys
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-anthropic-key

# Production File Storage
BLOB_READ_WRITE_TOKEN=your-production-blob-token
FRONTEND_URL=https://your-app.vercel.app

# Security
WEBHOOK_SECRET=your-webhook-secret
JWT_SECRET_KEY=your-jwt-secret
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# Application Settings
APP_VERSION=1.0.0
WORKER_CONCURRENCY=4
BATCH_PROCESSING_SIZE=10
```

## Development Workflow

### 1. Start Services

```bash
cd backend/docker
docker-compose --profile full up -d
```

### 2. View Logs

```bash
cd backend/docker
docker-compose logs -f [service-name]

# Examples:
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 3. Stop Services

```bash
cd backend/docker
docker-compose down
```

### 4. Rebuild Services

```bash
cd backend/docker
docker-compose build --no-cache
docker-compose --profile full up -d
```

### 5. Clean Up Volumes (Reset Database)

```bash
cd backend/docker
docker-compose down -v  # Removes volumes
```

## Service Profiles

The docker-compose.yml supports multiple profiles for different deployment scenarios:

### `local-db`
**Services**: PostgreSQL + Redis only

**Use Case**: When you want to run the database locally but run API/Worker outside Docker (e.g., in your IDE)

```bash
docker-compose --profile local-db up -d
```

### `api`
**Services**: PostgreSQL + Redis + API

**Use Case**: Local development with API in container, manual worker testing

```bash
docker-compose --profile api up -d
```

### `worker`
**Services**: PostgreSQL + Redis + Worker

**Use Case**: Testing background job processing in isolation

```bash
docker-compose --profile worker up -d
```

### `monitoring`
**Services**: PostgreSQL + Redis + Worker + Flower + Prometheus + Grafana + Exporters + AlertManager

**Use Case**: Full monitoring stack for observability testing

```bash
docker-compose --profile monitoring up -d
```

### `full`
**Services**: All services (PostgreSQL + Redis + API + Worker + Monitoring)

**Use Case**: Complete local development environment

```bash
docker-compose --profile full up -d
```

### `production-api`
**Services**: Redis + API (connects to external Neon DB)

**Use Case**: Production API deployment with managed database

**Requirements**: Set `NEON_DATABASE_URL` and `PRODUCTION_REDIS_URL` in environment

```bash
docker-compose --profile production-api up -d
```

### `production-worker`
**Services**: Redis + Worker (connects to external Neon DB)

**Use Case**: Production worker deployment with managed database

**Requirements**: Set `NEON_DATABASE_URL` and `PRODUCTION_REDIS_URL` in environment

```bash
docker-compose --profile production-worker up -d
```

### `production`
**Services**: Redis + API + Worker + Flower (all connect to external Neon DB)

**Use Case**: Full production stack with managed external database

**Requirements**: Set `NEON_DATABASE_URL` and `PRODUCTION_REDIS_URL` in environment

```bash
docker-compose --profile production up -d
```

## Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping`
- **API**: HTTP health endpoint
- **Worker**: Celery inspect ping

## GCP Deployment Guide

### Option 1: GCP Compute Engine (Quick Start)

**Best for**: Initial production release, proof-of-concept, easy deployment

**Steps**:

1. **Create a GCP VM**:
```bash
gcloud compute instances create doxin-server \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --tags=http-server,https-server
```

2. **SSH into the VM**:
```bash
gcloud compute ssh doxin-server --zone=us-central1-a
```

3. **Install Docker and Docker Compose**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes
exit
```

4. **Clone Repository and Deploy**:
```bash
# SSH back in
gcloud compute ssh doxin-server --zone=us-central1-a

# Clone your repo
git clone https://github.com/your-org/doxin.git
cd doxin/backend/docker

# Create .env file with your configuration
nano .env

# Start all services
docker-compose --profile full up -d

# View logs
docker-compose logs -f
```

5. **Configure Firewall**:
```bash
# Allow HTTP/HTTPS traffic
gcloud compute firewall-rules create doxin-http \
  --allow tcp:80,tcp:443,tcp:8000 \
  --target-tags=http-server

# Allow monitoring ports (optional)
gcloud compute firewall-rules create doxin-monitoring \
  --allow tcp:3001,tcp:5555,tcp:9090 \
  --target-tags=http-server
```

**Characteristics**:
- Single VM deployment
- All services containerized
- Data persisted in Docker volumes
- Easy to set up and manage
- Good for 100-1000 concurrent users
- Can scale vertically by increasing VM size

---

### Option 2: GCP Kubernetes Engine (GKE)

**Best for**: Production-ready deployment, auto-scaling, high availability

**Steps**:

1. **Create GKE Cluster**:
```bash
gcloud container clusters create doxin-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-standard-2 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10
```

2. **Convert Docker Compose to Kubernetes**:
```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/latest/download/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert docker-compose.yml
cd backend/docker
kompose convert -f docker-compose.yml -o k8s/
```

3. **Deploy to GKE**:
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services

# Expose API service
kubectl expose deployment api --type=LoadBalancer --port=8000
```

**Characteristics**:
- Multi-node cluster
- Automatic pod restarts
- Load balancing built-in
- Horizontal pod autoscaling
- Good for 1000+ concurrent users
- Higher operational complexity

---

### Option 3: GCP Cloud Run (Microservices)

**Best for**: Serverless deployment, pay-per-use, ultimate scalability

**Steps**:

1. **Build and Push Container Images**:
```bash
# Set up GCP Container Registry
gcloud auth configure-docker

# Build API image
cd backend/api
docker build -t gcr.io/YOUR_PROJECT_ID/doxin-api:latest .
docker push gcr.io/YOUR_PROJECT_ID/doxin-api:latest

# Build Worker image (same Dockerfile, different command)
docker build -t gcr.io/YOUR_PROJECT_ID/doxin-worker:latest .
docker push gcr.io/YOUR_PROJECT_ID/doxin-worker:latest
```

2. **Set Up Managed Services**:
```bash
# Create Cloud SQL for PostgreSQL (or use Neon)
gcloud sql instances create doxin-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create Memorystore for Redis (or use Upstash)
gcloud redis instances create doxin-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

3. **Deploy to Cloud Run**:
```bash
# Deploy API
gcloud run deploy doxin-api \
  --image=gcr.io/YOUR_PROJECT_ID/doxin-api:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...,REDIS_URL=redis://..."

# Deploy Worker
gcloud run deploy doxin-worker \
  --image=gcr.io/YOUR_PROJECT_ID/doxin-worker:latest \
  --platform=managed \
  --region=us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...,REDIS_URL=redis://..." \
  --command="poetry,run,celery,-A,app.services.async_processor.celery_app,worker,--loglevel=INFO"
```

**Characteristics**:
- Fully serverless
- Automatic scaling (0 to N)
- Pay only for requests
- No server management
- Best with Cloud SQL/Memorystore or Neon/Upstash
- Excellent for variable workloads

---

### Option 4: Scaled Production (Neon + Upstash + GCP)

**Best for**: Ultimate scalability, global distribution, serverless everything

**Architecture**:
- **Database**: Neon (serverless PostgreSQL)
- **Cache**: Upstash (serverless Redis)
- **Compute**: GCP Cloud Run or multiple VM instances
- **Frontend**: Vercel

**Steps**:

1. **Set Up Neon Database**:
   - Go to https://neon.tech
   - Create a new project
   - Copy the connection string
   - Enable connection pooling

2. **Set Up Upstash Redis**:
   - Go to https://upstash.com
   - Create a new Redis database
   - Copy the connection string (rediss://...)

3. **Configure Environment**:
```bash
# Create .env.production
cat > .env.production << EOF
NEON_DATABASE_URL=postgresql://user:pass@ep-name-123.us-east-1.aws.neon.tech/doxin?sslmode=require
PRODUCTION_REDIS_URL=rediss://default:pass@us1-flowing-mantis-12345.upstash.io:6379
FLASK_ENV=production
ENVIRONMENT=production
# ... other production vars
EOF
```

4. **Deploy API Containers**:
```bash
# Option A: Cloud Run
gcloud run deploy doxin-api \
  --image=gcr.io/YOUR_PROJECT_ID/doxin-api:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --env-vars-file=.env.production \
  --min-instances=1 \
  --max-instances=100

# Option B: Multiple VMs
# Deploy docker-compose with production profile to multiple VMs
docker-compose --profile production-api up -d
```

5. **Deploy Worker Containers**:
```bash
# Cloud Run
gcloud run deploy doxin-worker \
  --image=gcr.io/YOUR_PROJECT_ID/doxin-worker:latest \
  --platform=managed \
  --region=us-central1 \
  --no-allow-unauthenticated \
  --env-vars-file=.env.production \
  --min-instances=1 \
  --max-instances=20 \
  --command="poetry,run,celery,-A,app.services.async_processor.celery_app,worker,--loglevel=INFO"
```

**Horizontal Scaling Strategy**:

1. **API Scaling**:
   - Deploy multiple API container instances
   - Use GCP Load Balancer to distribute traffic
   - Each API instance connects to Neon and Upstash
   - Scale based on request load (CPU/Memory metrics)

2. **Worker Scaling**:
   - Deploy multiple Worker container instances
   - Each worker connects to same Celery queue (Upstash Redis)
   - Workers automatically pick up tasks from queue
   - Scale based on queue depth and processing time

3. **Database Scaling**:
   - Neon automatically scales compute and storage
   - Connection pooling handles multiple API/Worker connections
   - Read replicas for read-heavy workloads

4. **Cache Scaling**:
   - Upstash Redis scales automatically
   - Global replication for low latency
   - Automatic failover and high availability

**Benefits**:
- True horizontal scalability
- No single point of failure
- Pay only for what you use
- Global distribution
- Minimal operational overhead

---

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs

# Check service status
docker-compose ps

# Restart specific service
docker-compose restart api
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U doxin -d doxin
```

### Redis Connection Issues

```bash
# Check Redis logs
docker-compose logs redis

# Connect to Redis CLI
docker-compose exec redis redis-cli
```

### Debugging Redis Pub/Sub and Message Brokering

Redis is used for Celery task queuing and Socket.IO pub/sub communication between API processes and frontend.

**Monitor all Redis activity in real-time:**
```bash
docker-compose exec redis redis-cli MONITOR
```

**Monitor Socket.IO pub/sub channels (for frontend streaming):**
```bash
# Subscribe to Socket.IO channels
docker-compose exec redis redis-cli PSUBSCRIBE 'socket.io*'

# List active Socket.IO channels
docker-compose exec redis redis-cli PUBSUB CHANNELS 'socket.io*'
```

**Monitor Celery queues and tasks:**
```bash
# Enter Redis CLI
docker-compose exec redis redis-cli

# Inside CLI, run:
KEYS celery*              # See all Celery keys
LLEN celery               # Check default queue length
KEYS *task*               # See task-related keys
GET celery-task-meta-*    # View task results
```

**Debug specific pub/sub channels:**
```bash
# Subscribe to specific channel
docker-compose exec redis redis-cli SUBSCRIBE channel_name

# Subscribe with pattern matching
docker-compose exec redis redis-cli PSUBSCRIBE pattern*

# List all active channels
docker-compose exec redis redis-cli PUBSUB CHANNELS

# Count subscribers on a channel
docker-compose exec redis redis-cli PUBSUB NUMSUB channel_name
```

**Common debugging scenarios:**
```bash
# Check if messages are being published
docker-compose exec redis redis-cli MONITOR | grep PUBLISH

# View all keys to understand data structure
docker-compose exec redis redis-cli KEYS '*'

# Check memory usage
docker-compose exec redis redis-cli INFO memory

# Check connected clients
docker-compose exec redis redis-cli CLIENT LIST
```

### API Health Check

```bash
# Test API health
curl http://localhost:8000/api/health
```

## Production Deployment Summary

DoxIn supports multiple production deployment strategies:

### Recommended Path for Initial Release
Use **GCP Compute Engine** (Option 1 in [GCP Deployment Guide](#gcp-deployment-guide)) for quick production deployment:
- Deploy entire Docker Compose stack to a single GCP VM
- All services containerized for easy distribution
- Simple setup with `docker-compose --profile full up -d`
- Demonstrates solid deployment principles
- Ready for horizontal scaling when needed

### Recommended Path for Scaled Production
Use **Neon + Upstash + GCP Cloud Run** (Option 4 in [GCP Deployment Guide](#gcp-deployment-guide)) for ultimate scalability:
- Managed PostgreSQL (Neon) with auto-scaling
- Managed Redis (Upstash) with global edge caching
- Serverless containers on GCP Cloud Run
- True horizontal scalability
- Pay-per-use pricing model

### Other Options
- **GKE (Option 2)**: Kubernetes for production-grade orchestration
- **Cloud Run (Option 3)**: Fully serverless microservices

See the [GCP Deployment Guide](#gcp-deployment-guide) section above for detailed instructions on each option.

## File Structure

```
backend/
├── docker/
│   ├── docker-compose.yml    # Main compose file
│   └── README.md            # This file
├── scripts/
│   └── start-case-study.sh  # Startup script
├── Dockerfile               # Backend container
├── requirements.txt         # Python dependencies
└── .env.example            # Environment template
```
