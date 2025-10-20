# Case Study Backend API Documentation

> Complete API reference for the Case Study Invoice Processing System

## Overview

Modern Flask API with streamlined routes, real-time WebSocket streaming, and comprehensive invoice processing capabilities. The API follows a clean MVC architecture with consolidated routes and DRY services.

**Base URLs:**

- Development: `http://localhost:8000`
- Production: `https://your-api.azurecontainerapps.io`

**Version:** 2.0.0

## Architecture

**Current Route Structure:**

- `/health` - Health check endpoints
- `/invoices` - All invoice operations (CRUD + processing + generation)
- `/admin` - Administrative monitoring and management

**Services:**

- `llm_service` - AI/ML operations (GPT-4V, DALL-E)
- `async_processor` - Background processing with WebSocket streaming
- `websocket_manager` - Real-time communication

**Database:**

- Development: Docker PostgreSQL + Redis
- Production: Neon PostgreSQL + Azure Redis

## Authentication

Most endpoints require JWT token authentication:

```http
Authorization: Bearer <jwt_token>
```

**Roles:**

- `user` - Can access invoice CRUD and upload
- `admin` - Can access all endpoints including generation and monitoring

---

# 🔥 Invoice Endpoints

All invoice operations consolidated into `/invoices` routes with comprehensive functionality.

## CRUD Operations

### GET /invoices/

Get all invoices with pagination and filtering.

**Authentication:** User or Admin required

**Query Parameters:**

- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `customer_id` (string, optional): Filter by customer ID
- `salesperson_id` (string, optional): Filter by salesperson ID
- `status` (int, optional): Filter by order status
- `date_from` (string, optional): Filter by invoice date (YYYY-MM-DD)
- `date_to` (string, optional): Filter by invoice date (YYYY-MM-DD)

**Response (200):**

```json
{
  "invoices": [
    {
      "id": "uuid",
      "invoice_number": "SO43659",
      "invoice_date": "2011-05-31",
      "total_amount": "23153.23",
      "customer_id": "uuid",
      "order_status": 5
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET /invoices/{invoice_id}

Get a specific invoice with full details.

**Authentication:** User or Admin required

**Path Parameters:**

- `invoice_id` (string): UUID of the invoice

**Response (200):**

```json
{
  "id": "uuid",
  "invoice_number": "SO43659",
  "invoice_date": "2011-05-31",
  "due_date": "2011-06-12",
  "total_amount": "23153.23",
  "customer": {
    "id": "uuid",
    "company_name": "Adventure Works Cycles"
  },
  "line_items": [
    {
      "line_number": 1,
      "description": "Mountain-100 Black, 42",
      "quantity": 1,
      "unit_price": "3374.99",
      "line_total": "3374.99"
    }
  ]
}
```

**Error Responses:**

- `400` - Invalid invoice ID format
- `404` - Invoice not found

### POST /invoices/

Create a new invoice.

**Authentication:** User or Admin required

**Request Body:**

```json
{
  "customer_company": "Adventure Works Cycles",
  "customer_address": "1 Adventure Works Way",
  "invoice_number": "SO43659",
  "invoice_date": "2011-05-31",
  "due_date": "2011-06-12",
  "subtotal": "20565.62",
  "tax_amount": "1971.51",
  "total_amount": "23153.23",
  "line_items": [
    {
      "description": "Mountain-100 Black, 42",
      "quantity": 1,
      "unit_price": "3374.99"
    }
  ]
}
```

**Response (201):**

```json
{
  "success": true,
  "invoice": {
    "id": "uuid",
    "invoice_number": "SO43659",
    "total_amount": "23153.23"
  }
}
```

## 🚀 Processing Operations

### POST /invoices/upload

**🔥 PRIMARY ENDPOINT** - Upload invoice from Vercel blob URL with real-time streaming

**Authentication:** User or Admin required

**Purpose:** Process invoice from Vercel blob URL with WebSocket streaming throughout the entire process

**Request Body:**

```json
{
  "blob_url": "https://vercel-blob-url.com/invoice.pdf",
  "filename": "invoice.pdf",
  "auto_save": true,
  "confidence_threshold": 0.8
}
```

**Response (202 Accepted):**

```json
{
  "success": true,
  "task_id": "uuid-task-id",
  "celery_task_id": "celery-id",
  "filename": "invoice.pdf",
  "status": "queued",
  "message": "Invoice processing started. Connect to WebSocket for real-time updates.",

  "websocket": {
    "room": "task_uuid-task-id",
    "events": {
      "progress": "task_update",
      "streaming": "task_update",
      "complete": "task_update",
      "error": "task_update"
    }
  },

  "processing": {
    "auto_save": true,
    "confidence_threshold": 0.8,
    "estimated_duration_seconds": 30
  }
}
```

**Processing Stages:**

1. **`fetch`** (0-20%): Download image from Vercel blob URL
2. **`llm_extraction`** (20-80%): AI analysis of invoice with streaming progress
3. **`validation`** (80-90%): Data quality validation
4. **`save`** (90-95%): Save to database (if auto_save enabled)
5. **`complete`** (100%): Final results with notification

### POST /invoices/generate

**🔥 ADMIN ENDPOINT** - Generate sample invoice images for testing

**Authentication:** Admin required

**Purpose:** Generate realistic invoice images using DALL-E for testing and demonstration

**Request Body:**

```json
{
  "business_type": "retail",
  "complexity": "detailed",
  "company_name": "Test Company Inc"
}
```

**Parameters:**

- `business_type` (string): Business type for invoice generation
- `complexity` (string): `simple`, `detailed`, `complex`
- `company_name` (string, optional): Custom company name

**Response (200):**

```json
{
  "success": true,
  "image_url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
  "prompt_used": "Create a realistic business invoice...",
  "business_type": "retail",
  "processing_time_ms": 3420,
  "model_used": "dall-e-3",

  "generated_by": {
    "admin_user_id": "admin-id",
    "admin_email": "admin@example.com",
    "generated_at": "2025-01-01T12:00:00Z"
  },

  "usage": {
    "description": "Generated invoice image for testing",
    "next_steps": [
      "Download the image from the provided URL",
      "Upload to Vercel blob storage",
      "Use the /invoices/upload endpoint to test processing"
    ],
    "image_expires_in": "1 hour (OpenAI temporary URL)"
  }
}
```

### GET /invoices/status/{task_id}

Get current processing status for an async task.

**Authentication:** User or Admin required

**Path Parameters:**

- `task_id` (string): UUID of the processing task

**Response (200):**

```json
{
  "task_id": "uuid",
  "status": "completed",
  "progress": 100,
  "current_stage": "complete",
  "created_at": "2025-01-01T12:00:00Z",
  "completed_at": "2025-01-01T12:05:00Z",
  "result": {
    "structured_data": {
      "invoice_number": "INV-001",
      "total_amount": 1250.00,
      "line_items": [...]
    },
    "confidence_score": 0.92,
    "auto_saved": true,
    "invoice_id": "db-invoice-id"
  }
}
```

**For Active Tasks:**

```json
{
  "task_id": "uuid",
  "status": "running",
  "progress": 45,
  "current_stage": "llm_extraction",
  "websocket": {
    "room": "task_uuid",
    "events": ["task_update"]
  }
}
```

### GET /invoices/supported-types

Get supported business types and formats (public endpoint).

**Authentication:** None required

**Response (200):**

```json
{
  "business_types": [
    {
      "type": "retail",
      "name": "Retail Store",
      "description": "General retail and merchandise"
    },
    {
      "type": "restaurant",
      "name": "Restaurant",
      "description": "Food service and dining"
    }
  ],
  "complexity_levels": [
    {
      "level": "simple",
      "description": "3-5 line items, basic formatting"
    },
    {
      "level": "detailed",
      "description": "6-10 line items, detailed formatting"
    },
    {
      "level": "complex",
      "description": "10+ line items, complex formatting with discounts"
    }
  ],
  "supported_formats": ["jpeg", "jpg", "png", "pdf", "webp"]
}
```

---

# 🔄 WebSocket Real-Time Streaming

## Connection Setup

```javascript
import io from "socket.io-client";

// 1. Start invoice processing
const response = await fetch("/invoices/upload", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    blob_url: "https://vercel-blob-url.com/invoice.pdf",
    filename: "invoice.pdf",
    auto_save: true,
  }),
});

const { task_id } = await response.json();

// 2. Connect to WebSocket
const socket = io();

// 3. Join task room
socket.emit("join_task", { task_id });

// 4. Listen for real-time updates
socket.on("task_update", (data) => {
  switch (data.type) {
    case "progress":
      updateProgressBar(data.progress, data.message);
      break;
    case "complete":
      handleJobComplete(data.result);
      break;
    case "error":
      handleJobError(data.error);
      break;
  }
});
```

## WebSocket Event Types

### Progress Updates

```json
{
  "type": "progress",
  "progress": 45,
  "message": "Analyzing invoice with AI...",
  "stage": "llm_extraction",
  "timestamp": 1640995200000,
  "task_id": "uuid"
}
```

### Stage Updates

```json
{
  "type": "stage_start",
  "stage": "llm_extraction",
  "description": "Analyzing invoice with AI...",
  "timestamp": 1640995200000
}
```

### Completion Notification

```json
{
  "type": "complete",
  "result": {
    "structured_data": {...},
    "confidence_score": 0.92,
    "auto_saved": true,
    "invoice_id": "saved-invoice-id"
  },
  "timestamp": 1640995200000
}
```

### Error Notifications

```json
{
  "type": "error",
  "error": "LLM extraction failed: API error",
  "stage": "llm_extraction",
  "timestamp": 1640995200000
}
```

---

# 🏥 Health Endpoints

## GET /health

Basic health check endpoint.

**Authentication:** None required

**Response (200):**

```json
{
  "status": "healthy",
  "service": "case-study-invoice-extraction",
  "version": "2.0.0"
}
```

## GET /health/database

Database connectivity health check.

**Authentication:** None required

**Response (200):**

```json
{
  "status": "healthy",
  "database": "connected",
  "message": "Database connection successful"
}
```

## GET /health/detailed

Detailed health check with all components.

**Authentication:** None required

**Response (200):**

```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Connected"
    },
    "pgvector": {
      "status": "healthy",
      "message": "Extension available"
    },
    "redis": {
      "status": "healthy",
      "message": "Connected"
    }
  }
}
```

## GET /metrics

Prometheus metrics endpoint for monitoring.

**Authentication:** None required

**Response:** Plain text metrics in Prometheus format

---

# 👨‍💼 Admin Endpoints

## GET /admin/health

Comprehensive admin health check for all services.

**Authentication:** Admin required

**Response (200):**

```json
{
  "timestamp": "2023-12-01T10:30:00",
  "overall_status": "healthy",
  "services": {
    "flask_api": {
      "status": "healthy",
      "uptime": "running",
      "version": "2.0.0"
    },
    "postgres": {
      "status": "healthy",
      "connections": {
        "current": 5,
        "max": "100"
      }
    },
    "redis": {
      "status": "healthy",
      "memory_used": "2.5M",
      "connected_clients": 3
    },
    "celery_worker": {
      "status": "healthy",
      "active_workers": 2
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 25.0,
      "memory": {
        "total": 8589934592,
        "available": 4294967296,
        "percent": 50.0
      }
    }
  }
}
```

## GET /admin/jobs

Get all processing jobs with status and metrics.

**Authentication:** Admin required

**Query Parameters:**

- `page` (int, optional): Page number
- `per_page` (int, optional): Items per page (max: 100)
- `status` (string, optional): Filter by job status

**Response (200):**

```json
{
  "jobs": [
    {
      "id": "uuid",
      "status": "completed",
      "created_at": "2023-12-01T10:30:00",
      "completed_at": "2023-12-01T10:35:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 100,
    "pages": 2
  },
  "statistics": {
    "total_jobs": 100,
    "recent_jobs_24h": 25,
    "status_breakdown": {
      "completed": 80,
      "failed": 15,
      "processing": 5
    }
  }
}
```

---

# 📊 Frontend Integration Examples

## React Upload Component

```jsx
function InvoiceUpload() {
  const [uploading, setUploading] = useState(false);
  const [taskId, setTaskId] = useState(null);

  const handleUpload = async (blobUrl, filename) => {
    const response = await fetch("/invoices/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        blob_url: blobUrl,
        filename: filename,
        auto_save: true,
      }),
    });

    const data = await response.json();
    if (data.success) {
      setTaskId(data.task_id);
    }
  };

  if (taskId) {
    return <InvoiceUploadProgress taskId={taskId} />;
  }

  return (
    <div>
      <h2>Upload Invoice</h2>
      <VercelBlobUploader onUpload={handleUpload} />
    </div>
  );
}
```

## Progress Component with WebSocket

```jsx
function InvoiceUploadProgress({ taskId }) {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const socket = io();

    socket.emit("join_task", { task_id: taskId });

    socket.on("task_update", (data) => {
      switch (data.type) {
        case "progress":
          setProgress(data.progress);
          setMessage(data.message);
          setStage(data.stage);
          break;

        case "streaming_text":
          // Handle real-time LLM streaming
          appendStreamingText(data.text);
          break;

        case "stage_start":
          setStage(data.stage);
          setMessage(data.description);
          break;

        case "stage_complete":
          setMessage(`${data.stage} completed`);
          break;

        case "complete":
          setProgress(100);
          setMessage("Processing complete!");
          setResult(data.result);
          break;

        case "error":
          setError(data.error);
          break;
      }
    });

    socket.on("joined_task", (data) => {
      console.log(`Connected to task room: ${data.room}`);
    });

    return () => socket.disconnect();
  }, [taskId]);

  return (
    <div className="invoice-upload-progress">
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <div className="status">
        <span className="stage">{stage}</span>
        <span className="message">{message}</span>
      </div>

      {result && (
        <div className="result">
          <h3>Invoice Processed Successfully!</h3>
          <p>Confidence: {(result.confidence_score * 100).toFixed(1)}%</p>
          {result.auto_saved && (
            <p>✅ Saved to database (ID: {result.invoice_id})</p>
          )}
        </div>
      )}

      {error && (
        <div className="error">
          <h3>Processing Failed</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}
```

---

# 🧪 Testing Examples

## Manual Testing

```bash
# 1. Generate test invoice (admin)
curl -X POST http://localhost:8000/invoices/generate \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"business_type": "retail", "complexity": "detailed"}'

# 2. Upload invoice for processing (user)
curl -X POST http://localhost:8000/invoices/upload \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"blob_url": "https://your-blob-url.com/invoice.pdf", "filename": "test.pdf"}'

# 3. Check processing status
curl -X GET http://localhost:8000/invoices/status/TASK_ID \
  -H "Authorization: Bearer $TOKEN"

# 4. Health check
curl http://localhost:8000/health
```

## Automated Testing

```bash
# Run comprehensive route tests
poetry run python test_invoice_routes.py
```

---

# 🚨 Error Handling

## Standard HTTP Status Codes

- `200` - Success
- `201` - Created
- `202` - Accepted (async processing started)
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `413` - Payload Too Large
- `500` - Internal Server Error

## Error Response Format

```json
{
  "error": "Error description",
  "details": "Additional error details (optional)"
}
```

---

# ⚙️ Configuration

## Environment Variables

```bash
# Core Application
OPENAI_API_KEY          # Required for LLM operations
DATABASE_URL            # PostgreSQL connection
REDIS_URL               # Redis connection
FLASK_SECRET_KEY        # Flask session secret
JWT_SECRET              # JWT signing secret

# Processing
CONFIDENCE_THRESHOLD=0.8     # Default confidence threshold
MAX_CONTENT_LENGTH=16777216  # 16MB max file size

# CORS & Security
ALLOWED_ORIGINS         # Frontend origins
RATE_LIMIT_PER_MINUTE=100   # API rate limit
```

## File Upload Limits

- **Maximum file size:** 16MB
- **Supported formats:** PDF, PNG, JPG, JPEG, GIF, WebP, BMP, TIFF

---

# 🔐 Security

## Authentication & Authorization

- JWT tokens required for most endpoints
- Role-based access control (user/admin)
- Session management with expiration

## Input Validation

- All inputs validated before processing
- File type and size validation
- SQL injection protection via SQLAlchemy ORM

## CORS Configuration

- Configured for specific frontend origins
- Credentials support for authenticated requests

---

# 📈 Monitoring

## Prometheus Metrics

Available at `/metrics` endpoint:

- Request counts and response times
- Database connection pool metrics
- Celery task metrics
- Custom business metrics

## Health Checks

- Basic: `/health`
- Database: `/health/database`
- Detailed: `/health/detailed`
- Admin: `/admin/health`

---

**API Version:** 2.0.0
**Last Updated:** September 2025
**Documentation:** Complete and current
