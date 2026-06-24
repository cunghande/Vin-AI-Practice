"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        max_iters = self.settings.max_iterations

        # Enforce hard iteration limit
        if state.iteration >= max_iters:
            logger.warning(f"Max iterations reached ({state.iteration}/{max_iters}). Stopping.")
            next_step = "done"
            state.record_route(next_step)
            state.add_trace_event("supervisor", {"decision": next_step, "reason": "max_iterations_reached"})
            return state

        # Prepare system prompt for routing decision
        system_prompt = (
            "You are the Supervisor Agent of a Multi-Agent Research System.\n"
            "Your job is to inspect the current Research State and decide the next node to invoke:\n"
            "- 'researcher' if sources are empty, or further search is required.\n"
            "- 'analyst' if sources are available but analysis_notes are missing or incomplete.\n"
            "- 'critic' if analysis_notes are available but critic_feedback is missing or needs a review.\n"
            "- 'writer' if critic_feedback is available but the final_answer is missing or needs synthesis.\n"
            "- 'done' if the final_answer is complete and matches the quality requirements.\n\n"
            f"Current iteration: {state.iteration} / {max_iters}\n"
            f"Route history: {state.route_history}\n\n"
            "Respond ONLY with one of these lowercase words: researcher, analyst, critic, writer, done.\n"
            "Do not include any punctuation, markdown, formatting, or extra explanation."
        )

        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Sources count: {len(state.sources)}\n"
            f"Research notes present: {state.research_notes is not None}\n"
            f"Analysis notes present: {state.analysis_notes is not None}\n"
            f"Critic feedback present: {state.critic_feedback is not None}\n"
            f"Final answer present: {state.final_answer is not None}\n"
        )

        try:
            llm_res = self.llm.complete(system_prompt, user_prompt)
            decision = llm_res.content.strip().lower()
            # Clean possible markdown formatting
            decision = decision.replace("`", "").replace("'", "").replace("\"", "")
            
            valid_routes = {"researcher", "analyst", "critic", "writer", "done"}
            if decision in valid_routes:
                next_step = decision
                reason = "llm_decision"
            else:
                logger.warning(f"Invalid LLM routing decision: {decision}. Falling back to rule-based routing.")
                next_step = self._fallback_routing(state)
                reason = "llm_invalid_fallback"
        except Exception as e:
            logger.error(f"Supervisor LLM call failed: {e}. Falling back to rule-based routing.")
            next_step = self._fallback_routing(state)
            reason = "llm_error_fallback"

        state.record_route(next_step)
        state.add_trace_event("supervisor", {"decision": next_step, "reason": reason, "iteration": state.iteration})
        logger.info(f"Supervisor routed next step to: {next_step} (Reason: {reason}, Iteration: {state.iteration})")
        return state

    def _fallback_routing(self, state: ResearchState) -> str:
        """Deterministic rule-based routing fallback."""
        if not state.sources or not state.research_notes:
            return "researcher"
        if not state.analysis_notes:
            return "analyst"
        if not state.critic_feedback:
            return "critic"
        if not state.final_answer:
            return "writer"
        return "done"

