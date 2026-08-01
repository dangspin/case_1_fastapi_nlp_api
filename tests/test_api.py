"""API, model, rule, and artifact smoke tests."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from app.classifier import load_classifier, predict_category
from app.extractor import extract_entities
from app.main import MODEL_PATH, app
from app.rules import detect_priority, extract_keywords, needs_review

MODEL = load_classifier(MODEL_PATH)
client = TestClient(app)


def test_saved_classifier_loads_and_classifies_three_categories() -> None:
    assert MODEL_PATH.is_file()
    assert predict_category("The invoice has an unexpected charge.", MODEL)[0] == "billing"
    assert predict_category("My package delivery is late.", MODEL)[0] == "delivery"
    assert predict_category("The application returns an error when I log in.", MODEL)[0] == "technical"


def test_entity_extraction_supports_all_fields_and_first_match() -> None:
    text = (
        "Order ORD-10482 and ORD-10483 are affected. Email customer@example.com. "
        "Call +44 20 7946 0958 about £49.99 on 2026-07-29."
    )
    entities = extract_entities(text)
    assert entities == {
        "order_id": "ORD-10482",
        "email": "customer@example.com",
        "phone": "+44 20 7946 0958",
        "amount": "£49.99",
        "date": "2026-07-29",
    }


def test_priority_rules_are_explicit_and_ordered() -> None:
    assert detect_priority("This is an urgent issue and the payment is declined.") == "high"
    assert detect_priority("I have a problem with a late delivery.") == "medium"
    assert detect_priority("Please tell me about my account.") == "low"


def test_confidence_review_threshold() -> None:
    assert needs_review(0.69) is True
    assert needs_review(0.70) is False
    assert needs_review(0.91) is False


def test_health_endpoint_reports_loaded_model() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_openapi_exposes_analyze_endpoint() -> None:
    schema = client.get("/openapi.json").json()
    assert "/analyze" in schema["paths"]
    assert "/health" in schema["paths"]


def test_vite_origin_is_allowed_by_cors() -> None:
    response = client.options(
        "/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_analyze_returns_stable_workflow_response() -> None:
    response = client.post(
        "/analyze",
        json={"text": "My order ORD-10482 has not arrived. Please contact me at customer@example.com."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"category", "priority", "entities", "keywords", "confidence", "needs_review"}
    assert payload["category"] == "delivery"
    assert payload["priority"] == "high"
    assert payload["entities"]["order_id"] == "ORD-10482"
    assert payload["entities"]["email"] == "customer@example.com"
    assert len(payload["keywords"]) <= 5
    assert 0 <= payload["confidence"] <= 1


def test_input_validation_rejects_blank_and_overlong_messages() -> None:
    assert client.post("/analyze", json={"text": "   "}).status_code == 422
    assert client.post("/analyze", json={"text": "x" * 5001}).status_code == 422


def test_missing_model_returns_service_unavailable(monkeypatch) -> None:
    import app.main as main_module

    monkeypatch.setattr(main_module, "CLASSIFIER", None)
    monkeypatch.setattr(main_module, "CLASSIFIER_LOAD_ERROR", "Run scripts/train_model.py first.")
    response = client.post("/analyze", json={"text": "Please help with my order."})
    assert response.status_code == 503
    assert "train_model.py" in response.json()["detail"]


def test_keyword_summary_and_cover_exist() -> None:
    assert (PROJECT_ROOT / "outputs" / "keyword_summary.png").is_file()
    cover_path = PROJECT_ROOT / "portfolio" / "cover.png"
    assert cover_path.is_file()
    from PIL import Image

    assert Image.open(cover_path).size == (1600, 1000)
