MICRO_LESSON_FALLBACK_SYSTEM = (
    'Output strictly valid JSON matching: {"title": "...", "content": "..."}'
)

QUIZ_FALLBACK_SYSTEM = (
    'Output strictly valid JSON matching: '
    '{"questions": [{"question_text": "...", "options": ["A) ..."], "correct_answer": "A", "explanation": "..."}]}'
)


def build_intro_prompt(topic: str, level: str) -> str:
    return (
        f"You are an empathetic, anti-procrastination tutor. "
        f"Explain the absolute FIRST, most fundamental micro-concept of: '{topic}' for a '{level}' level learner. "
        f"Keep it extremely low-friction and under 80 words."
    )


def build_quiz_prompt(content: str) -> str:
    return (
        f"Based strictly on this micro-lesson content: \"{content}\", "
        f"generate 2 direct, simple multiple-choice questions to reinforce learning."
    )



def build_next_part_prompt(
    topic: str,
    level: str,
    history_summary: str,
    next_part_num: int,
    accuracy: float,
) -> str:

    return (
        f"Topic: '{topic}' (Proficiency Level: {level}).\n"
        f"The learner has completed the following sequence:\n{history_summary}\n\n"
        f"The learner's current quiz accuracy is {accuracy:.0%}.\n\n"
        f"If accuracy is below 60%, DO NOT introduce a new concept. "
        f"Instead, reinforce the previous concept, simplify it, and give a small practice action. "
        f"Clearly treat this as reinforcement of the previous part, not as a new micro-step.\n\n"
        f"If accuracy is 60% or higher, continue to the next micro-step "
        f"and explain Part {next_part_num} as the direct subsequent concept.\n\n"
        f"Keep it concise, actionable, and under 100 words."
    )