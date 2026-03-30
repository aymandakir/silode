# Silode

Silode is a **Mac-first local AI app** inspired by Ollama, designed around a clean desktop UX and the **MLX** ecosystem for Apple Silicon.

## Highlights

- FastAPI backend with `/api/health`, `/api/status`, `/api/tags`, `/api/generate`, and `/api/chat`
- Polished browser-based desktop UI with a clean macOS-inspired layout
- Native desktop launcher via `pywebview`
- Graceful stub fallback while MLX models are still downloading or unavailable
- Smoke-tested API and UI routes

## Quick start

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

4. Run the local server:

   ```bash
   python run.py serve --reload
   ```

5. Open the app in your browser:

   ```bash
   open http://127.0.0.1:11435
   ```

## Native macOS desktop mode

Launch the desktop window directly:

```bash
python run.py desktop
```

Build a distributable macOS app bundle:

```bash
./scripts/build_macos_app.sh
```

This creates:

```text
dist/Silode.app
```

A GitHub Actions workflow at `.github/workflows/macos-app.yml` also builds and uploads a downloadable `Silode-macOS-app` artifact on each push to `main`.

## API examples

### Health

```bash
curl http://127.0.0.1:11435/api/health
```

### Status

```bash
curl http://127.0.0.1:11435/api/status
```

### Chat

```bash
curl -X POST http://127.0.0.1:11435/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Give me a crisp product pitch for Silode."}
    ]
  }'
```

## Notes

- Best results come from Apple Silicon with MLX-compatible quantized models.
- Until a model is cached and ready, Silode falls back to a stub response so the UI and app shell remain usable.
- This is now a stronger product-style prototype, ready for continued iteration into a fuller macOS assistant.
