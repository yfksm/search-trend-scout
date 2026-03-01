from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.domain import Item, UserState

router = APIRouter()


async def get_or_create_state(db: AsyncSession, item_id: UUID) -> UserState:
    # Verify item exists
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    q = select(UserState).filter(UserState.item_id == item_id)
    result = await db.execute(q)
    state = result.scalar_one_or_none()

    if not state:
        state = UserState(item_id=item_id)
        db.add(state)

    return state


@router.post("/items/{id}/read")
async def mark_read(id: UUID, db: AsyncSession = Depends(get_db)):
    state = await get_or_create_state(db, id)
    state.read_at = datetime.utcnow()
    await db.commit()
    return {"status": "ok"}


@router.post("/items/{id}/bookmark")
async def add_bookmark(id: UUID, db: AsyncSession = Depends(get_db)):
    state = await get_or_create_state(db, id)
    state.bookmarked_at = datetime.utcnow()
    await db.commit()
    return {"status": "ok"}


@router.delete("/items/{id}/bookmark")
async def remove_bookmark(id: UUID, db: AsyncSession = Depends(get_db)):
    state = await get_or_create_state(db, id)
    state.bookmarked_at = None
    await db.commit()
    return {"status": "ok"}


@router.post("/items/{id}/hide")
async def hide_item(id: UUID, db: AsyncSession = Depends(get_db)):
    state = await get_or_create_state(db, id)
    state.hidden_at = datetime.utcnow()
    await db.commit()
    return {"status": "ok"}
