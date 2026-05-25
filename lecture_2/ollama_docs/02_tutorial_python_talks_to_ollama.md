# Ollama Tutorial 2

## Tutorial: Python Talks to Ollama (Console First)

---

### 🎯 Goal

- Send a prompt to a local Ollama model from Python
- Print the raw JSON response so students can see everything
- Explain what each field means
- Then we'll build a mini frontend in later steps

---

## Step 1: Confirm Ollama Is Running and a Model Exists

In a terminal:

```bash
ollama list
```

If you don't have a model yet:

```bash
ollama pull llama3
```

Quick test:

```bash
ollama run llama3
```

Exit with `Ctrl + D`.

---

## Step 2: Create a Python Project in PyCharm

In your PyCharm, add `requests` to the Python packages.

> 💡 You can use the **Python Packages** panel in the bottom left of PyCharm to install it via the UI.

---

## Step 3: Python Script That Calls Ollama (Non-Streaming)

Create `01_generate.py`:

```python
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:30b"

def generate(prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    prompt = "Explain what an API is in 2 sentences."
    data = generate(prompt)

    print("\n--- RAW JSON RESPONSE ---")
    print(json.dumps(data, indent=2))

    print("\n--- EXTRACTED TEXT ---")
    print(data.get("response", ""))
```

### How This Works

1. **`OLLAMA_URL`** — We call the localhost Ollama URL at its `/api/generate` endpoint.
2. **`MODEL`** — Defines which model we use from our downloaded models.
3. **`generate()` function** — The payload will almost always look the same. Since we only want one message and one return value, we set `"stream": False`.
4. **`requests.post()`** — Via the `requests` library, we use a `POST` call to send the prompt to the Ollama backend.
5. **`r.json()`** — We convert the return from the model into a JSON dictionary.
6. **`__main__` block** — We call the function and print the result/response into the terminal.

---

## Step 4: Understand Every Output Field (`generate` Endpoint)

When `"stream": false`, Ollama typically returns a JSON object with the following fields:

| Field                    | Type       | Description                                                                                                                                             |
| ------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`                  | `string`   | The model name used                                                                                                                                     |
| `created_at`             | `string`   | Timestamp of when the response was generated                                                                                                            |
| `response`               | `string`   | The actual generated text (the assistant's answer)                                                                                                      |
| `done`                   | `boolean`  | Indicates the generation is complete                                                                                                                    |
| `done_reason`            | `string`   | Why it stopped. Commonly `"stop"` (hit a stop condition) or `"length"` (hit token limit)                                                                |
| `context`                | `int[]`    | A list of token IDs representing the conversation context used internally by Ollama. Pass this back in the next request to continue the same conversation without resending the whole chat |
| `total_duration`         | `int` (ns) | Total time (nanoseconds) for the request end-to-end                                                                                                     |
| `load_duration`          | `int` (ns) | Time (nanoseconds) spent loading the model (often larger the first time)                                                                                |
| `prompt_eval_count`      | `int`      | How many tokens were in your prompt                                                                                                                     |
| `prompt_eval_duration`   | `int` (ns) | Time spent evaluating the prompt tokens                                                                                                                 |
| `eval_count`             | `int`      | Number of tokens generated in the response                                                                                                              |
| `eval_duration`          | `int` (ns) | Time spent generating those tokens                                                                                                                      |

> 🔑 **Key field — `context`:** This is the mechanism that enables multi-turn conversations. If you pass this array back in your next request, Ollama can continue the conversation without you having to resend the full chat history.
