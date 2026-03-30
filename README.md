# Silode

A local LLM runner for **MacBooks**, built as a lightweight Ollama-style API server on top of the **MLX** ecosystem.

## What this workspace includes

- FastAPI server with `/api/health`, `/api/tags`, and `/api/generate`
- MLX-backed inference path for Apple Silicon
- Graceful stub mode before a model is installed
- Simple CLI for serving and one-shot prompting
- Smoke tests for the API surface

## Quick start

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

4. Start the local server:

   ```bash
   python run.py serve --reload
   ```

The server defaults to `http://127.0.0.1:11435`.

## API examples

### Health check

```bash
curl http://127.0.0.1:11435/api/health
```

### List available models

```bash
curl http://127.0.0.1:11435/api/tags
```

### Generate text

```bash
curl -X POST http://127.0.0.1:11435/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
    "prompt": "Write a two-line haiku about MacBooks.",
    "stream": false
  }'
```

## Notes

- This is an **MVP starter** for a Mac-optimized local runtime, not a full Ollama replacement yet.
- For best performance, run on Apple Silicon and use quantized MLX-compatible models.
- If `mlx-lm` is not installed or a model is unavailable, the app falls back to a stub response so the workspace still boots cleanly.
