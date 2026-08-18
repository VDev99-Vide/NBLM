"""NBLM — FastAPI Application Entry Point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config import settings
from backend.db.engine import get_db
from backend.harness.loop import AgentLoop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nblm")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"NBLM starting on port {settings.APP_PORT}")
    yield
    logger.info("NBLM shutting down")

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])

@app.post("/api/chat")
async def chat(body: dict, db: AsyncSession = Depends(get_db)):
    msg = body.get("message","")
    if not msg: raise HTTPException(400, "Missing message")
    loop = AgentLoop(db)
    result = await loop.run(msg, body.get("history"))
    return {"ok": True, **result}

@app.get("/api/notebooks")
async def list_notebooks(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from backend.db.models import Notebook
    r = await db.execute(select(Notebook).order_by(Notebook.sort_order))
    return [{"id":n.id,"name":n.name,"icon":n.icon,"color":n.color} for n in r.scalars().all()]

@app.get("/api/entries")
async def list_entries(notebook_id: str = None, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from backend.db.models import Entry
    stmt = select(Entry)
    if notebook_id: stmt = stmt.where(Entry.notebook_id == notebook_id)
    stmt = stmt.order_by(Entry.updated_at.desc()).limit(100)
    r = await db.execute(stmt)
    return [{"id":e.id,"title":e.title,"tags":e.tags or [],"is_pinned":e.is_pinned} for e in r.scalars().all()]

@app.get("/api/health")
async def health():
    return {"status":"ok","app":settings.APP_NAME}
