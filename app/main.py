from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.core.redis import redis_client
from app.repositories import booking_repo


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await booking_repo.init_db()
    yield


app = FastAPI(title="RAG Booking API", lifespan=lifespan)
app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
async def health() -> dict[str, str]:
    await redis_client.ping()
    return {"status": "ok", "redis": "connected"}