"""NBLM — Multi-provider API Rotator with auto-fallback."""
import json
from datetime import datetime, timezone, timedelta
import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config import settings
from backend.db.models import APIProvider
from backend.services.crypto import decrypt_value

COOLDOWN_MINUTES = 5
MAX_RETRIES = 3

class RotatorError(Exception):
    def __init__(self, message: str, code: str = "rotator_error"):
        super().__init__(message)
        self.code = code

async def _get_active_providers(db: AsyncSession) -> list[dict]:
    now = datetime.now(timezone.utc)
    stmt = select(APIProvider).where(APIProvider.is_active == True).order_by(APIProvider.priority.desc())
    result = await db.execute(stmt)
    providers = []
    for row in result.scalars():
        if row.cooldown_until and row.cooldown_until > now:
            continue
        try:
            api_key = decrypt_value(row.encrypted_api_key, row.iv)
        except Exception:
            continue
        providers.append({"id": row.id, "name": row.name, "base_url": row.base_url,
            "api_key": api_key, "chat_model": row.chat_model, "vision_model": row.vision_model})
    return providers

async def _cooldown_provider(db: AsyncSession, provider_id: str):
    until = datetime.now(timezone.utc) + timedelta(minutes=COOLDOWN_MINUTES)
    stmt = update(APIProvider).where(APIProvider.id == provider_id).values(
        cooldown_until=until, error_count=APIProvider.error_count + 1)
    await db.execute(stmt)
    await db.commit()

async def call_llm(db: AsyncSession, messages: list[dict], *, role: str = "chat",
        temperature: float = 0.3, max_tokens: int = 4096, response_format: dict | None = None) -> dict:
    providers = await _get_active_providers(db)
    if not providers:
        if not settings.XKIRO_API_KEY:
            raise RotatorError("No active providers and no XKIRO_API_KEY")
        providers = [{"id": "env", "name": "xkiro-env", "base_url": settings.XKIRO_BASE_URL,
            "api_key": settings.XKIRO_API_KEY, "chat_model": settings.XKIRO_CHAT_MODEL,
            "vision_model": settings.XKIRO_VISION_MODEL}]
    last_error = None
    for attempt in range(MAX_RETRIES):
        for p in providers:
            model = p.get("vision_model" if role == "vision" else "chat_model")
            if not model: continue
            try:
                url = f"{p['base_url'].rstrip('/')}/chat/completions"
                payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
                if response_format: payload["response_format"] = response_format
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(url, json=payload, headers={"Authorization": f"Bearer {p['api_key']}"})
                    resp.raise_for_status()
                    data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                result = {"content": content}
                if response_format and response_format.get("type") == "json_object":
                    try: result["json"] = json.loads(content)
                    except json.JSONDecodeError: result["json"] = None
                return {**result, "model_used": model, "provider_used": p["name"]}
            except Exception as e:
                last_error = e
                if p["id"] != "env": await _cooldown_provider(db, p["id"])
    raise RotatorError(f"All providers failed: {last_error}")
