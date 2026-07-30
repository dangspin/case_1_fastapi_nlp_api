"""Stable request and response schemas for the FastAPI service."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """User-provided unstructured support message."""

    text: str = Field(..., min_length=1, max_length=5000, description="Customer support message")

    @field_validator("text", mode="before")
    @classmethod
    def trim_text(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("text must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text must not be blank")
        return cleaned


class EntityFields(BaseModel):
    """First matching structured fields extracted from the message."""

    order_id: str | None = None
    email: str | None = None
    phone: str | None = None
    amount: str | None = None
    date: str | None = None


class AnalyzeResponse(BaseModel):
    """Workflow-ready classification and extraction result."""

    category: Literal["billing", "delivery", "technical"]
    priority: Literal["low", "medium", "high"]
    entities: EntityFields
    keywords: list[str] = Field(default_factory=list, max_length=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    needs_review: bool


class HealthResponse(BaseModel):
    """Minimal service and model status response."""

    status: Literal["ok"] = "ok"
    model_loaded: bool

