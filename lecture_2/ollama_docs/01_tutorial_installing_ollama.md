# Ollama Tutorial 1

## Tutorial: Installing and Setting Up Ollama (Local LLM Runtime)

---

### What is Ollama?

Ollama is a **local runtime** that lets you download and run large language models (LLMs) directly on your own machine. It handles:

- **Model management** — downloading, caching, and updating models
- **Inference** — running the model to generate text
- **Local API** — a simple HTTP API for programmatic access

> You do **not** need Docker or complex GPU tooling to get started.

Ollama supports **CPU-only** setups and will automatically use your **GPU** if supported.

---

## Step 1: Download and Install Ollama

### macOS

1. Go to [https://ollama.com](https://ollama.com)
2. Download the macOS installer
3. Open the `.dmg` file
4. Drag **Ollama** into Applications
5. Launch Ollama once (this starts the background service)

Verify installation:

```bash
ollama --version
```

---

### Linux

Run the official install script:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This:

- Installs the Ollama binary
- Sets up a system service
- Starts Ollama automatically

Verify installation:

```bash
ollama --version
```

Check that the service is running:

```bash
ollama ps
```

---

### Windows

1. Go to [https://ollama.com](https://ollama.com)
2. Download the Windows installer
3. Run the installer
4. Restart your terminal (PowerShell or CMD)

Verify installation:

```bash
ollama --version
```

> Ollama runs as a **background service** on Windows.

---

## Step 2: Download Your Model

You can download a model through the Ollama interface or via the command line (see below).

---

## Step 3: Run Your First Model

Ollama uses a simple command:

```bash
ollama run <model-name>
```

**Example** (small, fast model):

```bash
ollama run llama3
```

### What Happens

1. Ollama **downloads** the model automatically
2. The model is **cached locally**
3. A **chat prompt** opens in your terminal

Type a message and press `Enter` to interact.

To exit:

```
Ctrl + D
```

> 💡 If you run it in the command prompt, you will also see its **chain of "thought"**. Later on we will learn a lot more about this.
