import os

from sqlmodel import Session, SQLModel, create_engine
from src.db.models import StudentAnswer


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db():
    SQLModel.metadata.create_all(engine)

    with engine.connect() as connection:
        result = connection.exec_driver_sql(
            "PRAGMA table_info(studysession)"
        )
        columns = [row[1] for row in result]

        if "available_time" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE studysession "
                "ADD COLUMN available_time INTEGER DEFAULT 1"
            )
            connection.commit()


def get_session():
    with Session(engine) as session:
        yield session