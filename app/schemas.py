from __future__ import annotations

from typing import Any, Literal, Optional

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


class StatusResponse(BaseModel):
    app_name: str
    display_name: str
    backend: str
    default_model: str
    models: list[TagInfo]
    suggestions: list[str]
    desktop_ready: bool


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


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    messages: list[ChatMessage] = Field(..., min_length=1)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    model: str
    message: ChatMessage
    backend: str
    done: bool = True
