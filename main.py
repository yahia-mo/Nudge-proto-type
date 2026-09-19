from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.sessions import router as sessions_router
from src.core.database import init_db

app = FastAPI(title="NUDGE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)

init_db()


@app.get("/")
def root():
    return {"message": "NUDGE API is running"}