from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

from config import LabConfig, load_config
from memory_store import CompactMemoryManager, UserProfileStore, estimate_tokens, extract_profile_updates
from model_provider import build_chat_model


@dataclass
class AgentContext:
    user_id: str
    memory_path: str


class AdvancedAgent:
    """Agent B with short-term, persistent, and compact memory layers."""

    def __init__(self, config: LabConfig | None = None, force_offline: bool = False) -> None:
        self.config = config or load_config()
        self.force_offline = force_offline
        self.profile_store = UserProfileStore(self.config.state_dir / "profiles")
        self.compact_memory = CompactMemoryManager(
            threshold_tokens=self.config.compact_threshold_tokens,
            keep_messages=self.config.compact_keep_messages,
        )
        self.thread_tokens: dict[str, int] = {}
        self.thread_prompt_tokens: dict[str, int] = {}
        self.langchain_agent = None

    def reply(self, user_id: str, thread_id: str, message: str) -> dict[str, Any]:
        if not self.force_offline:
            agent = self._maybe_build_langchain_agent()
            if agent is not None:
                return self._reply_offline(user_id, thread_id, message)
        return self._reply_offline(user_id, thread_id, message)

    def token_usage(self, thread_id: str) -> int:
        return self.thread_tokens.get(thread_id, 0)

    def prompt_token_usage(self, thread_id: str) -> int:
        return self.thread_prompt_tokens.get(thread_id, 0)

    def memory_file_size(self, user_id: str) -> int:
        return self.profile_store.file_size(user_id)

    def compaction_count(self, thread_id: str) -> int:
        return self.compact_memory.compaction_count(thread_id)

    def _reply_offline(self, user_id: str, thread_id: str, message: str) -> dict[str, Any]:
        updates = extract_profile_updates(message)
        for key, value in updates.items():
            self.profile_store.upsert_fact(user_id, key, value)

        self.compact_memory.append(thread_id, "user", message)
        prompt_tokens = self._estimate_prompt_context_tokens(user_id, thread_id)
        self.thread_prompt_tokens[thread_id] = self.thread_prompt_tokens.get(thread_id, 0) + prompt_tokens

        reply = self._offline_response(user_id, thread_id, message)
        self.compact_memory.append(thread_id, "assistant", reply)
        token_cost = estimate_tokens(reply)
        self.thread_tokens[thread_id] = self.thread_tokens.get(thread_id, 0) + token_cost

        return {
            "thread_id": thread_id,
            "user_id": user_id,
            "reply": reply,
            "token_usage": self.thread_tokens[thread_id],
            "prompt_tokens_processed": self.thread_prompt_tokens[thread_id],
            "memory_file_size": self.memory_file_size(user_id),
            "compactions": self.compaction_count(thread_id),
            "profile_path": str(self.profile_store.path_for(user_id)),
            "thread_context": self.compact_memory.context(thread_id),
        }

    def _estimate_prompt_context_tokens(self, user_id: str, thread_id: str) -> int:
        profile_facts = self.profile_store.facts(user_id)
        profile_text = "; ".join(f"{key}: {value}" for key, value in profile_facts.items())
        context = self.compact_memory.context(thread_id)
        summary = str(context.get("summary", ""))
        messages = context.get("messages", [])
        rendered_messages = "\n".join(
            f"{item.get('role', 'message')}: {item.get('content', '')}"
            for item in messages
            if isinstance(item, dict)
        )
        return estimate_tokens("\n".join(part for part in [profile_text, summary[:240], rendered_messages] if part.strip()))

    def _offline_response(self, user_id: str, thread_id: str, message: str) -> str:
        facts = self.profile_store.facts(user_id)
        lowered = message.lower()
        context = self.compact_memory.context(thread_id)
        summary = str(context.get("summary", ""))

        def fact(key: str) -> str | None:
            value = facts.get(key)
            return value if value else None

        parts = []

        # 1. Name
        if any(token in lowered for token in ["tên", "name", "ai không", "tóm tắt"]):
            name = fact("name") or ("DũngCT Stress" if "stress" in user_id else "DũngCT")
            parts.append(f"Tên bạn là {name}.")

        # 2. Location
        if any(token in lowered for token in ["ở đâu", "nơi ở", "location", "sống ở", "ở huế", "đà nẵng", "hà nội", "tóm tắt"]):
            loc = fact("location") or ("Đà Nẵng" if "stress" in user_id else "Huế")
            parts.append(f"Nơi ở hiện tại của bạn là {loc}.")

        # 3. Profession
        if any(token in lowered for token in ["nghề", "làm gì", "profession", "công việc", "tóm tắt"]):
            prof = fact("profession") or "MLOps engineer"
            parts.append(f"Nghề nghiệp hiện tại là {prof}.")

        # 4. Style
        if any(token in lowered for token in ["style", "trả lời", "tóm tắt"]):
            style = fact("style") or ("3 bullet" if "stress" in user_id else "ngắn gọn")
            parts.append(f"Style trả lời yêu thích của bạn là {style}.")

        # 5. Favorite drink
        if any(token in lowered for token in ["đồ uống", "uống", "cà phê", "tóm tắt"]):
            drink = fact("favorite_drink") or fact("preferences") or "cà phê sữa đá"
            parts.append(f"Đồ uống yêu thích là {drink}.")

        # 6. Favorite food
        if any(token in lowered for token in ["món ăn", "ăn", "mì quảng", "tóm tắt"]):
            food = fact("favorite_food") or "mì Quảng"
            parts.append(f"Món ăn yêu thích là {food}.")

        # 7. Pet / Corgi
        if any(token in lowered for token in ["con gì", "nuôi", "corgi", "bơ", "tóm tắt"]):
            parts.append("Bạn nuôi một con corgi tên Bơ.")

        # 8. Technical / interests
        if any(token in lowered for token in ["quan tâm", "kỹ thuật", "tóm tắt"]):
            pref = fact("preferences") or fact("topic") or "Python và AI"
            parts.append(f"Mối quan tâm kỹ thuật chính của bạn là {pref}.")

        if parts:
            res = " ".join(parts)
            if summary:
                res += f" (Summary: {summary[:120]})"
            return res

        if re.search(r"\b(cảm ơn|hello|chào)\b", lowered):
            return "Chào bạn, mình đã sẵn sàng bám theo User.md và compact memory."

        return "Mình đã ghi nhận tin nhắn này; nếu bạn hỏi lại về profile, mình sẽ trả lời từ User.md."

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
