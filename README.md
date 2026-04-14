# AegisAI - Internal Document Q&A

Multi-tenant RAG platform for Q&A over Notion, Confluence, and PDF documents.

## Quick Start

### 1. Copy environment config
```bash
cp .env.example .env
```

### 2. Start with Docker (GPU machine)
```bash
docker compose up
```

### 3. Start with Docker (CPU-only machine)
```bash
docker compose -f docker-compose.cpu.yml up
```

### 4. Pull the LLM model
```bash
docker exec -it aegis-backend-1 ollama pull llama3.2     # GPU
docker exec -it aegis-backend-1 ollama pull phi3:3.8b   # CPU
```

### 5. Open the UI
Navigate to `http://localhost:8000`

### 6. Ingest documents and chat
1. Enter API key `aegis-demo-key-12345` (demo tenant from `.env`)
2. Go to **Ingest Documents**, add PDF paths, click **Ingest**
3. Go to **Chat**, ask questions

---

## Local Development (no Docker)

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Ollama
```bash
ollama serve
ollama pull llama3.2     # or phi3:3.8b for CPU
```

### 3. Run backend
```bash
cd aegis
uvicorn backend.main:app --reload --port 8000
```

### 4. Open UI
Navigate to `http://localhost:8000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ask` | Ask a question |
| POST | `/api/ingest` | Ingest documents |
| GET | `/api/me` | Get tenant status |
| GET | `/api/tenants` | List tenants |
| GET | `/health` | Health check |

### Example: Ingest PDFs via curl
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "X-Tenant-Key: aegis-demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "pdf", "source_config": {"paths": ["/path/to/doc.pdf"]}}'
```

### Example: Ask a question via curl
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "X-Tenant-Key: aegis-demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

---

## Adding More Tenants

Edit `.env`:
```
TENANTS=demo=aegis-demo-key-12345,acme=acme-secret-key,globex=globex-key
```

---

## Project Structure
```
aegis/
├── backend/
│   ├── main.py           # FastAPI app
│   ├── models.py         # Pydantic schemas
│   ├── api/
│   │   ├── rag.py        # /ask endpoint
│   │   ├── ingest.py     # /ingest endpoint
│   │   └── tenants.py    # tenant info
│   ├── connectors/
│   │   ├── pdf.py        # PDF ingestion
│   │   ├── notion.py     # Notion connector
│   │   └── confluence.py # Confluence connector
│   ├── core/
│   │   ├── embedder.py   # sentence-transformers
│   │   ├── vectorstore.py # FAISS
│   │   └── llm.py        # Ollama client
│   └── middleware/
│       └── auth.py       # API key auth
├── frontend/
│   └── index.html        # Chat UI
├── data/                 # Per-tenant FAISS indexes (created at runtime)
├── Dockerfile
├── docker-compose.yml    # GPU
├── docker-compose.cpu.yml # CPU
└── .env
```
