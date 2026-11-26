# Conversational RAG API

A FastAPI backend that:
- Answers questions about your uploaded documents (custom RAG, no FAISS, Chroma, or RetrievalQAChain)
- Remembers each conversation (Redis chat memory, multi-turn)
- Books interviews through chat (name, email, date, time) using an LLM, and stores them in SQLite

## Requirements

- Python 3.11+
- Docker (for Redis)
- A free Groq API key: https://console.groq.com/keys

## Setup

**1. Create and activate a virtual environment**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Start Redis**

```bash
docker run -d --name redis -p 6379:6379 redis:7
```

If the container already exists: `docker start redis`

**4. Create `.env`** (copy `.env.example` and fill in your key)

```env
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=your_groq_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=unused
DATABASE_URL=sqlite+aiosqlite:///./data/bookings.db
```

No quotes and no spaces around `=`. If the model is rejected, set `LLM_MODEL` to another model your Groq key can use.

**5. Run the server**

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. Every endpoint can be tested from this page: click an endpoint, press **Try it out**, then **Execute**.

## How to use

Do these in order.

### 1. Health check

`GET /health` returns `{"status": "ok", "redis": "connected"}`.

### 2. Upload a document

`POST /documents/ingest`: choose a `.pdf`, `.txt`, or `.md` file.

```json
{"filename": "guide.pdf", "chunks": 3}
```

Upload at least one document before asking questions.

### 3. Ask about the document

`POST /chat`

```json
{"session_id": "doc1", "message": "Explain the uploaded document in simple terms. Give a summary and the key points."}
```

The response has `answer` and `sources` (the files used).

### 4. Ask a follow-up (multi-turn)

Use the same `session_id`:

```json
{"session_id": "doc1", "message": "Explain the second point in more detail"}
```

### 5. Book an interview

All details in one message:

```json
{"session_id": "s1", "message": "Book an interview. Name: Abhigya Rai, email: abhigya@example.com, date: 2026-12-01, time: 10:00"}
```

Or step by step. The system asks for whatever is missing: