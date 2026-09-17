import json
import uuid
from typing import Any

from sqlmodel import Session

from ..db import repository
from ..db.models import Question
from ..llm.client import get_llm_client
from ..llm.generate import generate_parsed
from ..llm.prompts import (
    MICRO_LESSON_FALLBACK_SYSTEM as MICRO_LESSON_FALLBACK,
)
from ..llm.prompts import (
    QUIZ_FALLBACK_SYSTEM as QUIZ_FALLBACK,
)
from ..llm.prompts import (
    build_intro_prompt,
    build_next_part_prompt,
    build_quiz_prompt,
)
from ..llm.schemas import MicroLessonSchema, QuizSchema


class LearningService:
    @staticmethod
    def create_session(
        db: Session, topic: str, level: str = "beginner", api_key: str | None = None
    ) -> dict[str, Any]:
        """Creates a new study session and generates Part 1 using the LLM."""
        study_session = repository.create_study_session(db, topic, level)

        prompt = build_intro_prompt(topic, level)
        client = get_llm_client(api_key)
        data = generate_parsed(
            client, prompt, MicroLessonSchema, temperature=0.6, fallback_system=MICRO_LESSON_FALLBACK
        )

        part = repository.add_lesson_part(db, study_session.id, 1, data.title, data.content)

        return {
            "session_id": str(study_session.id),
            "current_part": 1,
            "title": part.title,
            "content": part.content,
        }

    @staticmethod
    def get_or_generate_questions(
        db: Session, session_id: uuid.UUID | str, api_key: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetches existing questions or generates 2 verification questions for the current part."""
        study_session = repository.get_study_session(db, session_id)
        if not study_session:
            raise ValueError(f"Session with ID {session_id} not found.")

        existing_questions = repository.get_questions(
            db, session_id, study_session.current_part
        )
        if existing_questions:
            return [_serialize_question(q) for q in existing_questions]

        current_part = repository.get_lesson_part(
            db, session_id, study_session.current_part
        )
        if not current_part:
            raise ValueError(f"Lesson part {study_session.current_part} not found.")

        prompt = build_quiz_prompt(current_part.content)
        client = get_llm_client(api_key)
        quiz = generate_parsed(
            client, prompt, QuizSchema, temperature=0.4, fallback_system=QUIZ_FALLBACK
        )

        saved_questions = repository.save_questions(
            db, session_id, study_session.current_part, quiz.questions
        )
        return [_serialize_question(q) for q in saved_questions]

    @staticmethod
    def generate_next_part(
        db: Session, session_id: uuid.UUID | str, api_key: str | None = None
    ) -> dict[str, Any]:
        """Generates the next logical micro-step preserving previous conversational context."""
        study_session = repository.get_study_session(db, session_id)
        if not study_session:
            raise ValueError(f"Session with ID {session_id} not found.")

        history = repository.get_parts_history(db, session_id)
        history_summary = "\n".join(
            [f"Part {p.part_number}: {p.title} - {p.content}" for p in history]
        )

        next_part_num = study_session.current_part + 1

        prompt = build_next_part_prompt(
            study_session.topic, study_session.level, history_summary, next_part_num
        )
        client = get_llm_client(api_key)
        data = generate_parsed(
            client, prompt, MicroLessonSchema, temperature=0.6, fallback_system=MICRO_LESSON_FALLBACK
        )

        part = repository.add_lesson_part(db, study_session.id, next_part_num, data.title, data.content)
        repository.set_current_part(db, study_session, next_part_num)

        return {
            "session_id": str(study_session.id),
            "current_part": next_part_num,
            "title": part.title,
            "content": part.content,
        }


def _serialize_question(q: Question) -> dict[str, Any]:
    return {
        "question": q.question_text,
        "options": json.loads(q.options_json),
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
    }