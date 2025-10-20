# Vercel + Neon DB Deployment Guide

Complete guide for deploying your Flask API to Azure Container Apps and Vercel frontend, both connecting to Neon database.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Vercel App     │    │  Azure Flask    │    │  Neon Database  │
│  (Next.js)      │────│  API Container  │────│  (PostgreSQL)   │
│                 │    │  Apps           │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │
         └────────────────────────┼────────────────────────
                                  │
                            ┌─────────────────┐
                            │  Azure Cache    │
                            │  for Redis      │
                            └─────────────────┘
```

## Step 1: Set Up Neon Database

### 1.1 Create Neon Project
1. Go to [console.neon.tech](https://console.neon.tech)
2. Sign up and create project: `case-study-invoices`
3. Choose region: `us-east-1` (or closest to your users)
4. Note down connection string:
   ```
   postgresql://username:password@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require
   ```

### 1.2 Apply Database Schema
```bash
# From backend directory
cd backend

# Set your Neon connection string
export NEON_DATABASE_URL="postgresql://username:password@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require"

# Run migration script
python scripts/migrate_to_neon.py

# Verify setup
python scripts/verify_neon.py
```

## Step 2: Deploy Flask API to Azure Container Apps

### 2.1 Create Azure Resources
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-casestudy --location eastus

# Create Azure Container Registry
az acr create --resource-group rg-casestudy --name casestudyacr --sku Basic

# Create Container Apps environment
az containerapp env create \
  --name case-study-env \
  --resource-group rg-casestudy \
  --location eastus
```

### 2.2 Create Azure Cache for Redis
```bash
# Create Redis instance
az redis create \
  --resource-group rg-casestudy \
  --name case-study-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0

# Get Redis connection string
az redis show-connection-string \
  --resource-group rg-casestudy \
  --name case-study-redis
```

### 2.3 Build and Push Container
```bash
# Login to ACR
az acr login --name casestudyacr

# Build and push API container
cd backend/api
docker build -t casestudyacr.azurecr.io/case-study-api:latest .
docker push casestudyacr.azurecr.io/case-study-api:latest

# Build and push worker container
docker build -t casestudyacr.azurecr.io/case-study-worker:latest .
docker push casestudyacr.azurecr.io/case-study-worker:latest
```

### 2.4 Deploy API Container App
```bash
# Create API container app
az containerapp create \
  --name case-study-api \
  --resource-group rg-casestudy \
  --environment case-study-env \
  --image casestudyacr.azurecr.io/case-study-api:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 5 \
  --cpu 1.0 \
  --memory 2Gi \
  --registry-server casestudyacr.azurecr.io \
  --env-vars \
    DATABASE_URL="postgresql://username:password@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require" \
    REDIS_URL="redis://case-study-redis.redis.cache.windows.net:6380?ssl=true&password=your-redis-password" \
    FLASK_ENV=production \
    SECRET_KEY=your-production-secret \
    OPENAI_API_KEY=your-openai-key \
    ANTHROPIC_API_KEY=your-anthropic-key \
    BLOB_READ_WRITE_TOKEN=your-blob-token \
    FRONTEND_URL=https://your-app.vercel.app

# Create worker container app
az containerapp create \
  --name case-study-worker \
  --resource-group rg-casestudy \
  --environment case-study-env \
  --image casestudyacr.azurecr.io/case-study-worker:latest \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --registry-server casestudyacr.azurecr.io \
  --env-vars \
    DATABASE_URL="postgresql://username:password@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require" \
    REDIS_URL="redis://case-study-redis.redis.cache.windows.net:6380?ssl=true&password=your-redis-password" \
    FLASK_ENV=production \
    SECRET_KEY=your-production-secret \
    OPENAI_API_KEY=your-openai-key \
    ANTHROPIC_API_KEY=your-anthropic-key \
    BLOB_READ_WRITE_TOKEN=your-blob-token
```

### 2.5 Get API URL
```bash
# Get the API URL
az containerapp show \
  --name case-study-api \
  --resource-group rg-casestudy \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv

# Example output: case-study-api.happyfield-12345.eastus.azurecontainerapps.io
```

## Step 3: Deploy Vercel Frontend

### 3.1 Configure Vercel Environment Variables
Create environment variables in Vercel dashboard or use CLI:

```bash
# Install Vercel CLI
npm install -g vercel

# Login and link project
vercel login
vercel link

# Set environment variables
vercel env add DATABASE_URL
# Enter: postgresql://username:password@ep-name-123.us-east-1.aws.neon.tech/casestudy?sslmode=require

vercel env add NEXT_PUBLIC_API_URL
# Enter: https://case-study-api.happyfield-12345.eastus.azurecontainerapps.io

vercel env add API_URL
# Enter: https://case-study-api.happyfield-12345.eastus.azurecontainerapps.io

vercel env add NEXTAUTH_URL
# Enter: https://your-app.vercel.app

vercel env add NEXTAUTH_SECRET
# Enter: your-nextauth-secret

vercel env add GOOGLE_CLIENT_ID
# Enter: your-google-oauth-client-id

vercel env add GOOGLE_CLIENT_SECRET
# Enter: your-google-oauth-client-secret

vercel env add BLOB_READ_WRITE_TOKEN
# Enter: your-vercel-blob-token
```

### 3.2 Deploy to Vercel
```bash
# Deploy to production
vercel --prod

# Or use automatic deployment via GitHub integration
```

## Step 4: Configure Database Connections

### 4.1 Update Flask API Configuration
Your `config.py` is already configured to detect Neon and optimize connections. Verify with:

```bash
# Test API health
curl https://case-study-api.happyfield-12345.eastus.azurecontainerapps.io/api/health

# Test detailed health (includes database)
curl https://case-study-api.happyfield-12345.eastus.azurecontainerapps.io/api/health/detailed
```

### 4.2 Verify Vercel Connection
In your Vercel app, both the frontend and any API routes can connect to Neon:

```javascript
// pages/api/test-db.js (example API route in Vercel)
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

export default async function handler(req, res) {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW() as current_time');
    client.release();

    res.status(200).json({
      success: true,
      currentTime: result.rows[0].current_time,
      message: 'Neon DB connection successful'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
}
```

## Step 5: Monitoring and Scaling

### 5.1 Container App Scaling
```bash
# Update scaling rules
az containerapp update \
  --name case-study-api \
  --resource-group rg-casestudy \
  --min-replicas 2 \
  --max-replicas 10 \
  --scale-rule-name http-requests \
  --scale-rule-type http \
  --scale-rule-metadata concurrentRequests=50
```

### 5.2 Monitor with Azure Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app case-study-insights \
  --location eastus \
  --resource-group rg-casestudy

# Get instrumentation key
az monitor app-insights component show \
  --app case-study-insights \
  --resource-group rg-casestudy \
  --query "instrumentationKey"
```

Add to your container environment variables:
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key-here"
```

### 5.3 Neon Database Monitoring
- Monitor connections and performance in [Neon Console](https://console.neon.tech)
- Set up alerts for connection limits
- Use database branching for staging environments

## Step 6: CI/CD Pipeline (Optional)

### 6.1 GitHub Actions for API Deployment
Create `.github/workflows/deploy-api.yml`:

```yaml
name: Deploy API to Azure Container Apps

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push to ACR
        run: |
          az acr login --name casestudyacr
          cd backend/api
          docker build -t casestudyacr.azurecr.io/case-study-api:${{ github.sha }} .
          docker push casestudyacr.azurecr.io/case-study-api:${{ github.sha }}

      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name case-study-api \
            --resource-group rg-casestudy \
            --image casestudyacr.azurecr.io/case-study-api:${{ github.sha }}
```

### 6.2 Vercel Automatic Deployment
Vercel automatically deploys when you push to your GitHub repository. Ensure your environment variables are set in the Vercel dashboard.

## Step 7: Testing the Deployment

### 7.1 Test API Endpoints
```bash
# API base URL
API_URL="https://case-study-api.happyfield-12345.eastus.azurecontainerapps.io"

# Test health
curl $API_URL/api/health

# Test database connectivity
curl $API_URL/api/health/database

# Test invoice endpoints (with auth)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" $API_URL/api/invoices/
```

### 7.2 Test Vercel App
1. Visit your Vercel app URL
2. Test Google OAuth login
3. Try uploading an invoice
4. Verify real-time processing updates
5. Check invoice management features

### 7.3 End-to-End Testing
```bash
# Test the full pipeline
# 1. Upload file via Vercel app
# 2. Check processing job creation in API
# 3. Monitor WebSocket updates
# 4. Verify invoice creation in Neon DB
```

## Troubleshooting

### Common Issues

#### 1. Container App Not Starting
```bash
# Check logs
az containerapp logs show \
  --name case-study-api \
  --resource-group rg-casestudy \
  --follow

# Check revisions
az containerapp revision list \
  --name case-study-api \
  --resource-group rg-casestudy
```

#### 2. Database Connection Issues
```bash
# Test Neon connection directly
python scripts/verify_neon.py

# Check connection string format
# Should be: postgresql://user:pass@host/db?sslmode=require
```

#### 3. CORS Issues
Update your Flask API CORS configuration:
```python
CORS(app, origins=[
    "https://your-app.vercel.app",
    "http://localhost:3000"  # For local development
])
```

#### 4. Environment Variables Not Loading
```bash
# Verify environment variables in Container Apps
az containerapp show \
  --name case-study-api \
  --resource-group rg-casestudy \
  --query "properties.template.containers[0].env"
```

## Cost Optimization

### Azure Container Apps
- Use consumption-based pricing
- Set appropriate min/max replicas
- Scale to zero when not in use

### Neon Database
- Use the free tier (10GB storage, 100 compute hours)
- Enable auto-pause for development branches
- Monitor usage in Neon console

### Vercel
- Free tier supports most use cases
- Monitor function execution time
- Optimize bundle size

## Security Considerations

1. **Environment Variables**: Use Azure Key Vault for sensitive data
2. **Network Security**: Configure private endpoints for production
3. **SSL/TLS**: Both Vercel and Azure provide SSL by default
4. **API Authentication**: Implement proper JWT validation
5. **Database Security**: Neon provides SSL by default, use connection pooling

## Next Steps

1. Set up monitoring and alerting
2. Configure backup and disaster recovery
3. Implement rate limiting
4. Add comprehensive logging
5. Set up staging environments using Neon branches
6. Configure custom domains
7. Implement health checks and monitoring

Your Flask API and Vercel app are now both connected to the same Neon database, providing a unified data layer for your application!