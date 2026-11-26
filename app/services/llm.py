import asyncio

import httpx

from app.core.config import settings

MAX_RETRIES = 4


class LLMClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.llm_base_url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=httpx.Timeout(60.0, connect=15.0),
        )

    async def chat(self, messages: list[dict[str, str]], json_mode: bool = False) -> str:
        payload: dict[str, object] = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": 0.2,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        for attempt in range(MAX_RETRIES):
            resp = await self._client.post("/chat/completions", json=payload)
            if resp.status_code in (429, 503):
                await asyncio.sleep(2**attempt)
                continue
            break
        if resp.is_error:
            raise RuntimeError(f"LLM error {resp.status_code}: {resp.text}")
        return str(resp.json()["choices"][0]["message"]["content"])


llm_client = LLMClient()