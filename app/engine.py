from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

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
        self._loaded_model_name: Optional[str] = None
        self._model = None
        self._tokenizer = None

    @property
    def is_available(self) -> bool:
        return bool(mlx_generate and mlx_load)

    @property
    def backend_name(self) -> str:
        return "mlx" if self.is_available else "stub"

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

    def _build_chat_prompt(
        self,
        *,
        messages: Sequence[dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        settings = get_settings()
        prompt_blocks = [
            f"System:\n{(system_prompt or settings.system_prompt).strip()}",
        ]

        for item in messages:
            role = item.get("role", "user").strip().title()
            content = item.get("content", "").strip()
            if content:
                prompt_blocks.append(f"{role}:\n{content}")

        prompt_blocks.append("Assistant:\n")
        return "\n\n".join(prompt_blocks)

    def generate(
        self,
        *,
        model_name: str,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> GenerationResult:
        settings = get_settings()
        preview = prompt.strip().replace("\n", " ")[:200]

        if not mlx_generate or not mlx_load:
            if settings.allow_stub_runtime:
                return GenerationResult(
                    text=f"[stub:{model_name}] MLX is not active yet. Prompt received: {preview}",
                    backend="stub",
                )
            raise RuntimeError("MLX runtime is unavailable and stub mode is disabled.")

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

    def chat(
        self,
        *,
        model_name: str,
        messages: Sequence[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> GenerationResult:
        prompt = self._build_chat_prompt(
            messages=messages,
            system_prompt=system_prompt,
        )
        return self.generate(
            model_name=model_name,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )


engine = LocalEngine()
