# Secure Deployment Guide

This guide covers deploying the Stryker invoice processing system with secure file storage and user authentication.

## Architecture Overview

### Frontend (Next.js on Vercel)

- **Authentication**: NextAuth.js with Google OAuth
- **File Upload**: Direct to Vercel Blob Storage
- **Security**: JWT tokens, CSRF protection, file validation

### Backend (Azure Container Instances/App Service)

- **API**: Flask with Vercel Blob Storage integration
- **Database**: Azure PostgreSQL with pgvector
- **Security**: JWT validation, RBAC (Role-Based Access Control)

### File Storage

- **Primary Storage**: Vercel Blob Storage
- **Access Control**: Vercel Blob API with time-limited access
- **Organization**: User-specific folders with UUID-based file naming

## Prerequisites

1. **Azure Account** with active subscription
2. **Vercel Account** for frontend deployment and blob storage
3. **Google Cloud Console** account for OAuth setup
4. **Domain name** (optional but recommended)

## Step 1: Azure Setup

### 1.1 Create Azure Resources

```bash
# Create resource group
az group create --name stryker-rg --location eastus

# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group stryker-rg \
  --name stryker-postgres \
  --admin-user strykeradmin \
  --admin-password YourSecurePassword123! \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0-255.255.255.255

# Note: File storage will be handled by Vercel Blob Storage
# No Azure storage account needed
```

### 1.2 Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
5. Configure OAuth consent screen:
   - **Application name**: Stryker Invoice Processor
   - **Authorized domains**: your-app.vercel.app
6. Create OAuth 2.0 Client ID:
   - **Application type**: Web application
   - **Authorized redirect URIs**: `https://your-app.vercel.app/api/auth/callback/google`
7. Note down:
   - Client ID
   - Client secret

### 1.3 Set up Vercel Blob Storage

1. Go to Vercel Dashboard → Storage → Blob
2. Create a new Blob store for your project
3. Note down the Blob store URL and access token

## Step 2: Database Setup

### 2.1 Connect to PostgreSQL

```bash
# Get connection string
az postgres flexible-server show-connection-string \
  --server-name stryker-postgres \
  --admin-user strykeradmin \
  --admin-password YourSecurePassword123! \
  --database-name postgres
```

### 2.2 Run Schema Migration

```bash
# Connect to database and run schema.sql
psql "host=stryker-postgres.postgres.database.azure.com port=5432 dbname=postgres user=strykeradmin password=YourSecurePassword123! sslmode=require"

# Run the schema
\i schema.sql
```

## Step 3: Frontend Deployment (Vercel)

### 3.1 Install Dependencies

```bash
cd frontend
npm install next-auth @next-auth/prisma-adapter @vercel/blob prisma @prisma/client bcryptjs
```

### 3.2 Configure Environment Variables

Create `.env.local`:

```env
# Next.js Configuration
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=your-nextauth-secret-key-here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Vercel Blob Storage Configuration
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token

# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend.azurecontainer.io
API_URL=https://your-backend.azurecontainer.io

# Database Configuration
DATABASE_URL=postgresql://strykeradmin:YourSecurePassword123!@stryker-postgres.postgres.database.azure.com:5432/postgres?sslmode=require
```

### 3.3 Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
# Go to Project Settings → Environment Variables
```

## Step 4: Backend Deployment (Azure Container Instances)

### 4.1 Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### 4.2 Create requirements.txt

```txt
Flask==2.3.3
gunicorn==21.2.0
psycopg2-binary==2.9.7
vercel-blob==0.15.0
redis==5.0.1
PyJWT==2.8.0
python-dotenv==1.0.0
flask-cors==4.0.0
openai==1.3.0
numpy==1.24.3
pandas==2.0.3
bcrypt==4.0.1
```

### 4.3 Deploy to Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr create --resource-group stryker-rg --name strykeracr --sku Basic

# Login to ACR
az acr login --name strykeracr

# Build and push image
docker build -t strykeracr.azurecr.io/stryker-backend:latest .
docker push strykeracr.azurecr.io/stryker-backend:latest

# Create container instance
az container create \
  --resource-group stryker-rg \
  --name stryker-backend \
  --image strykeracr.azurecr.io/stryker-backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 5000 \
  --environment-variables \
    FLASK_ENV=production \
    DATABASE_URL=postgresql://strykeradmin:YourSecurePassword123!@stryker-postgres.postgres.database.azure.com:5432/postgres?sslmode=require \
    BLOB_READ_WRITE_TOKEN=your-vercel-blob-token \
    JWT_SECRET=your-jwt-secret \
    CORS_ORIGINS=https://your-app.vercel.app
```

## Step 5: Security Configuration

### 5.1 Configure CORS

Update your Flask app to allow only your Vercel domain:

```python
from flask_cors import CORS

CORS(app, origins=[
    "https://your-app.vercel.app",
    "http://localhost:3000"  # For development
])
```

### 5.2 Set up SSL/TLS

- Vercel automatically provides SSL certificates
- Azure Container Instances can use Application Gateway for SSL termination

### 5.3 Configure Firewall Rules

```bash
# Allow only Vercel IPs to access your backend
# Get Vercel IP ranges from: https://vercel.com/docs/concepts/edge-network/regions
```

### 5.4 Configure Vercel Blob Storage Security

```javascript
// Example: Secure file upload with Vercel Blob
import { put } from "@vercel/blob";

const blob = await put(`invoices/${userId}/${fileName}`, file, {
  access: "public", // or 'private' for restricted access
  token: process.env.BLOB_READ_WRITE_TOKEN,
});
```

## Step 6: Monitoring and Logging

### 6.1 Azure Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app stryker-insights \
  --location eastus \
  --resource-group stryker-rg
```

### 6.2 Vercel Analytics

Enable in Vercel dashboard:

- Go to Project Settings → Analytics
- Enable Web Analytics

## Step 7: Testing

### 7.1 Test Authentication

1. Visit your Vercel app
2. Click "Sign In with Google"
3. Complete Google OAuth flow
4. Verify user is created in database

### 7.2 Test File Upload

1. Upload a test invoice file
2. Verify file appears in Vercel Blob Storage
3. Check processing job is created
4. Monitor WebSocket updates

### 7.3 Test Security

1. Try accessing other users' files
2. Verify file access permissions work correctly
3. Test file type validation
4. Check file size limits

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS configuration in Flask app
2. **Authentication Failures**: Verify Google OAuth configuration
3. **File Upload Errors**: Check Vercel Blob Storage token and permissions
4. **Database Connection**: Verify PostgreSQL firewall rules

### Logs

- **Frontend**: Check Vercel function logs
- **Backend**: Check Azure Container Instance logs
- **Database**: Check Azure PostgreSQL logs

## Cost Optimization

1. **Use Azure Reserved Instances** for predictable workloads
2. **Configure auto-scaling** for container instances
3. **Use Vercel Blob Storage** with automatic optimization
4. **Monitor usage** with Azure Cost Management and Vercel Analytics

## Security Best Practices

1. **Rotate secrets regularly**
2. **Use Azure Key Vault** for sensitive configuration
3. **Enable audit logging** for all file operations
4. **Implement rate limiting** on API endpoints
5. **Regular security scans** with Azure Security Center
6. **Use Vercel Blob Storage access controls** for file security
7. **Implement proper JWT token validation** for API access
