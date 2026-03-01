import uuid
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, nullslast, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db import get_db
from models.domain import Item, LaneType, Tag, UserState
from models.schemas import FeedResponse, ItemBase, ItemDetail, TagSchema

router = APIRouter()


def build_query(
    base_query, range_days: int | None, lane: str | None, tag_id_or_name: str | None, q: str | None
):
    query = base_query

    if range_days:
        cutoff = datetime.utcnow() - timedelta(days=range_days)
        query = query.filter(Item.published_at >= cutoff)

    if lane:
        try:
            lane_eval = LaneType(lane)
            query = query.filter(Item.lane == lane_eval)
        except ValueError:
            pass  # ignore invalid lane

    if tag_id_or_name:
        try:
            # Check if it's a valid UUID
            tag_uuid = uuid.UUID(tag_id_or_name)
            query = query.filter(Item.tags.any(Tag.id == tag_uuid))
        except ValueError:
            # It's a string tag name like "event"
            query = query.filter(Item.tags.any(Tag.name == tag_id_or_name.lower()))

    if q:
        query = query.filter(Item.title.ilike(f"%{q}%") | Item.content_text.ilike(f"%{q}%"))

    return query


def enhance_items_with_state(items: list[Item], states: list[UserState]) -> list[ItemBase]:
    state_map = {state.item_id: state for state in states}
    res = []

    for item in items:
        base = ItemBase.model_validate(item)
        if item.lane:
            base.lane = item.lane.value

        state = state_map.get(item.id)
        if state:
            base.is_read = state.read_at is not None
            base.is_bookmarked = state.bookmarked_at is not None
        res.append(base)

    return res


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    range: int | None = Query(7, description="Days to go back"),
    lane: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * size

    # Hide items user has explicitly hidden
    hidden_subq = select(UserState.item_id).filter(UserState.hidden_at.isnot(None))

    base_q = (
        select(Item).options(selectinload(Item.source), selectinload(Item.tags)).filter(Item.id.notin_(hidden_subq))
    )
    base_q = build_query(base_q, range, lane, tag, q)

    # Count total
    count_q = select(func.count()).select_from(base_q.subquery())
    total = await db.scalar(count_q)

    # Fetch paginated items, ordered by score descending then published_at
    items_q = base_q.order_by(desc(Item.score), nullslast(desc(Item.published_at))).offset(offset).limit(size)
    result = await db.execute(items_q)
    items = result.scalars().all()

    # Fetch user states for these items
    item_ids = [i.id for i in items]
    states_q = select(UserState).filter(UserState.item_id.in_(item_ids))
    states_res = await db.execute(states_q)
    states = states_res.scalars().all()

    return FeedResponse(items=enhance_items_with_state(items, states), total=total, page=page, size=size)


@router.get("/items/{id}", response_model=ItemDetail)
async def get_item(id: UUID, db: AsyncSession = Depends(get_db)):
    q = select(Item).options(selectinload(Item.source), selectinload(Item.tags)).filter(Item.id == id)
    result = await db.execute(q)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Get user state
    sq = select(UserState).filter(UserState.item_id == id)
    sr = await db.execute(sq)
    state = sr.scalar_one_or_none()

    detail = ItemDetail.model_validate(item)
    if item.lane:
        detail.lane = item.lane.value

    if state:
        detail.is_read = state.read_at is not None
        detail.is_bookmarked = state.bookmarked_at is not None

    return detail


@router.get("/tags", response_model=list[TagSchema])
async def get_tags(db: AsyncSession = Depends(get_db)):
    # Optional: order by popularity, for now just alphabetical
    q = select(Tag).order_by(Tag.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/bookmarks", response_model=list[ItemBase])
async def get_bookmarks(db: AsyncSession = Depends(get_db)):
    q = (
        select(Item)
        .join(UserState, Item.id == UserState.item_id)
        .options(selectinload(Item.source), selectinload(Item.tags))
        .filter(UserState.bookmarked_at.isnot(None))
        .order_by(desc(UserState.bookmarked_at))
    )

    result = await db.execute(q)
    items = result.scalars().all()

    # Get user states
    item_ids = [i.id for i in items]
    if not item_ids:
        return []

    states_q = select(UserState).filter(UserState.item_id.in_(item_ids))
    states_res = await db.execute(states_q)
    states = states_res.scalars().all()

    return enhance_items_with_state(items, states)
