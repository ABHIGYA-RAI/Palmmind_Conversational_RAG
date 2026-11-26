import json
from redis.asyncio import Redis
from app.core.redis import redis_client
MAX_MESSAGES = 20
TTL_SECONDS = 86400


class ChatMemory:
    def __init__(self, redis: Redis) -> None:
        self._r = redis

    @staticmethod
    def _key(session_id: str) -> str:
        return f"chat:{session_id}"

    async def add(self, session_id: str, role: str, content: str) -> None:
        key = self._key(session_id)
        await self._r.rpush(key, json.dumps({"role": role, "content": content}))
        await self._r.ltrim(key, -MAX_MESSAGES, -1)
        await self._r.expire(key, TTL_SECONDS)

    async def get(self, session_id: str) -> list[dict[str, str]]:
        raw = await self._r.lrange(self._key(session_id), 0, -1)
        return [json.loads(r) for r in raw]


chat_memory = ChatMemory(redis_client)