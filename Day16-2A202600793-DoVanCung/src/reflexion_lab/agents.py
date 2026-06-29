from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
from .mock_runtime import FAILURE_MODE_BY_QID
from .runtimes import AgentRuntime, MockRuntime
from .schemas import AttemptTrace, QAExample, ReflectionEntry, RunRecord

@dataclass
class BaseAgent:
    agent_type: Literal["react", "reflexion"]
    max_attempts: int = 1
    runtime: AgentRuntime = field(default_factory=MockRuntime)

    def run(self, example: QAExample) -> RunRecord:
        reflection_memory: list[str] = []
        reflections: list[ReflectionEntry] = []
        traces: list[AttemptTrace] = []
        final_answer = ""
        final_score = 0
        for attempt_id in range(1, self.max_attempts + 1):
            answer_result = self.runtime.actor_answer(example, attempt_id, self.agent_type, reflection_memory)
            answer = answer_result.value
            judge_result = self.runtime.evaluator(example, answer)
            judge = judge_result.value
            token_estimate = answer_result.token_count + judge_result.token_count
            latency_ms = answer_result.latency_ms + judge_result.latency_ms
            trace = AttemptTrace(attempt_id=attempt_id, answer=answer, score=judge.score, reason=judge.reason, token_estimate=token_estimate, latency_ms=latency_ms)
            final_answer = answer
            final_score = judge.score
            if judge.score == 1:
                traces.append(trace)
                break
            if self.agent_type == "reflexion" and attempt_id < self.max_attempts:
                reflection_result = self.runtime.reflector(example, attempt_id, judge)
                reflection = reflection_result.value
                reflections.append(reflection)
                reflection_memory.append(reflection.next_strategy)
                trace.reflection = reflection
                trace.token_estimate += reflection_result.token_count
                trace.latency_ms += reflection_result.latency_ms
            traces.append(trace)
        total_tokens = sum(t.token_estimate for t in traces)
        total_latency = sum(t.latency_ms for t in traces)
        failure_mode = "none" if final_score == 1 else FAILURE_MODE_BY_QID.get(example.qid, "wrong_final_answer")
        return RunRecord(qid=example.qid, question=example.question, gold_answer=example.gold_answer, agent_type=self.agent_type, predicted_answer=final_answer, is_correct=bool(final_score), attempts=len(traces), token_estimate=total_tokens, latency_ms=total_latency, failure_mode=failure_mode, reflections=reflections, traces=traces)

class ReActAgent(BaseAgent):
    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        super().__init__(agent_type="react", max_attempts=1, runtime=runtime or MockRuntime())

class ReflexionAgent(BaseAgent):
    def __init__(self, max_attempts: int = 3, runtime: AgentRuntime | None = None) -> None:
        super().__init__(agent_type="reflexion", max_attempts=max_attempts, runtime=runtime or MockRuntime())
