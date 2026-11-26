# Conversational RAG API

FastAPI backend with custom RAG, Redis chat memory, and LLM-based interview booking.

## Stack
FastAPI, Redis (chat memory, vector store, booking state), SQLite (bookings), Groq LLM (OpenAI-compatible API). Retrieval is custom cosine similarity with NumPy. No FAISS, Chroma, or RetrievalQAChain.

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
docker run -d --name redis -p 6379:6379 redis:7
```

Create `.env`:
```env
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=your_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=unused
DATABASE_URL=sqlite+aiosqlite:///./data/bookings.db
```

Run:
```bash
uvicorn app.main:app --reload
```
Docs: http://127.0.0.1:8000/docs

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | /documents/ingest | Upload PDF/TXT/MD, chunk, embed, store |
| POST | /chat | Multi-turn RAG chat and interview booking |
| GET | /bookings | List stored bookings |
| GET | /health | Health and Redis check |

## How it works
1. **Ingestion:** text is chunked (800 chars, 150 overlap), embedded, and stored in Redis.
2. **Retrieval:** the query is embedded and the top 4 chunks are found by cosine similarity.
3. **Memory:** the last 20 messages per `session_id` are kept in a Redis list (24h TTL).
4. **Booking:** booking intent triggers LLM JSON extraction. Partial details are kept in Redis across turns until name, email, date and time are complete, then saved to SQLite.

## Note
Embeddings use a local hashing embedder (`app/services/embeddings.py`) behind an `Embedder` protocol, so it can be swapped for a provider embedding API.