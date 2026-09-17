# Nudge-proto-type

NUDGE helps students overcome Overcoming laziness in learning and procrastination caused by large or complex study goals. The app breaks a topic into small micro-lessons, generates a short quiz after each one, and moves to the next part step by step.

## Install

```bash
git clone https://github.com/yahia-mo/Nudge-proto-type.git

cd Nudge-proto-type
```

## Setup

```bash
# install dependencies
uv sync

# copu default venv into you env variables
cp .env.example .env   # then add your GROQ_API_KEY
```

## Usage

Run the integration test (creates a session, generates a quiz, then the next part):

```bash
uv run test
```

## Project structure

```text
src/
  core/       # entry helpers (engine re-exports for main.py / tests)
  db/         # engine, SQLModel models, repository (data access)
  llm/        # LLM client, schemas, prompts, generation helpers
  services/   # business logic (LearningService)
  service.py  # services link layer
tests/        # integration test
docs/         # API & database design docs
```

## How it works

1. `create_session` — stores the session and asks the LLM to explain the first micro-concept.
2. `get_or_generate_questions` — reuses existing questions or generates a short quiz for the current part (cached per part).
3. `generate_next_part` — generates the next micro-step using the previous parts as context.

LLM responses are requested as structured output and fall back to JSON mode if parsing fails.

## Env vars

- `GROQ_API_KEY` — required, used to call the LLM.
- `DATABASE_URL` — optional, defaults to `sqlite:///./database.db`
  