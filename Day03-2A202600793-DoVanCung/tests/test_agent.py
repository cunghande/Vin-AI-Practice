import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import ReActAgent
from src.core.fake_provider import ScriptedProvider
from src.tools import get_tools


def test_agent_completes_multi_step_order():
    agent = ReActAgent(ScriptedProvider(), get_tools(), max_steps=6)

    answer = agent.run("I want 2 headphones with coupon SAVE10 shipped to Hanoi. What is the total?")

    assert "$149.00" in answer
    assert len(agent.history) == 5


def test_agent_reports_hallucinated_tool():
    agent = ReActAgent(ScriptedProvider(), get_tools())

    observation = agent._execute_tool("unknown_tool", {})

    assert "tool_not_found" in observation


def test_legacy_action_arguments_are_supported():
    agent = ReActAgent(ScriptedProvider(), get_tools())

    action = agent._parse_action('Thought: test\nAction: get_discount(coupon_code="SAVE10")')

    assert action == ("get_discount", {"coupon_code": "SAVE10"})
