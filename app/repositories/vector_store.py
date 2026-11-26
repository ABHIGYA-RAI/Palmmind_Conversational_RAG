import json
import uuid

import numpy as np
from redis.asyncio import Redis

from app.core.redis import redis_client

INDEX_KEY = "vs:index"


class VectorStore:
    def __init__(self, redis: Redis) -> None:
        self._r = redis

    async def add(self, source: str, chunks: list[str], vectors: list[list[float]]) -> None:
        pipe = self._r.pipeline()
        for text, vec in zip(chunks, vectors):
            key = f"vs:chunk:{uuid.uuid4().hex}"
            pipe.set(key, json.dumps({"source": source, "text": text, "vec": vec}))
            pipe.sadd(INDEX_KEY, key)
        await pipe.execute()

    async def search(self, query_vec: list[float], top_k: int = 4) -> list[dict[str, str | float]]:
        keys = list(await self._r.smembers(INDEX_KEY))
        if not keys:
            return []
        raw = await self._r.mget(keys)
        items = [json.loads(r) for r in raw if r]
        mat = np.array([i["vec"] for i in items], dtype=np.float32)
        q = np.array(query_vec, dtype=np.float32)
        scores = mat @ q / (np.linalg.norm(mat, axis=1) * np.linalg.norm(q) + 1e-9)
        top = np.argsort(scores)[::-1][:top_k]
        return [
            {"source": items[i]["source"], "text": items[i]["text"], "score": float(scores[i])}
            for i in top
        ]


vector_store = VectorStore(redis_client)