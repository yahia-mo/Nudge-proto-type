
from pydantic import BaseModel, Field


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

