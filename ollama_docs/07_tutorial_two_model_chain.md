# Olama Tutorial 5

## Tutorial: Two-Model Chain (Classifier → Writer) for Email Replies

## What we are building

image.png

The user pastes an email. Then:

**Classifier model** decides:

- **category**: family | boss | school
- **tone**: for example warm | professional | polite

**Writer model** generates:

- an email reply matching the category + tone

**We will learn:**

- "context" as structured data (JSON)
- dividing tasks across models
- predictable outputs from Model A → better behavior from Model B

---

## Step 1 Use The previous solution to start off this tutorial:

## Step 1 — Add new imports for JSON + parsing

### Why

The classifier model returns JSON. We need to parse that JSON robustly (even if the model sometimes adds extra text).

### Change

**Before**

```python
import os
import time
import uuid
import requests
```

**After**

```python
import os
import time
import uuid
import json
import re
import requests
```

- `json` is used to parse model output.
- `re` is used to "extract the first JSON object" if the model returns extra text around it.

---

## Step 2 — Separate the models: classifier vs writer

### Why

We want two models with different roles:

- A smaller/faster classifier model for categorization
- A bigger/better writer model for drafting the reply

### Change

**Before**

```python
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:30b")
```

**After**

```python
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:30b")
OLLAMA_CLASSIFIER = os.environ.get("OLLAMA_CLASSIFIER", "qwen3:8b")

CLASSIFIER_MODEL = os.environ.get("CLASSIFIER_MODEL", OLLAMA_CLASSIFIER)
WRITER_MODEL = os.environ.get("WRITER_MODEL", OLLAMA_MODEL)
```

What this enables:

- You can configure models without changing code by setting environment variables.
- `CLASSIFIER_MODEL` and `WRITER_MODEL` are used in different parts of the app.

---

## Step 3 — Add debug prints for configuration

### Why

When something goes wrong, it's often because the wrong model name or wrong URL was used. Printing these at startup makes debugging easy.

### Change

Added:

```python
print("OLLAMA_URL:", OLLAMA_URL)
print("CLASSIFIER_MODEL:", CLASSIFIER_MODEL)
print("WRITER_MODEL:", WRITER_MODEL)
```

Now the server tells you on startup exactly what it will use.

---

## Step 4 — Replace ollama_generate with a model-parameter function

### Why

The old function could only call one fixed model (`OLLAMA_MODEL`). We need a function that can call different models by name.

### Before

```python
def ollama_generate(message: str, context=None, stream: bool = False) -> dict:
    payload = {"model": OLLAMA_MODEL, "prompt": message, "stream": stream}
```

### After

```python
def ollama_generate_model(model: str, prompt: str, context=None, stream: bool = False) -> dict:
    payload = {"model": model, "prompt": prompt, "stream": stream}
```

Key difference:

We pass `model` as an argument, so we can call:

- `ollama_generate_model(CLASSIFIER_MODEL, ...)`
- `ollama_generate_model(WRITER_MODEL, ...)`

---

## Step 5 — Add extract_json_object() to safely parse classifier output

### Why

Even when we ask for "ONLY JSON", models can sometimes return:

- extra whitespace
- explanations
- markdown
- a JSON block inside other text

This helper function increases reliability.

### Added

```python
def extract_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except Exception:
        return {}
```

What it does:

1. First tries `json.loads(text)`
2. If that fails, searches the response for the first `{ ... }` block
3. Attempts to parse that block

---

## Step 6 — Add Model A: classify_email(email_text)

### Why

This is the first step in the chain:

- take raw email text
- output structured "context":
  - **category**: family | boss | school
  - **tone**: warm | professional | polite
  - plus a **reason** for teaching/debugging

### Added function

```python
def classify_email(email_text: str) -> dict:
    prompt = """... output ONLY valid JSON ..."""
    result = ollama_generate_model(CLASSIFIER_MODEL, prompt, stream=False)
    raw = result.get("response", "").strip()
    data = extract_json_object(raw)

    # Validate / fallback
    ...
    return {"category": category, "tone": tone, "reason": reason, "raw": raw}
```

**Important detail:**

We validate and apply defaults if the model outputs something unexpected.

This prevents the pipeline from crashing on weird outputs.

---

## Step 7 — Add Model B: write_reply(email_text, classification)

### Why

The second model uses the structured context from Model A to craft a reply with the right tone.

### Added function

```python
def write_reply(email_text: str, classification: dict) -> str:
    category = classification["category"]
    tone = classification["tone"]

    style_rules = {...}
    tone_rules = {...}

    prompt = f"""Context: Category={category}, Tone={tone} ..."""
    result = ollama_generate_model(WRITER_MODEL, prompt, stream=False)
    return result.get("response", "").strip()
```

**Key teaching point:**

We are **not** relying on the writer to "figure out category" again.

We inject the classification as context, which makes results more consistent.

---

## Step 8 — Modify /chat to use "Selective Memory" (remember:)

### Why

We want to teach that memory is a system feature, not magic:

- The system decides when to store context.
- Only messages starting with `remember:` update the stored context.

### What changed conceptually

**Before**

If `use_memory` is true, every message updates context.

**After**

Only update context if message starts with `remember:`

### Core new logic

```python
remember_prefix = "remember:"
is_remember_message = message.lower().startswith(remember_prefix)

if is_remember_message:
    message_to_model = message[len(remember_prefix):].strip()
else:
    message_to_model = message
```

And the key storage rule:

```python
stored = False
if use_memory and is_remember_message:
    SESSION_CONTEXT[sid] = new_context
    stored = True
```

We also return debug fields:

```python
"is_remember_message": is_remember_message,
"memory_updated": stored,
```

So the UI can show when memory was actually updated.

---

## Step 9 — Add new endpoint: /email_chain

### Why

This endpoint runs the two-model pipeline:

1. classify the email
2. write the reply based on classification context

### Added endpoint

```python
@app.post("/email_chain")
def email_chain():
    email_text = data.get("email_text", "").strip()
    classification = classify_email(email_text)
    reply = write_reply(email_text, classification)
    return jsonify({...})
```

The response returns:

- **classification** (category, tone, reason)
- **reply** (final drafted email)
- **models used** + elapsed time

This endpoint is the "LLM chain" in one request.

---

## Summary of the main upgrade

### Old system

- One model
- One endpoint (`/chat`)
- Optional memory: context was always updated when enabled

### New system

- **Two model roles:**
  - classifier model (small)
  - writer model (big)
- **New helper tools:**
  - JSON extraction + validation
- **New chain endpoint** (`/email_chain`)
- **Selective memory in chat:**
  - context only updates on `remember:` messages

**This is the bridge from "chat demo" → "real AI system design."**
