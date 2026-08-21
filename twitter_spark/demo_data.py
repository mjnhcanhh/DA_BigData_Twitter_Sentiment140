from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


POSITIVE = [
    "I love this amazing product",
    "What a great and wonderful day",
    "I really enjoyed this experience",
    "Feeling happy and excited today",
    "This movie was excellent and fun",
    "The service was good and friendly",
    "Everything works perfectly for me",
    "Such a beautiful pleasant surprise",
]

NEGATIVE = [
    "I hate this awful product",
    "What a terrible and horrible day",
    "I really disliked this experience",
    "Feeling sad and disappointed today",
    "This movie was bad and boring",
    "The service was poor and rude",
    "Nothing works and I am frustrated",
    "Such an ugly unpleasant surprise",
]


def generate_demo_csv(path: Path, rows: int = 400, seed: int = 42) -> int:
    """Create a labelled synthetic CSV for smoke tests; never use it as report evidence."""
    if rows < 100:
        raise ValueError("Demo data needs at least 100 rows so every split has both labels.")

    rng = random.Random(seed)
    start = datetime(2009, 4, 6, 8, 0, 0)
    records: list[list[object]] = []
    for index in range(rows):
        positive = index % 2 == 0
        label = 4 if positive else 0
        phrase = rng.choice(POSITIVE if positive else NEGATIVE)
        link_or_mention = " @demo_user http://example.com" if index % 17 == 0 else ""
        text = f"{phrase}; sample number {index}{link_or_mention}"
        moment = start + timedelta(hours=(index * 7) % (24 * 8), seconds=index % 60)
        zone = "PDT" if index % 3 else "PST"
        date_text = moment.strftime(f"%a %b %d %H:%M:%S {zone} %Y")
        records.append(
            [label, str(1_000_000 + index), date_text, "NO_QUERY", f"user_{index % 53}", text]
        )

    rng.shuffle(records)
    # Deliberate quality cases for the preprocessing log.
    records.append(records[0].copy())  # duplicate ID
    records.append([0, "9900001", "not-a-date", "NO_QUERY", "date_case", "bad delay sample"])
    records.append([4, "9900002", "Mon Apr 06 10:00:00 PDT 2009", "NO_QUERY", "empty_case", ""])
    records.append([0, "9900003", "Mon Apr 06 11:00:00 PDT 2009", "NO_QUERY", "conflict_a", "same conflicting statement"])
    records.append([4, "9900004", "Mon Apr 06 12:00:00 PDT 2009", "NO_QUERY", "conflict_b", "same conflicting statement"])

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="ISO-8859-1") as handle:
        csv.writer(handle).writerows(records)
    return len(records)

