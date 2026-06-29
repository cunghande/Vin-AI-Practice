"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.search_client = SearchClient()
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        query = state.request.query
        max_sources = state.request.max_sources

        logger.info(f"ResearcherAgent running search for query: {query}")
        
        # 1. Retrieve sources
        sources = self.search_client.search(query, max_results=max_sources)
        state.sources = sources

        # 2. Format sources for LLM prompt
        formatted_sources = []
        for idx, doc in enumerate(sources, 1):
            formatted_sources.append(
                f"[Source {idx}]\n"
                f"Title: {doc.title}\n"
                f"URL: {doc.url or 'N/A'}\n"
                f"Snippet: {doc.snippet}\n"
            )
        sources_text = "\n".join(formatted_sources)

        # 3. Request LLM to synthesize research notes
        system_prompt = (
            "You are the Researcher Agent.\n"
            "Your task is to review the search results and compile concise, objective research notes.\n"
            "Organize the notes logically and cite your sources using the format [Source X] (where X is the number of the source).\n"
            "Focus on factual information, main themes, and key claims in the documents."
        )

        user_prompt = (
            f"User Query: {query}\n\n"
            f"Search Results:\n{sources_text}"
        )

        logger.info("ResearcherAgent synthesizing research notes via LLM.")
        llm_res = self.llm.complete(system_prompt, user_prompt)
        notes = llm_res.content

        # 4. Save results to state
        state.research_notes = notes
        
        metadata = {
            "sources_found": len(sources),
            "input_tokens": llm_res.input_tokens,
            "output_tokens": llm_res.output_tokens,
            "cost_usd": llm_res.cost_usd
        }
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=notes,
                metadata=metadata
            )
        )
        
        state.add_trace_event(
            "researcher",
            {"sources_count": len(sources), "cost_usd": llm_res.cost_usd}
        )
        
        logger.info(f"ResearcherAgent finished. Found {len(sources)} sources.")
        return state

