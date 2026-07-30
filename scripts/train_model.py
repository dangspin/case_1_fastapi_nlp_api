"""Train the saved classifier and export the supporting keyword chart."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.classifier import train_classifier  # noqa: E402
from app.rules import STOPWORDS, TOKEN_PATTERN  # noqa: E402


DATA_PATH = PROJECT_ROOT / "data" / "training_examples.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "intent_classifier.joblib"
SUMMARY_PATH = PROJECT_ROOT / "outputs" / "keyword_summary.png"


def _keyword_counts(data: pd.DataFrame) -> Counter[str]:
    counts: Counter[str] = Counter()
    for text in data["text"].astype(str):
        seen: set[str] = set()
        for token in TOKEN_PATTERN.findall(text.lower()):
            if token in STOPWORDS or token in seen:
                continue
            seen.add(token)
            counts[token] += 1
    return counts


def build_keyword_summary(data_path: Path, output_path: Path) -> None:
    data = pd.read_csv(data_path)
    counts = _keyword_counts(data).most_common(10)
    labels = [label for label, _count in reversed(counts)]
    values = [value for _label, value in reversed(counts)]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots(figsize=(10, 5), facecolor="#F5F8FC")
    axis.barh(labels, values, color="#2F80ED")
    axis.set_title("Synthetic Ticket Keyword Summary", loc="left", fontsize=17, fontweight="bold", color="#102A43")
    axis.set_xlabel("Number of training messages", color="#243B53")
    axis.set_ylabel("")
    axis.grid(axis="x", color="#D9E2EC", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_visible(False)
    axis.spines["bottom"].set_color("#D9E2EC")
    axis.tick_params(colors="#243B53")
    fig.text(0.01, 0.01, "Synthetic training examples • Supporting visual only", color="#627D98", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="#F5F8FC")
    plt.close(fig)


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    model = train_classifier(DATA_PATH, MODEL_PATH)
    build_keyword_summary(DATA_PATH, SUMMARY_PATH)
    print(f"Trained {model.__class__.__name__} on {len(data)} synthetic examples.")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved keyword summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()

