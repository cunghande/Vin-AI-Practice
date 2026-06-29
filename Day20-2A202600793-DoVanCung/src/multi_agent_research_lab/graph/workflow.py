"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


import logging
from langgraph.graph import StateGraph, END

from multi_agent_research_lab.agents import (
    SupervisorAgent,
    ResearcherAgent,
    AnalystAgent,
    CriticAgent,
    WriterAgent
)
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.critic = CriticAgent()
        self.writer = WriterAgent()
        self.graph = self.build()

    def build(self) -> object:
        """Create a compiled LangGraph graph."""
        builder = StateGraph(ResearchState)

        # 1. Add nodes
        builder.add_node("supervisor", self.supervisor.run)
        builder.add_node("researcher", self.researcher.run)
        builder.add_node("analyst", self.analyst.run)
        builder.add_node("critic", self.critic.run)
        builder.add_node("writer", self.writer.run)

        # 2. Set entry point
        builder.set_entry_point("supervisor")

        # 3. Define routing logic
        def route_next(state: ResearchState) -> str:
            if not state.route_history:
                logger.warning("No route history found in supervisor decision. Routing to done.")
                return "done"
            
            return state.route_history[-1]

        # 4. Add conditional edges
        builder.add_conditional_edges(
            "supervisor",
            route_next,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "critic": "critic",
                "writer": "writer",
                "done": END
            }
        )

        # 5. Add direct edges from workers back to supervisor
        builder.add_edge("researcher", "supervisor")
        builder.add_edge("analyst", "supervisor")
        builder.add_edge("critic", "supervisor")
        builder.add_edge("writer", "supervisor")

        logger.info("Compiled Multi-Agent Workflow StateGraph successfully.")
        return builder.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        logger.info("Starting Multi-Agent Workflow execution.")
        result = self.graph.invoke(state)
        
        # Ensure we return a ResearchState object
        if isinstance(result, dict):
            return ResearchState.model_validate(result)
        return result

