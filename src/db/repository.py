import json
import uuid
from typing import Any

from sqlmodel import Session, select

from .models import LessonPart, Question, StudentAnswer, StudySession


def create_study_session(
    db: Session, topic: str, level: str, available_time: int
) -> StudySession:
    study_session = StudySession(
        topic=topic,
        level=level,
        available_time=available_time,
        current_part=1,
    )
    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


def get_study_session(db: Session, session_id: uuid.UUID | str) -> StudySession | None:
    return db.get(StudySession, uuid.UUID(str(session_id)))


def get_lesson_part(
    db: Session, session_id: uuid.UUID | str, part_number: int
) -> LessonPart | None:
    stmt = select(LessonPart).where(
        LessonPart.session_id == uuid.UUID(str(session_id)),
        LessonPart.part_number == part_number,
    )
    return db.exec(stmt).first()


def get_parts_history(db: Session, session_id: uuid.UUID | str) -> list[LessonPart]:
    stmt = (
        select(LessonPart)
        .where(LessonPart.session_id == uuid.UUID(str(session_id)))
        .order_by(LessonPart.part_number)
    )
    return list(db.exec(stmt).all())


def get_questions(
    db: Session, session_id: uuid.UUID | str, part_number: int
) -> list[Question]:
    stmt = select(Question).where(
        Question.session_id == uuid.UUID(str(session_id)),
        Question.part_number == part_number,
    )
    return list(db.exec(stmt).all())


def add_lesson_part(
    db: Session,
    session_id: uuid.UUID | str,
    part_number: int,
    title: str,
    content: str,
) -> LessonPart:
    part = LessonPart(
        session_id=uuid.UUID(str(session_id)),
        part_number=part_number,
        title=title,
        content=content,
    )
    db.add(part)
    db.commit()
    return part


def save_questions(
    db: Session,
    session_id: uuid.UUID | str,
    part_number: int,
    question_items: list[Any],
) -> list[Question]:
    saved: list[Question] = []
    for item in question_items:
        question = Question(
            session_id=uuid.UUID(str(session_id)),
            part_number=part_number,
            question_text=item.question_text,
            options_json=json.dumps(item.options),
            correct_answer=item.correct_answer,
            explanation=item.explanation,
        )
        db.add(question)
        saved.append(question)
    db.commit()
    return saved


def set_current_part(db: Session, study_session: StudySession, part_number: int) -> None:
    study_session.current_part = part_number
    db.add(study_session)
    db.commit()

def get_student_answers(
    db: Session, session_id: uuid.UUID | str
) -> list[StudentAnswer]:
    stmt = select(StudentAnswer).where(
        StudentAnswer.session_id == uuid.UUID(str(session_id))
    )
    return list(db.exec(stmt).all())