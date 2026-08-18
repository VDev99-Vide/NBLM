"""NBLM — File upload + Vision analysis endpoint."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.engine import get_db
from backend.services.r2 import upload_file
from backend.services.api_rotator import call_llm

router = APIRouter()

@router.post("/api/upload")
async def upload(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    data = await file.read()
    if len(data) > 10_000_000:
        raise HTTPException(413, "File quá lớn (max 10MB)")
    result = await upload_file(data, file.filename, file.content_type)
    return {"ok": True, **result}

@router.post("/api/vision")
async def vision(body: dict, db: AsyncSession = Depends(get_db)):
    image_url = body.get("image_url", "")
    prompt = body.get("prompt", "Mô tả chi tiết nội dung ảnh này bằng tiếng Việt.")
    if not image_url:
        raise HTTPException(400, "Thiếu image_url")
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}
    ]
    result = await call_llm(db, messages, use_vision=True)
    return {"ok": True, "description": result.get("content", ""), "model_used": result.get("model_used")}
