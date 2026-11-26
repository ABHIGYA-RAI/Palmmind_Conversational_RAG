import hashlib
import re
from typing import Protocol
import numpy as np
DIMS = 512

class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class LocalHashEmbedder:
    """Offline bag-of-words hashing embedder. No API calls."""

    def _vec(self, text: str) -> list[float]:
        v = np.zeros(DIMS, dtype=np.float32)
        for tok in re.findall(r"\w+", text.lower()):
            idx = int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIMS
            v[idx] += 1.0
        norm = float(np.linalg.norm(v))
        return (v / norm if norm else v).tolist()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]


embedder: Embedder = LocalHashEmbedder()