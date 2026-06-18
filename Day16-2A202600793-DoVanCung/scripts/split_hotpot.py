from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


@app.command()
def main(
    source: str = "data/hotpot_data.json",
    dev_output: str = "data/hotpot_dev.json",
    test_output: str = "data/hotpot_test.json",
    dev_size: int = 100,
    seed: int = 42,
) -> None:
    if dev_size < 1:
        raise typer.BadParameter("dev_size must be positive")

    data = json.loads(Path(source).read_text(encoding="utf-8"))
    if dev_size >= len(data):
        raise typer.BadParameter("dev_size must be smaller than the dataset size")

    rng = random.Random(seed)
    by_difficulty: dict[str, list[dict]] = defaultdict(list)
    for item in data:
        by_difficulty[item["difficulty"]].append(item)

    for items in by_difficulty.values():
        rng.shuffle(items)

    dev_indexes = _stratified_dev_counts(by_difficulty, dev_size, len(data))
    dev: list[dict] = []
    test: list[dict] = []
    for difficulty, items in by_difficulty.items():
        split_at = dev_indexes[difficulty]
        dev.extend(items[:split_at])
        test.extend(items[split_at:])

    rng.shuffle(dev)
    rng.shuffle(test)

    _write_json(dev_output, dev)
    _write_json(test_output, test)
    typer.echo(f"Saved {len(dev)} dev examples to {dev_output}")
    typer.echo(f"Saved {len(test)} test examples to {test_output}")


def _stratified_dev_counts(
    by_difficulty: dict[str, list[dict]],
    dev_size: int,
    total_size: int,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    allocated = 0
    fractional: list[tuple[float, str]] = []
    for difficulty, items in by_difficulty.items():
        exact = dev_size * len(items) / total_size
        base = int(exact)
        counts[difficulty] = base
        allocated += base
        fractional.append((exact - base, difficulty))

    remaining = dev_size - allocated
    for _, difficulty in sorted(fractional, reverse=True)[:remaining]:
        counts[difficulty] += 1
    return counts


def _write_json(path_text: str, payload: list[dict]) -> None:
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    app()
