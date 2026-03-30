from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings

try:
    from mlx_lm import generate as mlx_generate
    from mlx_lm import load as mlx_load
except Exception:  # pragma: no cover - optional dependency during bootstrap
    mlx_generate = None
    mlx_load = None


@dataclass
class GenerationResult:
    text: str
    backend: str


class LocalEngine:
    def __init__(self) -> None:
        self._loaded_model_name: str | None = None
        self._model = None
        self._tokenizer = None

    @property
    def backend_name(self) -> str:
        return "mlx" if mlx_generate and mlx_load else "stub"

    def list_models(self) -> list[str]:
        settings = get_settings()
        configured = [item.strip() for item in settings.available_models.split(",") if item.strip()]
        models = {settings.default_model, *configured}
        return sorted(models)

    def _ensure_model(self, model_name: str) -> None:
        if not mlx_generate or not mlx_load:
            raise RuntimeError(
                "MLX runtime is unavailable. Install requirements on a MacBook to enable generation."
            )

        if self._loaded_model_name == model_name and self._model is not None and self._tokenizer is not None:
            return

        self._model, self._tokenizer = mlx_load(model_name)
        self._loaded_model_name = model_name

    def generate(
        self,
        *,
        model_name: str,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> GenerationResult:
        settings = get_settings()
        preview = prompt.strip().replace("\n", " ")[:200]

        if not mlx_generate or not mlx_load:
            if settings.allow_stub_runtime:
                return GenerationResult(
                    text=f"[stub:{model_name}] MLX is not active yet. Prompt received: {preview}",
                    backend="stub",
                )
            raise RuntimeError(
                "MLX runtime is unavailable and stub mode is disabled."
            )

        try:
            self._ensure_model(model_name)
            text = mlx_generate(
                self._model,
                self._tokenizer,
                prompt=prompt,
                max_tokens=max_tokens or settings.max_tokens,
                temp=temperature if temperature is not None else settings.temperature,
                verbose=False,
            )
            return GenerationResult(text=text, backend="mlx")
        except Exception as exc:
            if settings.allow_stub_runtime:
                return GenerationResult(
                    text=(
                        f"[stub:{model_name}] MLX fallback engaged after {exc.__class__.__name__}. "
                        f"Prompt received: {preview}"
                    ),
                    backend="stub",
                )
            raise


engine = LocalEngine()
