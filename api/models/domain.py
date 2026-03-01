import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base


class SourceType(enum.StrEnum):
    rss = "rss"
    url = "url"
    arxiv = "arxiv"
    connpass_api = "connpass_api"


class LaneType(enum.StrEnum):
    research = "research"
    practice = "practice"
    ecosystem = "ecosystem"


# Association table for Item <-> Tag many-to-many relationship
item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(SourceType), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    enabled = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("Item", back_populates="source", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=True)
    url = Column(String, nullable=False, unique=True)
    canonical_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    site = Column(String, nullable=True)
    author = Column(String, nullable=True)
    language = Column(String, nullable=True)

    # Content
    content_text = Column(Text, nullable=True)
    summary_tldr = Column(Text, nullable=True)
    summary_bullets = Column(JSONB, nullable=True)  # List of strings
    why_important = Column(Text, nullable=True)
    tradeoffs = Column(Text, nullable=True)
    lane = Column(Enum(LaneType), nullable=True)

    # Scoring
    score = Column(Float, default=0.0)
    hash = Column(String, nullable=True)

    # Relationships
    source = relationship("Source", back_populates="items")
    tags = relationship("Tag", secondary=item_tags, back_populates="items")
    user_states = relationship("UserState", back_populates="item", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)

    items = relationship("Item", secondary=item_tags, back_populates="tags")


class UserState(Base):
    __tablename__ = "user_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"))
    read_at = Column(DateTime, nullable=True)
    bookmarked_at = Column(DateTime, nullable=True)
    hidden_at = Column(DateTime, nullable=True)

    item = relationship("Item", back_populates="user_states")


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_started_at = Column(DateTime, default=datetime.utcnow)
    run_ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="running")  # "running", "completed", "failed"
    items_processed = Column(Integer, default=0)
    items_added = Column(Integer, default=0)
    errors = Column(Integer, default=0)
