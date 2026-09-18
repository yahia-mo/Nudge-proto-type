from fastapi import FastAPI
from src.api.routes.sessions import router as sessions_router

from src.core.database import init_db

app = FastAPI(title="NUDGE API")
app.include_router(sessions_router)

init_db()


@app.get("/")
def root():
    return {"message": "NUDGE API is running"}