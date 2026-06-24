"""Optional critic agent skeleton for bonus work."""

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


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        research_notes = state.research_notes or "No research notes found."
        analysis_notes = state.analysis_notes or "No analysis notes found."

        logger.info("CriticAgent performing safety and quality review.")

        system_prompt = (
            "You are the Critic Agent.\n"
            "Your task is to inspect the analysis_notes against the research_notes and original source list.\n"
            "Provide a critical review covering:\n"
            "1. Fact-checking: Are claims consistent with the research notes?\n"
            "2. Citation Coverage: Are references correctly cited? Are there any unsupported assertions?\n"
            "3. Hallucination Checks: Identify any fabricated claims or logical flaws."
        )

        user_prompt = (
            f"Sources count: {len(state.sources)}\n\n"
            f"Research Notes:\n{research_notes}\n\n"
            f"Analysis Notes:\n{analysis_notes}"
        )

        llm_res = self.llm.complete(system_prompt, user_prompt)
        feedback = llm_res.content

        state.critic_feedback = feedback
        
        metadata = {
            "input_tokens": llm_res.input_tokens,
            "output_tokens": llm_res.output_tokens,
            "cost_usd": llm_res.cost_usd
        }
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=feedback,
                metadata=metadata
            )
        )
        
        state.add_trace_event(
            "critic",
            {"cost_usd": llm_res.cost_usd}
        )

        logger.info("CriticAgent finished reviewing.")
        return state

