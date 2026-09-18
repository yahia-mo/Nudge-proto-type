from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from ...core.database import engine
from ...services.learning import LearningService

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


class StartSessionRequest(BaseModel):
    topic: str
    level: str = "beginner"
    available_time: int = 1


class AnswerRequest(BaseModel):
    question_id: int
    selected_answer: str


@router.post("/start")
def start_session(request: StartSessionRequest):
    try:
        with Session(engine) as db:
            return LearningService.create_session(
                db=db,
                topic=request.topic,
                level=request.level,
                available_time=request.available_time,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/questions")
def get_questions(session_id: str):
    try:
        with Session(engine) as db:
            return LearningService.get_or_generate_questions(
                db=db,
                session_id=session_id,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/answer")
def submit_answer(session_id: str, request: AnswerRequest):
    try:
        with Session(engine) as db:
            return LearningService.submit_answer(
                db=db,
                session_id=session_id,
                question_id=request.question_id,
                selected_answer=request.selected_answer,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/next")
def next_part(session_id: str):
    try:
        with Session(engine) as db:
            return LearningService.generate_next_part(
                db=db,
                session_id=session_id,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
