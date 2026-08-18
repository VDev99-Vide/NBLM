"""NBLM — Cloudflare R2 storage service."""
import uuid
from datetime import datetime, timezone
import boto3
from botocore.config import Config as BotoConfig
from backend.config import settings

def _client():
    return boto3.client("s3", endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.CF_R2_ACCESS_KEY,
        aws_secret_access_key=settings.CF_R2_SECRET_KEY,
        config=BotoConfig(signature_version="s3v4"), region_name="auto")

async def upload_file(data: bytes, filename: str, content_type: str) -> dict:
    c = _client()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    key = f"uploads/{datetime.now(timezone.utc):%Y/%m/%d}/{uuid.uuid4().hex[:12]}.{ext}"
    c.put_object(Bucket=settings.CF_R2_BUCKET, Key=key, Body=data, ContentType=content_type)
    url = f"{settings.CF_R2_PUBLIC_URL}/{key}" if settings.CF_R2_PUBLIC_URL else None
    return {"r2_key": key, "public_url": url, "size_bytes": len(data)}

async def delete_file(r2_key: str):
    _client().delete_object(Bucket=settings.CF_R2_BUCKET, Key=r2_key)

async def get_presigned_url(r2_key: str, expires: int = 3600) -> str:
    return _client().generate_presigned_url("get_object",
        Params={"Bucket": settings.CF_R2_BUCKET, "Key": r2_key}, ExpiresIn=expires)
