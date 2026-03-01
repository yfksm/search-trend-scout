from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.domain import IngestionRun
from services.ingestion import run_ingestion_task

router = APIRouter()


class StatusResponse(BaseModel):
    is_running: bool
    last_run: str | None
    items_processed: int
    errors: int


@router.post("/run")
async def trigger_ingest(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    active_q = select(IngestionRun).filter(IngestionRun.status == "running")
    res = await db.execute(active_q)
    if res.scalar_one_or_none():
        return {"status": "already_running"}

    background_tasks.add_task(run_ingestion_task)
    return {"status": "started"}


@router.get("/status", response_model=StatusResponse)
async def get_status(db: AsyncSession = Depends(get_db)):
    # Check if running
    active_q = select(IngestionRun).filter(IngestionRun.status == "running")
    active_res = await db.execute(active_q)
    is_running = active_res.scalar_one_or_none() is not None

    # Get last run info
    last_q = select(IngestionRun).order_by(desc(IngestionRun.run_started_at)).limit(1)
    last_res = await db.execute(last_q)
    last_run = last_res.scalar_one_or_none()

    if not last_run:
        return StatusResponse(
            is_running=False,
            last_run=None,
            items_processed=0,
            errors=0
        )

    return StatusResponse(
        is_running=is_running,
        last_run=last_run.run_started_at.isoformat() if last_run.run_started_at else None,
        items_processed=last_run.items_processed,
        errors=last_run.errors
    )
