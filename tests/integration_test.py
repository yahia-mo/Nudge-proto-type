import os

from sqlmodel import Session

from src.database import engine, init_db
from src.service import LearningService


def run_integration_test():
    # Make sure the API key in env variables .

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[-] Error: GROQ_API_KEY is not set. Check your env variables .")
        return

    print("[+] GROQ_API_KEY detected.")

    # 2. init the Tables .
    print("[+] Initializing SQLite database...")
    init_db()

    with Session(engine) as db:
        # 3. test creating session and generate part ons .
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

        # 4. test generate the quiz .
        print(f"\n[+] Step 2: Fetching/Generating questions for Part {session_data['current_part']}...")
        questions = LearningService.get_or_generate_questions(db=db, session_id=session_id)
        
        for idx, q in enumerate(questions, 1):
            print(f"    Q{idx}: {q['question']}")
            for opt in q['options']:
                print(f"       {opt}")
            print(f"       [Correct: {q['correct_answer']}] - Reason: {q['explanation']}")

        # 5. test go to next part generation .
        print("\n[+] Step 3: Generating Part 2 (Dependency test)...")
        next_part = LearningService.generate_next_part(db=db, session_id=session_id)
        
        print(f"    -> Current Part Index: {next_part['current_part']}")
        print(f"    -> Part 2 Title: {next_part['title']}")
        print(f"    -> Content: {next_part['content']}")

    print("\n[✓] All integration steps completed successfully!")


if __name__ == "__main__":
    run_integration_test()