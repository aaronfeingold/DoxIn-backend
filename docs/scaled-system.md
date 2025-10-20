# DoxIn - Production Architecture (GCP)

> **Scalable, cloud-native invoice processing system with AI chatbot on Google Cloud Platform**

## Table of Contents

1. [System Overview](#system-overview)
2. [Infrastructure Architecture](#infrastructure-architecture)
3. [Service Architecture](#service-architecture)
4. [Data Architecture](#data-architecture)
5. [AI & ML Architecture](#ai--ml-architecture)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Monitoring & Observability](#monitoring--observability)

---

## System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Layer"
        Users[End Users]
        Admins[Admin Users]
    end

    subgraph "CDN & Edge"
        Vercel[Vercel Edge Network<br/>Next.js Frontend]
        CDN[Google Cloud CDN<br/>Static Assets]
    end

    subgraph "GCP - Compute"
        direction LR
        LB[Cloud Load Balancer<br/>HTTPS/WebSocket]
        CloudRun[Cloud Run Services<br/>Flask API]
        CloudTasks[Cloud Tasks<br/>Background Jobs]
    end

    subgraph "GCP - Data & AI"
        Neon[(Neon DB<br/>PostgreSQL)]
        Redis[(Memorystore<br/>Redis)]
        Qdrant[(Qdrant Vector DB<br/>Cloud Run)]
        GCS[Cloud Storage<br/>Document Files]
    end

    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT-4]
        Anthropic[Anthropic API<br/>Claude]
        HuggingFace[Hugging Face<br/>Inference API]
    end

    Users --> Vercel
    Admins --> Vercel
    Vercel --> LB
    Vercel --> GCS
    LB --> CloudRun
    CloudRun --> CloudTasks
    CloudRun --> Neon
    CloudRun --> Redis
    CloudRun --> Qdrant
    CloudRun --> GCS
    CloudRun --> OpenAI
    CloudRun --> Anthropic
    CloudRun --> HuggingFace
    CloudTasks --> CloudRun

    style Vercel fill:#0070f3
    style CloudRun fill:#4285f4
    style Neon fill:#16a34a
    style Qdrant fill:#dc0073
    style GCS fill:#ea4335
```

### System Capabilities

1. **Invoice Processing**
   - AI-powered document extraction
   - Real-time WebSocket updates
   - Batch processing support

2. **AI Chatbot Assistant**
   - Natural language queries
   - RAG (Retrieval-Augmented Generation)
   - Text-to-SQL capabilities
   - Streaming responses

3. **Analytics & Reporting**
   - Custom report generation
   - Data visualization
   - Export capabilities

---

## Infrastructure Architecture

### GCP Resource Topology

```mermaid
graph TB
    subgraph "GCP Project: doxin-production"
        subgraph "Region: us-central1"
            subgraph "Compute Services"
                CR1[Cloud Run: api-service<br/>Min: 2, Max: 20]
                CR2[Cloud Run: worker-service<br/>Min: 1, Max: 10]
                CR3[Cloud Run: qdrant-vector-db<br/>Min: 1, Max: 3]
                CT[Cloud Tasks Queue<br/>invoice-processing]
            end

            subgraph "Data Services"
                MS[Memorystore Redis<br/>2GB, HA]
                GCS1[GCS Bucket: documents]
                GCS2[GCS Bucket: exports]
            end

            subgraph "Networking"
                LB[Global Load Balancer]
                VPC[VPC Network]
                NAT[Cloud NAT]
            end
        end

        subgraph "External: AWS us-east-1"
            Neon[(Neon PostgreSQL<br/>Serverless)]
        end

        subgraph "Monitoring"
            CloudMon[Cloud Monitoring]
            CloudLog[Cloud Logging]
            CloudTrace[Cloud Trace]
        end
    end

    LB --> CR1
    CR1 --> CR2
    CR1 --> CR3
    CR1 --> MS
    CR1 --> Neon
    CR1 --> GCS1
    CR2 --> Neon
    CR2 --> MS
    CR2 --> GCS1
    CR3 --> GCS2
    CT --> CR2
    CR1 -.logs.-> CloudLog
    CR1 -.metrics.-> CloudMon
    CR1 -.traces.-> CloudTrace

    style CR1 fill:#4285f4
    style CR2 fill:#4285f4
    style CR3 fill:#dc0073
    style Neon fill:#16a34a
    style MS fill:#ea4335
```

### Service Specifications

| Service | Type | Scaling | CPU | Memory | Storage |
|---------|------|---------|-----|--------|---------|
| **api-service** | Cloud Run | 2-20 instances | 2 vCPU | 4GB | N/A |
| **worker-service** | Cloud Run | 1-10 instances | 1 vCPU | 2GB | N/A |
| **qdrant-vector-db** | Cloud Run | 1-3 instances | 2 vCPU | 8GB | 50GB SSD |
| **memorystore-redis** | Managed | N/A | N/A | 2GB | N/A |
| **neon-db** | External | Auto | N/A | N/A | 100GB |
| **documents-bucket** | GCS | N/A | N/A | N/A | Unlimited |

---

## Service Architecture

### API Service Architecture

```mermaid
graph LR
    subgraph "Cloud Run: api-service"
        direction TB
        API[Flask API<br/>Port 8000]

        subgraph "Route Handlers"
            AuthR[/auth/*<br/>Authentication]
            InvR[/invoices/*<br/>Invoice CRUD]
            JobsR[/jobs/*<br/>Job Tracking]
            ChatR[/chat/*<br/>AI Chatbot]
            ReportR[/reports/*<br/>Analytics]
            AdminR[/admin/*<br/>Admin Panel]
        end

        subgraph "Services Layer"
            LLM[LLM Service<br/>OpenAI/Anthropic]
            Chat[Chat Service<br/>Streaming]
            RAG[RAG Service<br/>Vector Search]
            SQL[Text-to-SQL<br/>Generator]
            WS[WebSocket Manager<br/>Real-time Updates]
        end

        API --> AuthR & InvR & JobsR & ChatR & ReportR & AdminR
        ChatR --> Chat
        Chat --> LLM & RAG & SQL
        InvR --> LLM & WS
        JobsR --> WS
    end

    Chat --> Redis[(Redis Cache)]
    RAG --> Qdrant[(Qdrant)]
    SQL --> Neon[(Neon DB)]

    style API fill:#4285f4
    style Chat fill:#34a853
    style RAG fill:#dc0073
```

### Chat Service Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as Cloud Run API
    participant Chat as Chat Service
    participant RAG as RAG Service
    participant Qdrant as Qdrant DB
    participant SQL as Text-to-SQL
    participant Neon as Neon DB
    participant HF as Hugging Face

    User->>Frontend: Ask question
    Frontend->>API: POST /chat/stream {message}
    API->>Chat: Process chat message

    par Determine Intent
        Chat->>Chat: Analyze user intent
    end

    alt Documentation Query
        Chat->>RAG: Search docs
        RAG->>Qdrant: Vector similarity search
        Qdrant-->>RAG: Relevant docs
        RAG-->>Chat: Context chunks
    else Data Query
        Chat->>SQL: Generate SQL
        SQL->>Neon: Execute query
        Neon-->>SQL: Query results
        SQL-->>Chat: Formatted data
    else General Query
        Chat->>HF: Stream inference
        HF-->>Chat: Streamed tokens
    end

    Chat->>API: Stream response chunks
    API-->>Frontend: SSE stream
    Frontend-->>User: Display answer
```

---

## Data Architecture

### Database Schema Overview

```mermaid
erDiagram
    USERS ||--o{ INVOICES : uploads
    USERS ||--o{ PROCESSING_JOBS : owns
    USERS ||--o{ CHAT_SESSIONS : has

    INVOICES ||--o{ INVOICE_LINE_ITEMS : contains
    INVOICES }o--|| COMPANIES : "billed to"
    INVOICES }o--o| SALESPERSONS : "sold by"
    INVOICES }o--o| TERRITORIES : "in region"

    PROCESSING_JOBS }o--|| FILE_STORAGE : processes
    PROCESSING_JOBS }o--|| INVOICES : creates

    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : contains

    PRODUCTS ||--o{ INVOICE_LINE_ITEMS : ordered
    PRODUCTS }o--|| PRODUCT_SUBCATEGORIES : categorized
    PRODUCT_SUBCATEGORIES }o--|| PRODUCT_CATEGORIES : grouped

    USERS {
        uuid id PK
        string email
        string name
        string role
        timestamp created_at
    }

    INVOICES {
        uuid id PK
        uuid uploaded_by_user_id FK
        uuid customer_id FK
        string invoice_number
        date invoice_date
        decimal total_amount
        string status
    }

    PROCESSING_JOBS {
        uuid id PK
        uuid user_id FK
        uuid file_storage_id FK
        string status
        int progress
        jsonb result_data
    }

    CHAT_SESSIONS {
        uuid id PK
        uuid user_id FK
        string title
        timestamp created_at
    }

    CHAT_MESSAGES {
        uuid id PK
        uuid session_id FK
        string role
        text content
        jsonb metadata
        timestamp created_at
    }

    FILE_STORAGE {
        uuid id PK
        uuid user_id FK
        string file_name
        string blob_url
        string mime_type
    }
```

### Data Flow Architecture

```mermaid
graph TB
    subgraph "Ingestion Layer"
        Upload[File Upload]
        WebForm[Web Form Entry]
        API[API Import]
    end

    subgraph "Processing Layer"
        Queue[Cloud Tasks Queue]
        Worker[Worker Service]
        LLM[LLM Extraction]
        Validation[Data Validation]
    end

    subgraph "Storage Layer"
        GCS[(Cloud Storage<br/>Documents)]
        Neon[(Neon DB<br/>Structured Data)]
        Redis[(Redis<br/>Cache & Sessions)]
        Qdrant[(Qdrant<br/>Vector Embeddings)]
    end

    subgraph "Application Layer"
        CRUD[Invoice CRUD]
        Search[Search & Filter]
        Reports[Report Generation]
        Chat[AI Chatbot]
    end

    Upload --> GCS
    Upload --> Queue
    Queue --> Worker
    Worker --> LLM
    LLM --> Validation
    Validation --> Neon

    WebForm --> Neon
    API --> Neon

    CRUD --> Neon
    CRUD --> Redis
    Search --> Neon
    Reports --> Neon
    Chat --> Qdrant
    Chat --> Neon

    GCS -.backup.-> Neon

    style GCS fill:#ea4335
    style Neon fill:#16a34a
    style Redis fill:#dc382d
    style Qdrant fill:#dc0073
```

---

## AI & ML Architecture

### AI Services Stack

```mermaid
graph TB
    subgraph "AI Service Layer"
        direction TB

        subgraph "LLM Services"
            GPT4[OpenAI GPT-4<br/>Vision & Text]
            Claude[Anthropic Claude<br/>Advanced Reasoning]
            HF[Hugging Face<br/>Open Source Models]
        end

        subgraph "AI Capabilities"
            Vision[Document Vision<br/>Invoice Extraction]
            Chat[Conversational AI<br/>User Assistant]
            SQL[Text-to-SQL<br/>Natural Language Queries]
            Embed[Embeddings<br/>Semantic Search]
        end

        subgraph "RAG Pipeline"
            Chunker[Document Chunker<br/>Markdown Processing]
            Vectorizer[Embedding Generator<br/>text-embedding-3-small]
            Retriever[Vector Retriever<br/>Hybrid Search]
        end
    end

    subgraph "Vector Storage"
        Qdrant[(Qdrant Vector DB<br/>Cosine Similarity)]
        DocStore[Document Store<br/>frontend/docs<br/>backend/docs]
    end

    subgraph "Application Integration"
        InvoiceProc[Invoice Processing]
        ChatBot[AI Chatbot]
        HelpSystem[Context-Aware Help]
    end

    Vision --> GPT4
    Chat --> Claude & HF
    SQL --> GPT4 & Claude
    Embed --> GPT4

    InvoiceProc --> Vision
    ChatBot --> Chat & SQL & Retriever
    HelpSystem --> Retriever

    DocStore --> Chunker
    Chunker --> Vectorizer
    Vectorizer --> Qdrant
    Retriever --> Qdrant

    style GPT4 fill:#10a37f
    style Claude fill:#cc785c
    style HF fill:#ff9d00
    style Qdrant fill:#dc0073
```

### RAG (Retrieval-Augmented Generation) Pipeline

```mermaid
sequenceDiagram
    participant Docs as Documentation<br/>(Markdown Files)
    participant Indexer as RAG Indexer
    participant Embed as Embedding Model
    participant Qdrant as Qdrant Vector DB
    participant User
    participant Chat as Chat Service
    participant LLM as Language Model

    Note over Docs,Qdrant: Indexing Phase (Offline)
    Docs->>Indexer: Read markdown files
    Indexer->>Indexer: Chunk documents
    loop For each chunk
        Indexer->>Embed: Generate embedding
        Embed-->>Indexer: Vector (1536 dims)
        Indexer->>Qdrant: Store vector + metadata
    end

    Note over User,LLM: Query Phase (Real-time)
    User->>Chat: Ask question
    Chat->>Embed: Embed query
    Embed-->>Chat: Query vector
    Chat->>Qdrant: Search similar vectors
    Qdrant-->>Chat: Top-k relevant chunks
    Chat->>LLM: Prompt with context + query
    LLM-->>Chat: Generated answer
    Chat-->>User: Stream response
```

### Qdrant Collection Schema

```yaml
collections:
  - name: "documentation"
    vectors:
      size: 1536  # OpenAI text-embedding-3-small
      distance: Cosine

    payload_schema:
      source: string       # "frontend/docs" or "backend/docs"
      filename: string     # e.g., "API_DOCUMENTATION.md"
      title: string        # Document title
      chunk_index: integer # Position in document
      content: text        # Actual text chunk
      metadata: object     # Additional context
      created_at: timestamp

  - name: "invoice_descriptions"
    vectors:
      size: 1536
      distance: Cosine

    payload_schema:
      invoice_id: string
      company_name: string
      line_items: array
      semantic_tags: array
```

---

## Security Architecture

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Google as Google OAuth
    participant API as Cloud Run API
    participant Redis
    participant Neon as Neon DB

    User->>Frontend: Click "Sign In"
    Frontend->>Google: OAuth 2.0 request
    Google-->>User: Login prompt
    User->>Google: Credentials
    Google-->>Frontend: Auth code
    Frontend->>API: POST /auth/callback {code}
    API->>Google: Verify code
    Google-->>API: User profile + tokens
    API->>Neon: Get/Create user record
    API->>API: Generate JWT token
    API->>Redis: Store session
    API-->>Frontend: JWT token + user data
    Frontend->>Frontend: Store token in cookie

    Note over User,Neon: Subsequent Requests
    User->>Frontend: Access protected page
    Frontend->>API: GET /invoices (JWT in header)
    API->>API: Verify JWT signature
    API->>Redis: Check session validity
    Redis-->>API: Session active
    API->>Neon: Fetch user's invoices
    Neon-->>API: Invoice data
    API-->>Frontend: Authorized response
```

### Security Layers

```mermaid
graph TB
    subgraph "Edge Security"
        CDN[Vercel Edge<br/>DDoS Protection]
        CloudArmor[Cloud Armor<br/>WAF Rules]
        SSL[SSL/TLS<br/>Certificate]
    end

    subgraph "Application Security"
        Auth[JWT Authentication<br/>OAuth 2.0]
        RBAC[Role-Based Access<br/>Admin/User]
        CORS[CORS Policy<br/>Origin Validation]
        RateLimit[Rate Limiting<br/>Cloud Armor]
    end

    subgraph "Data Security"
        Encrypt[Encryption at Rest<br/>GCS/Neon]
        TLS[TLS in Transit<br/>All Connections]
        Audit[Audit Logging<br/>All Changes]
        Secrets[Secret Manager<br/>API Keys]
    end

    subgraph "Network Security"
        VPC[VPC Peering<br/>Private Network]
        FW[Firewall Rules<br/>Egress/Ingress]
        IAM[Cloud IAM<br/>Service Accounts]
    end

    CDN --> CloudArmor
    CloudArmor --> Auth
    Auth --> RBAC
    RBAC --> Encrypt
    Encrypt --> VPC

    style Auth fill:#34a853
    style Encrypt fill:#ea4335
    style VPC fill:#4285f4
```

---

## Deployment Architecture

### CI/CD Pipeline

```mermaid
graph LR
    subgraph "Source Control"
        GH[GitHub Repository<br/>main branch]
    end

    subgraph "CI Pipeline - GitHub Actions"
        Test[Run Tests<br/>pytest, jest]
        Lint[Code Quality<br/>pylint, eslint]
        Build[Build Images<br/>Docker]
    end

    subgraph "Artifact Registry"
        GAR[Google Artifact Registry<br/>us-central1]
    end

    subgraph "CD Pipeline"
        Deploy[Deploy to Cloud Run<br/>Blue-Green]
        Migrate[Run Migrations<br/>Alembic]
        Smoke[Smoke Tests<br/>Health Checks]
    end

    subgraph "Production Environment"
        CR1[Cloud Run: api-service<br/>Revision: abc123]
        CR2[Cloud Run: worker-service<br/>Revision: def456]
        CR3[Cloud Run: qdrant<br/>Revision: ghi789]
    end

    GH -->|Push| Test
    Test --> Lint
    Lint --> Build
    Build --> GAR
    GAR --> Deploy
    Deploy --> Migrate
    Migrate --> Smoke
    Smoke -->|Success| CR1 & CR2 & CR3
    Smoke -->|Failure| Deploy

    style GH fill:#181717
    style GAR fill:#4285f4
    style CR1 fill:#34a853
```

### Multi-Environment Strategy

```mermaid
graph TB
    subgraph "Development"
        DevFE[Vercel Preview<br/>dev-*.vercel.app]
        DevAPI[Cloud Run Dev<br/>dev-api-*.run.app]
        DevDB[(Neon Branch<br/>dev)]
        DevQdrant[Qdrant Dev<br/>In-Memory]
    end

    subgraph "Staging"
        StageFE[Vercel Staging<br/>staging.doxin.com]
        StageAPI[Cloud Run Staging<br/>api-staging.doxin.com]
        StageDB[(Neon Branch<br/>staging)]
        StageQdrant[Qdrant Staging<br/>Persistent]
    end

    subgraph "Production"
        ProdFE[Vercel Production<br/>app.doxin.com]
        ProdAPI[Cloud Run Production<br/>api.doxin.com]
        ProdDB[(Neon Main<br/>production)]
        ProdQdrant[Qdrant Production<br/>HA Mode]
    end

    DevFE --> DevAPI
    DevAPI --> DevDB & DevQdrant

    StageFE --> StageAPI
    StageAPI --> StageDB & StageQdrant

    ProdFE --> ProdAPI
    ProdAPI --> ProdDB & ProdQdrant

    DevDB -.promote.-> StageDB
    StageDB -.promote.-> ProdDB

    style ProdFE fill:#0070f3
    style ProdAPI fill:#34a853
    style ProdDB fill:#16a34a
```

---

## Monitoring & Observability

### Observability Stack

```mermaid
graph TB
    subgraph "Application Layer"
        API[Cloud Run API]
        Worker[Cloud Run Worker]
        Chat[Cloud Run Chat Service]
    end

    subgraph "Google Cloud Operations"
        CloudLog[Cloud Logging<br/>Centralized Logs]
        CloudMon[Cloud Monitoring<br/>Metrics & Alerts]
        CloudTrace[Cloud Trace<br/>Distributed Tracing]
        CloudProfile[Cloud Profiler<br/>Performance]
    end

    subgraph "Dashboards & Alerts"
        GrafDash[Grafana Cloud<br/>Custom Dashboards]
        AlertMgr[Alert Manager<br/>PagerDuty/Slack]
        Uptime[Uptime Monitoring<br/>Better Uptime]
    end

    subgraph "Business Metrics"
        AnalyticDB[(BigQuery<br/>Analytics)]
        DataStudio[Looker Studio<br/>Reporting]
    end

    API --> CloudLog & CloudMon & CloudTrace
    Worker --> CloudLog & CloudMon & CloudTrace
    Chat --> CloudLog & CloudMon & CloudTrace

    CloudLog --> GrafDash
    CloudMon --> GrafDash & AlertMgr
    CloudTrace --> CloudProfile

    CloudLog --> AnalyticDB
    AnalyticDB --> DataStudio

    style CloudLog fill:#4285f4
    style CloudMon fill:#34a853
    style GrafDash fill:#f46800
```

### Key Metrics & Alerts

```yaml
metrics:
  api_service:
    - request_rate: requests/second
    - request_latency_p95: milliseconds
    - error_rate: 4xx/5xx errors
    - concurrent_connections: active WebSocket connections

  worker_service:
    - job_queue_depth: pending jobs
    - job_processing_time: seconds
    - job_success_rate: percentage

  qdrant_service:
    - vector_search_latency: milliseconds
    - collection_size: number of vectors
    - memory_usage: GB

  database:
    - connection_pool_usage: percentage
    - query_latency_p95: milliseconds
    - active_connections: count
    - storage_usage: GB

alerts:
  critical:
    - name: "API Service Down"
      condition: "health_check_failures > 3"
      channel: "pagerduty"

    - name: "Database Connection Pool Exhausted"
      condition: "connection_pool_usage > 90%"
      channel: "pagerduty"

  warning:
    - name: "High Error Rate"
      condition: "error_rate > 5%"
      channel: "slack"

    - name: "Slow Response Time"
      condition: "request_latency_p95 > 1000ms"
      channel: "slack"
```

---

## Cost Optimization

### Resource Cost Breakdown (Monthly Estimate)

| Service | Usage | Cost |
|---------|-------|------|
| **Cloud Run (API)** | 2-20 instances, 2vCPU, 4GB | $150-$800 |
| **Cloud Run (Worker)** | 1-10 instances, 1vCPU, 2GB | $50-$300 |
| **Cloud Run (Qdrant)** | 1-3 instances, 2vCPU, 8GB | $100-$250 |
| **Memorystore Redis** | 2GB, HA | $50 |
| **Neon Database** | 100GB, 200 compute hours | $69 |
| **Cloud Storage** | 1TB, 1M operations | $26 |
| **Cloud Load Balancer** | 1TB egress | $25 |
| **Cloud Logging** | 50GB | $25 |
| **Cloud Monitoring** | Custom metrics | $10 |
| **Vercel** | Pro Plan | $20 |
| **OpenAI API** | 10M tokens | $100-$200 |
| **Total** | | **$625-$1,905/month** |

### Scaling Strategy

```yaml
autoscaling:
  api_service:
    min_instances: 2  # High availability
    max_instances: 20
    target_cpu_utilization: 70%
    target_concurrency: 100
    scale_down_delay: 5m

  worker_service:
    min_instances: 1
    max_instances: 10
    target_cpu_utilization: 80%
    queue_depth_threshold: 50

  qdrant_service:
    min_instances: 1  # Can be 0 for dev
    max_instances: 3
    target_memory_utilization: 75%
```

---

## Architecture Decision Records

### ADR-001: GCP over Azure for Production

**Status**: Accepted

**Context**: Need cloud platform for production deployment.

**Decision**: Use Google Cloud Platform instead of Azure.

**Rationale**:
- Better Cloud Run pricing and scaling model
- Superior global load balancing
- More cost-effective Memorystore Redis
- Excellent integration with Vercel
- Better cold start times

**Consequences**:
- Migration from Azure-focused documentation
- New IAM and networking setup
- Team needs GCP training

### ADR-002: Neon Database for PostgreSQL

**Status**: Accepted

**Context**: Need scalable, serverless PostgreSQL database.

**Decision**: Use Neon serverless PostgreSQL.

**Rationale**:
- Serverless scaling (scale to zero)
- Branch-based development workflow
- Excellent connection pooling
- Cost-effective for variable workloads
- PostgreSQL compatibility

**Consequences**:
- Cross-cloud latency (Neon on AWS, API on GCP)
- Connection pooling critical
- Need monitoring for connection limits

### ADR-003: Qdrant for Vector Database

**Status**: Accepted

**Context**: Need vector database for RAG and semantic search.

**Decision**: Self-host Qdrant on Cloud Run.

**Rationale**:
- Open source, no vendor lock-in
- Excellent performance for our scale
- Can run in container on Cloud Run
- Cost-effective vs. managed alternatives
- Rich filtering and hybrid search

**Consequences**:
- Need to manage persistence (GCS volumes)
- Manual backup strategy
- Scaling requires monitoring

### ADR-004: Hugging Face for AI Inference Streaming

**Status**: Accepted

**Context**: Need streaming AI inference for chatbot responses.

**Decision**: Use Hugging Face Inference API for streaming alongside OpenAI/Anthropic.

**Rationale**:
- Open source model options
- Cost-effective for high volume
- True streaming support
- Can self-host if needed
- Good latency from Europe

**Consequences**:
- Multiple AI providers to manage
- Fallback logic needed
- Different rate limits per provider

---

## Next Steps

1. **Phase 1: Infrastructure Setup** (Week 1-2)
   - Create GCP project and enable APIs
   - Set up VPC network and Cloud NAT
   - Deploy Memorystore Redis
   - Configure Neon database

2. **Phase 2: Core Services** (Week 3-4)
   - Deploy Cloud Run API service
   - Deploy Cloud Run worker service
   - Set up Cloud Tasks queue
   - Configure Cloud Storage buckets

3. **Phase 3: AI Features** (Week 5-6)
   - Deploy Qdrant vector database
   - Implement RAG pipeline
   - Build chat service endpoints
   - Index documentation

4. **Phase 4: Monitoring & Production** (Week 7-8)
   - Configure Cloud Operations
   - Set up alerting
   - Performance testing
   - Production launch

---

**Document Version**: 1.0
**Last Updated**: 2025-10-20
**Maintained By**: Platform Team
