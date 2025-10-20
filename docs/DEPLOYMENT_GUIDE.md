# Container Deployment Guide

## Overview

This guide covers deploying the backend service using Docker containers across development and production environments. The configuration has been unified to support both local PostgreSQL and Neon database deployments.

## Environment Configuration

### Unified Environment Variables

All environment configurations now use consistent variable names across development and production:

#### **Database Configuration**
```bash
# Standard variables (used in both dev and prod)
POSTGRES_DB=case-study
POSTGRES_USER=case-study
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost  # or Neon endpoint
POSTGRES_PORT=5433       # 5433 for local, 5432 for Neon

# Computed DATABASE_URL
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Production Neon URL (overrides computed URL)
NEON_DATABASE_URL=postgresql://username:password@ep-your-endpoint.us-east-1.aws.neon.tech/your-database?sslmode=require
```

#### **Redis Configuration**
```bash
# Local Redis (development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

# External Redis (production)
PRODUCTION_REDIS_URL=redis://your-redis-instance.redis.cache.windows.net:6380?ssl=true&password=your-redis-password

# Container Redis URLs (when running in Docker)
CONTAINER_REDIS_URL=redis://redis:6379/0
CONTAINER_CELERY_BROKER_URL=redis://redis:6379/0
CONTAINER_CELERY_RESULT_BACKEND=redis://redis:6379/1
```

### Environment Files

#### `.env.development` - Local Development
- Uses local PostgreSQL on port 5433
- Uses local Redis on port 6379
- Debug mode enabled
- Lower worker concurrency for development

#### `.env.production` - Production Deployment
- Uses Neon PostgreSQL
- Uses external Redis (Azure/AWS)
- Production security settings
- Higher worker concurrency

## Deployment Scenarios

### 1. Development with Local Services

**Setup:**
```bash
# Copy development environment
cp .env.development .env

# Start local database and Redis
docker-compose --profile local-db up -d

# Run API locally (outside container)
cd backend/api
pip install -r requirements.txt
python app.py
```

**Database URL:** `postgresql://case-study:password@localhost:5433/case-study`

### 2. Development with Containerized API

**Setup:**
```bash
# Copy development environment
cp .env.development .env

# Start all development services
docker-compose --profile full up -d
```

**Services:**
- **PostgreSQL**: `localhost:5433` (pgvector enabled)
- **Redis**: `localhost:6379`
- **API**: `localhost:8000`
- **Worker**: Background processing
- **Flower**: `localhost:5555` (Celery monitoring)

### 3. Production with External Database

**Setup:**
```bash
# Copy and configure production environment
cp .env.production .env

# Edit .env with your actual values:
# - NEON_DATABASE_URL
# - PRODUCTION_REDIS_URL
# - SECRET_KEY
# - OPENAI_API_KEY
# - etc.

# Start production services
docker-compose --profile production up -d
```

**Services:**
- **External PostgreSQL**: Neon database
- **External Redis**: Azure/AWS Redis
- **API**: `localhost:8000` (production mode)
- **Worker**: Background processing (production)

### 4. Hybrid: Production with Containerized Redis

**Setup:**
```bash
# Use production env but override Redis to use local container
cp .env.production .env

# Override Redis settings in .env:
REDIS_URL=${CONTAINER_REDIS_URL}
CELERY_BROKER_URL=${CONTAINER_CELERY_BROKER_URL}
CELERY_RESULT_BACKEND=${CONTAINER_CELERY_RESULT_BACKEND}

# Start production API with local Redis
docker-compose --profile production --profile local-db up -d
```

## Docker Compose Profiles

The docker-compose.yml uses profiles to control which services start:

### Available Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `local-db` | postgres, redis | Local database development |
| `api` | api | Development API only |
| `worker` | worker | Development worker only |
| `production` | api-production, worker-production | Production deployment |
| `production-api` | api-production | Production API only |
| `production-worker` | worker-production | Production worker only |
| `monitoring` | prometheus, grafana, exporters | Monitoring stack |
| `full` | All development services | Complete development environment |

### Profile Commands

```bash
# Development with all services
docker-compose --profile full up -d

# Production services only
docker-compose --profile production up -d

# Local database + production API
docker-compose --profile local-db --profile production-api up -d

# Add monitoring to any setup
docker-compose --profile full --profile monitoring up -d
```

## Service Configurations

### API Service

**Development (`api`):**
- Port: `8000`
- Database: Local PostgreSQL container
- Redis: Local Redis container
- Concurrency: 2 workers
- Debug mode enabled

**Production (`api-production`):**
- Port: `8000`
- Database: External Neon
- Redis: External or container Redis
- Concurrency: 4 workers
- Production optimizations

### Worker Service

**Development (`worker`):**
- Concurrency: 2
- Debug logging
- Local dependencies

**Production (`worker-production`):**
- Concurrency: 4
- Info logging
- External dependencies

### Health Checks

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Environment Variable Reference

### Core Application
```bash
FLASK_ENV=development|production
ENVIRONMENT=development|production
SECRET_KEY=your-secret-key
DEBUG=true|false
APP_VERSION=1.0.0
```

### Database
```bash
POSTGRES_DB=database-name
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_HOST=hostname
POSTGRES_PORT=5432
DATABASE_URL=full-connection-string
NEON_DATABASE_URL=neon-connection-string
```

### Redis & Celery
```bash
REDIS_HOST=hostname
REDIS_PORT=6379
REDIS_URL=redis-connection-string
CELERY_BROKER_URL=broker-url
CELERY_RESULT_BACKEND=result-backend-url
PRODUCTION_REDIS_URL=external-redis-url
```

### AI/LLM
```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
DEFAULT_LLM_MODEL=gpt-4o-mini
CONFIDENCE_THRESHOLD=0.8
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

### Frontend & CORS
```bash
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
CORS_ORIGINS=frontend-urls
```

### Security
```bash
WEBHOOK_SECRET=webhook-secret
JWT_SECRET_KEY=jwt-secret
SSL_DISABLE=false
SECURE_HEADERS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

### Performance
```bash
MAX_CONTENT_LENGTH=16777216
BATCH_PROCESSING_SIZE=5|10
WORKER_CONCURRENCY=2|4
REQUEST_TIMEOUT=120|300
```

### Monitoring
```bash
METRICS_ENABLED=true
PROMETHEUS_METRICS_PATH=/metrics
LOG_LEVEL=DEBUG|INFO
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
ENABLE_PROFILING=true|false
```

## Quick Start Commands

### Development Setup
```bash
# 1. Copy environment
cp .env.development .env

# 2. Start everything
docker-compose --profile full up -d

# 3. Check logs
docker-compose logs -f api

# 4. Access services
# API: http://localhost:8000
# Flower: http://localhost:5555
# Database: localhost:5433
```

### Production Deployment
```bash
# 1. Configure production environment
cp .env.production .env
# Edit .env with your actual credentials

# 2. Start production services
docker-compose --profile production up -d

# 3. Monitor
docker-compose logs -f api-production worker-production

# 4. Health check
curl http://localhost:8000/api/health
```

### Monitoring Setup
```bash
# Add monitoring to any profile
docker-compose --profile full --profile monitoring up -d

# Access dashboards:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
# AlertManager: http://localhost:9093
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres

   # Check PostgreSQL logs
   docker-compose logs postgres

   # Test connection
   docker-compose exec postgres psql -U case-study -d case-study
   ```

2. **Redis Connection Failed**
   ```bash
   # Check Redis status
   docker-compose ps redis

   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

3. **API Not Starting**
   ```bash
   # Check API logs
   docker-compose logs api

   # Verify environment variables
   docker-compose exec api env | grep -E "(DATABASE_URL|REDIS_URL)"
   ```

4. **Worker Not Processing Jobs**
   ```bash
   # Check worker logs
   docker-compose logs worker

   # Check Celery status
   docker-compose exec worker celery -A app.services.background_processor.celery_app inspect ping
   ```

### Environment Variable Debugging

```bash
# Show all environment variables in container
docker-compose exec api env | sort

# Test database connection
docker-compose exec api python -c "
import os
from sqlalchemy import create_engine
url = os.getenv('DATABASE_URL')
print(f'Testing: {url}')
engine = create_engine(url)
conn = engine.connect()
print('Database connection successful!')
conn.close()
"
```

## Migration from Old Configuration

If upgrading from the previous configuration:

1. **Backup existing `.env`**
   ```bash
   cp .env .env.backup
   ```

2. **Update to new format**
   ```bash
   # Use appropriate template
   cp .env.development .env  # or .env.production

   # Migrate your custom values from .env.backup
   ```

3. **Test the new configuration**
   ```bash
   docker-compose --profile full up -d
   ```

The new configuration is backward compatible but provides more flexibility for container deployments across different environments.