# Ollama Exercise 2

## Student Task: "Selective Memory"

---

### 🎯 Goal

Only remember **important** information, not everything.

---

## Task Description

Change the system so:

- The assistant remembers **only** when the message starts with:

```
remember:
```

- All other messages **do not** update memory

---

## Example

**User input (remembered):**

```
remember: my name is Alex
```

**Normal message (not remembered):**

```
what is my name?
```

---

## Implementation Hint (No Full Solution)

Inside `/chat`:

1. Check if the message starts with `"remember:"`
2. If **not**:
   - Call Ollama **without saving** the returned context

---

## What Students Will Learn

- Memory should be **intentional**
- Not everything belongs in context
- This is the basis of **"important fact extraction"**

---

## 📝 Why This Matters

This is exactly how real-world systems work:

| System                      | What It Does                                        |
| --------------------------- | --------------------------------------------------- |
| **Assistants**              | Remember user preferences                           |
| **CRMs**                    | Store customer facts                                |
| **Long-term memory systems** | Persist important information across conversations  |

> 🔑 **Key insight:** Not everything belongs in memory. You can even link **another model** to the conversation and have it mark certain pieces of chat as `remember:` — this way you build up memory **only with important information**.
