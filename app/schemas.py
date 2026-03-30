from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    backend: str
    default_model: str


class TagInfo(BaseModel):
    name: str
    backend: str


class TagListResponse(BaseModel):
    models: list[TagInfo]


class GenerateRequest(BaseModel):
    model: Optional[str] = None
    prompt: str = Field(..., min_length=1)
    stream: bool = False
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    options: Optional[dict[str, Any]] = None


class GenerateResponse(BaseModel):
    model: str
    response: str
    done: bool = True
    backend: str
