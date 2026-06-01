from typing import Any, Dict

from src.core.llm_provider import LLMProvider
from src.telemetry.metrics import tracker


class BaselineChatbot:
    """Minimal chatbot baseline with no tool access."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def run(self, user_input: str) -> str:
        result: Dict[str, Any] = self.llm.generate(
            user_input,
            system_prompt=(
                "You are a helpful chatbot. Answer directly from your own knowledge. "
                "You cannot call external tools."
            ),
        )
        tracker.track_request(
            result.get("provider", "unknown"),
            self.llm.model_name,
            result.get("usage", {}),
            result.get("latency_ms", 0),
        )
        return result.get("content", "").strip()
