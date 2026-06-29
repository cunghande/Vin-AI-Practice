from __future__ import annotations

import json
import random
from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


@app.command()
def main(
    source: str = "data/hotpot_dev_distractor_v1.json/hotpot_dev_distractor_v1.json",
    output: str = "data/hotpot_dev_qa.json",
    limit: int = 100,
    difficulty_strategy: str = "source",
    seed: int = 42,
) -> None:
    if limit < 0:
        raise typer.BadParameter("limit cannot be negative")
    if difficulty_strategy not in {"source", "balanced"}:
        raise typer.BadParameter("difficulty_strategy must be 'source' or 'balanced'")

    raw = json.loads(Path(source).read_text(encoding="utf-8"))
    difficulties: list[str] | None = None
    if difficulty_strategy == "balanced":
        rng = random.Random(seed)
        raw = rng.sample(raw, k=limit) if limit else raw[:]
        rng.shuffle(raw)
        difficulties = _balanced_difficulties(len(raw), rng)
    elif limit:
        raw = raw[:limit]

    converted = []
    for index, item in enumerate(raw):
        converted.append(
            {
                "qid": item["_id"],
                "difficulty": difficulties[index] if difficulties else _difficulty(item.get("level", "medium")),
                "question": item["question"],
                "gold_answer": item["answer"],
                "context": [
                    {"title": title, "text": " ".join(sentences)}
                    for title, sentences in item.get("context", [])
                ],
            }
        )

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(converted, indent=2, ensure_ascii=False), encoding="utf-8")
    typer.echo(f"Saved {len(converted)} examples to {out_path}")


def _balanced_difficulties(count: int, rng: random.Random) -> list[str]:
    labels = ["easy", "medium", "hard"]
    difficulties = [labels[index % len(labels)] for index in range(count)]
    rng.shuffle(difficulties)
    return difficulties


def _difficulty(value: str) -> str:
    value = value.lower()
    if value in {"easy", "medium", "hard"}:
        return value
    return "medium"


if __name__ == "__main__":
    app()
