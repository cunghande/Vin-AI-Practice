from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from agent_advanced import AdvancedAgent
from agent_baseline import BaselineAgent
from config import load_config


@dataclass
class BenchmarkRow:
    agent_name: str
    agent_tokens_only: int
    prompt_tokens_processed: int
    recall_score: float
    response_quality: float
    memory_growth_bytes: int
    compactions: int


def load_conversations(path: Path) -> list[dict[str, Any]]:
    """Read JSON conversations from disk."""

    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def recall_points(answer: str, expected: list[str]) -> float:
    """Return 0 / 0.5 / 1 depending on how many expected facts appear."""

    if not expected:
        return 1.0 if answer.strip() else 0.0
    normalized = _normalize_text(answer)
    found = sum(1 for item in expected if _normalize_text(item) in normalized)
    if found == len(expected):
        return 1.0
    if found > 0:
        return 0.5
    return 0.0


def heuristic_quality(answer: str, expected: list[str]) -> float:
    """Lightweight quality score for offline mode."""

    if not answer.strip():
        return 0.0
    base = recall_points(answer, expected)
    if len(answer) < 240:
        base += 0.1
    if any(token in _normalize_text(answer) for token in ["mình đã ghi nhận", "mình đã lưu", "mình sẽ"]):
        base += 0.1
    return min(1.0, base)


def run_agent_benchmark(agent_name: str, agent, conversations: list[dict[str, Any]], config) -> BenchmarkRow:
    """Evaluate one agent over many conversations."""

    unique_users = sorted({conversation["user_id"] for conversation in conversations})
    memory_before = 0
    if hasattr(agent, "memory_file_size"):
        memory_before = sum(agent.memory_file_size(user_id) for user_id in unique_users)

    total_agent_tokens = 0
    total_prompt_tokens = 0
    recall_scores: list[float] = []
    quality_scores: list[float] = []
    thread_token_seen: dict[str, int] = {}
    thread_prompt_seen: dict[str, int] = {}
    thread_compaction_seen: dict[str, int] = {}
    total_compactions = 0

    def account(thread_id: str, result: dict[str, Any]) -> None:
        nonlocal total_agent_tokens, total_prompt_tokens, total_compactions
        token_now = int(result.get("token_usage", 0))
        prompt_now = int(result.get("prompt_tokens_processed", 0))
        compaction_now = int(result.get("compactions", 0))
        total_agent_tokens += token_now - thread_token_seen.get(thread_id, 0)
        total_prompt_tokens += prompt_now - thread_prompt_seen.get(thread_id, 0)
        total_compactions += compaction_now - thread_compaction_seen.get(thread_id, 0)
        thread_token_seen[thread_id] = token_now
        thread_prompt_seen[thread_id] = prompt_now
        thread_compaction_seen[thread_id] = compaction_now

    for conversation in conversations:
        user_id = conversation["user_id"]
        conv_id = conversation["id"]
        thread_id = f"{conv_id}-chat"

        for turn in conversation.get("turns", []):
            result = agent.reply(user_id, thread_id, turn)
            account(thread_id, result)

        for index, recall_question in enumerate(conversation.get("recall_questions", []), start=1):
            recall_thread = f"{conv_id}-recall-{index}"
            result = agent.reply(user_id, recall_thread, recall_question["question"])
            account(recall_thread, result)
            answer = str(result.get("reply", ""))
            recall_scores.append(recall_points(answer, recall_question.get("expected_contains", [])))
            quality_scores.append(heuristic_quality(answer, recall_question.get("expected_contains", [])))

    memory_after = memory_before
    if hasattr(agent, "memory_file_size"):
        memory_after = sum(agent.memory_file_size(user_id) for user_id in unique_users)

    recall_score = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0
    quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

    return BenchmarkRow(
        agent_name=agent_name,
        agent_tokens_only=total_agent_tokens,
        prompt_tokens_processed=total_prompt_tokens,
        recall_score=recall_score,
        response_quality=quality_score,
        memory_growth_bytes=max(0, memory_after - memory_before),
        compactions=total_compactions if hasattr(agent, "compaction_count") else 0,
    )


def format_rows(rows: list[BenchmarkRow]) -> str:
    """Print a markdown table."""

    header = (
        "| Agent | Agent tokens only | Prompt tokens processed | Cross-session recall | Response quality | Memory growth (bytes) | Compactions |"
    )
    divider = "|---|---:|---:|---:|---:|---:|---:|"
    body = [
        "| {agent_name} | {agent_tokens_only} | {prompt_tokens_processed} | {recall_score:.2f} | {response_quality:.2f} | {memory_growth_bytes} | {compactions} |".format(
            **row.__dict__
        )
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def main() -> None:
    """Run both benchmark suites."""

    config = load_config(Path(__file__).resolve().parent.parent)
    baseline = BaselineAgent(config=config, force_offline=True)
    advanced = AdvancedAgent(config=config, force_offline=True)

    standard_dataset = load_conversations(config.data_dir / "conversations.json")
    long_context_dataset = load_conversations(config.data_dir / "advanced_long_context.json")

    standard_rows = [
        run_agent_benchmark("Baseline", baseline, standard_dataset, config),
        run_agent_benchmark("Advanced", advanced, standard_dataset, config),
    ]
    stress_rows = [
        run_agent_benchmark("Baseline", BaselineAgent(config=config, force_offline=True), long_context_dataset, config),
        run_agent_benchmark("Advanced", AdvancedAgent(config=config, force_offline=True), long_context_dataset, config),
    ]

    print("## Standard Benchmark")
    print(format_rows(standard_rows))
    print()
    print("## Long-Context Stress Benchmark")
    print(format_rows(stress_rows))


if __name__ == "__main__":
    main()
