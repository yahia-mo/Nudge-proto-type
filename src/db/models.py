import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class StudySession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    topic: str
    level: str = Field(default="beginner")
    available_time: int
    current_part: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.now)

    parts: list["LessonPart"] = Relationship(
        back_populates="session", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    questions: list["Question"] = Relationship(
        back_populates="session", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class LessonPart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="studysession.id")
    part_number: int
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

    session: StudySession = Relationship(back_populates="parts")


class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="studysession.id")
    part_number: int
    question_text: str
    options_json: str
    correct_answer: str
    explanation: str

    session: StudySession = Relationship(back_populates="questions")

class StudentAnswer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="studysession.id")
    question_id: int = Field(foreign_key="question.id")
    selected_answer: str
    is_correct: bool
    created_at: datetime = Field(default_factory=datetime.now)