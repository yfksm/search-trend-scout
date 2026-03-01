from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TagSchema(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)


class SourceSchema(BaseModel):
    id: UUID
    name: str
    url: str
    model_config = ConfigDict(from_attributes=True)


class ItemBase(BaseModel):
    id: UUID
    title: str
    url: str
    published_at: datetime | None
    site: str | None
    why_important: str | None
    score: float
    lane: str | None

    tags: list[TagSchema] = []
    source: SourceSchema | None = None

    # Computed user states
    is_read: bool = False
    is_bookmarked: bool = False

    model_config = ConfigDict(from_attributes=True)


class ItemDetail(ItemBase):
    summary_tldr: str | None = None
    summary_bullets: list[str] | None = None
    tradeoffs: str | None = None
    content_text: str | None = None

    model_config = ConfigDict(from_attributes=True)


class FeedResponse(BaseModel):
    items: list[ItemBase]
    total: int
    page: int
    size: int
