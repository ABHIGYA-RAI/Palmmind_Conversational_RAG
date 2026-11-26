# Conversational RAG API

A FastAPI backend that:
- Answers questions from your uploaded documents 
- Remembers the conversation per session (Redis chat memory)
- Books interviews through chat (name, email, date, time) and stores them in SQLite

## What you need first

- Python 3.11 or newer
- Docker (for Redis)
- A free Groq API key: https://console.groq.com/keys

## Setup (5 steps)

**1. Open a terminal in the project folder and create a virtual environment**

```bash
python -m venv .venv
```

Activate it:

```bash
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

If the container already exists, run `docker start redis` instead.

**4. Create a `.env` file in the project root**

```env
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=your_groq_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=unused
DATABASE_URL=sqlite+aiosqlite:///./data/bookings.db
```

Replace `your_groq_key_here` with your real key. No quotes, no spaces.

**5. Run the server**

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. This page lets you test every endpoint.

## How to use it

Do these in order on the `/docs` page. Click an endpoint, press **Try it out**, fill the input, press **Execute**.

### 1. Check it is running

`GET /health` should return:

```json
{"status": "ok", "redis": "connected"}
```

### 2. Upload a document

`POST /documents/ingest`: choose a `.pdf`, `.txt`, or `.md` file.

Response:

```json
{"filename": "guide.pdf", "chunks": 3}
```

You must upload at least one document before asking questions.

### 3. Ask a question

`POST /chat`

```json
{"session_id": "s2", "message": "What is this document about?"}
```

The answer comes from your document, and `sources` shows which file was used.

### 4. Ask a follow-up (multi-turn)

Use the **same** `session_id`:

```json
{"session_id": "s2", "message": "Explain that in more detail"}
```

The system remembers the previous messages, so "that" is understood.

### 5. Book an interview

Use a session and mention booking. You can give details in any order, across several messages.

Message 1:

```json
{"session_id": "s1", "message": "I want to book an interview, my name is Abhigya"}
```

The system replies asking for the missing details. Message 2:

```json
{"session_id": "s1", "message": "abhigya@example.com, 2026-12-01 at 14:30"}
```

Response: `Interview booked (ID 1) for Abhigya on 2026-12-01 at 14:30:00.`

### 6. See stored bookings

`GET /bookings` returns all saved bookings.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Checks the server and Redis |
| POST | /documents/ingest | Upload a document for RAG |
| POST | /chat | Chat with your documents or book an interview |
| GET | /bookings | List saved bookings |

## How it works

1. **Ingest:** the file text is split into chunks (800 characters, 150 overlap), converted to vectors, and saved in Redis.
2. **Retrieve:** your question is converted to a vector. The 4 most similar chunks are found with cosine similarity (NumPy, written from scratch).
3. **Answer:** the chunks and the chat history are sent to the LLM, which answers using only that context.
4. **Memory:** the last 20 messages per `session_id` are stored in a Redis list and expire after 24 hours.
5. **Booking:** messages containing words like "book", "interview", or "schedule" start the booking flow. The LLM extracts details as JSON. Missing details are asked for, and partial progress is kept in Redis. When all four fields are complete, the booking is saved to SQLite.

## Project structure

```
app/
  main.py            App startup and routers
  api/               REST endpoints (chat, documents)
  core/              Settings and Redis connection
  models/            Pydantic schemas
  services/          LLM client, chunking, embeddings, RAG, booking logic
  repositories/      Redis chat memory, vector store, SQLite bookings
```
## How to write the request body

In `/docs`, click an endpoint, press **Try it out**, edit the **Request body** box, then press **Execute**.

### `POST /chat`

The body is JSON with two required fields:

```json
{
  "session_id": "s1",
  "message": "Explain the uploaded document in simple terms."
}
```

| Field | Type | Meaning |
|---|---|---|
| `session_id` | string | Conversation ID. Use the same one for follow-ups. A new one starts a new conversation. |
| `message` | string | Your question or booking text. |

Rules:
- Use double quotes `"` around every key and value.
- Put a comma between the two fields, but not after the last one.
- The field is `message`, not `query`.

### Booking message

Put the details in `message`. Include the word "book" or "interview":

```json
{
  "session_id": "s2",
  "message": "Book an interview. Name: Abhigya Rai, email: abhigya@example.com, date: 2026-12-01, time: 10:00"
}
```

Use `YYYY-MM-DD` for the date and `HH:MM` (24-hour) for the time.

You can also send the details in parts using the same `session_id`:

```json
{"session_id": "s3", "message": "I want to book an interview, my name is Abhigya"}
```

```json
{"session_id": "s3", "message": "abhigya@example.com, 2026-12-01 at 14:30"}
```

### `POST /documents/ingest`

There is no JSON body. Press **Choose File**, select a `.pdf`, `.txt` or `.md` file, then press **Execute**.

### `GET /health` and `GET /bookings`

No body. Press **Execute**.
