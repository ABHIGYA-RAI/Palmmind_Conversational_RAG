from datetime import date, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"session_id": "s1", "message": "What is this document about?"},
                {
                    "session_id": "s2",
                    "message": "Book an interview. Name: Abhigya Rai, "
                    "email: abhigya@example.com, date: 2026-12-01, time: 10:00",
                },
            ]
        }
    )

    session_id: str = Field(min_length=1, description="Conversation ID. Reuse it for follow-ups.")
    message: str = Field(min_length=1, description="The user's message.")


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