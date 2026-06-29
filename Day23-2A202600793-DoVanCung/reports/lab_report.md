# Day 08 Lab Report

## 1. Team / student

- Name: Do Van Cung
- Student ID: 2A202600793
- Date: 2026-06-29

## 2. Architecture

The LangGraph workflow follows a support-ticket agent pattern:

```
START → intake → classify → [conditional routing]
  simple       → answer → finalize → END
  tool         → tool → evaluate → [retry loop] → answer → finalize → END
  missing_info → clarify → finalize → END
  risky        → risky_action → approval → [HITL gate] → tool → ... → END
  error        → retry → [bounded retry] → tool/dead_letter → finalize → END
```

Key design decisions:
- **LLM-based classification** using `with_structured_output()` for reliable intent parsing
- **Bounded retry loop** with configurable `max_attempts` to prevent infinite loops
- **Mock HITL approval** for CI compatibility, with real `interrupt()` support via env var
- **Append-only audit events** for full traceability through the workflow

## 3. State schema

| Field | Reducer | Purpose |
|---|---|---|
| query | overwrite | Original user query |
| route | overwrite | Classification result (simple/tool/missing_info/risky/error) |
| attempt | overwrite | Current retry counter |
| max_attempts | overwrite | Retry ceiling (default 3) |
| final_answer | overwrite | LLM-generated response |
| evaluation_result | overwrite | Tool result quality (success/needs_retry) |
| pending_question | overwrite | Clarification question for vague queries |
| proposed_action | overwrite | Risky action description for approval |
| approval | overwrite | HITL decision dict {approved, reviewer, comment} |
| messages | append | Audit trail of node executions |
| tool_results | append | Accumulated tool outputs |
| errors | append | Error history for retry tracking |
| events | append | Structured audit events (LabEvent) |

## 4. Scenario results

- **Total scenarios**: 7
- **Success rate**: 85.7%
- **Avg nodes visited**: 6.3
- **Total retries**: 2
- **Total interrupts**: 2

| Scenario | Expected | Actual | Success | Retries | Interrupts |
|---|---|---|:---:|---:|---:|
| S01_simple | simple | simple | ✅ | 0 | 0 |
| S02_tool | tool | tool | ✅ | 0 | 0 |
| S03_missing | missing_info | missing_info | ✅ | 0 | 0 |
| S04_risky | risky | risky | ✅ | 0 | 1 |
| S05_error | error | error | ✅ | 2 | 0 |
| S06_delete | risky | risky | ✅ | 0 | 1 |
| S07_dead_letter | error | simple | ❌ | 0 | 0 |

## 5. Failure analysis

1. **Transient tool failures (retry loop)**: When a tool call returns an ERROR, the evaluate node detects it and routes to the retry node. The retry node increments the attempt counter, and `route_after_retry` checks `attempt < max_attempts`. If exceeded, the request is dead-lettered for manual review.

2. **Risky action without approval**: Risky routes (refunds, deletions) always pass through the approval_node HITL gate. In mock mode, actions are auto-approved. With `LANGGRAPH_INTERRUPT=true`, the graph pauses for real human review, preventing unauthorized side effects.

### Failed scenarios:

- **S07_dead_letter**: Expected `error`, got `simple`. Errors: none

## 6. Persistence / recovery evidence

- **MemorySaver** checkpointer used by default for in-memory state persistence
- **SQLite checkpointer** implemented via `build_checkpointer('sqlite')` with WAL mode
- Each scenario gets a unique `thread_id` (`thread-{scenario_id}`) for state isolation
- Checkpointer enables crash-resume: if a process is killed mid-graph, re-invoking with the same thread_id resumes from the last checkpoint

## 7. Extension work

- **SQLite persistence**: Full SQLite checkpointer with WAL mode for durability
- **Real HITL support**: `interrupt()` integration, toggled via `LANGGRAPH_INTERRUPT` env var
- **Structured LLM output**: Pydantic-based classification model for reliable intent parsing

## 8. Improvement plan

- Add **LLM-as-judge** in evaluate_node for smarter retry decisions based on result quality
- Implement **parallel fan-out** with `Send()` for concurrent multi-tool calls
- Build a **Streamlit UI** for real-time approval interface with action context display
- Add **time travel** with `get_state_history()` for debugging and state replay
- Implement **graph diagram** export via `graph.get_graph().draw_mermaid()`
