"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        research_notes = state.research_notes or "No research notes found."

        logger.info("AnalystAgent analyzing research notes.")

        system_prompt = (
            "You are the Analyst Agent.\n"
            "Your task is to turn raw research notes into structured insights.\n"
            "Analyze the content carefully and compile:\n"
            "1. Key Claims: What are the primary arguments/claims?\n"
            "2. Viewpoint Comparison: Compare differing techniques, perspectives, pros/cons, or viewpoints.\n"
            "3. Weak Evidence Flags: Identify any areas where evidence is weak, missing, or requires more details."
        )

        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{research_notes}"
        )

        llm_res = self.llm.complete(system_prompt, user_prompt)
        analysis = llm_res.content

        state.analysis_notes = analysis
        
        metadata = {
            "input_tokens": llm_res.input_tokens,
            "output_tokens": llm_res.output_tokens,
            "cost_usd": llm_res.cost_usd
        }
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=analysis,
                metadata=metadata
            )
        )
        
        state.add_trace_event(
            "analyst",
            {"cost_usd": llm_res.cost_usd}
        )

        logger.info("AnalystAgent finished processing.")
        return state

