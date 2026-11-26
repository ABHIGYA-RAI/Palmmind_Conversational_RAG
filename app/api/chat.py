import httpx
from fastapi import APIRouter, HTTPException
from app.models.schemas import BookingRecord, ChatRequest, ChatResponse
from app.repositories import booking_repo
from app.services import rag

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Answer a message from documents, or continue an interview booking."""
    try:
        reply, sources = await rag.answer(req.session_id, req.message)
    except (RuntimeError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=f"LLM service error: {exc}") from exc
    return ChatResponse(session_id=req.session_id, answer=reply, sources=sources)


@router.get("/bookings", response_model=list[BookingRecord])
async def bookings() -> list[BookingRecord]:
    """List all stored interview bookings."""
    return await booking_repo.list_bookings()