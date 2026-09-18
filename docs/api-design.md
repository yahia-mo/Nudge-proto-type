# API Design

NUDGE exposes a set of API endpoints that manage the student's learning session, generate micro-lessons and questions, record student answers, and adapt the next learning step based on the student's performance.

## 1. Start Session

**Endpoint:** `POST /api/sessions/start`

Starts a new learning session and generates the first micro-lesson using the LLM.

### Request Body

```json
{
  "topic": "Concurrency in Operating Systems",
  "level": "beginner",
  "available_time": 1
}
```

* `topic`: The learning topic selected by the student.
* `level`: The student's current knowledge level.
* `available_time`: Total time available for the learning session, in hours.

### Response Body

```json
{
  "session_id": "a3b8e8f2-9c12-4e56-b09a-1c88d1234567",
  "current_part": 1,
  "title": "What is Concurrency?",
  "content": "A simple explanation of the first micro-concept..."
}
```

* `session_id`: Unique identifier for the learning session.
* `current_part`: The current learning part.
* `title`: Title of the generated micro-lesson.
* `content`: Content of the generated micro-lesson.

---

## 2. Get Questions

**Endpoint:** `POST /api/sessions/{session_id}/questions`

Generates or retrieves the questions for the student's current learning part.

The backend first checks whether questions already exist for the current part. If they do, the existing questions are returned. Otherwise, the LLM generates new questions based on the current micro-lesson.

### Request Body

No request body is required.

### Response Body

```json
[
  {
    "id": 101,
    "question": "Which of the following is an essential condition for a deadlock to occur?",
    "options": [
      "A) Mutual Exclusion",
      "B) High CPU Clock Speed",
      "C) Running on SSD",
      "D) Multiple Monitors"
    ]
  },
  {
    "id": 102,
    "question": "Which concept describes two processes making progress during the same period?",
    "options": [
      "A) Concurrency",
      "B) Compilation",
      "C) Encryption",
      "D) Serialization"
    ]
  }
]
```

The correct answer and explanation are intentionally not included in this response. They are kept in the backend and used when evaluating the student's answer.

---

## 3. Submit Answer

**Endpoint:** `POST /api/sessions/{session_id}/answer`

Records the student's answer to a question and evaluates whether the selected answer is correct.

### Request Body

```json
{
  "question_id": 101,
  "selected_answer": "A"
}
```

* `question_id`: ID of the question being answered.
* `selected_answer`: The option selected by the student.

### Response Body

If the answer is correct:

```json
{
  "question_id": 101,
  "selected_answer": "A",
  "is_correct": true,
  "explanation": null
}
```

If the answer is incorrect:

```json
{
  "question_id": 101,
  "selected_answer": "B",
  "is_correct": false,
  "explanation": "Mutual Exclusion means that a resource can be reserved for only one process at a time."
}
```

The backend stores the answer in the `StudentAnswer` table.

---

## 4. Get Next Learning Step

**Endpoint:** `POST /api/sessions/{session_id}/next`

Generates the next learning step based on the student's performance in the current part.

The student must answer all questions for the current part before requesting the next step.

### Request Body

No request body is required.

### Adaptive Logic

The backend calculates the student's accuracy for the current part.

If the accuracy is **below 60%**, the backend asks the LLM to reinforce the previous concept instead of introducing a new concept.

If the accuracy is **60% or higher**, the backend asks the LLM to generate the next micro-step.

```text
                Current Part
                     |
                 Quiz Answers
                     |
                 Calculate
                  Accuracy
                     |
             ┌───────┴───────┐
             ↓               ↓
          < 60%           >= 60%
             ↓               ↓
       Reinforcement     Next Micro-step
```

### Response Body

Example when the student progresses to the next concept:

```json
{
  "session_id": "a3b8e8f2-9c12-4e56-b09a-1c88d1234567",
  "current_part": 2,
  "title": "Processes and Threads",
  "content": "A simple explanation of the next micro-concept..."
}
```

Example when reinforcement is needed:

```json
{
  "session_id": "a3b8e8f2-9c12-4e56-b09a-1c88d1234567",
  "current_part": 1,
  "title": "Reinforce: Understanding Concurrency",
  "content": "A simpler explanation and a small practice action..."
}
```

The current part number remains the same during reinforcement. When the student demonstrates sufficient understanding, the system moves to the next micro-step.

---

## Learning Flow

The main interaction between the frontend and backend is:

```text
Student enters topic, level and available time
                    ↓
              POST /start
                    ↓
            First micro-lesson
                    ↓
             POST /questions
                    ↓
              Show questions
                    ↓
       POST /answer for each answer
                    ↓
          Record performance
                    ↓
               POST /next
                    ↓
          Calculate accuracy
             ↙             ↘
        < 60%             >= 60%
          ↓                  ↓
   Reinforcement       Next micro-step
          ↓                  ↓
          └──────────┬───────┘
                     ↓
               Repeat the loop
```

## Current Endpoints Summary

| Endpoint                               | Method | Purpose                                              |
| -------------------------------------- | ------ | ---------------------------------------------------- |
| `/api/sessions/start`                  | POST   | Create a session and generate the first micro-lesson |
| `/api/sessions/{session_id}/questions` | POST   | Get or generate questions for the current part       |
| `/api/sessions/{session_id}/answer`    | POST   | Submit and evaluate a student's answer               |
| `/api/sessions/{session_id}/next`      | POST   | Generate the next adaptive learning step             |
