# Ollama Exercise 1

## Student Task: "The Forgetful Assistant" (Intro, Fun, Very Visual)

---

### ⚠️ Before You Start

To save time, download a smaller model ahead of time:

```bash
ollama pull qwen3:8b
```

---

### 🎯 Goal

Make the assistant **intentionally forget** information after a fixed number of messages.

---

## Task Description

Modify the server so that:

- The assistant **remembers** things
- But **forgets automatically** after **N messages** (for example: 3) — without unclicking the "use memory" button

---

## Requirements

### 1. Add a Counter Per Session

```python
SESSION_TURNS = {}
```

### 2. Every Time `/chat` Is Called

1. **Increment** the counter
2. If counter > N:
   - **Clear** `SESSION_CONTEXT[session_id]`
   - **Reset** the counter
3. Return a flag in the response:

```json
"memory_reset": true
```

---

## Demo Script

Follow these steps to test your implementation:

| Step | Action                                  | Expected Result                      |
| ---- | --------------------------------------- | ------------------------------------ |
| 1    | Tell the assistant your name            | It acknowledges your name            |
| 2    | Ask it to repeat your name              | It remembers and responds correctly  |
| 3    | Send more messages until N is exceeded  | Counter triggers a memory reset      |
| 4    | Ask your name again                     | It has **forgotten** — memory reset! |

> 👀 This exercise is very **visual** — students can clearly see the moment the assistant "forgets" what it knew just one message ago.
