from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, Any]],
    fieldnames: Sequence[str] | None = None,
) -> None:
    materialized = [dict(row) for row in rows]
    if fieldnames is None:
        fieldnames = list(materialized[0].keys()) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(materialized)


def spark_rows_to_dicts(rows: Iterable[Any]) -> list[dict[str, Any]]:
    return [row.asDict(recursive=True) for row in rows]

