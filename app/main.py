"""FastAPI entrypoint for the customer-support NLP service."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .classifier import load_classifier, predict_category
from .extractor import extract_entities
from .rules import detect_priority, extract_keywords, needs_review
from .schemas import AnalyzeRequest, AnalyzeResponse, EntityFields, HealthResponse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "intent_classifier.joblib"

try:
    CLASSIFIER = load_classifier(MODEL_PATH)
    CLASSIFIER_LOAD_ERROR: str | None = None
except (FileNotFoundError, ValueError, OSError) as error:
    CLASSIFIER = None
    CLASSIFIER_LOAD_ERROR = str(error)


app = FastAPI(
    title="Customer Support Ticket Intelligence API",
    description="A lightweight hybrid NLP service for ticket routing and field extraction.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service availability and saved-model loading status."""

    return HealthResponse(model_loaded=CLASSIFIER is not None)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Classify, enrich, and prioritize one customer-support message."""

    if CLASSIFIER is None:
        detail = CLASSIFIER_LOAD_ERROR or "Classifier model is not loaded."
        raise HTTPException(status_code=503, detail=detail)

    category, confidence = predict_category(request.text, CLASSIFIER)
    entities = extract_entities(request.text)
    priority = detect_priority(request.text)
    keywords = extract_keywords(request.text, entities)

    return AnalyzeResponse(
        category=category,
        priority=priority,
        entities=EntityFields(**entities),
        keywords=keywords,
        confidence=round(confidence, 4),
        needs_review=needs_review(confidence),
    )
