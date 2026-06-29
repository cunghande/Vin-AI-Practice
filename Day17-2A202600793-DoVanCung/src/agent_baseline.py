from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import re

from config import LabConfig, load_config
from memory_store import estimate_tokens, extract_profile_updates
from model_provider import build_chat_model


@dataclass
class SessionState:
    messages: list[dict[str, str]] = field(default_factory=list)
    token_usage: int = 0
    prompt_tokens_processed: int = 0
    profile: dict[str, str] = field(default_factory=dict)


class BaselineAgent:
    """A short-term-memory-only agent used as the baseline."""

    def __init__(self, config: LabConfig | None = None, force_offline: bool = False) -> None:
        self.config = config or load_config()
        self.force_offline = force_offline
        self.sessions: dict[str, SessionState] = {}
        self.langchain_agent = None

    def reply(self, user_id: str, thread_id: str, message: str) -> dict[str, Any]:
        if not self.force_offline:
            agent = self._maybe_build_langchain_agent()
            if agent is not None:
                return self._reply_offline(thread_id, message)
        return self._reply_offline(thread_id, message)

    def token_usage(self, thread_id: str) -> int:
        return self.sessions.get(thread_id, SessionState()).token_usage

    def prompt_token_usage(self, thread_id: str) -> int:
        return self.sessions.get(thread_id, SessionState()).prompt_tokens_processed

    def compaction_count(self, thread_id: str) -> int:
        return 0

    def _reply_offline(self, thread_id: str, message: str) -> dict[str, Any]:
        session = self.sessions.setdefault(thread_id, SessionState())
        session.messages.append({"role": "user", "content": message})
        session.profile.update(extract_profile_updates(message))

        prompt_tokens = estimate_tokens(
            "\n".join(f"{item['role']}: {item['content']}" for item in session.messages)
        )
        session.prompt_tokens_processed += prompt_tokens

        reply = self._offline_response(session, message)
        session.messages.append({"role": "assistant", "content": reply})
        session.token_usage += estimate_tokens(reply)

        return {
            "thread_id": thread_id,
            "reply": reply,
            "token_usage": session.token_usage,
            "prompt_tokens_processed": session.prompt_tokens_processed,
            "session_messages": list(session.messages),
        }

    def _offline_response(self, session: SessionState, message: str) -> str:
        lowered = message.lower()
        facts = session.profile

        def answer_from_fact(key: str, fallback: str = "mình chưa thấy thông tin đó trong thread này") -> str:
            return facts.get(key, fallback)

        if any(token in lowered for token in ["tên", "name"]):
            name = answer_from_fact("name")
            style = facts.get("style")
            if style:
                return f"Tên bạn là {name}. Style bạn thích: {style}."
            return f"Tên bạn là {name}."
        if any(token in lowered for token in ["ở đâu", "nơi ở", "location", "sống ở"]):
            return f"Bạn đang ở {answer_from_fact('location')}."
        if any(token in lowered for token in ["nghề", "làm gì", "profession", "công việc"]):
            return f"Hiện bạn đang làm {answer_from_fact('profession')}."
        if "style" in lowered or "trả lời" in lowered:
            return f"Bạn thích style: {answer_from_fact('style')}."

        if session.profile:
            top_facts = ", ".join(f"{k}={v}" for k, v in list(session.profile.items())[:3])
            return f"Mình đã ghi nhận: {top_facts}. Nếu bạn hỏi lại, mình sẽ bám theo thread hiện tại."

        if re.search(r"\b(cảm ơn|hello|chào)\b", lowered):
            return "Chào bạn, mình sẵn sàng hỗ trợ."
        return "Mình đã nhận tin nhắn của bạn và sẽ bám theo ngữ cảnh trong thread này."

    def _maybe_build_langchain_agent(self):
        if self.langchain_agent is not None:
            return self.langchain_agent
        try:
            from langgraph.checkpoint.memory import InMemorySaver
            from langgraph.prebuilt import create_react_agent
        except Exception:
            return None

        try:
            model = build_chat_model(self.config.model)
        except Exception:
            return None

        self.langchain_agent = create_react_agent(model, tools=[], checkpointer=InMemorySaver())
        return self.langchain_agent
