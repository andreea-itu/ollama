# Ollama Tutorial 4

## Tutorial: Context and Conversation Memory (Ollama Context)

---

### 💡 Did you know?

- The LLM does **not** "remember" between requests.
- Memory is **simulated** by sending context back in the next request.
- Ollama returns a **context array** that represents internal state for continuing generation.

### ⚠️ Important Note

> This context is **model-specific** (don't reuse it across different models).
>
> It's **not human-readable**. It's a token-state mechanism.

---

## Step 1: Update Flask to Store Context Server-Side (Sessions)

Right now your webpage stores context in JavaScript and sends it back. That works, but for teaching memory it's clearer if the **server stores it**, like a real app.

**We'll do this:**

- Frontend sends only `{ message, session_id, use_memory }`
- Backend keeps a dictionary: `SESSION_CONTEXT[session_id] = context_array`

> 📥 Download the tutorial4 project → unzip it and let's go over the changes together.

---

## 1. `SESSION_CONTEXT`: Server-Side Memory Storage

### Code Added

```python
SESSION_CONTEXT = {}
```

### What This Does

This dictionary stores conversation memory **per session**.

| Key            | Value                              |
| -------------- | ---------------------------------- |
| `session_id`   | A unique conversation identifier   |
| Value          | `context` array returned by Ollama |

**Example:**

```python
SESSION_CONTEXT["abc123"] = [12, 55, 998, ...]
```

### Why This Matters

**Without this:**

- Each request is stateless
- The model forgets everything between messages

**With this:**

- We can decide **when** the model remembers
- We can reset memory at any time
- This mirrors how **real chat systems** work

---

## 2. Creating a New Conversation: `/new_session`

### Code Added

```python
@app.post("/new_session")
def new_session():
    sid = uuid.uuid4().hex
    SESSION_CONTEXT[sid] = None
    return jsonify({"session_id": sid})
```

### What This Does

This creates a **new conversation session**:

1. Generates a unique `session_id`
2. Initializes memory for that session
3. Returns the ID to the frontend

### Why This Matters

Each conversation needs its own memory.

**Without sessions:**

- All users would share the same memory
- Conversations would leak into each other

> 📝 **Teaching takeaway:**
> A session is just a label that tells the server *which memory belongs to which conversation*.

---

## 3. Forgetting Memory: `/reset_session`

### Code Added

```python
@app.post("/reset_session")
def reset_session():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")

    SESSION_CONTEXT[sid] = None
    return jsonify({"ok": True})
```

### What This Does

This **clears** the stored context for a session.

### Why This Matters

This lets us demonstrate:

- Forgetting is **explicit**
- Memory is **not permanent**
- "Reset conversation" is just **clearing stored context**

> 🧠 **Teaching moment:**
> Forgetting is not the model "choosing" to forget — it's the **system deciding not to send memory** anymore.

---

## 4. `use_memory`: Toggling Context On/Off

### Code Added (Request Field)

```python
use_memory = bool(data.get("use_memory", True))
```

### What This Does

Allows the frontend to decide:

- `use_memory = true` → send stored context
- `use_memory = false` → ignore stored context

### Why This Matters

This makes memory **visible and controllable**.

Students can now directly compare:

| Mode              | Behavior                  |
| ----------------- | ------------------------- |
| With context      | Continuous conversation   |
| Without context   | Isolated responses        |

> 🔑 This is one of the **most important teaching tools** in the tutorial.

---

## 5. Reading Stored Context Before Calling Ollama

### Code Added

```python
context = SESSION_CONTEXT.get(sid) if use_memory else None
```

### What This Does

- Retrieves the previous context for this session
- Only uses it if memory is enabled

### Why This Matters

This is the moment where **memory actually happens**.

| Condition            | Behavior                                          |
| -------------------- | ------------------------------------------------- |
| `context` is `None`  | The model behaves as if this is the first message  |
| `context` exists     | The model continues the conversation internally    |

> 📣 **Teaching line you can use:**
> *"Memory only exists at the moment we send context back to the model."*

---

## 6. Saving Updated Context After the Response

### Code Added

```python
new_context = result.get("context")

if use_memory:
    SESSION_CONTEXT[sid] = new_context
```

### What This Does

- Ollama returns a **new context** after each response.
- We store it so the next request can continue the conversation.

### Why This Matters

This forms the **feedback loop**:

```
request → model → new context → store → next request
```

**Without this step:**

- Memory would never update
- Conversation would stall

---

## 7. Exposing `context_len` for Teaching

### Code Added

```python
context_len = len(new_context) if isinstance(new_context, list) else 0
```

Returned in response:

```python
"context_len": context_len
```

### What This Does

Shows how large the context is growing.

### Why This Matters

Students can now see that:

- Every message **increases** context
- Memory has a **cost**
- Context windows are **finite**

> 📚 This sets up later lessons on:
> - Summarization
> - Retrieval
> - Context pruning

---

## 8. Why We Did NOT Store Messages as Text

### Important Clarification

Ollama's context is an **internal token state**, not human-readable conversation history.

That's why:

- We don't **inspect** it
- We don't **edit** it
- We don't **reuse** it across different models

This leads naturally into later lessons where:

- We store messages ourselves
- We summarize
- We pass structured context between models

---

## Demonstration

Once we **don't send the context/memory** anymore, the AI won't remember information from earlier in the conversation (e.g., a number you asked it to remember). This clearly illustrates that **memory is not intrinsic** to the model — it is entirely dependent on the context being passed back with each request.

---

## The Flow
Client sends:   { "session_id": "abc123", "message": "Hello" }
                         │
                         ▼
Flask app:       Looks up SESSION_CONTEXT["abc123"] → gets stored context tokens
                         │
                         ▼
Sends to Ollama: { "model": "tinyllama", "prompt": "Hello", "context": [12, 55, 998, ...] }


Ollama has no concept of sessions. 
It's stateless — it just takes a context token array and returns a new one.

Your Flask app wraps that with a session_id so the client doesn't have to store and resend the (potentially huge) context array each time.
Compare with 02_app.py where there's no session management — the client itself had to pass context back and forth:
02_app.py
Lines 51-52
    Request:        { "message": "...", "context": [...] } context is optional
So 04_app.py is an improvement: it hides the context management behind a simple session_id.

---

Sure! Here's how Flask and Ollama interact in this code, step by step:

## The Big Picture

```
Client (curl/browser)  ←→  Flask app (your code)  ←→  Ollama server (LLM)
```

Flask is the **middleman**. It manages sessions and translates between what the client sends and what Ollama understands.

---

## Step 1: Create a session (`/new_session`)

```48:56:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
@app.post("/new_session")
def new_session():
    """
    Creates a new session_id.
    Creates a new conversation session as Each conversation needs its own memory.
    """
    sid = uuid.uuid4().hex
    SESSION_CONTEXT[sid] = None
    return jsonify({"session_id": sid})
```

- **Flask only** — Ollama is not involved here at all.
- Generates a random ID like `"a3f8b2c1..."`.
- Stores it in the Python dictionary `SESSION_CONTEXT` with `None` (no memory yet).
- Returns the ID to the client so it can use it in future requests.

---

## Step 2: Reset a session (`/reset_session`)

```59:70:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
@app.post("/reset_session")
def reset_session():
    """
    Clears (forgets) stored context for a session.
    """
    data = request.get_json(silent=True) or {}
    sid = (data.get("session_id") or "").strip()
    if not sid:
        return jsonify({"error": "Field 'session_id' is required."}), 400

    SESSION_CONTEXT[sid] = None
    return jsonify({"ok": True})
```

- **Flask only** — again, no Ollama call.
- Sets the stored context back to `None` → the model "forgets" the conversation.

---

## Step 3: Chat (`/chat`) — where Flask and Ollama work together

This is where it gets interesting. Here's the flow:

### 3a. Flask reads the client's request

```86:97:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
    data = request.get_json(silent=True) or {}

    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Field 'message' is required."}), 400

    sid = (data.get("session_id") or "").strip()
    if not sid:
        return jsonify({"error": "Field 'session_id' is required. Create one via /new_session."}), 400

    # Send stored context:This makes memory visible and controllable.
    use_memory = bool(data.get("use_memory", True))
```

Flask parses the client JSON and validates it. These are **custom fields** — Ollama doesn't know about `session_id` or `use_memory`.

### 3b. Flask looks up the stored context

```99:100:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
    # Get existing context only if memory is enabled: The model continues the conversation internally
    context = SESSION_CONTEXT.get(sid) if use_memory else None
```

This is the **bridge** between Flask's session system and Ollama's memory system:
- If `use_memory=True` → retrieves the token array from previous conversations
- If `use_memory=False` → sends `None` (model has no memory of past messages)

### 3c. Flask calls Ollama

```102:108:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
    start = time.time()
    try:
        result = ollama_generate(message=message, context=context, stream=False)
    except requests.HTTPError as e:
        return jsonify({"error": "Ollama request failed.", "details": str(e), "body": getattr(e.response, "text", None)}), 502
    except Exception as e:
        return jsonify({"error": "Server error calling Ollama.", "details": str(e)}), 500
```

**This is the only line that actually talks to Ollama.** It sends:

```json
{ "model": "tinyllama", "prompt": "user's message", "stream": false, "context": [12, 55, 998, ...] }
```

Ollama processes the prompt (+ context for memory) and returns a response with the generated text and a **new** context array.

### 3d. Flask stores the new context

```112:120:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
    reply = result.get("response", "")
    
    # Ollama returns a new context after each response.
    # We store it so the next request can continue the conversation.
    new_context = result.get("context")

    # Store context back only if memory is enabled
    if use_memory:
        SESSION_CONTEXT[sid] = new_context
```

Ollama returns a **new context** (updated token array that now includes this exchange). Flask saves it back into `SESSION_CONTEXT[sid]` so the **next** request can continue the conversation.

### 3e. Flask builds and sends the response to the client

```122:145:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
    meta = {
        "model": result.get("model"),
        // ... performance stats from Ollama ...
        "server_elapsed_ms": elapsed_ms,
    }

    context_len = len(new_context) if isinstance(new_context, list) else 0

    return jsonify({
        "reply": reply,
        "session_id": sid,
        "memory_used": use_memory,
        "context_len": context_len,
        "meta": meta,
    })
```

Flask reformats Ollama's response into a **cleaner** JSON for the client. The client never sees the raw context tokens — just the reply and metadata.

---

## Visual Summary of a Conversation

```
Request 1:
  Client → Flask:   { "session_id": "abc", "message": "I'm Andreea" }
  Flask  → Ollama:  { "model": "tinyllama", "prompt": "I'm Andreea", "context": null }
  Ollama → Flask:   { "response": "Nice to meet you!", "context": [12, 55, 998] }
  Flask saves:      SESSION_CONTEXT["abc"] = [12, 55, 998]
  Flask  → Client:  { "reply": "Nice to meet you!", "context_len": 3 }

Request 2:
  Client → Flask:   { "session_id": "abc", "message": "What's my name?" }
  Flask  → Ollama:  { "model": "tinyllama", "prompt": "What's my name?", "context": [12, 55, 998] }
  Ollama → Flask:   { "response": "Your name is Andreea!", "context": [12, 55, 998, 44, 77] }
  Flask saves:      SESSION_CONTEXT["abc"] = [12, 55, 998, 44, 77]
  Flask  → Client:  { "reply": "Your name is Andreea!", "context_len": 5 }
```

The key insight: **Ollama is stateless** — it doesn't remember anything between requests. Flask provides the illusion of memory by storing and resending the context array each time, keyed by `session_id`.

---
Yes, every HTTP request to `/chat` contains a **new question** (the `message` field). But how the model **answers** depends on whether it has memory:

## With memory (`use_memory: true`)

Each request is a new question, but the model **remembers** what was said before via the `context` token array:

```
Request 1: { "message": "My name is Andreea" }     → context: null (first time)
Request 2: { "message": "What's my name?" }         → context: [12, 55, 998, ...] (from request 1)
Request 3: { "message": "What's the weather?" }     → context: [12, 55, 998, ..., 44, 77] (from request 2)
```

Each request is **independent at the HTTP level** (a brand new POST), but the `context` array carries the conversation history forward. The model can answer "Your name is Andreea!" in request 2 because Flask sent the stored context.

## Without memory (`use_memory: false`)

Each request is a completely **isolated** question — the model has zero knowledge of anything said before:

```
Request 1: { "message": "My name is Andreea" }     → context: null
Request 2: { "message": "What's my name?" }         → context: null
  → Model: "I don't know your name" ❌
```

## Every request = one new question

The `context` array doesn't contain the actual text of previous messages. It contains **tokens** (compressed numerical representations) that let Ollama internally reconstruct the conversation state. That's why the context grows with each exchange:

```154:155:ai_project/lecture_2/04_app/OlamaTutorial/04_app.py
    # Shows how large the context is growing.
    context_len = len(new_context) if isinstance(new_context, list) else 0
```

Think of it like this:
- **Request** = a single letter you mail to someone
- **Context** = a photocopy of all previous letters you attach to each new one, so the recipient remembers the whole conversation