import pytest
from unittest.mock import MagicMock

from multi_agent_research_lab.agents import (
    SupervisorAgent,
    ResearcherAgent,
    AnalystAgent,
    CriticAgent,
    WriterAgent
)
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


@pytest.fixture(autouse=True)
def mock_no_api_keys(monkeypatch) -> None:
    """Ensure tests run in Mock mode by clearing keys from settings."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("TAVILY_API_KEY", "")


def test_supervisor_runs_successfully() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    supervisor = SupervisorAgent()
    new_state = supervisor.run(state)
    assert new_state.route_history == ["researcher"]
    assert new_state.iteration == 1


def test_all_agents_run_successfully() -> None:
    state = ResearchState(request=ResearchQuery(query="Research GraphRAG state-of-the-art"))
    
    # 1. Researcher
    state = ResearcherAgent().run(state)
    assert len(state.sources) > 0
    assert state.research_notes is not None
    
    # 2. Analyst
    state = AnalystAgent().run(state)
    assert state.analysis_notes is not None
    
    # 3. Critic
    state = CriticAgent().run(state)
    assert state.critic_feedback is not None
    
    # 4. Writer
    state = WriterAgent().run(state)
    assert state.final_answer is not None

