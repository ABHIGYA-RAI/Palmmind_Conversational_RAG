from app.repositories.chat_memory import chat_memory
from app.repositories.vector_store import vector_store
from app.services import booking
from app.services.embeddings import embedder
from app.services.llm import llm_client

TOP_K = 4
SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer using only the provided context. "
    "If the answer is not in the context, say you don't know."
)


async def _remember(session_id: str, message: str, reply: str) -> None:
    """Save one user/assistant exchange to Redis chat memory."""
    await chat_memory.add(session_id, "user", message)
    await chat_memory.add(session_id, "assistant", reply)


async def _rag_answer(session_id: str, message: str) -> tuple[str, list[str]]:
    """Retrieve relevant chunks and answer using them plus the chat history."""
    history = await chat_memory.get(session_id)
    query_vec = (await embedder.embed([message]))[0]
    hits = await vector_store.search(query_vec, top_k=TOP_K)
    context = "\n\n".join(str(h["text"]) for h in hits)
    sources = sorted({str(h["source"]) for h in hits})

    messages: list[dict[str, str]] = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context}"},
        *history,
        {"role": "user", "content": message},
    ]
    reply = await llm_client.chat(messages)
    await _remember(session_id, message, reply)
    return reply, sources


async def answer(session_id: str, message: str) -> tuple[str, list[str]]:
    """Route the message to the booking flow or to RAG."""
    if await booking.has_active_booking(session_id) or booking.is_booking_intent(message):
        reply = await booking.handle(session_id, message)
        await _remember(session_id, message, reply)
        return reply, []
    return await _rag_answer(session_id, message)