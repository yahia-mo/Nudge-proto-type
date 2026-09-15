import json
import os
import uuid
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from .database import LessonPart, Question, StudySession

DEFAULT_MODEL = "qwen/qwen3.8-27b"


#  Pydantic Schemas for Structured Model Outputs .
class MicroLessonSchema(BaseModel):
    title: str = Field(description="Short title representing the micro-concept")
    content: str = Field(
        description="Concise, friction-reducing pedagogical explanation under 80 words"
    )


class QuestionItemSchema(BaseModel):
    question_text: str
    options: list[str] = Field(
        description="Array containing four distinct options, e.g., ['A) Option', 'B) Option', ...]"
    )
    correct_answer: str = Field(
        description="Identifier of the correct option, e.g., 'A'"
    )
    explanation: str = Field(
        description="Concise justification for why this answer is correct"
    )


class QuizSchema(BaseModel):
    questions: list[QuestionItemSchema]


def get_llm_client(api_key: str | None = None) -> OpenAI:
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not configured in the environment or request payload.")
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)


class LearningService:
    @staticmethod
    def create_session(
        db: Session, topic: str, level: str = "beginner", api_key: str | None = None
    ) -> dict[str, Any]:
        """Creates a new study session and generates Part 1 using the LLM."""
        new_session = StudySession(topic=topic, level=level, current_part=1)
        # put into database FIRST .
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        client = get_llm_client(api_key)
        prompt = (
            f"You are an empathetic, anti-procrastination tutor. "
            f"Explain the absolute FIRST, most fundamental micro-concept of: '{topic}' for a '{level}' level learner. "
            f"Keep it extremely low-friction and under 80 words."
        )

        try:
            completion = client.beta.chat.completions.parse(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format=MicroLessonSchema,
                temperature=0.6,
            )
            data = completion.choices[0].message.parsed
            if not data:
                raise ValueError("Parsed output returned None.")
        except Exception:
            raw_res = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": 'Output strictly valid JSON matching: {"title": "...", "content": "..."}',
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.6,
            )
            content_str = raw_res.choices[0].message.content or "{}"
            data = MicroLessonSchema(**json.loads(content_str))

        part = LessonPart(
            session_id=new_session.id,
            part_number=1,
            title=data.title,
            content=data.content,
        )
        db.add(part)
        db.commit()

        return {
            "session_id": str(new_session.id),
            "current_part": 1,
            "title": part.title,
            "content": part.content,
        }

    @staticmethod
    def get_or_generate_questions(
        db: Session, session_id: uuid.UUID | str, api_key: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetches existing questions or generates 2 verification questions for the current part."""
        target_uuid = uuid.UUID(str(session_id))
        study_session = db.get(StudySession, target_uuid)
        if not study_session:
            raise ValueError(f"Session with ID {target_uuid} not found.")

        # Check for cached questions to Save tockens
        stmt = select(Question).where(
            Question.session_id == target_uuid,
            Question.part_number == study_session.current_part,
        )
        existing_questions = list(db.exec(stmt).all())
        if existing_questions:
            return [
                {
                    "question": q.question_text,
                    "options": json.loads(q.options_json),
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                }
                for q in existing_questions
            ]

        # Retrieve the current part content to anchor questions directly on the covered material
        part_stmt = select(LessonPart).where(
            LessonPart.session_id == target_uuid,
            LessonPart.part_number == study_session.current_part,
        )
        current_part = db.exec(part_stmt).first()
        if not current_part:
            raise ValueError(f"Lesson part {study_session.current_part} not found.")

        client = get_llm_client(api_key)
        prompt = (
            f"Based strictly on this micro-lesson content: \"{current_part.content}\", "
            f"generate 2 direct, simple multiple-choice questions to reinforce learning."
        )
    

        try:
            completion = client.beta.chat.completions.parse(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format=QuizSchema,
                temperature=0.4,
            )
            quiz_data = completion.choices[0].message.parsed
            questions_list = quiz_data.questions if quiz_data else []
        except Exception:
            raw_res = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            'Output strictly valid JSON matching: '
                            '{"questions": [{"question_text": "...", "options": ["A) ..."], "correct_answer": "A", "explanation": "..."}]}'
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
            )
            content_str = raw_res.choices[0].message.content or "{}"
            quiz_data = QuizSchema(**json.loads(content_str))
            questions_list = quiz_data.questions

        saved_questions: list[dict[str, Any]] = []
        for q_item in questions_list:
            q = Question(
                session_id=target_uuid,
                part_number=study_session.current_part,
                question_text=q_item.question_text,
                options_json=json.dumps(q_item.options),
                correct_answer=q_item.correct_answer,
                explanation=q_item.explanation,
            )
            db.add(q)
            saved_questions.append(
                {
                    "question": q_item.question_text,
                    "options": q_item.options,
                    "correct_answer": q_item.correct_answer,
                    "explanation": q_item.explanation,
                }
            )

        db.commit()
        return saved_questions

    @staticmethod
    def generate_next_part(
        db: Session, session_id: uuid.UUID | str, api_key: str | None = None
    ) -> dict[str, Any]:
        """Generates the next logical micro-step preserving previous conversational context."""
        target_uuid = uuid.UUID(str(session_id))
        study_session = db.get(StudySession, target_uuid)
        if not study_session:
            raise ValueError(f"Session with ID {target_uuid} not found.")

        # Compile historical context to prevent repetitive outputs
        history_stmt = (
            select(LessonPart)
            .where(LessonPart.session_id == target_uuid)
            .order_by(LessonPart.part_number)
        )
        history = list(db.exec(history_stmt).all())
        history_summary = "\n".join(
            [f"Part {p.part_number}: {p.title} - {p.content}" for p in history]
        )

        next_part_num = study_session.current_part + 1

        client = get_llm_client(api_key)
        prompt = (
            f"Topic: '{study_session.topic}' (Proficiency Level: {study_session.level}).\n"
            f"The learner has completed the following sequence:\n{history_summary}\n\n"
            f"Now explain Part {next_part_num} as the direct subsequent micro-step. "
            f"Keep it concise, actionable, and under 100 words."
        )

        try:
            completion = client.beta.chat.completions.parse(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format=MicroLessonSchema,
                temperature=0.6,
            )
            data = completion.choices[0].message.parsed
            if not data:
                raise ValueError("Parsed output returned None.")
        except Exception:
            raw_res = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": 'Output strictly valid JSON matching: {"title": "...", "content": "..."}',
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.6,
            )
            content_str = raw_res.choices[0].message.content or "{}"
            data = MicroLessonSchema(**json.loads(content_str))

        new_part = LessonPart(
            session_id=target_uuid,
            part_number=next_part_num,
            title=data.title,
            content=data.content,
        )
        study_session.current_part = next_part_num

        db.add(new_part)
        db.add(study_session)
        db.commit()

        return {
            "session_id": str(target_uuid),
            "current_part": next_part_num,
            "title": new_part.title,
            "content": new_part.content,
        }