from datetime import date, time
from pydantic import BaseModel, EmailStr, Field

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[str] = []


class BookingDetails(BaseModel):
    name: str
    email: EmailStr
    date: date
    time: time


class BookingRecord(BookingDetails):
    id: int
    session_id: str


class IngestResponse(BaseModel):
    filename: str
    chunks: int