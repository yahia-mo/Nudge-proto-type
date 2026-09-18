import os

from dotenv import load_dotenv
from sqlmodel import Session

from src.core.database import engine, init_db
from src.services.learning import LearningService


load_dotenv()


def run_integration_test():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("[-] Error: GROQ_API_KEY is not set. Check your .env file.")
        return

    print("[+] GROQ_API_KEY detected.")

    print("[+] Initializing SQLite database...")
    init_db()

    with Session(engine) as db:
        # Step 1: Create a learning session
        topic_to_test = "Virtual Memory and Paging"

        print(
            f"\n[+] Step 1: Creating session for topic: "
            f"'{topic_to_test}'..."
        )

        session_data = LearningService.create_session(
            db=db,
            topic=topic_to_test,
            level="beginner",
            available_time=1,
        )

        session_id = session_data["session_id"]

        print(f"    -> Session ID: {session_id}")
        print(f"    -> Part {session_data['current_part']} Title: "
              f"{session_data['title']}")
        print(f"    -> Content: {session_data['content']}")

        # Step 2: Generate or fetch questions
        print(
            f"\n[+] Step 2: Fetching/Generating questions "
            f"for Part {session_data['current_part']}..."
        )

        questions = LearningService.get_or_generate_questions(
            db=db,
            session_id=session_id,
        )

        if not questions:
            print("[-] No questions were generated.")
            return

        for idx, question in enumerate(questions, 1):
            print(f"\n    Q{idx}: {question['question']}")

            for option in question["options"]:
                print(f"       {option}")

        # Step 3: Submit answers
        print("\n[+] Step 3: Submitting answers...")

        for idx, question in enumerate(questions, 1):
            selected_answer = question["options"][0][0]

            result = LearningService.submit_answer(
                db=db,
                session_id=session_id,
                question_id=question["id"],
                selected_answer=selected_answer,
            )

            print(
                f"    -> Q{idx}: "
                f"{'Correct' if result['is_correct'] else 'Incorrect'}"
            )

            if not result["is_correct"]:
                print(f"       Explanation: {result['explanation']}")

        # Step 4: Generate the next adaptive learning step
        print("\n[+] Step 4: Generating adaptive next step...")

        next_part = LearningService.generate_next_part(
            db=db,
            session_id=session_id,
        )

        print(
            f"    -> Current Part Index: "
            f"{next_part['current_part']}"
        )
        print(f"    -> Title: {next_part['title']}")
        print(f"    -> Content: {next_part['content']}")

    print("\n[✓] All integration steps completed successfully!")


if __name__ == "__main__":
    run_integration_test()