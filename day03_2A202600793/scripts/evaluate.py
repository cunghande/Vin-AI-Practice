import csv
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.agent.agent import ReActAgent
from src.chatbot import BaselineChatbot
from src.core.fake_provider import ScriptedProvider
from src.tools import get_tools


CASES = [
    {
        "id": "multi_step_order_iphone",
        "input": "I want to buy 2 iphone using coupon WINNER and ship to Hanoi. What is the final total?",
        "expected": "$1363.30",
    },
    {
        "id": "multi_step_order_headphones",
        "input": "I want 2 headphones with coupon SAVE10 shipped to Hanoi. What is the total?",
        "expected": "$149.00",
    },
    {
        "id": "simple_concept",
        "input": "Explain what a ReAct agent is in one sentence.",
        "expected": "tool",
    },
]


def is_success(output: str, expected: str) -> bool:
    return expected.lower() in output.lower()


def main() -> None:
    output_dir = PROJECT_ROOT / "report" / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "evaluation_results.csv"

    rows = []
    for case in CASES:
        chatbot = BaselineChatbot(ScriptedProvider())
        agent = ReActAgent(ScriptedProvider(), get_tools(), max_steps=6)

        chatbot_output = chatbot.run(case["input"])
        agent_output = agent.run(case["input"])

        rows.append(
            {
                "case_id": case["id"],
                "input": case["input"],
                "expected": case["expected"],
                "chatbot_output": chatbot_output,
                "chatbot_success": is_success(chatbot_output, case["expected"]),
                "agent_output": agent_output,
                "agent_success": is_success(agent_output, case["expected"]),
                "agent_steps": len(agent.history),
            }
        )

    with results_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    chatbot_success = sum(row["chatbot_success"] for row in rows)
    agent_success = sum(row["agent_success"] for row in rows)
    print(f"Wrote {results_path}")
    print(f"Chatbot success: {chatbot_success}/{len(rows)}")
    print(f"Agent success: {agent_success}/{len(rows)}")
    for row in rows:
        print(f"- {row['case_id']}: chatbot={row['chatbot_success']} agent={row['agent_success']} steps={row['agent_steps']}")


if __name__ == "__main__":
    main()
