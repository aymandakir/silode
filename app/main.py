from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.engine import engine
from app.schemas import GenerateRequest, GenerateResponse, HealthResponse, TagInfo, TagListResponse

settings = get_settings()
app = FastAPI(title="Silode", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "message": "Silode is running.",
        "docs_hint": "Use /api/health, /api/tags, and /api/generate.",
    }


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        backend=engine.backend_name,
        default_model=settings.default_model,
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
