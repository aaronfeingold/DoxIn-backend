# DoxIn - Prototype Architecture with AI Agent

> **Development architecture featuring self-serving AI chatbot agent with RAG capabilities**

## Table of Contents

1. [Prototype Overview](#prototype-overview)
2. [AI Agent Architecture](#ai-agent-architecture)
3. [RAG Pipeline](#rag-pipeline)
4. [Chat Service Implementation](#chat-service-implementation)
5. [Streaming Infrastructure](#streaming-infrastructure)
6. [Development Environment](#development-environment)
7. [Testing Strategy](#testing-strategy)

---

## Prototype Overview

### System Architecture

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        UI[User Interface]
        ChatUI[Chat Widget]
        HelpPanel[Context Help Panel]
    end

    subgraph "Backend API - Flask"
        direction TB
        API[API Gateway]

        subgraph "Core Services"
            InvService[Invoice Service]
            JobService[Job Service]
            AuthService[Auth Service]
        end

        subgraph "AI Agent Services"
            ChatService[Chat Service<br/>Intent Router]
            RAGService[RAG Service<br/>Doc Retrieval]
            SQLService[Text-to-SQL<br/>Data Queries]
            ToolService[Tool Executor<br/>Actions]
        end
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL<br/>Structured Data)]
        Redis[(Redis<br/>Cache & Sessions)]
        Qdrant[(Qdrant Vector DB<br/>Documentation)]
        FileStore[Local Storage<br/>Documents]
    end

    subgraph "AI/ML Layer"
        OpenAI[OpenAI API<br/>GPT-4]
        Anthropic[Anthropic API<br/>Claude]
        HuggingFace[Hugging Face<br/>Llama/Mistral]
        Embeddings[Embedding Model<br/>text-embedding-3-small]
    end

    UI --> API
    ChatUI --> API
    HelpPanel --> API

    API --> InvService & JobService & AuthService & ChatService

    ChatService --> RAGService & SQLService & ToolService
    ChatService --> OpenAI & Anthropic & HuggingFace

    RAGService --> Qdrant
    RAGService --> Embeddings
    SQLService --> PostgreSQL
    ToolService --> InvService & JobService

    InvService --> PostgreSQL & FileStore
    JobService --> PostgreSQL & Redis
    AuthService --> PostgreSQL & Redis

    RAGService -.indexes.-> FileStore

    style ChatService fill:#34a853
    style RAGService fill:#dc0073
    style Qdrant fill:#dc0073
    style ChatUI fill:#0070f3
```

### Key Features

1. **Multi-Modal AI Agent**
   - Natural language understanding
   - Context-aware responses
   - Multi-tool capabilities

2. **RAG-Powered Documentation Assistant**
   - Searches frontend/docs and backend/docs
   - Provides accurate, cited answers
   - Context-aware help suggestions

3. **Streaming Responses**
   - Real-time token streaming
   - SSE (Server-Sent Events)
   - Progressive UI updates

4. **Tool Integration**
   - Text-to-SQL for data queries
   - Invoice operations
   - System status checks

---

## AI Agent Architecture

### Agent Flow & Decision Tree

```mermaid
graph TB
    Start[User Message] --> Intent[Intent Classification]

    Intent --> |Documentation| DocCheck{Specific Topic?}
    Intent --> |Data Query| DataCheck{Query Type?}
    Intent --> |Action| ActionCheck{What Action?}
    Intent --> |Conversational| ChatResponse[General Chat Response]

    DocCheck --> |Yes| RAG[RAG Retrieval]
    DocCheck --> |No| Browse[Browse Docs]

    DataCheck --> |Simple| DirectSQL[Text-to-SQL]
    DataCheck --> |Complex| Analytical[Analytics Query]

    ActionCheck --> |Invoice| InvTool[Invoice Tool]
    ActionCheck --> |Job| JobTool[Job Tool]
    ActionCheck --> |Export| ExportTool[Export Tool]

    RAG --> GenResp[Generate Response with Context]
    DirectSQL --> FormatData[Format Data]
    InvTool --> Confirm[Confirm Action]

    GenResp --> Stream[Stream Response to User]
    FormatData --> Stream
    ChatResponse --> Stream
    Confirm --> Stream

    style Intent fill:#fbbf24
    style RAG fill:#dc0073
    style DirectSQL fill:#3b82f6
    style Stream fill:#34a853
```

### Agent Service Architecture

```mermaid
graph LR
    subgraph "Chat Service Core"
        Router[Intent Router<br/>Classify Intent]
        Context[Context Manager<br/>Session History]
        Stream[Streaming Manager<br/>SSE/WebSocket]
    end

    subgraph "Agent Tools"
        direction TB
        Tool1[Documentation Search<br/>RAG Retrieval]
        Tool2[Data Query<br/>Text-to-SQL]
        Tool3[Invoice Actions<br/>CRUD Operations]
        Tool4[Job Status<br/>Progress Tracking]
        Tool5[Export Data<br/>Reports & CSV]
    end

    subgraph "LLM Providers"
        Primary[OpenAI GPT-4<br/>Primary]
        Secondary[Anthropic Claude<br/>Complex Reasoning]
        Fallback[Hugging Face<br/>Cost-Effective Fallback]
    end

    Router --> Tool1 & Tool2 & Tool3 & Tool4 & Tool5
    Tool1 --> Primary
    Tool2 --> Primary
    Tool3 --> Context
    Context --> Primary | Secondary | Fallback
    Primary --> Stream
    Secondary --> Stream
    Fallback --> Stream

    style Router fill:#fbbf24
    style Tool1 fill:#dc0073
    style Stream fill:#34a853
```

### Agent Tools Specification

```yaml
tools:
  - name: "search_documentation"
    description: "Search through DoxIn documentation (frontend & backend)"
    parameters:
      query: string
      source_filter: ["frontend", "backend", "all"]
      max_results: integer
    returns: list[DocumentChunk]

  - name: "query_invoices"
    description: "Query invoice data using natural language"
    parameters:
      query: string
      user_scope: boolean
    returns: QueryResult

  - name: "get_job_status"
    description: "Check processing job status"
    parameters:
      job_id: string
    returns: JobStatus

  - name: "create_invoice"
    description: "Create a new invoice"
    parameters:
      invoice_data: object
    returns: Invoice
    requires_confirmation: true

  - name: "export_data"
    description: "Export invoices or reports"
    parameters:
      format: ["csv", "json", "pdf"]
      filters: object
    returns: FileURL

  - name: "explain_error"
    description: "Explain system errors and suggest fixes"
    parameters:
      error_code: string
      context: string
    returns: Explanation
```

---

## RAG Pipeline

### Document Indexing Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Indexer as RAG Indexer Service
    participant FS as File System
    participant Embed as Embedding Model
    participant Qdrant as Qdrant Vector DB
    participant Meta as Metadata Store

    Admin->>Indexer: Trigger indexing
    Indexer->>FS: Scan documentation directories
    FS-->>Indexer: List of markdown files

    loop For each markdown file
        Indexer->>FS: Read file content
        FS-->>Indexer: Raw markdown
        Indexer->>Indexer: Parse frontmatter & metadata
        Indexer->>Indexer: Chunk document (500 tokens)

        loop For each chunk
            Indexer->>Embed: Generate embedding
            Embed-->>Indexer: Vector (1536 dims)
            Indexer->>Qdrant: Upsert vector + payload
            Indexer->>Meta: Store chunk metadata
        end
    end

    Indexer-->>Admin: Indexing complete
    Note over Admin,Meta: Indexed: 150 docs, 2,345 chunks
```

### Document Chunking Strategy

```mermaid
graph TB
    subgraph "Input Processing"
        MD[Markdown File]
        Parser[Markdown Parser<br/>Extract Structure]
    end

    subgraph "Chunking Logic"
        Headers[Identify Headers<br/>H1, H2, H3]
        CodeBlocks[Extract Code Blocks<br/>Preserve Syntax]
        Sections[Split by Sections<br/>Logical Boundaries]
    end

    subgraph "Chunk Generation"
        SizeCheck{Chunk Size?}
        Overlap[Add Overlap<br/>100 tokens]
        Metadata[Add Metadata<br/>Title, Source, Tags]
    end

    subgraph "Output"
        Chunks[Document Chunks<br/>400-600 tokens each]
        Index[Ready for Indexing]
    end

    MD --> Parser
    Parser --> Headers & CodeBlocks & Sections

    Headers --> SizeCheck
    CodeBlocks --> SizeCheck
    Sections --> SizeCheck

    SizeCheck --> |Too Large| Sections
    SizeCheck --> |Just Right| Overlap
    Overlap --> Metadata
    Metadata --> Chunks
    Chunks --> Index

    style MD fill:#f97316
    style Chunks fill:#34a853
```

### Retrieval Process

```mermaid
sequenceDiagram
    participant User
    participant Chat as Chat Service
    participant Embed as Embedding Model
    participant Qdrant as Qdrant Vector DB
    participant Ranker as Re-ranking Service
    participant LLM as Language Model

    User->>Chat: "How do I upload invoices?"
    Chat->>Chat: Extract search query
    Chat->>Embed: Embed query
    Embed-->>Chat: Query vector (1536 dims)

    Chat->>Qdrant: Vector search (top 20)
    Note over Chat,Qdrant: Cosine similarity > 0.7
    Qdrant-->>Chat: 20 candidate chunks

    Chat->>Ranker: Re-rank by relevance
    Note over Chat,Ranker: Consider query intent & metadata
    Ranker-->>Chat: Top 5 chunks

    Chat->>Chat: Build context prompt
    Note over Chat: Context = query + top 5 chunks

    Chat->>LLM: Generate answer with context
    LLM-->>Chat: Streamed response
    Chat-->>User: Display answer with citations

    Note over User,Chat: Citations link to source docs
```

### Qdrant Collection Structure

```yaml
# Collection: documentation
collection_name: "documentation"
vector_config:
  size: 1536
  distance: Cosine

payload_schema:
  # Source Information
  source: string              # "frontend/docs" or "backend/docs"
  file_path: string           # Relative path
  file_name: string           # e.g., "API_DOCUMENTATION.md"

  # Document Structure
  doc_title: string           # Main document title
  section_title: string       # Section heading
  chunk_index: integer        # Position in document
  total_chunks: integer       # Total chunks in document

  # Content
  content: text               # Actual text chunk (400-600 tokens)
  code_language: string       # If chunk contains code
  has_code: boolean

  # Metadata
  tags: array<string>         # ["api", "authentication", "setup"]
  keywords: array<string>     # Extracted key terms
  related_endpoints: array    # API endpoints mentioned

  # Timestamps
  indexed_at: timestamp
  doc_updated_at: timestamp

# Example document
example:
  id: "fe-docs-api-123-chunk-5"
  vector: [0.123, -0.456, ...]
  payload:
    source: "frontend/docs"
    file_path: "frontend/docs/API_DOCUMENTATION.md"
    file_name: "API_DOCUMENTATION.md"
    doc_title: "API Documentation"
    section_title: "Authentication"
    chunk_index: 5
    total_chunks: 23
    content: "## Authentication\n\nThe API uses JWT tokens..."
    has_code: true
    code_language: "javascript"
    tags: ["api", "authentication", "jwt"]
    keywords: ["token", "bearer", "login"]
    related_endpoints: ["/auth/login", "/auth/refresh"]
    indexed_at: "2025-10-20T10:00:00Z"
    doc_updated_at: "2025-10-15T14:30:00Z"
```

---

## Chat Service Implementation

### API Endpoints

```yaml
# Chat Endpoints
endpoints:
  # Initialize chat session
  - path: /api/v1/chat/sessions
    method: POST
    description: Create new chat session
    request:
      title: string (optional)
    response:
      session_id: uuid
      created_at: timestamp

  # Send message (streaming)
  - path: /api/v1/chat/sessions/{session_id}/messages
    method: POST
    description: Send message and receive streaming response
    headers:
      Accept: text/event-stream
    request:
      message: string
      context: object (optional)
    response:
      stream: SSE
      events:
        - type: "token"
          data: string
        - type: "tool_call"
          data: {tool: string, args: object}
        - type: "complete"
          data: {message_id: uuid, tokens: int}

  # Get session history
  - path: /api/v1/chat/sessions/{session_id}/messages
    method: GET
    description: Retrieve chat history
    params:
      limit: integer (default: 50)
      offset: integer (default: 0)
    response:
      messages: array<Message>
      pagination: object

  # Get user sessions
  - path: /api/v1/chat/sessions
    method: GET
    description: List user's chat sessions
    response:
      sessions: array<Session>

  # Delete session
  - path: /api/v1/chat/sessions/{session_id}
    method: DELETE
    description: Delete chat session
    response:
      success: boolean
```

### Request/Response Flow

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Flask API
    participant Chat as Chat Service
    participant Tools as Agent Tools
    participant LLM as LLM Provider
    participant DB as PostgreSQL

    FE->>API: POST /chat/sessions/{id}/messages<br/>{message: "Show my invoices"}
    API->>Chat: Process message
    Chat->>Chat: Classify intent: "data_query"

    Chat->>Tools: query_invoices(user_scope=true)
    Tools->>DB: SELECT * FROM invoices WHERE user_id=...
    DB-->>Tools: Invoice records
    Tools-->>Chat: Formatted data

    Chat->>LLM: Generate natural language response<br/>with invoice data
    Note over Chat,LLM: Streaming enabled

    loop Stream tokens
        LLM-->>Chat: Token chunk
        Chat-->>API: SSE event: {type: "token", data: "Here"}
        API-->>FE: SSE stream
        FE->>FE: Update UI progressively
    end

    LLM-->>Chat: Stream complete
    Chat->>DB: Save message to session
    Chat-->>API: SSE event: {type: "complete"}
    API-->>FE: Close stream

    FE->>FE: Display complete response
```

### Chat Service Code Structure

```python
# app/services/chat_service.py
from typing import AsyncGenerator, Dict, Any
from app.services.llm_service import get_llm_service
from app.services.rag_service import get_rag_service
from app.services.sql_service import get_sql_service

class ChatService:
    """AI-powered chat service with tool integration"""

    def __init__(self):
        self.llm_service = get_llm_service()
        self.rag_service = get_rag_service()
        self.sql_service = get_sql_service()
        self.tools = self._register_tools()

    async def process_message_stream(
        self,
        session_id: str,
        message: str,
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process message and stream response"""

        # 1. Classify intent
        intent = await self._classify_intent(message)
        yield {"type": "intent", "data": intent}

        # 2. Execute appropriate tool(s)
        if intent == "documentation":
            context = await self.rag_service.search(message)
            yield {"type": "context", "data": context}

        elif intent == "data_query":
            sql_result = await self.sql_service.query(message, user_id)
            yield {"type": "data", "data": sql_result}
            context = self._format_data_context(sql_result)

        elif intent == "action":
            tool_result = await self._execute_tool(message, user_id)
            yield {"type": "tool_result", "data": tool_result}
            context = tool_result

        else:
            context = None

        # 3. Generate streaming response
        async for token in self.llm_service.generate_stream(
            message=message,
            context=context,
            session_id=session_id
        ):
            yield {"type": "token", "data": token}

        # 4. Save to database
        await self._save_message(session_id, message, response)
        yield {"type": "complete", "data": {"saved": True}}

    async def _classify_intent(self, message: str) -> str:
        """Classify user intent using LLM"""
        # Implementation details...
        pass

    def _register_tools(self) -> Dict[str, callable]:
        """Register available agent tools"""
        return {
            "search_docs": self.rag_service.search,
            "query_data": self.sql_service.query,
            "get_invoices": self._get_invoices_tool,
            "create_invoice": self._create_invoice_tool,
            # ... more tools
        }
```

---

## Streaming Infrastructure

### Server-Sent Events (SSE) Implementation

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask SSE Endpoint
    participant Chat as Chat Service
    participant LLM as LLM Provider

    Client->>API: POST /chat/stream<br/>Accept: text/event-stream
    API->>API: Set headers<br/>Content-Type: text/event-stream
    API->>Chat: Start message processing

    loop Stream tokens
        Chat->>LLM: Request next token
        LLM-->>Chat: Token: "The"
        Chat->>API: Yield SSE event
        API-->>Client: data: {"type":"token","data":"The"}\n\n
        Note over Client: Display "The"

        Chat->>LLM: Request next token
        LLM-->>Chat: Token: " invoice"
        Chat->>API: Yield SSE event
        API-->>Client: data: {"type":"token","data":" invoice"}\n\n
        Note over Client: Display "The invoice"
    end

    Chat->>API: Yield complete event
    API-->>Client: data: {"type":"complete"}\n\n
    API->>API: Close connection
```

### SSE Endpoint Implementation

```python
# app/routes/chat.py
from flask import Blueprint, request, Response, stream_with_context
from app.services.chat_service import get_chat_service
from app.utils.auth import require_auth
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
@require_auth
def chat_stream(session_id):
    """Stream chat responses using Server-Sent Events"""
    data = request.get_json()
    message = data.get('message')
    user_id = g.current_user_id

    def generate():
        """SSE generator function"""
        chat_service = get_chat_service()

        try:
            # Stream events from chat service
            for event in chat_service.process_message_stream(
                session_id=session_id,
                message=message,
                user_id=user_id
            ):
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            # Send error event
            error_event = {
                "type": "error",
                "data": {"message": str(e)}
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'  # Disable nginx buffering
        }
    )
```

### Frontend SSE Consumer

```typescript
// frontend/lib/chat/useChatStream.ts
import { useState, useCallback } from 'react';

export function useChatStream(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [currentChunk, setCurrentChunk] = useState('');

  const sendMessage = useCallback(async (message: string) => {
    setStreaming(true);
    setCurrentChunk('');

    const response = await fetch(
      `/api/v1/chat/sessions/${sessionId}/messages`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({ message }),
      }
    );

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const eventData = JSON.parse(line.slice(6));

          switch (eventData.type) {
            case 'token':
              setCurrentChunk(prev => prev + eventData.data);
              break;

            case 'complete':
              setMessages(prev => [...prev, {
                role: 'assistant',
                content: currentChunk,
              }]);
              setCurrentChunk('');
              setStreaming(false);
              break;

            case 'error':
              console.error('Chat error:', eventData.data);
              setStreaming(false);
              break;
          }
        }
      }
    }
  }, [sessionId, currentChunk]);

  return { messages, sendMessage, streaming, currentChunk };
}
```

---

## Development Environment

### Local Docker Compose Setup

```yaml
# docker-compose.yml for development
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: pgvector/pgvector:pg16
    container_name: doxin-postgres-dev
    environment:
      POSTGRES_DB: doxin
      POSTGRES_USER: doxin
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/schema_refined.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: doxin-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: doxin-qdrant-dev
    ports:
      - "6333:6333"  # HTTP API
      - "6334:6334"  # gRPC API
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

  # Flask API (development)
  api:
    build:
      context: ./backend/api
      dockerfile: Dockerfile.dev
    container_name: doxin-api-dev
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://doxin:dev_password@postgres:5432/doxin
      REDIS_URL: redis://redis:6379/0
      QDRANT_URL: http://qdrant:6333
      FLASK_ENV: development
      FLASK_DEBUG: 1
    volumes:
      - ./backend/api:/app
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis
      - qdrant
    command: python app.py

  # Next.js Frontend (development)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: doxin-frontend-dev
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:5000
      DATABASE_URL: postgresql://doxin:dev_password@postgres:5432/doxin
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

### Environment Variables

```bash
# .env.development
# Database
DATABASE_URL=postgresql://doxin:dev_password@localhost:5433/doxin
POSTGRES_DB=doxin
POSTGRES_USER=doxin
POSTGRES_PASSWORD=dev_password

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Empty for dev

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HUGGINGFACE_API_KEY=hf_...

# Embedding Model
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# LLM Models
DEFAULT_LLM_MODEL=gpt-4o-mini
VISION_MODEL=gpt-4o
CHAT_MODEL=gpt-4o-mini

# App Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
FRONTEND_URL=http://localhost:3000

# File Storage
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=100
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7

# Chat Configuration
CHAT_MAX_HISTORY=20
CHAT_SESSION_TIMEOUT=3600  # 1 hour
```

---

## Testing Strategy

### Test Coverage Architecture

```mermaid
graph TB
    subgraph "Unit Tests"
        U1[RAG Service Tests<br/>Chunking, Embedding]
        U2[Chat Service Tests<br/>Intent, Tools]
        U3[SQL Service Tests<br/>Query Generation]
    end

    subgraph "Integration Tests"
        I1[API Endpoint Tests<br/>Chat Streaming]
        I2[Database Tests<br/>Session Management]
        I3[Qdrant Tests<br/>Vector Search]
    end

    subgraph "End-to-End Tests"
        E1[Chat Flow Tests<br/>User to Response]
        E2[RAG Pipeline Tests<br/>Index to Retrieval]
        E3[Tool Execution Tests<br/>Actions & Confirmations]
    end

    subgraph "Performance Tests"
        P1[Streaming Latency<br/>Token Throughput]
        P2[Vector Search Speed<br/>Query Response Time]
        P3[Concurrent Users<br/>Load Testing]
    end

    U1 & U2 & U3 --> I1 & I2 & I3
    I1 & I2 & I3 --> E1 & E2 & E3
    E1 & E2 & E3 --> P1 & P2 & P3

    style E1 fill:#34a853
    style P1 fill:#fbbf24
```

### Sample Test Cases

```python
# tests/test_chat_service.py
import pytest
from app.services.chat_service import ChatService

@pytest.fixture
def chat_service():
    return ChatService()

@pytest.mark.asyncio
async def test_intent_classification(chat_service):
    """Test intent classification for different message types"""
    # Documentation query
    intent = await chat_service._classify_intent(
        "How do I upload invoices?"
    )
    assert intent == "documentation"

    # Data query
    intent = await chat_service._classify_intent(
        "Show me my invoices from last month"
    )
    assert intent == "data_query"

    # Action request
    intent = await chat_service._classify_intent(
        "Create a new invoice for Acme Corp"
    )
    assert intent == "action"

@pytest.mark.asyncio
async def test_streaming_response(chat_service, mock_session):
    """Test streaming response generation"""
    message = "What is DoxIn?"
    stream = chat_service.process_message_stream(
        session_id=mock_session.id,
        message=message,
        user_id="test-user"
    )

    events = []
    async for event in stream:
        events.append(event)

    # Check event types
    assert any(e['type'] == 'intent' for e in events)
    assert any(e['type'] == 'token' for e in events)
    assert events[-1]['type'] == 'complete'

# tests/test_rag_service.py
from app.services.rag_service import RAGService

def test_document_chunking(rag_service):
    """Test document chunking logic"""
    markdown = """
# API Documentation

## Authentication

The API uses JWT tokens for authentication.

## Endpoints

### GET /invoices
Returns list of invoices.
    """

    chunks = rag_service.chunk_document(markdown, chunk_size=100)

    assert len(chunks) > 0
    assert all('content' in chunk for chunk in chunks)
    assert all('metadata' in chunk for chunk in chunks)

@pytest.mark.asyncio
async def test_vector_search(rag_service, indexed_docs):
    """Test vector similarity search"""
    results = await rag_service.search(
        query="How to authenticate API requests?",
        top_k=5
    )

    assert len(results) <= 5
    assert all(r['score'] >= 0.7 for r in results)
    assert 'authentication' in results[0]['content'].lower()
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)

```yaml
tasks:
  - name: "Set up Qdrant vector database"
    subtasks:
      - Deploy Qdrant container
      - Create documentation collection
      - Test basic CRUD operations

  - name: "Implement document indexing"
    subtasks:
      - Build markdown parser
      - Implement chunking logic
      - Create embedding pipeline
      - Index existing docs

  - name: "Basic RAG service"
    subtasks:
      - Vector search implementation
      - Relevance scoring
      - Context formatting
```

### Phase 2: Chat Service (Week 3-4)

```yaml
tasks:
  - name: "Chat API endpoints"
    subtasks:
      - Session management
      - Message storage
      - SSE streaming setup

  - name: "Intent classification"
    subtasks:
      - Intent classifier
      - Tool routing logic
      - Context handling

  - name: "Tool integration"
    subtasks:
      - Documentation search tool
      - Text-to-SQL tool
      - Invoice action tools
```

### Phase 3: Frontend Integration (Week 5-6)

```yaml
tasks:
  - name: "Chat UI component"
    subtasks:
      - Message display
      - Streaming text renderer
      - Citation links

  - name: "Context-aware help"
    subtasks:
      - Page-specific suggestions
      - Embedded help widget
      - Search interface

  - name: "User experience"
    subtasks:
      - Loading states
      - Error handling
      - Accessibility
```

### Phase 4: Testing & Optimization (Week 7-8)

```yaml
tasks:
  - name: "Testing"
    subtasks:
      - Unit test coverage
      - Integration tests
      - E2E chat flows
      - Load testing

  - name: "Optimization"
    subtasks:
      - Response latency
      - Vector search performance
      - Caching strategy

  - name: "Documentation"
    subtasks:
      - API documentation
      - User guide
      - Development docs
```

---

## Next Steps

1. **Start with RAG Pipeline**
   - Index documentation first
   - Test retrieval quality
   - Iterate on chunking strategy

2. **Build Basic Chat Service**
   - Simple Q&A without tools
   - Get streaming working
   - Add conversation history

3. **Add Tool Integration**
   - Start with read-only tools
   - Add data query capabilities
   - Implement action tools with confirmation

4. **Frontend Implementation**
   - Build chat UI component
   - Integrate with API
   - Polish user experience

5. **Production Preparation**
   - Performance testing
   - Security review
   - Deployment to GCP

---

**Document Version**: 1.0
**Last Updated**: 2025-10-20
**Maintained By**: Development Team
