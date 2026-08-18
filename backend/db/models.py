"""NBLM — SQLAlchemy ORM models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

def utcnow():
    return datetime.now(timezone.utc)

def new_uuid():
    return str(uuid.uuid4())

class Notebook(Base):
    __tablename__ = "notebooks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(10), default="📁")
    color: Mapped[str] = mapped_column(String(20), default="#6366f1")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    entries = relationship("Entry", back_populates="notebook", cascade="all, delete-orphan")

class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    notebook_id: Mapped[str] = mapped_column(String(36), ForeignKey("notebooks.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), default="")
    blocks: Mapped[dict] = mapped_column(JSONB, default=list)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    notebook = relationship("Notebook", back_populates="entries")
    attachments = relationship("Attachment", back_populates="entry", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    entry_id: Mapped[str] = mapped_column(String(36), ForeignKey("entries.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    r2_key: Mapped[str] = mapped_column(String(500), default="")
    public_url: Mapped[str] = mapped_column(Text, default="")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    entry = relationship("Entry", back_populates="attachments")

class StoredCredential(Base):
    __tablename__ = "stored_credentials"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="api_key")
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    iv: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AISession(Base):
    __tablename__ = "ai_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    messages: Mapped[list] = mapped_column(JSONB, default=list)
    model_used: Mapped[str] = mapped_column(String(100), default="")
    provider_used: Mapped[str] = mapped_column(String(100), default="")
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class APIProvider(Base):
    __tablename__ = "api_providers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    api_protocol: Mapped[str] = mapped_column(String(50), default="openai-completions")
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    iv: Mapped[str] = mapped_column(String(32), nullable=False)
    chat_model: Mapped[str] = mapped_column(String(255), default="")
    vision_model: Mapped[str] = mapped_column(String(255), default="")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), default="")
    entity_id: Mapped[str] = mapped_column(String(36), default="")
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
