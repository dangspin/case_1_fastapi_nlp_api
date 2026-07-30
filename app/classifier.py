"""TF-IDF and Logistic Regression classifier lifecycle."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


CATEGORIES = ("billing", "delivery", "technical")


def build_classifier() -> Pipeline:
    """Create the fixed, lightweight classifier used by the demo."""

    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42, C=10.0)),
        ]
    )


def _validate_training_data(data: pd.DataFrame) -> None:
    required_columns = {"text", "category"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Training data is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Training data must contain at least one example.")
    if data["text"].isna().any() or data["category"].isna().any():
        raise ValueError("Training data cannot contain null text or category values.")
    categories = set(data["category"].astype(str))
    if categories != set(CATEGORIES):
        raise ValueError(f"Training data categories must be exactly: {', '.join(CATEGORIES)}")
    counts = data["category"].value_counts()
    if any(counts.get(category, 0) < 2 for category in CATEGORIES):
        raise ValueError("Each category must contain at least two training examples.")


def train_classifier(data_path: Path | str, model_path: Path | str) -> Pipeline:
    """Train the classifier on the full synthetic dataset and save it."""

    data_path = Path(data_path)
    model_path = Path(model_path)
    data = pd.read_csv(data_path)
    _validate_training_data(data)

    model = build_classifier()
    model.fit(data["text"].astype(str), data["category"].astype(str))
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    return model


def load_classifier(model_path: Path | str) -> Pipeline:
    """Load the saved model without retraining it."""

    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(
            f"Saved classifier not found at {model_path}. Run scripts/train_model.py first."
        )
    model = joblib.load(model_path)
    if not hasattr(model, "predict") or not hasattr(model, "predict_proba"):
        raise ValueError("Saved classifier does not expose predict and predict_proba.")
    return model


def predict_category(text: str, model: Pipeline) -> tuple[str, float]:
    """Return the predicted category and maximum class probability."""

    prediction = str(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    confidence = float(max(probabilities))
    return prediction, confidence
