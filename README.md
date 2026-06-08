# DocuMind AI

**Upload any PDF and ask questions about it — powered by RAG, LangChain, and Groq LLaMA 3.**

🔗 **Live Demo:** [https://documind-ai.vercel.app](https://documind-ai.vercel.app) ← update this after deploying

---

## What it does

- Upload a PDF document
- Ask questions in natural language
- Get accurate answers extracted from the document
- Supports multiple languages — detects document language and lets you choose reply language
- Dark / Light mode

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python), LangChain v1.x |
| LLM | Groq — LLaMA 3.1 8B (free API) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local, free) |
| Vector Store | ChromaDB (local) |
| Deployment | Vercel (frontend) + Render (backend) |

---

## Architecture

```
User uploads PDF
      │
      ▼
Next.js Frontend (Vercel)
      │  HTTP
      ▼
FastAPI Backend (Render)
      │
      ├── PyPDFLoader → loads PDF pages
      ├── RecursiveCharacterTextSplitter → chunks text
      ├── HuggingFaceEmbeddings → converts chunks to vectors
      ├── ChromaDB → stores and retrieves vectors
      └── Groq LLaMA 3 → generates answers
```

---

## Project Structure

```
DocuMind-AI/
├── frontend/                  # Next.js app
│   ├── app/
│   │   └── page.tsx
│   ├── components/
│   │   └── ChatWindow.tsx
│   └── .env.local
│
└── backend/                   # FastAPI app
    ├── main.py
    ├── Procfile               # Render deployment
    ├── requirements.txt
    └── app/
        ├── config.py
        ├── logger.py
        ├── api/v1/routes/
        │   ├── health.py
        │   ├── document.py
        │   ├── chat.py
        │   └── usage.py
        ├── services/
        │   ├── rag_service.py
        │   ├── embedding_service.py
        │   ├── language_service.py
        │   └── rate_limit_service.py
        └── models/
            └── schemas.py
```

---

## Run locally

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop (for local ChromaDB persistence — optional)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Start backend
python main.py
# Runs on http://localhost:8001
# API docs at http://localhost:8001/docs
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local

# Start frontend
npm run dev
# Runs on http://localhost:3000
```

---

## Environment variables

### Backend `.env`

```
GROQ_API_KEY=your_groq_api_key
ENV=development
FRONTEND_ORIGIN=http://localhost:3000
DEMO_ACCESS_KEY=optional_demo_key
LOG_LEVEL=INFO
MAX_PDF_MB=5
MAX_PDF_PAGES=20
DAILY_UPLOAD_LIMIT=5
DAILY_REQUEST_LIMIT=50
```

### Frontend `.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_DEMO_KEY=optional_demo_key
```

---

## Deploy

### Backend → Render

1. Go to [render.com](https://render.com) → New Web Service
2. Connect GitHub repo → set root directory to `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see above, set `ENV=production`)

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project
2. Connect GitHub repo → set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com`
4. Deploy

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/api/v1/health/` | Versioned health check |
| POST | `/api/v1/documents/upload` | Upload PDF |
| POST | `/api/v1/chat` | Ask a question |
| POST | `/api/v1/set-language` | Set reply language preference |
| GET | `/api/v1/usage` | Check daily usage stats |
| GET | `/docs` | Interactive API documentation (Swagger) |

---

## Features in progress

- [ ] Chat history persistence
- [ ] Multiple PDF support
- [ ] Agent mode — answer questions that require reasoning across documents
- [ ] pgvector migration for production vector storage

---

## Author

**Vishveshwar Hiremath**
Full Stack Engineer — SaaS & AI Products

[LinkedIn](https://linkedin.com/in/vishveshwar-hiremath) · [GitLab](https://github.com/vishveshwarh)
