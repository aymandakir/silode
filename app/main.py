from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.engine import engine
from app.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    StatusResponse,
    TagInfo,
    TagListResponse,
)

settings = get_settings()
app = FastAPI(title="Silode", version="0.2.0")


def get_static_dir() -> Path:
    bundled_dir = getattr(sys, "_MEIPASS", None)
    if bundled_dir:
        candidate = Path(bundled_dir) / "app" / "static"
        if candidate.exists():
            return candidate
    return Path(__file__).resolve().parent / "static"


STATIC_DIR = get_static_dir()
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        backend=engine.backend_name,
        default_model=settings.default_model,
    )


@app.get("/api/status", response_model=StatusResponse)
def status() -> StatusResponse:
    models = [TagInfo(name=model_name, backend=engine.backend_name) for model_name in engine.list_models()]
    return StatusResponse(
        app_name=settings.app_name,
        display_name=settings.display_name,
        backend=engine.backend_name,
        default_model=settings.default_model,
        models=models,
        suggestions=[
            "Summarize my notes into action items.",
            "Rewrite this email in a calmer tone.",
            "Brainstorm a feature roadmap for a Mac app.",
        ],
        desktop_ready=True,
    )


@app.get("/api/tags", response_model=TagListResponse)
def tags() -> TagListResponse:
    return TagListResponse(
        models=[TagInfo(name=model_name, backend=engine.backend_name) for model_name in engine.list_models()]
    )


@app.post("/api/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    model_name = request.model or settings.default_model

    try:
        result = engine.generate(
            model_name=model_name,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
    except Exception as exc:  # pragma: no cover - runtime dependency failure
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return GenerateResponse(
        model=model_name,
        response=result.text,
        done=True,
        backend=result.backend,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    model_name = request.model or settings.default_model
    messages = [item.model_dump() for item in request.messages]

    try:
        result = engine.chat(
            model_name=model_name,
            messages=messages,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
    except Exception as exc:  # pragma: no cover - runtime dependency failure
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(
        model=model_name,
        message=ChatMessage(role="assistant", content=result.text),
        backend=result.backend,
        done=True,
    )
