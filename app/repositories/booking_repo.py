from pathlib import Path
import aiosqlite
from app.core.config import settings
from app.models.schemas import BookingDetails, BookingRecord

DB_PATH = settings.database_url.split("///")[-1]


async def init_db() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS bookings ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, "
            "name TEXT NOT NULL, email TEXT NOT NULL, date TEXT NOT NULL, time TEXT NOT NULL)"
        )
        await db.commit()


async def save_booking(session_id: str, b: BookingDetails) -> BookingRecord:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO bookings (session_id, name, email, date, time) VALUES (?, ?, ?, ?, ?)",
            (session_id, b.name, b.email, b.date.isoformat(), b.time.isoformat()),
        )
        await db.commit()
        return BookingRecord(id=cur.lastrowid or 0, session_id=session_id, **b.model_dump())


async def list_bookings() -> list[BookingRecord]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, session_id, name, email, date, time FROM bookings")
        rows = await cur.fetchall()
    return [
        BookingRecord(id=r[0], session_id=r[1], name=r[2], email=r[3], date=r[4], time=r[5])
        for r in rows
    ]