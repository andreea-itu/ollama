import os
import time
import uuid
import json
import re
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Ollama settings
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Existing chat model (your current one)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OLLAMA_CLASSIFIER = os.environ.get("OLLAMA_CLASSIFIER", "llama3")

# New: Two-model chain defaults
CLASSIFIER_MODEL = os.environ.get("CLASSIFIER_MODEL", OLLAMA_CLASSIFIER)
WRITER_MODEL = os.environ.get("WRITER_MODEL", OLLAMA_MODEL)

print("OLLAMA_URL:", OLLAMA_URL)
print("CLASSIFIER_MODEL:", CLASSIFIER_MODEL)
print("WRITER_MODEL:", WRITER_MODEL)

# In-memory storage for demo purposes:
# session_id -> ollama context array
SESSION_CONTEXT = {}


def ollama_generate_model(model: str, prompt: str, context=None, stream: bool = False) -> dict:
    """
    Calls Ollama /api/generate with a specific model.
    """
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
    }
    if context is not None:
        payload["context"] = context

    r = requests.post(url, json=payload, timeout=500)
    r.raise_for_status()
    return r.json()


def extract_json_object(text: str) -> dict:
    """
    Extracts the first JSON object from model text.
    This helps when the model wraps JSON in extra explanation.

    Returns {} if parsing fails.
    """
    if not text:
        return {}

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to find a JSON object inside the text
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


def classify_email(email_text: str) -> dict:
    """
    Model A: Classifier.
    Must output strict JSON only.
    """
    prompt = f"""
You are an email classifier.

Task:
- Read the email.
- Output ONLY valid JSON (no markdown, no commentary).
- Choose category from: "family", "boss", "school".
- Choose tone from: "warm", "professional", "polite".
- Also include a short 1-sentence reason.

JSON schema:
{{
  "category": "family|boss|school",
  "tone": "warm|professional|polite",
  "reason": "string"
}}

Email:
\"\"\"{email_text}\"\"\"
""".strip()

    result = ollama_generate_model(CLASSIFIER_MODEL, prompt, stream=False)
    raw = (result.get("response") or "").strip()
    data = extract_json_object(raw)

    # Validate / fallback
    category = data.get("category")
    tone = data.get("tone")
    reason = data.get("reason", "")

    if category not in {"family", "boss", "school"}:
        category = "school"  # safe default
    if tone not in {"warm", "professional", "polite"}:
        tone = "polite"

    return {"category": category, "tone": tone, "reason": reason, "raw": raw}


def write_reply(email_text: str, classification: dict) -> str:
    """
    Model B: Writer.
    Uses the structured output from the classifier as context.
    """
    category = classification["category"]
    tone = classification["tone"]

    # Style rules based on category + tone
    # (kept simple for teaching — students can extend later)
    style_rules = {
        "family": "Keep it friendly, human, and warm. Use simple language.",
        "boss": "Keep it professional, concise, and clear. No slang.",
        "school": "Keep it polite, clear, and structured. Ask clarifying questions if needed.",
    }

    tone_rules = {
        "warm": "Sound supportive and friendly.",
        "professional": "Sound formal and businesslike.",
        "polite": "Sound respectful and neutral.",
    }

    prompt = f"""
You are an assistant that drafts email replies.

Context:
- Category: {category}
- Tone: {tone}

Rules:
- {style_rules[category]}
- {tone_rules[tone]}
- Keep it between 6 and 12 lines.
- Do not invent facts not present in the email.
- If important information is missing (dates, attachments, details), ask 1-2 clear questions.

Email:
\"\"\"{email_text}\"\"\"

Now write the reply email text only (no subject line, no markdown).
""".strip()

    result = ollama_generate_model(WRITER_MODEL, prompt, stream=False)
    return (result.get("response") or "").strip()


@app.get("/health")
def health():
    try:
        tags = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10).json()
        return jsonify({
            "ok": True,
            "ollama": True,
            "models": [m["name"] for m in tags.get("models", [])],
            "classifier_model": CLASSIFIER_MODEL,
            "writer_model": WRITER_MODEL
        })
    except Exception as e:
        return jsonify({"ok": False, "ollama": False, "error": str(e)}), 503


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/new_session")
def new_session():
    sid = uuid.uuid4().hex
    SESSION_CONTEXT[sid] = None
    return jsonify({"session_id": sid})


@app.post("/reset_session")
def reset_session():
    data = request.get_json(silent=True) or {}
    sid = (data.get("session_id") or "").strip()
    if not sid:
        return jsonify({"error": "Field 'session_id' is required."}), 400

    SESSION_CONTEXT[sid] = None
    return jsonify({"ok": True})


@app.post("/chat")
def chat():
    """
    Selective Memory Rules (Task 2 solution):
    - Memory is only UPDATED if the message starts with "remember:"
    - Memory can still be USED (context sent) for any message if use_memory=true
    """
    data = request.get_json(silent=True) or {}

    raw_message = (data.get("message") or "")
    message = raw_message.strip()
    if not message:
        return jsonify({"error": "Field 'message' is required."}), 400

    sid = (data.get("session_id") or "").strip()
    if not sid:
        return jsonify({"error": "Field 'session_id' is required. Create one via /new_session."}), 400

    use_memory = bool(data.get("use_memory", True))

    remember_prefix = "remember:"
    is_remember_message = message.lower().startswith(remember_prefix)

    if is_remember_message:
        cleaned = message[len(remember_prefix):].strip()
        message_to_model = cleaned if cleaned else message
    else:
        message_to_model = message

    context = SESSION_CONTEXT.get(sid) if use_memory else None

    start = time.time()
    try:
        result = ollama_generate_model(OLLAMA_MODEL, message_to_model, context=context, stream=False)
    except requests.HTTPError as e:
        return jsonify({"error": "Ollama request failed.", "details": str(e), "body": getattr(e.response, "text", None)}), 502
    except Exception as e:
        return jsonify({"error": "Server error calling Ollama.", "details": str(e)}), 500

    elapsed_ms = int((time.time() - start) * 1000)

    reply = result.get("response", "")
    new_context = result.get("context")

    stored = False
    if use_memory and is_remember_message:
        SESSION_CONTEXT[sid] = new_context
        stored = True

    meta = {
        "model": result.get("model"),
        "created_at": result.get("created_at"),
        "done": result.get("done"),
        "done_reason": result.get("done_reason"),
        "prompt_eval_count": result.get("prompt_eval_count"),
        "eval_count": result.get("eval_count"),
        "server_elapsed_ms": elapsed_ms,
    }

    context_len = len(new_context) if isinstance(new_context, list) else 0

    return jsonify({
        "reply": reply,
        "session_id": sid,
        "memory_used": use_memory,
        "context_len": context_len,
        "meta": meta,
        "is_remember_message": is_remember_message,
        "memory_updated": stored,
    })


@app.post("/email_chain")
def email_chain():
    """
    Two-model chain endpoint:
    Request:
      { "email_text": "..." }

    Response:
      {
        "classification": {...},
        "reply": "..."
      }
    """
    data = request.get_json(silent=True) or {}
    email_text = (data.get("email_text") or "").strip()
    if not email_text:
        return jsonify({"error": "Field 'email_text' is required."}), 400

    start = time.time()
    classification = classify_email(email_text)
    reply = write_reply(email_text, classification)
    elapsed_ms = int((time.time() - start) * 1000)

    return jsonify({
        "classification": {
            "category": classification["category"],
            "tone": classification["tone"],
            "reason": classification["reason"],
            # Keep raw for teaching/debugging; you can remove later
            "raw_classifier_output": classification["raw"],
            "classifier_model": CLASSIFIER_MODEL
        },
        "reply": reply,
        "writer_model": WRITER_MODEL,
        "elapsed_ms": elapsed_ms
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
