from app.repositories.chat_memory import chat_memory
from app.repositories.vector_store import vector_store
from app.services import booking
from app.services.embeddings import embedder
from app.services.llm import llm_client

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer using only the provided context. "
    "If the answer is not in the context, say you don't know."
)


async def answer(session_id: str, message: str) -> tuple[str, list[str]]:
    if await booking.has_active_booking(session_id) or booking.is_booking_intent(message):
        reply = await booking.handle(session_id, message)
        await chat_memory.add(session_id, "user", message)
        await chat_memory.add(session_id, "assistant", reply)
        return reply, []

    history = await chat_memory.get(session_id)
    query_vec = (await embedder.embed([message]))[0]
    hits = await vector_store.search(query_vec, top_k=4)
    context = "\n\n".join(str(h["text"]) for h in hits)
    sources = sorted({str(h["source"]) for h in hits})

    messages: list[dict[str, str]] = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context}"},
        *history,
        {"role": "user", "content": message},
    ]
    reply = await llm_client.chat(messages)
    await chat_memory.add(session_id, "user", message)
    await chat_memory.add(session_id, "assistant", reply)
    return reply, sources