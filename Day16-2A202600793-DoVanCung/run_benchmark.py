from __future__ import annotations
import json
from pathlib import Path
import typer
from rich import print
from rich.table import Table
from src.reflexion_lab.agents import ReActAgent, ReflexionAgent
from src.reflexion_lab.reporting import build_report, save_report
from src.reflexion_lab.runtimes import MockRuntime, OpenAIRuntime
from src.reflexion_lab.utils import load_dataset, save_jsonl
app = typer.Typer(add_completion=False)

@app.command()
def main(
    dataset: str = "data/hotpot_mini.json",
    out_dir: str = "outputs/sample_run",
    reflexion_attempts: int = 3,
    repeat: int = 1,
    mode: str = "mock",
    model: str = "",
    limit: int = 0,
    key_prompt: str = "hidden",
) -> None:
    examples = load_dataset(dataset)
    if repeat < 1:
        raise typer.BadParameter("repeat must be at least 1")
    if limit < 0:
        raise typer.BadParameter("limit cannot be negative")
    if limit:
        examples = examples[:limit]
    examples = examples * repeat
    if mode == "mock":
        runtime = MockRuntime()
        report_mode = "mock"
    elif mode == "llm":
        if key_prompt not in {"hidden", "visible"}:
            raise typer.BadParameter("key_prompt must be either 'hidden' or 'visible'")
        runtime = OpenAIRuntime(model=model or None, key_prompt=key_prompt)
        report_mode = f"llm:{runtime.model}"
    else:
        raise typer.BadParameter("mode must be either 'mock' or 'llm'")
    react = ReActAgent(runtime=runtime)
    reflexion = ReflexionAgent(max_attempts=reflexion_attempts, runtime=runtime)
    react_records = [react.run(example) for example in examples]
    reflexion_records = [reflexion.run(example) for example in examples]
    all_records = react_records + reflexion_records
    out_path = Path(out_dir)
    save_jsonl(out_path / "react_runs.jsonl", react_records)
    save_jsonl(out_path / "reflexion_runs.jsonl", reflexion_records)
    report = build_report(all_records, dataset_name=Path(dataset).name, mode=report_mode)
    json_path, md_path = save_report(report, out_path)
    print(f"[green]Saved[/green] {json_path}")
    print(f"[green]Saved[/green] {md_path}")
    print_metrics(report.summary)
    print(json.dumps(report.summary, indent=2))


def print_metrics(summary: dict) -> None:
    table = Table(title="Benchmark Metrics")
    table.add_column("Metric")
    table.add_column("ReAct", justify="right")
    table.add_column("Reflexion", justify="right")
    table.add_column("Delta", justify="right")

    react = summary.get("react", {})
    reflexion = summary.get("reflexion", {})
    delta = summary.get("delta_reflexion_minus_react", {})
    rows = [
        ("Records", "count", "count", ""),
        ("Correct", "correct", "correct", ""),
        ("EM", "em", "em", "em_abs"),
        ("Avg attempts", "avg_attempts", "avg_attempts", "attempts_abs"),
        ("Total tokens", "total_token_estimate", "total_token_estimate", "tokens_abs"),
        ("Avg tokens", "avg_token_estimate", "avg_token_estimate", "avg_tokens_abs"),
        ("Total latency ms", "total_latency_ms", "total_latency_ms", "latency_abs"),
        ("Avg latency ms", "avg_latency_ms", "avg_latency_ms", "avg_latency_abs"),
    ]
    for label, react_key, reflexion_key, delta_key in rows:
        table.add_row(
            label,
            str(react.get(react_key, 0)),
            str(reflexion.get(reflexion_key, 0)),
            str(delta.get(delta_key, "")),
        )
    print(table)

if __name__ == "__main__":
    app()
