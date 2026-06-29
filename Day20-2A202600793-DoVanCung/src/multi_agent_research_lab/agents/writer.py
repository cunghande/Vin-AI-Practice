"""Writer agent skeleton."""

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


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        research_notes = state.research_notes or "No research notes found."
        analysis_notes = state.analysis_notes or "No analysis notes found."
        critic_feedback = state.critic_feedback or "No critic feedback found."

        logger.info("WriterAgent synthesizing final answer.")

        system_prompt = (
            "You are the Writer Agent.\n"
            "Your task is to write a final, comprehensive response to the user's query.\n"
            f"The target audience is: '{state.request.audience}'.\n"
            "Use the provided research notes, analysis notes, and critic feedback to synthesize a coherent markdown report.\n"
            "Include proper section headings and ensure all facts are cited using [Source X] references.\n"
            "Strive for high quality, clarity, and depth."
        )

        user_prompt = (
            f"User Query: {state.request.query}\n\n"
            f"Research Notes:\n{research_notes}\n\n"
            f"Analysis Notes:\n{analysis_notes}\n\n"
            f"Critic Feedback:\n{critic_feedback}"
        )

        llm_res = self.llm.complete(system_prompt, user_prompt)
        final_answer = llm_res.content

        state.final_answer = final_answer
        
        metadata = {
            "input_tokens": llm_res.input_tokens,
            "output_tokens": llm_res.output_tokens,
            "cost_usd": llm_res.cost_usd
        }
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=final_answer,
                metadata=metadata
            )
        )
        
        state.add_trace_event(
            "writer",
            {"cost_usd": llm_res.cost_usd}
        )

        logger.info("WriterAgent finished writing.")
        return state

