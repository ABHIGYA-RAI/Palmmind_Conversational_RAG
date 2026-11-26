# Conversational RAG API

A FastAPI backend that answers questions about uploaded documents, remembers each conversation, and books interviews through chat.

- **Custom RAG:** no FAISS, Chroma, or RetrievalQAChain
- **Redis:** chat memory (multi-turn), vector storage, and booking progress
- **LLM booking:** extracts name, email, date and time from chat, then saves to SQLite

## Requirements

- Python 3.11+
- Docker (for Redis)
- Free Groq API key: https://console.groq.com/keys

## Setup

```bash
# 1. Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Redis
docker run -d --name redis -p 6379:6379 redis:7   # or: docker start redis

# 4. Config
copy .env.example .env          # Mac/Linux: cp .env.example .env
```

Open `.env` and set `LLM_API_KEY` to your Groq key. No quotes, no spaces.

```bash
# 5. Run
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs and test every endpoint there: click an endpoint, **Try it out**, **Execute**.

> If PowerShell blocks activation, skip it and use `.venv\Scripts\python -m uvicorn app.main:app`.

## How to use

| Step | Endpoint | Body |
|---|---|---|
| Check | `GET /health` | none |
| Upload a document | `POST /documents/ingest` | a `.pdf`, `.txt` or `.md` file |
| Ask | `POST /chat` | `{"session_id": "s1", "message": "Explain the uploaded document."}` |
| Follow up | `POST /chat` | same `session_id`: `{"session_id": "s1", "message": "Explain that in more detail"}` |
| Book | `POST /chat` | `{"session_id": "s2", "message": "Book an interview. Name: Abhigya Rai, email: abhigya@example.com, date: 2026-12-01, time: 10:00"}` |
| View bookings | `GET /bookings` | none |

Upload a document before asking questions. Booking details can also come across several messages, and the system asks for whatever is missing.

## How it works

1. **Ingest:** text is split into 800-character chunks (150 overlap), converted to vectors, and stored in Redis.
2. **Retrieve:** the question becomes a vector, and the top 4 chunks are found with cosine similarity (NumPy).
3. **Answer:** the chunks and chat history go to the LLM, which answers only from that context.
4. **Memory:** the last 20 messages per `session_id` are kept in Redis for 24 hours.
5. **Booking:** messages with "book", "interview", "schedule" or "appointment" start the booking flow. The LLM extracts the fields as JSON, partial progress stays in Redis, and a complete booking is validated and saved to SQLite.

## Project structure

```
app/
  main.py          App startup
  api/             Endpoints (chat, documents)
  core/            Settings, Redis connection
  models/          Pydantic schemas
  services/        LLM client, chunking, embeddings, RAG, booking
  repositories/    Redis memory, vector store, SQLite bookings
tests/             Unit tests (run with: pytest)
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Redis error on `/health` | `docker start redis` |
| `LLM error 401` | Wrong API key in `.env` |
| `LLM error 404` | Set `LLM_MODEL` to a model your key can use |
| `.env` change ignored | Restart uvicorn |
| "I don't know" answers | Upload a document first |
| Normal question starts booking | Avoid the words "book", "schedule", "interview", "appointment" |

## Known limitations

- Embeddings come from a local hashing embedder: they match shared words, not meaning. It sits behind an `Embedder` interface so a real embedding API can replace it.
- Answers use the top 4 chunks only, so broad questions cover the most relevant parts, not the whole document.
- Booking intent is keyword-based.
- No authentication and no check for conflicting booking slots.

## Screenshots

See the screenshots folder in this repo for the health check, document upload, RAG answer, multi-turn follow-up, booking, and stored bookings.