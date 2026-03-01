from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

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
    published_at: Optional[datetime]
    site: Optional[str]
    why_important: Optional[str]
    score: float
    lane: Optional[str]
    
    tags: List[TagSchema] = []
    source: Optional[SourceSchema] = None
    
    # Computed user states
    is_read: bool = False
    is_bookmarked: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class ItemDetail(ItemBase):
    summary_tldr: Optional[str] = None
    summary_bullets: Optional[List[str]] = None
    tradeoffs: Optional[str] = None
    content_text: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class FeedResponse(BaseModel):
    items: List[ItemBase]
    total: int
    page: int
    size: int
