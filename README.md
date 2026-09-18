# NUDGE

NUDGE is an AI-powered learning assistant designed to help students overcome procrastination and the difficulty of starting large or complex learning goals.

Instead of giving students a large study plan, NUDGE breaks a learning goal into small, manageable micro-lessons. After each lesson, the student answers a short quiz, and the system uses their performance to decide whether to reinforce the current concept or move to the next learning step.

## How It Works

The core learning loop is:

```text
Learning Goal
      ↓
Micro-Lesson
      ↓
Short Quiz
      ↓
Student Answers
      ↓
Performance Evaluation
      ↓
Reinforcement or Next Step
      ↓
Repeat
```

The current adaptive logic is based on quiz accuracy:

* **Below 60%** → reinforce and simplify the previous concept.
* **60% or higher** → continue to the next micro-step.

This allows the learning experience to respond to the student's performance instead of following a fixed study plan.

## Features

* AI-generated micro-lessons based on the student's topic and level.
* Short multiple-choice quizzes after each micro-lesson.
* Automatic evaluation of student answers.
* Adaptive next-step generation based on performance.
* Reinforcement when the student struggles.
* Persistent storage of sessions, lessons, questions, and answers.
* Structured LLM output validated with Pydantic schemas.
* JSON fallback when structured parsing is unavailable.

## Tech Stack

**Backend**

* Python
* FastAPI
* SQLModel
* SQLite

**AI / LLM**

* Groq API
* OpenAI-compatible API client
* Pydantic structured output

**Development**

* uv
* Git / GitHub

## Project Structure

```text
Nudge-proto-type/
│
├── src/
│   ├── api/          # FastAPI routes
│   ├── core/         # Application configuration
│   ├── db/           # Database models and repository
│   ├── llm/          # LLM client, prompts and schemas
│   └── services/     # Learning and adaptation logic
│
├── tests/            # Integration tests
├── docs/             # API and database documentation
├── main.py           # FastAPI application entry point
├── pyproject.toml
├── uv.lock
└── .env.example
```

## Installation

Clone the repository:

```bash
git clone https://github.com/yahia-mo/Nudge-proto-type.git
cd Nudge-proto-type
```

Install dependencies:

```bash
uv sync
```

## Environment Setup

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Add your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
```

`DATABASE_URL` is optional. If it is not provided, the project uses SQLite:

```text
sqlite:///./database.db
```

## Running the API

Start the development server:

```bash
uv run uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available through FastAPI at:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the integration test:

```bash
uv run test
```

The integration test covers the main adaptive learning flow:

```text
Create Session
      ↓
Generate Questions
      ↓
Submit Answers
      ↓
Calculate Accuracy
      ↓
Generate Adaptive Next Step
```

## Documentation

For more details:

* **API Design:** `docs/api-design.md`
* **Database Design:** `docs/database-schema-desing.md`
