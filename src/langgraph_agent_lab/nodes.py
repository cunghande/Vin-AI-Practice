"""Node functions for the LangGraph workflow.

Each function receives AgentState and returns a partial state update dict.
Do NOT mutate input state — return new values only.

LLM REQUIREMENT:
- classify_node MUST use a real LLM call (structured output for intent classification)
- answer_node MUST use a real LLM call (grounded response generation)
- evaluate_node SHOULD use LLM-as-judge (bonus points; heuristic acceptable for base score)
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from .state import AgentState, make_event


# ─── EXAMPLE: working node (provided for reference) ──────────────────
def intake_node(state: AgentState) -> dict:
    """Normalize raw query. This node is provided as a working example."""
    query = state.get("query", "").strip()
    return {
        "query": query,
        "messages": [f"intake:{query[:40]}"],
        "events": [make_event("intake", "completed", "query normalized")],
    }


# ─── Pydantic model for structured LLM classification ────────────────
class IntentClassification(BaseModel):
    """Structured output model for LLM-based intent classification."""

    intent: str = Field(
        description=(
            "The classified intent of the support ticket query. "
            "Must be exactly one of: simple, tool, missing_info, risky, error"
        )
    )


# ─── 1. classify_node ────────────────────────────────────────────────
def classify_node(state: AgentState) -> dict:
    """Classify the query into a route using an LLM with structured output.

    Uses .with_structured_output() for reliable enum classification.
    Falls back to raw text parsing if structured output is not supported.
    Priority guide: risky > tool > missing_info > error > simple
    """
    from .llm import get_llm

    llm = get_llm()
    query = state.get("query", "")

    classification_prompt = (
        "You are a support-ticket classifier. Classify the following query into exactly one category.\n\n"
        "Categories (in STRICT priority order — if multiple could apply, pick the HIGHEST priority):\n"
        "1. risky — Actions with side effects: refunds, deletions, cancellations, sending emails, "
        "modifying accounts, any destructive or irreversible operations\n"
        "2. tool — Information lookups: order status, tracking numbers, search queries, "
        "database lookups, any query requesting specific data retrieval\n"
        "3. missing_info — Vague or incomplete queries that lack actionable context. "
        "The user hasn't specified what they need help with. Examples: 'fix it', 'help me', 'can you do that?'\n"
        "4. error — System failures, timeouts, crashes, service unavailable, processing errors. "
        "The query describes a technical failure or system malfunction\n"
        "5. simple — General questions answerable without tools or actions. "
        "FAQs, how-to questions, password resets, general information\n\n"
        f"Query: {query}\n\n"
        "Respond with ONLY the intent classification as a JSON object: "
        '{"intent": "<one of: simple, tool, missing_info, risky, error>"}'
    )

    valid_intents = {"simple", "tool", "missing_info", "risky", "error"}
    intent = "simple"  # default fallback

    # Try structured output first, then fall back to raw text parsing
    try:
        structured_llm = llm.with_structured_output(IntentClassification)
        result = structured_llm.invoke(classification_prompt)
        intent = result.intent.strip().lower()
    except Exception:
        # Fallback: parse raw LLM response
        try:
            response = llm.invoke(classification_prompt)
            raw_text = response.content if hasattr(response, "content") else str(response)
            raw_text = raw_text.strip().lower()
            # Try to extract intent from JSON-like response
            import json as _json
            try:
                parsed = _json.loads(raw_text)
                intent = parsed.get("intent", "simple").strip().lower()
            except _json.JSONDecodeError:
                # Try to find a valid intent keyword in the raw text
                for candidate in ["risky", "tool", "missing_info", "error", "simple"]:
                    if candidate in raw_text:
                        intent = candidate
                        break
        except Exception:
            intent = "simple"

    if intent not in valid_intents:
        intent = "simple"

    risk_level = "high" if intent == "risky" else "low"

    return {
        "route": intent,
        "risk_level": risk_level,
        "messages": [f"classify:{intent}"],
        "events": [make_event("classify", "completed", f"classified as {intent}", intent=intent)],
    }


# ─── 2. tool_node ────────────────────────────────────────────────────
def tool_node(state: AgentState) -> dict:
    """Execute a mock tool call with error simulation for retry testing.

    Simulates transient failures: if the route is "error" and attempt < 2,
    returns an error result to trigger the retry loop.
    """
    attempt = state.get("attempt", 0)
    route = state.get("route", "")
    query = state.get("query", "")

    # Simulate transient failure for error-route scenarios
    if route == "error" and attempt < 2:
        result = "ERROR: Transient failure — service temporarily unavailable. Please retry."
    else:
        # Mock success result based on query content
        if "order" in query.lower():
            result = f"Tool result: Order lookup completed. Order found — status: shipped, ETA: 2 business days."
        elif "delete" in query.lower() or "refund" in query.lower():
            result = f"Tool result: Action executed successfully for query: {query[:60]}"
        else:
            result = f"Tool result: Query processed successfully. Data retrieved for: {query[:60]}"

    return {
        "tool_results": [result],
        "messages": [f"tool:{result[:50]}"],
        "events": [make_event("tool", "completed", f"tool executed", result_preview=result[:80])],
    }


# ─── 3. evaluate_node ────────────────────────────────────────────────
def evaluate_node(state: AgentState) -> dict:
    """Evaluate tool results — the retry-loop gate.

    Checks whether the latest tool result contains error indicators.
    Sets evaluation_result to "needs_retry" or "success".
    """
    tool_results = state.get("tool_results", [])
    latest = tool_results[-1] if tool_results else ""

    # Heuristic: check for ERROR substring in the latest result
    if "ERROR" in latest.upper():
        evaluation_result = "needs_retry"
        message = "tool result contains error — needs retry"
    else:
        evaluation_result = "success"
        message = "tool result satisfactory"

    return {
        "evaluation_result": evaluation_result,
        "messages": [f"evaluate:{evaluation_result}"],
        "events": [make_event("evaluate", "completed", message, evaluation_result=evaluation_result)],
    }


# ─── 4. answer_node ──────────────────────────────────────────────────
def answer_node(state: AgentState) -> dict:
    """Generate a final response using an LLM, grounded in available context.

    Incorporates tool_results and approval decisions when available.
    """
    from .llm import get_llm

    llm = get_llm()

    query = state.get("query", "")
    tool_results = state.get("tool_results", [])
    approval = state.get("approval")

    # Build context from available information
    context_parts: list[str] = []
    if tool_results:
        context_parts.append("Tool results:\n" + "\n".join(f"  - {r}" for r in tool_results))
    if approval:
        status = "approved" if approval.get("approved") else "rejected"
        context_parts.append(f"Approval decision: {status} (reviewer: {approval.get('reviewer', 'N/A')})")

    context = "\n".join(context_parts) if context_parts else "No additional context available."

    prompt = (
        "You are a helpful customer support agent. Generate a concise, professional response "
        "to the user's query. Ground your answer in the available context.\n\n"
        f"User query: {query}\n\n"
        f"Available context:\n{context}\n\n"
        "Provide a clear, helpful response in 2-3 sentences."
    )

    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    return {
        "final_answer": answer,
        "messages": [f"answer:{answer[:50]}"],
        "events": [make_event("answer", "completed", "LLM-grounded answer generated")],
    }


# ─── 5. ask_clarification_node ───────────────────────────────────────
def ask_clarification_node(state: AgentState) -> dict:
    """Ask the user for more information when the query is vague or incomplete."""
    query = state.get("query", "")

    question = (
        f"I'd like to help, but I need more details. Your message \"{query}\" "
        "doesn't provide enough context for me to assist you. "
        "Could you please specify:\n"
        "- What product or service this is about?\n"
        "- What specific issue you're experiencing?\n"
        "- Any relevant order numbers or account details?"
    )

    return {
        "pending_question": question,
        "final_answer": question,
        "messages": [f"clarify:{question[:50]}"],
        "events": [make_event("clarify", "completed", "clarification requested")],
    }


# ─── 6. risky_action_node ────────────────────────────────────────────
def risky_action_node(state: AgentState) -> dict:
    """Prepare a risky action for human approval.

    Describes the proposed action and flags it for HITL review.
    """
    query = state.get("query", "")
    proposed = (
        f"Proposed risky action: '{query}'. "
        "This action involves side effects (e.g., refund, deletion, account modification) "
        "and requires human approval before execution."
    )

    return {
        "proposed_action": proposed,
        "messages": [f"risky_action:{query[:40]}"],
        "events": [make_event("risky_action", "completed", f"risky action prepared", action=query[:80])],
    }


# ─── 7. approval_node ────────────────────────────────────────────────
def approval_node(state: AgentState) -> dict:
    """Human-in-the-loop approval step.

    Default: mock approval (approved=True) so tests and CI run offline.
    Extension: set LANGGRAPH_INTERRUPT=true for real HITL with interrupt().
    """
    use_interrupt = os.getenv("LANGGRAPH_INTERRUPT", "").lower() == "true"

    if use_interrupt:
        try:
            from langgraph.types import interrupt

            decision = interrupt({
                "proposed_action": state.get("proposed_action", ""),
                "message": "Please approve or reject this action.",
            })
            approved = decision.get("approved", True) if isinstance(decision, dict) else True
            reviewer = decision.get("reviewer", "human") if isinstance(decision, dict) else "human"
            comment = decision.get("comment", "") if isinstance(decision, dict) else ""
        except Exception:
            approved = True
            reviewer = "mock-reviewer"
            comment = "Auto-approved (interrupt failed)"
    else:
        # Mock approval for CI/testing
        approved = True
        reviewer = "mock-reviewer"
        comment = "Auto-approved for testing"

    approval_decision: dict[str, Any] = {
        "approved": approved,
        "reviewer": reviewer,
        "comment": comment,
    }

    status_text = "approved" if approved else "rejected"

    return {
        "approval": approval_decision,
        "messages": [f"approval:{status_text}"],
        "events": [make_event("approval", "completed", f"action {status_text}", approved=approved)],
    }


# ─── 8. retry_or_fallback_node ───────────────────────────────────────
def retry_or_fallback_node(state: AgentState) -> dict:
    """Record a retry attempt. Increments the attempt counter.

    The routing function (route_after_retry) decides whether to retry or dead-letter
    based on attempt vs max_attempts.
    """
    attempt = state.get("attempt", 0) + 1
    max_attempts = state.get("max_attempts", 3)

    return {
        "attempt": attempt,
        "errors": [f"Retry attempt {attempt}/{max_attempts}: transient failure encountered"],
        "messages": [f"retry:attempt {attempt}/{max_attempts}"],
        "events": [make_event("retry", "completed", f"retry attempt {attempt}", attempt=attempt, max_attempts=max_attempts)],
    }


# ─── 9. dead_letter_node ─────────────────────────────────────────────
def dead_letter_node(state: AgentState) -> dict:
    """Handle unresolvable failures after max retries exceeded.

    Logs the failure and sets a final_answer explaining the dead-letter status.
    """
    attempt = state.get("attempt", 0)
    max_attempts = state.get("max_attempts", 3)

    answer = (
        f"This request could not be completed after exhausting all {max_attempts} retry attempts "
        f"(attempted {attempt} times). It has been moved to the dead-letter queue for manual review "
        "and escalation. A support specialist will follow up within 24 hours."
    )

    return {
        "final_answer": answer,
        "messages": [f"dead_letter:exhausted {attempt} attempts"],
        "events": [make_event("dead_letter", "completed", "moved to dead letter queue", attempts=attempt)],
    }


# ─── 10. finalize_node ───────────────────────────────────────────────
def finalize_node(state: AgentState) -> dict:
    """Emit a final audit event. All routes must pass through here before END."""
    return {
        "messages": [f"finalize:workflow complete"],
        "events": [make_event("finalize", "completed", "workflow finished")],
    }
