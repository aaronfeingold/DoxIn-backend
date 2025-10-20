# Case Study Invoice Intelligence - Docker Setup

This directory contains the Docker Compose configuration for the Case Study Invoice Intelligence system.

## Services

### Core Services

- **case-study-postgres**: PostgreSQL database with pgvector support
- **case-study-redis**: Redis for message brokering and caching
- **case-study-api**: Flask API with WebSocket support
- **case-study-worker**: Celery background worker for processing
- **case-study-flower**: Celery monitoring dashboard (optional)

## Quick Start

### 1. Start All Services

```bash
cd backend/docker
docker-compose --profile full up -d
```

### 2. Start Specific Services

```bash
# Database only (PostgreSQL + Redis)
docker-compose --profile local-db up -d

# API services (with local database)
docker-compose --profile api up -d

# Worker services (with local database)
docker-compose --profile worker up -d

# Production API (with Neon DB)
docker-compose --profile production-api up -d

# Production Worker (with Neon DB)
docker-compose --profile production-worker up -d

# Full production stack (API + Worker + Monitoring, uses Neon DB)
docker-compose --profile production up -d

# Monitoring
docker-compose --profile monitoring up -d
```

### 3. Using the Startup Script

```bash
cd backend
./scripts/start-case-study.sh [profile]

# Examples:
./scripts/start-case-study.sh full      # Start everything
./scripts/start-case-study.sh db        # Database only
./scripts/start-case-study.sh api       # API services
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
POSTGRES_DB=case-study
POSTGRES_USER=case-study
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

### Production with Neon (.env.production)
For production deployment with Neon DB:

```bash
# Neon Database
NEON_DATABASE_URL=postgresql://user:pass@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require

# Production Redis (Azure Cache for Redis)
PRODUCTION_REDIS_URL=redis://your-redis.cache.windows.net:6380?ssl=true&password=your-password

# Flask Production
FLASK_ENV=production
SECRET_KEY=your-production-secret

# AI/LLM Production Keys
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-anthropic-key

# Production File Storage
BLOB_READ_WRITE_TOKEN=your-production-blob-token
FRONTEND_URL=https://your-app.vercel.app
```

## Development Workflow

### 1. Start Services

```bash
cd backend
./scripts/start-case-study.sh full
```

### 2. View Logs

```bash
cd docker
docker-compose logs -f [service-name]

# Examples:
docker-compose logs -f case-study-api
docker-compose logs -f case-study-worker
```

### 3. Stop Services

```bash
cd docker
docker-compose down
```

### 4. Rebuild Services

```bash
cd docker
docker-compose build --no-cache
docker-compose up -d
```

## Service Profiles

### `local-db`

- PostgreSQL
- Redis

### `api`

- PostgreSQL
- Redis
- Flask API

### `worker`

- PostgreSQL
- Redis
- Celery Worker

### `monitoring`

- Redis
- Flower

### `full`

- All services

## Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping`
- **API**: HTTP health endpoint
- **Worker**: Celery inspect ping

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs

# Check service status
docker-compose ps

# Restart specific service
docker-compose restart case-study-api
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose logs case-study-postgres

# Connect to database
docker-compose exec case-study-postgres psql -U case-study -d case-study
```

### Redis Connection Issues

```bash
# Check Redis logs
docker-compose logs case-study-redis

# Connect to Redis CLI
docker-compose exec case-study-redis redis-cli
```

### Debugging Redis Pub/Sub and Message Brokering

Redis is used for Celery task queuing and Socket.IO pub/sub communication between API processes and frontend.

**Monitor all Redis activity in real-time:**
```bash
docker-compose exec case-study-redis redis-cli MONITOR
```

**Monitor Socket.IO pub/sub channels (for frontend streaming):**
```bash
# Subscribe to Socket.IO channels
docker-compose exec case-study-redis redis-cli PSUBSCRIBE 'socket.io*'

# List active Socket.IO channels
docker-compose exec case-study-redis redis-cli PUBSUB CHANNELS 'socket.io*'
```

**Monitor Celery queues and tasks:**
```bash
# Enter Redis CLI
docker-compose exec case-study-redis redis-cli

# Inside CLI, run:
KEYS celery*              # See all Celery keys
LLEN celery               # Check default queue length
KEYS *task*               # See task-related keys
GET celery-task-meta-*    # View task results
```

**Debug specific pub/sub channels:**
```bash
# Subscribe to specific channel
docker-compose exec case-study-redis redis-cli SUBSCRIBE channel_name

# Subscribe with pattern matching
docker-compose exec case-study-redis redis-cli PSUBSCRIBE pattern*

# List all active channels
docker-compose exec case-study-redis redis-cli PUBSUB CHANNELS

# Count subscribers on a channel
docker-compose exec case-study-redis redis-cli PUBSUB NUMSUB channel_name
```

**Common debugging scenarios:**
```bash
# Check if messages are being published
docker-compose exec case-study-redis redis-cli MONITOR | grep PUBLISH

# View all keys to understand data structure
docker-compose exec case-study-redis redis-cli KEYS '*'

# Check memory usage
docker-compose exec case-study-redis redis-cli INFO memory

# Check connected clients
docker-compose exec case-study-redis redis-cli CLIENT LIST
```

### API Health Check

```bash
# Test API health
curl http://localhost:8000/api/health
```

## Production Deployment

For production deployment to Azure Container Apps:

1. Build and push images to Azure Container Registry
2. Deploy using Azure Container Apps
3. Configure environment variables
4. Set up monitoring and logging

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
