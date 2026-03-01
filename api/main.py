from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from routers import read, mutate, ingest

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(read.router, prefix="/api", tags=["read"])
app.include_router(mutate.router, prefix="/api", tags=["mutate"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])

@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
