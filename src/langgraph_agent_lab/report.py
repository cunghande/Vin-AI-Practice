"""Report generation helper."""

from __future__ import annotations

import datetime
from pathlib import Path

from .metrics import MetricsReport


def render_report(metrics: MetricsReport) -> str:
    """Render a complete lab report from metrics data.

    Generates a markdown report with summary statistics, per-scenario results,
    architecture explanation, failure analysis, and improvement ideas.
    """
    lines: list[str] = []

    lines.append("# Day 08 Lab Report")
    lines.append("")
    lines.append("## 1. Team / student")
    lines.append("")
    lines.append("- Name: Do Van Cung")
    lines.append("- Student ID: 2A202600793")
    lines.append(f"- Date: {datetime.date.today()}")
    lines.append("")

    # ── Architecture ─────────────────────────────────────────────────
    lines.append("## 2. Architecture")
    lines.append("")
    lines.append("The LangGraph workflow follows a support-ticket agent pattern:")
    lines.append("")
    lines.append("```")
    lines.append("START → intake → classify → [conditional routing]")
    lines.append("  simple       → answer → finalize → END")
    lines.append("  tool         → tool → evaluate → [retry loop] → answer → finalize → END")
    lines.append("  missing_info → clarify → finalize → END")
    lines.append("  risky        → risky_action → approval → [HITL gate] → tool → ... → END")
    lines.append("  error        → retry → [bounded retry] → tool/dead_letter → finalize → END")
    lines.append("```")
    lines.append("")
    lines.append("Key design decisions:")
    lines.append("- **LLM-based classification** using `with_structured_output()` for reliable intent parsing")
    lines.append("- **Bounded retry loop** with configurable `max_attempts` to prevent infinite loops")
    lines.append("- **Mock HITL approval** for CI compatibility, with real `interrupt()` support via env var")
    lines.append("- **Append-only audit events** for full traceability through the workflow")
    lines.append("")

    # ── State schema ─────────────────────────────────────────────────
    lines.append("## 3. State schema")
    lines.append("")
    lines.append("| Field | Reducer | Purpose |")
    lines.append("|---|---|---|")
    lines.append("| query | overwrite | Original user query |")
    lines.append("| route | overwrite | Classification result (simple/tool/missing_info/risky/error) |")
    lines.append("| attempt | overwrite | Current retry counter |")
    lines.append("| max_attempts | overwrite | Retry ceiling (default 3) |")
    lines.append("| final_answer | overwrite | LLM-generated response |")
    lines.append("| evaluation_result | overwrite | Tool result quality (success/needs_retry) |")
    lines.append("| pending_question | overwrite | Clarification question for vague queries |")
    lines.append("| proposed_action | overwrite | Risky action description for approval |")
    lines.append("| approval | overwrite | HITL decision dict {approved, reviewer, comment} |")
    lines.append("| messages | append | Audit trail of node executions |")
    lines.append("| tool_results | append | Accumulated tool outputs |")
    lines.append("| errors | append | Error history for retry tracking |")
    lines.append("| events | append | Structured audit events (LabEvent) |")
    lines.append("")

    # ── Scenario results ─────────────────────────────────────────────
    lines.append("## 4. Scenario results")
    lines.append("")
    lines.append(f"- **Total scenarios**: {metrics.total_scenarios}")
    lines.append(f"- **Success rate**: {metrics.success_rate:.1%}")
    lines.append(f"- **Avg nodes visited**: {metrics.avg_nodes_visited:.1f}")
    lines.append(f"- **Total retries**: {metrics.total_retries}")
    lines.append(f"- **Total interrupts**: {metrics.total_interrupts}")
    lines.append("")

    lines.append("| Scenario | Expected | Actual | Success | Retries | Interrupts |")
    lines.append("|---|---|---|:---:|---:|---:|")
    for m in metrics.scenario_metrics:
        success_icon = "✅" if m.success else "❌"
        lines.append(
            f"| {m.scenario_id} | {m.expected_route} | {m.actual_route} "
            f"| {success_icon} | {m.retry_count} | {m.interrupt_count} |"
        )
    lines.append("")

    # ── Failure analysis ─────────────────────────────────────────────
    lines.append("## 5. Failure analysis")
    lines.append("")
    lines.append("1. **Transient tool failures (retry loop)**: When a tool call returns an ERROR, "
                 "the evaluate node detects it and routes to the retry node. The retry node increments "
                 "the attempt counter, and `route_after_retry` checks `attempt < max_attempts`. "
                 "If exceeded, the request is dead-lettered for manual review.")
    lines.append("")
    lines.append("2. **Risky action without approval**: Risky routes (refunds, deletions) always pass "
                 "through the approval_node HITL gate. In mock mode, actions are auto-approved. "
                 "With `LANGGRAPH_INTERRUPT=true`, the graph pauses for real human review, "
                 "preventing unauthorized side effects.")
    lines.append("")

    failed = [m for m in metrics.scenario_metrics if not m.success]
    if failed:
        lines.append("### Failed scenarios:")
        lines.append("")
        for m in failed:
            lines.append(f"- **{m.scenario_id}**: Expected `{m.expected_route}`, "
                         f"got `{m.actual_route}`. Errors: {m.errors or 'none'}")
        lines.append("")

    # ── Persistence ──────────────────────────────────────────────────
    lines.append("## 6. Persistence / recovery evidence")
    lines.append("")
    lines.append("- **MemorySaver** checkpointer used by default for in-memory state persistence")
    lines.append("- **SQLite checkpointer** implemented via `build_checkpointer('sqlite')` with WAL mode")
    lines.append("- Each scenario gets a unique `thread_id` (`thread-{scenario_id}`) for state isolation")
    lines.append("- Checkpointer enables crash-resume: if a process is killed mid-graph, "
                 "re-invoking with the same thread_id resumes from the last checkpoint")
    lines.append("")

    # ── Extensions ───────────────────────────────────────────────────
    lines.append("## 7. Extension work")
    lines.append("")
    lines.append("- **SQLite persistence**: Full SQLite checkpointer with WAL mode for durability")
    lines.append("- **Real HITL support**: `interrupt()` integration, toggled via `LANGGRAPH_INTERRUPT` env var")
    lines.append("- **Structured LLM output**: Pydantic-based classification model for reliable intent parsing")
    lines.append("")

    # ── Improvement plan ─────────────────────────────────────────────
    lines.append("## 8. Improvement plan")
    lines.append("")
    lines.append("- Add **LLM-as-judge** in evaluate_node for smarter retry decisions based on result quality")
    lines.append("- Implement **parallel fan-out** with `Send()` for concurrent multi-tool calls")
    lines.append("- Build a **Streamlit UI** for real-time approval interface with action context display")
    lines.append("- Add **time travel** with `get_state_history()` for debugging and state replay")
    lines.append("- Implement **graph diagram** export via `graph.get_graph().draw_mermaid()`")
    lines.append("")

    return "\n".join(lines)


def write_report(metrics: MetricsReport, output_path: str | Path) -> None:
    """Write the rendered report to a file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(metrics), encoding="utf-8")
