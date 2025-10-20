# Case Study Backend

Flask API with PostgreSQL and Redis infrastructure for invoice processing, and general data analytics.

## Quick Start

### Start Services

```bash
# Start PostgreSQL and Redis containers
cd docker
docker-compose up -d postgres redis
```

### Environment Setup

```bash
# Create environment file
cp .env.template .env
# Edit .env with your configuration (see Environment Variables section)
```

### Run API

For API development setup, see `api/README.md`.

## Environment Variables

### Development

Create a `.env` file in the backend directory with these essential variables:

```env
# AI Services (required)
OPENAI_API_KEY=your-openai-api-key-here

# Database (defaults work for local Docker)
DATABASE_URL=postgresql://case-study:password@localhost:5433/case-study

# Flask
FLASK_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Redis (defaults work for local Docker)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# CORS
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# File uploads
UPLOAD_FOLDER=/tmp/uploads
MAX_CONTENT_LENGTH=16777216
```

### Production (GitHub Secrets)

Required secrets for production deployment:

```
OPENAI_API_KEY          # OpenAI API key
DATABASE_URL            # Neon PostgreSQL connection
REDIS_URL               # Azure Redis connection
FLASK_SECRET_KEY        # Flask session secret
JWT_SECRET_KEY          # JWT signing secret
AZURE_CREDENTIALS       # Service principal JSON
```

## Project Structure

```
backend/
├── api/                 # Flask API application
├── docker/             # Docker Compose services
├── terraform/          # Infrastructure as code
├── monitoring/         # Observability stack
└── docs/              # Documentation
```

## Services

### PostgreSQL Database

```bash
# Start
docker-compose up -d postgres

# Access
psql postgresql://case-study:password@localhost:5433/case-study

# Stop
docker-compose stop postgres
```

### Redis Cache

```bash
# Start
docker-compose up -d redis

# Test connection
redis-cli -h localhost -p 6379 ping

# Stop
docker-compose stop redis
```

### Monitoring (Optional)

```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access:
# - Grafana: http://localhost:3001 (admin/admin)
# - Prometheus: http://localhost:9090
```

## Troubleshooting

### Container Issues

```bash
# Check running containers
docker ps

# View container logs
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose restart postgres redis
```

### Database Connection

```bash
# Test PostgreSQL connection
psql postgresql://case-study:password@localhost:5433/case-study -c "SELECT version();"

# Test Redis connection
redis-cli -h localhost -p 6379 ping
```

### Environment Variables

```bash
# Check if .env file exists
ls -la .env

# Verify environment is loaded
cd api
poetry run python -c "import os; print('OPENAI_API_KEY set:', bool(os.getenv('OPENAI_API_KEY')))"
```

## Documentation

For detailed documentation:

- `api/README.md` - API development setup
- `docs/` - Complete documentation
- `.env.template` - All available environment variables

### Model selection

By default, the API uses `DEFAULT_LLM_MODEL=gpt-4o` for chat/completions, `gpt-4o` for vision (images in, text out), and `dall-e-3` for image generation. Recommended alternatives:

- `gpt-4o`: best general ChatGPT-capable model (multimodal, strong reasoning)
- `gpt-4o-mini`: cost-optimized chat model
- `text-embedding-3-large` or `text-embedding-3-small`: embeddings (set via `EMBEDDING_MODEL`)

Reasoning-focused models like `o3`/`o4-mini` use a different API pattern and are not drop-in replacements for `chat.completions`.
