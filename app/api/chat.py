from fastapi import APIRouter

from app.models.schemas import BookingRecord, ChatRequest, ChatResponse
from app.repositories import booking_repo
from app.services import rag

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    reply, sources = await rag.answer(req.session_id, req.message)
    return ChatResponse(session_id=req.session_id, answer=reply, sources=sources)


@router.get("/bookings", response_model=list[BookingRecord])
async def bookings() -> list[BookingRecord]:
    return await booking_repo.list_bookings()