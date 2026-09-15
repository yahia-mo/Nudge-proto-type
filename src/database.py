import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./database.db"

# create the DB engine  
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

class StudySession(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    topic: str
    
    level: str = Field(default="beginner")
    current_part: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.now)
    
    #made a back_populates Relation ship and, if Delete item deletes all item which took his id as a Forein. 
    parts: list["LessonPart"] = Relationship(back_populates="session", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    questions: list["Question"] = Relationship(back_populates="session", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

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
    options_json: str  # choices list with JSON format .
    correct_answer: str
    explanation: str

    session: StudySession = Relationship(back_populates="questions")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session