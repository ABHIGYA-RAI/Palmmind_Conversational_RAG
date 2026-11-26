import json
from datetime import date

from pydantic import ValidationError

from app.core.redis import redis_client
from app.models.schemas import BookingDetails
from app.repositories import booking_repo
from app.services.llm import llm_client

FIELDS = ("name", "email", "date", "time")
KEYWORDS = ("book", "interview", "schedule", "appointment")


def _key(session_id: str) -> str:
    return f"booking:{session_id}"


def is_booking_intent(message: str) -> bool:
    return any(k in message.lower() for k in KEYWORDS)


async def has_active_booking(session_id: str) -> bool:
    return bool(await redis_client.exists(_key(session_id)))


async def _extract(message: str, known: dict[str, str]) -> dict[str, str]:
    prompt = (
        f"Today is {date.today().isoformat()}. Extract interview booking details from the "
        "user message. Return JSON with keys: name, email, date (YYYY-MM-DD), "
        "time (HH:MM, 24h). Use null for anything not provided. "
        f"Already known: {json.dumps(known)}"
    )
    raw = await llm_client.chat(
        [{"role": "system", "content": prompt}, {"role": "user", "content": message}],
        json_mode=True,
    )
    data: dict[str, object] = json.loads(raw)
    return {k: str(data[k]) for k in FIELDS if data.get(k)}


async def handle(session_id: str, message: str) -> str:
    key = _key(session_id)
    raw = await redis_client.get(key)
    known: dict[str, str] = json.loads(raw) if raw else {}
    known.update(await _extract(message, known))

    missing = [f for f in FIELDS if f not in known]
    if missing:
        await redis_client.set(key, json.dumps(known), ex=3600)
        return f"To book your interview, please provide your {', '.join(missing)}."

    try:
        details = BookingDetails(**known)  # type: ignore[arg-type]
    except ValidationError:
        await redis_client.delete(key)
        return "Some details were invalid. Please send your name, email, date and time again."

    record = await booking_repo.save_booking(session_id, details)
    await redis_client.delete(key)
    return f"Interview booked (ID {record.id}) for {record.name} on {record.date} at {record.time}."