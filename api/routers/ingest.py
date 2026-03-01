from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from services.ingestion import run_ingestion_task, INGESTION_STATUS

router = APIRouter()

class StatusResponse(BaseModel):
    is_running: bool
    last_run: str | None
    items_processed: int
    errors: int


@router.post("/run")
async def trigger_ingest(background_tasks: BackgroundTasks):
    if INGESTION_STATUS["is_running"]:
        return {"status": "already_running"}
        
    background_tasks.add_task(run_ingestion_task)
    return {"status": "started"}


@router.get("/status", response_model=StatusResponse)
async def get_status():
    return INGESTION_STATUS
