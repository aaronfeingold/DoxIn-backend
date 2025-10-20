# Quick Start Guide - Neon DB Integration

Get up and running quickly with your Docker development environment and Neon DB production setup.

## 🚀 TL;DR - What You Get

- **Local Development**: Full Docker stack with PostgreSQL + Redis + monitoring
- **Production**: Flask API and Vercel app both connecting to the same Neon database
- **Zero Disruption**: Your current Docker workflow remains unchanged

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for Vercel)
- Azure CLI (for production deployment)

## 🏃‍♂️ Quick Start

### 1. Local Development (Docker) - Same as Before

```bash
# Start full local stack (unchanged from your current setup)
cd backend/docker
docker-compose --profile full up -d

# Services available:
# - API: http://localhost:8000
# - PostgreSQL: localhost:5433
# - Redis: localhost:6379
# - Grafana: http://localhost:3001
# - Prometheus: http://localhost:9090
# - Flower: http://localhost:5555
```

### 2. Set Up Neon DB (5 minutes)

```bash
# 1. Create Neon account: https://console.neon.tech
# 2. Create project: "case-study-invoices"
# 3. Copy connection string
# 4. Apply your schema:

cd backend
export NEON_DATABASE_URL="postgresql://user:pass@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require"
python scripts/migrate_to_neon.py
```

### 3. Test Production Connection (Local)

```bash
# Test Flask API with Neon DB
cp .env.production .env
export FLASK_ENV=production

# Test connection
python scripts/verify_neon.py

# Start production-mode API (connects to Neon)
docker-compose --profile production-api up -d
```

## 🔄 Switching Between Environments

### Local Development Mode
```bash
# Use local Docker PostgreSQL
cp .env.development .env
docker-compose --profile full up -d
```

### Production Mode
```bash
# Use Neon DB
cp .env.production .env
docker-compose --profile production up -d
```

## 🌐 Deploy to Production

### Option 1: Azure Container Apps (Recommended)
```bash
# Deploy API to Azure (connects to Neon)
az containerapp create \
  --name case-study-api \
  --image your-registry/case-study-api:latest \
  --env-vars DATABASE_URL="$NEON_DATABASE_URL"

# Deploy Vercel app (connects to same Neon DB)
vercel env add DATABASE_URL
vercel --prod
```

### Option 2: Test Locally with Production Config
```bash
# Run production stack locally (connects to Neon)
docker-compose --profile production up -d
```

## 📁 File Structure

```
backend/
├── .env.development     # Local Docker config
├── .env.production      # Neon DB config
├── scripts/
│   ├── migrate_to_neon.py   # Apply schema to Neon
│   └── verify_neon.py       # Test Neon connection
├── docker/
│   └── docker-compose.yml   # Updated with production profiles
├── api/
│   └── config.py            # Auto-detects Neon and optimizes
└── NEON_SETUP.md           # Detailed setup guide
```

## 🔧 Configuration Files

### `.env.development` (Local Docker)
```env
DATABASE_URL=postgresql://case-study:password@localhost:5433/case-study
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=development
```

### `.env.production` (Neon DB)
```env
DATABASE_URL=postgresql://user:pass@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require
REDIS_URL=redis://your-production-redis:6380
FLASK_ENV=production
```

## 🎯 Key Benefits

### Development
- **Unchanged workflow**: Your Docker setup works exactly as before
- **Full monitoring stack**: Grafana, Prometheus, AlertManager
- **Fast iteration**: No network latency, work offline

### Production
- **Shared database**: Both Flask API and Vercel app use same Neon DB
- **Auto-scaling**: Neon scales to zero when inactive
- **Database branching**: Create staging environments instantly
- **Cost-effective**: Pay only for usage

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test Neon connection
python scripts/verify_neon.py

# Check Flask app config
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('DB URL:', db.engine.url)"
```

### Docker Issues
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs case-study-api

# Restart services
docker-compose restart case-study-api
```

### Environment Issues
```bash
# Check current environment
echo $FLASK_ENV
echo $DATABASE_URL

# Verify config loading
cd backend/api
python -c "from config import config; print(config['development'].__dict__)"
```

## 📖 Next Steps

1. **Read detailed guides**:
   - `NEON_SETUP.md` - Complete Neon database setup
   - `DEPLOYMENT_VERCEL_NEON.md` - Full production deployment

2. **Set up monitoring**: Use Neon console + your existing Grafana

3. **Configure CI/CD**: Deploy API to Azure, frontend to Vercel

4. **Database branching**: Create staging branches in Neon

## 💡 Tips

- Keep `.env.development` for local work
- Use `.env.production` for production testing
- Your Docker development environment is unchanged
- Both Flask and Vercel connect to the same Neon database
- Use database branching for testing without affecting production

You now have the best of both worlds: rich local development with Docker and simple, cost-effective production with Neon! 🎉