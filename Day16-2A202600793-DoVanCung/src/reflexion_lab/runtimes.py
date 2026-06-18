from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from getpass import getpass
from typing import Generic, Protocol, TypeVar

from dotenv import load_dotenv

from .mock_runtime import actor_answer as mock_actor_answer
from .mock_runtime import evaluator as mock_evaluator
from .mock_runtime import reflector as mock_reflector
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .schemas import JudgeResult, QAExample, ReflectionEntry

T = TypeVar("T")


@dataclass
class RuntimeResult(Generic[T]):
    value: T
    token_count: int = 0
    latency_ms: int = 0


class AgentRuntime(Protocol):
    def actor_answer(
        self,
        example: QAExample,
        attempt_id: int,
        agent_type: str,
        reflection_memory: list[str],
    ) -> RuntimeResult[str]:
        ...

    def evaluator(self, example: QAExample, answer: str) -> RuntimeResult[JudgeResult]:
        ...

    def reflector(
        self,
        example: QAExample,
        attempt_id: int,
        judge: JudgeResult,
    ) -> RuntimeResult[ReflectionEntry]:
        ...


class MockRuntime:
    def actor_answer(
        self,
        example: QAExample,
        attempt_id: int,
        agent_type: str,
        reflection_memory: list[str],
    ) -> RuntimeResult[str]:
        value = mock_actor_answer(example, attempt_id, agent_type, reflection_memory)
        tokens = 320 + (attempt_id * 65) + (120 if agent_type == "reflexion" else 0)
        latency = 160 + (attempt_id * 40) + (90 if agent_type == "reflexion" else 0)
        return RuntimeResult(value=value, token_count=tokens, latency_ms=latency)

    def evaluator(self, example: QAExample, answer: str) -> RuntimeResult[JudgeResult]:
        return RuntimeResult(value=mock_evaluator(example, answer))

    def reflector(
        self,
        example: QAExample,
        attempt_id: int,
        judge: JudgeResult,
    ) -> RuntimeResult[ReflectionEntry]:
        return RuntimeResult(value=mock_reflector(example, attempt_id, judge))


class OpenAIRuntime:
    def __init__(self, model: str | None = None, key_prompt: str = "hidden") -> None:
        load_dotenv()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.4-nano")
        self.key_prompt = key_prompt
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "Missing OpenAI SDK. Run: python -m pip install -r requirements.txt"
                ) from exc
            api_key = os.getenv("OPENAI_API_KEY") or _prompt_api_key(self.key_prompt)
            if not api_key:
                raise RuntimeError("Missing OpenAI API key.")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def actor_answer(
        self,
        example: QAExample,
        attempt_id: int,
        agent_type: str,
        reflection_memory: list[str],
    ) -> RuntimeResult[str]:
        user_prompt = _actor_prompt(example, attempt_id, agent_type, reflection_memory)
        call = self._call(ACTOR_SYSTEM, user_prompt, max_output_tokens=120)
        return RuntimeResult(value=call.value.strip(), token_count=call.token_count, latency_ms=call.latency_ms)

    def evaluator(self, example: QAExample, answer: str) -> RuntimeResult[JudgeResult]:
        user_prompt = _evaluator_prompt(example, answer)
        call = self._call(EVALUATOR_SYSTEM, user_prompt, max_output_tokens=300)
        payload = _loads_json_object(call.value)
        judge = JudgeResult.model_validate(payload)
        return RuntimeResult(value=judge, token_count=call.token_count, latency_ms=call.latency_ms)

    def reflector(
        self,
        example: QAExample,
        attempt_id: int,
        judge: JudgeResult,
    ) -> RuntimeResult[ReflectionEntry]:
        user_prompt = _reflector_prompt(example, attempt_id, judge)
        call = self._call(REFLECTOR_SYSTEM, user_prompt, max_output_tokens=300)
        payload = _loads_json_object(call.value)
        payload.setdefault("attempt_id", attempt_id)
        reflection = ReflectionEntry.model_validate(payload)
        return RuntimeResult(value=reflection, token_count=call.token_count, latency_ms=call.latency_ms)

    def _call(self, system_prompt: str, user_prompt: str, max_output_tokens: int) -> RuntimeResult[str]:
        start = time.perf_counter()
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_output_tokens=max_output_tokens,
        )
        latency_ms = round((time.perf_counter() - start) * 1000)
        text = getattr(response, "output_text", "").strip()
        usage = getattr(response, "usage", None)
        token_count = _usage_total_tokens(usage)
        return RuntimeResult(value=text, token_count=token_count, latency_ms=latency_ms)


def _context_text(example: QAExample) -> str:
    return "\n\n".join(f"Title: {chunk.title}\nText: {chunk.text}" for chunk in example.context)


def _prompt_api_key(key_prompt: str) -> str:
    if key_prompt == "visible":
        return input("OpenAI API key (visible input): ").strip()
    print("OpenAI API key input is hidden. Paste may look blank; press Enter after pasting.")
    return getpass("OpenAI API key: ").strip()


def _actor_prompt(
    example: QAExample,
    attempt_id: int,
    agent_type: str,
    reflection_memory: list[str],
) -> str:
    memory = "\n".join(f"- {item}" for item in reflection_memory) or "None"
    return (
        f"Agent type: {agent_type}\n"
        f"Attempt: {attempt_id}\n"
        f"Question: {example.question}\n\n"
        f"Context:\n{_context_text(example)}\n\n"
        f"Reflection memory:\n{memory}\n\n"
        "Return only the final answer."
    )


def _evaluator_prompt(example: QAExample, answer: str) -> str:
    return (
        f"Question: {example.question}\n"
        f"Gold answer: {example.gold_answer}\n"
        f"Predicted answer: {answer}\n\n"
        "Return strict JSON for JudgeResult."
    )


def _reflector_prompt(example: QAExample, attempt_id: int, judge: JudgeResult) -> str:
    return (
        f"Attempt: {attempt_id}\n"
        f"Question: {example.question}\n"
        f"Gold answer: {example.gold_answer}\n"
        f"Evaluator reason: {judge.reason}\n"
        f"Missing evidence: {judge.missing_evidence}\n"
        f"Spurious claims: {judge.spurious_claims}\n\n"
        f"Context:\n{_context_text(example)}\n\n"
        "Return strict JSON for ReflectionEntry."
    )


def _loads_json_object(text: str) -> dict:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return JSON: {text}")
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError(f"LLM JSON must be an object: {text}")
    return payload


def _usage_total_tokens(usage: object | None) -> int:
    if usage is None:
        return 0
    total = getattr(usage, "total_tokens", None)
    if isinstance(total, int):
        return total
    input_tokens = getattr(usage, "input_tokens", None) or getattr(usage, "prompt_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", None) or getattr(usage, "completion_tokens", 0) or 0
    return int(input_tokens) + int(output_tokens)
