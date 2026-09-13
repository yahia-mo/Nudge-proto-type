# API Desin

## Start Session

* endpoint : ```POST /api/sessions/start```
* start new session and explain First part .

### Request body

```json
{
  "topic": "Concurancy in Operating Systems", // the topic
  "level": "beginner" // level of Knoledge 
}
```

### Response body

```json
{
  "session_id": "a3b8e8f2-9c12-4e56-b09a-1c88d1234567", // id of Seccion UUID / INT For simplefing for now 
  "topic": "Concurancy in Operating Systems", // the topic 
  "current_part": 1, // num of decomposed part .
  "part_title": "What is Concurancy in simply",
  "content": "A very simple and concise explanation in just 3 to 5 lines that clarifies the concept without going into too much detail..."
}
```

## Get Question

* endpoint : ```POST /api/sessions/{session_id}/questions```
* after understanding the part then the user click on **Takequiz** whcich give him a short exam .

### Request Body

```json
{} //empty for now (then add the choice of questions number)  
```

### Response Body

```json
{
  "session_id": "a3b8e8f2-9c12-4e56-b09a-1c88d1234567",
  "part_number": 1,
  "questions": [
    {
      "id": 101,
      "question": "Which of the following is the essential condition for a Deadlock to occur?",
      "options": [
        "A) Mutual Exclusion",
        "B) High CPU Clock Speed",
        "C) Running on SSD",
        "D) Multiple Monitors"
      ],
      "correct_answer": "A",
      "explanation": "Because Mutual Exclusion means that the resource is reserved for only one process at a time."
    }
  ]
}
```

## Next Part

* endpont : ```POST /api/sessions/{session_id}/next```
* after ending first part and it's quiz the user click on **nest part**

### Request body

```json
{} // empty
```

* The Logic in the backend: It retrieves **history_summary** and **current_part** from the database, sends them to the LLM and tells it: "The user understands this part, now explain part number (current_part + 1) as a logical extension to it," and then it increases the counter in the database .
  
### Response body

```json
{
  "session_id": "a3b8e8f2-9c12-4e56-b09a-1c88d1234567", 
  "current_part": 2,
  "part_title": "next part to study",
  "content": "the content ......"
}
```
