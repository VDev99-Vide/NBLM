"""NBLM — Context Manager (Component 2 of 9)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models import Entry

SYSTEM_PROMPT = """Bạn là Quản Gia AI của NBLM — trợ lý cá nhân thông minh.
Nhiệm vụ: giúp anh quản lý và tra cứu dữ liệu trong notebook cá nhân.
Luôn dùng tools để tìm kiếm/thao tác dữ liệu, KHÔNG bịa thông tin.
Gọi người dùng là "anh", trả lời tiếng Việt ngắn gọn."""

class ContextManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_messages(self, user_msg: str, history: list = None) -> list:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Recent entries as context
        stmt = select(Entry).order_by(Entry.updated_at.desc()).limit(5)
        result = await self.db.execute(stmt)
        entries = result.scalars().all()
        if entries:
            ctx = "\n".join([f"- {e.title} (tags: {','.join(e.tags or [])})" for e in entries])
            msgs.append({"role": "system", "content": f"Dữ liệu gần đây:\n{ctx}"})
        if history:
            for h in history[-16:]:
                msgs.append({"role": h.get("role","user"), "content": h.get("content","")})
        msgs.append({"role": "user", "content": user_msg})
        return msgs
