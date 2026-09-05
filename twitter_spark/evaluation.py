from __future__ import annotations

from typing import Mapping, Tuple


CellMap = Mapping[Tuple[int, int], int]


def metrics_from_cells(cells: CellMap) -> dict:
    total = sum(int(value) for value in cells.values())
    correct = sum(int(cells.get((label, label), 0)) for label in (0, 1))
    result: dict = {
        "rows": total,
        "accuracy": correct / total if total else 0.0,
        "per_class": {},
    }
    f1_values = []
    weighted_f1_sum = 0.0
    for label in (0, 1):
        tp = int(cells.get((label, label), 0))
        fp = int(cells.get((1 - label, label), 0))
        fn = int(cells.get((label, 1 - label), 0))
        support = tp + fn
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / support if support else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        result["per_class"][str(label)] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
        f1_values.append(f1)
        weighted_f1_sum += f1 * support
    result["macro_f1"] = sum(f1_values) / 2
    result["weighted_f1"] = weighted_f1_sum / total if total else 0.0
    result["confusion_matrix"] = [
        [int(cells.get((actual, predicted), 0)) for predicted in (0, 1)]
        for actual in (0, 1)
    ]
    result["confusion_matrix_orientation"] = (
        "rows=actual [negative, positive], columns=predicted [negative, positive]"
    )
    return result


def evaluate_predictions(predictions) -> dict:
    cells = {
        (int(row["label"]), int(row["prediction"])): int(row["count"])
        for row in predictions.groupBy("label", "prediction").count().collect()
    }
    return metrics_from_cells(cells)

