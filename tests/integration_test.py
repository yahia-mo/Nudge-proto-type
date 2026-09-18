import os

from dotenv import load_dotenv
from sqlmodel import Session

from src.core.database import engine, init_db
from src.db.repository import get_questions
from src.service import LearningService

# load the env variables .
load_dotenv()

def run_integration_test():
    # Make sure the API key in env variables .

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[-] Error: GROQ_API_KEY is not set. Check your env variables .")
        return

    print("[+] GROQ_API_KEY detected.")

    # 1. init the Tables .
    print("[+] Initializing SQLite database...")
    init_db()

    with Session(engine) as db:
        # 2. test creating session and generate part one .
        topic_to_test = "Virtual Memory and Paging"
        print(f"\n[+] Step 1: Creating session for topic: '{topic_to_test}'...")

        session_data = LearningService.create_session(
            db=db,
            topic=topic_to_test,
            level="beginner"
        )
        session_id = session_data["session_id"]

        print(f"    -> Session ID: {session_id}")
        print(f"    -> Part 1 Title: {session_data['title']}")
        print(f"    -> Content: {session_data['content']}")

        # 3. test generate the quiz .
        print(f"\n[+] Step 2: Fetching/Generating questions for Part {session_data['current_part']}...")
        questions = LearningService.get_or_generate_questions(db=db, session_id=session_id)

        # the service hides answers from the client; fetch ground truth from the DB
        db_questions = get_questions(db, session_id, session_data["current_part"])
        correct_answers = {
            question.id: question.correct_answer for question in db_questions
        }
        explanations = {
            question.id: question.explanation for question in db_questions
        }

        for idx, q in enumerate(questions, 1):
            print(f"    Q{idx}: {q['question']}")
            for opt in q['options']:
                print(f"       {opt}")
            print(f"       [Correct: {correct_answers[q['id']]}] - Reason: {explanations[q['id']]}")

        # 4. answer every question (correctly) so the flow can advance .
        print("\n[+] Step 3: Answering all questions (simulating the student)...")
        for q in questions:
            result = LearningService.submit_answer(
                db=db,
                session_id=session_id,
                question_id=q["id"],
                selected_answer=correct_answers[q["id"]],
            )
            verdict = "correct" if result["is_correct"] else "wrong"
            print(f"    Q{q['id']}: answered '{result['selected_answer']}' -> {verdict}")

        # 5. test go to next part generation .
        print("\n[+] Step 4: Generating Part 2 (Dependency test)...")
        next_part = LearningService.generate_next_part(db=db, session_id=session_id)

        print(f"    -> Current Part Index: {next_part['current_part']}")
        print(f"    -> Part 2 Title: {next_part['title']}")
        print(f"    -> Content: {next_part['content']}")

    print("\n[✓] All integration steps completed successfully!")


if __name__ == "__main__":
    run_integration_test()