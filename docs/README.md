# Backend Documentation

> Comprehensive documentation for the Case-Study backend system

## 📚 Documentation Index

### 🚀 Getting Started & Development
- [**Main README**](../README.md) - Project setup and local development
- [**Quick Start Guide**](QUICK_START.md) - Fast setup for development
- [**Database Connection Guide**](#%EF%B8%8F-database-connection-guide) - Connect to PostgreSQL and Redis

### 🔌 API & Integration
- [**Complete API Documentation**](API_DOCUMENTATION.md) - Full API reference with endpoints, WebSocket streaming, and React examples
- [**LLM Integration Summary**](LLM_INTEGRATION_SUMMARY.md) - AI/ML service architecture and implementation

### 🏗️ Architecture & Design
- [**System Architecture**](ARCHITECTURE.md) - Component relationships and system design
- [**Deployment Guide**](DEPLOYMENT_GUIDE.md) - Production deployment procedures and best practices

### ☁️ Cloud & Production
- [**Neon Database Setup**](NEON_SETUP.md) - Serverless PostgreSQL configuration
- [**Vercel Deployment**](DEPLOYMENT_VERCEL_NEON.md) - Frontend deployment with Vercel and Neon

### 📜 Legacy Documentation
- [**Legacy Deployment**](DEPLOYMENT.md) - Original deployment documentation (archived)

## 🚀 Quick Navigation

| I want to... | Go to... |
|---------------|----------|
| **Set up the project locally** | [Main README](../README.md) |
| **Connect to the database** | [Database Connection Guide](#%EF%B8%8F-database-connection-guide) |
| **Use the API endpoints** | [Complete API Documentation](API_DOCUMENTATION.md) |
| **Understand the system design** | [System Architecture](ARCHITECTURE.md) |
| **Deploy to production** | [Deployment Guide](DEPLOYMENT_GUIDE.md) |
| **Set up cloud database** | [Neon Database Setup](NEON_SETUP.md) |

### 🏃‍♂️ First Time Setup
1. Follow the [Main README](../README.md) for project setup
2. Use the [Database Connection Guide](#%EF%B8%8F-database-connection-guide) to connect to PostgreSQL
3. Test with [API Documentation](API_DOCUMENTATION.md) endpoints
4. Review [System Architecture](ARCHITECTURE.md) to understand the codebase

## 🗄️ Database Connection Guide

### Docker PostgreSQL (Development)

**Connection Details:**
- **Host**: `localhost`
- **Port**: `5433` (external), `5432` (internal)
- **Database**: `case-study`
- **Username**: `case-study`
- **Password**: `password`

**Connection String:**
```
postgresql://case-study:password@localhost:5433/case-study
```

### Connecting with CLI Tools

**PostgreSQL CLI (psql):**
```bash
# Connect directly to Docker container
docker exec -it case-study-postgres psql -U case-study -d case-study

# Connect from host machine
psql -h localhost -p 5433 -U case-study -d case-study
```

**Using Docker Compose:**
```bash
cd backend/docker
docker-compose exec case-study-postgres psql -U case-study -d case-study
```

### Connecting with GUI Clients

**pgAdmin, DBeaver, DataGrip:**
- Host: `localhost`
- Port: `5433`
- Database: `case-study`
- Username: `case-study`
- Password: `password`
- SSL Mode: `disable` (for local development)

### API Environment Configuration

**Local Development (.env file):**
```bash
# Database Configuration
DATABASE_URL=postgresql://case-study:password@localhost:5433/case-study
POSTGRES_DB=case-study
POSTGRES_USER=case-study
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

**Docker Container Environment:**
```bash
# When API runs in Docker, use internal networking
DATABASE_URL=postgresql://case-study:password@postgres:5432/case-study
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

### Redis Connection

**Connection Details:**
- **Host**: `localhost`
- **Port**: `6379`
- **No authentication** (development only)

**Connection String:**
```
redis://localhost:6379/0
```

**Connect with CLI:**
```bash
# Connect directly to Docker container
docker exec -it case-study-redis redis-cli

# Connect from host machine
redis-cli -h localhost -p 6379
```

### Health Checks

**Test Database Connection:**
```bash
# PostgreSQL health check
docker exec case-study-postgres pg_isready -U case-study -d case-study

# Test from host
psql -h localhost -p 5433 -U case-study -d case-study -c "SELECT 1;"
```

**Test Redis Connection:**
```bash
# Redis health check
docker exec case-study-redis redis-cli ping

# Test from host
redis-cli -h localhost -p 6379 ping
```

### Troubleshooting Database Connections

**Common Issues:**

1. **Port conflicts**: Ensure port 5433 (PostgreSQL) and 6379 (Redis) are available
2. **Service not ready**: Wait for health checks to pass after starting containers
3. **Wrong host**: Use `localhost` from host machine, `postgres`/`redis` from within Docker
4. **Environment variables**: Verify `.env` file contains correct database credentials

**Check Container Status:**
```bash
cd backend/docker
docker-compose ps
docker-compose logs postgres
docker-compose logs redis
```

**Reset Database:**
```bash
# Stop containers and remove volumes
docker-compose down -v

# Restart with fresh database
docker-compose --profile local-db up -d
```

---

**Note**: This docs directory contains all backend documentation in one place for easy navigation and maintenance.