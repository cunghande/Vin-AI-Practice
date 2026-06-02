import os
import re
import json
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5, prompt_version: str = "v2"):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.prompt_version = prompt_version
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            [
                f"- {tool['name']}({tool.get('args_schema', 'input')}): {tool['description']}"
                for tool in self.tools
            ]
        )
        if self.prompt_version == "v1":
            return f"""
You are an intelligent assistant. You can use tools.

Available tools:
{tool_descriptions}

Use this format:
Thought: your reasoning
Action: tool_name(arguments)
Observation: tool result
Final Answer: final response
"""

        return f"""
You are a careful ReAct agent. Solve the user's task by thinking, calling tools, and using observations.

Available tools:
{tool_descriptions}

Rules:
- Use a tool when the answer depends on inventory, price, discount, shipping, tax, or calculation data.
- Call exactly one tool per step.
- Tool calls must be plain text in this exact format: Action: tool_name({{"arg": "value"}})
- Use valid JSON inside the parentheses.
- Never invent a tool name. Never invent tool results.
- After you have enough observations, stop with: Final Answer: ...

Example:
User: I want 2 headphones with coupon SAVE10 shipped to Hanoi. What is the total?
Thought: I need the product price and weight first.
Action: get_product_info({{"item_name": "headphones"}})
Observation: {{"name": "headphones", "price": 80, "weight_kg": 0.5, "stock": 10}}
Thought: I need the coupon discount.
Action: get_discount({{"coupon_code": "SAVE10"}})
Observation: {{"coupon_code": "SAVE10", "discount_percent": 10}}
Thought: I need shipping cost.
Action: calc_shipping({{"weight_kg": 1.0, "destination": "Hanoi"}})
Observation: {{"destination": "Hanoi", "shipping_cost": 5}}
Thought: I can calculate final total.
Action: calculator({{"expression": "2*80*(1-10/100)+5"}})
Observation: {{"result": 149}}
Final Answer: The total is $149.
"""

    def _build_prompt(self, user_input: str, scratchpad: List[str]) -> str:
        if not scratchpad:
            return f"User: {user_input}"
        return f"User: {user_input}\n\nTrace so far:\n" + "\n".join(scratchpad)

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        self.history = []
        scratchpad = []

        for step in range(1, self.max_steps + 1):
            current_prompt = self._build_prompt(user_input, scratchpad)
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            content = result.get("content", "").strip()
            self.history.append({"step": step, "llm_output": content})

            tracker.track_request(
                result.get("provider", "unknown"),
                self.llm.model_name,
                result.get("usage", {}),
                result.get("latency_ms", 0),
            )
            logger.log_event("AGENT_STEP", {"step": step, "output": content})

            final_answer = self._parse_final_answer(content)
            if final_answer:
                logger.log_event("AGENT_END", {"steps": step, "status": "final_answer"})
                return final_answer

            action = self._parse_action(content)
            if not action:
                logger.log_event("AGENT_ERROR", {"step": step, "code": "PARSER_ERROR", "output": content})
                return "I could not parse the model action. Please retry with a clearer tool call format."

            tool_name, args = action
            observation = self._execute_tool(tool_name, args)
            scratchpad.append(content)
            scratchpad.append(f"Observation: {observation}")
            self.history[-1]["action"] = {"tool": tool_name, "args": args}
            self.history[-1]["observation"] = observation
            logger.log_event(
                "TOOL_OBSERVATION",
                {"step": step, "tool": tool_name, "args": args, "observation": observation},
            )

        logger.log_event("AGENT_END", {"steps": self.max_steps, "status": "timeout"})
        return "I reached the maximum number of reasoning steps before a final answer."

    def _parse_final_answer(self, text: str) -> Optional[str]:
        match = re.search(r"Final Answer\s*:\s*(.+)", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        return match.group(1).strip()

    def _parse_action(self, text: str) -> Optional[tuple[str, Dict[str, Any]]]:
        match = re.search(r"Action\s*:\s*([a-zA-Z_][\w]*)\s*\((.*?)\)\s*$", text, flags=re.DOTALL | re.MULTILINE)
        if not match:
            return None

        tool_name = match.group(1)
        raw_args = match.group(2).strip()
        if not raw_args:
            return tool_name, {}

        try:
            parsed = json.loads(raw_args)
        except json.JSONDecodeError:
            parsed = self._parse_legacy_args(raw_args)

        if not isinstance(parsed, dict):
            parsed = {"input": parsed}
        return tool_name, parsed

    def _parse_legacy_args(self, raw_args: str) -> Dict[str, Any]:
        args = {}
        for part in raw_args.split(","):
            if "=" not in part:
                return {"input": raw_args.strip().strip("\"'")}
            key, value = part.split("=", 1)
            args[key.strip()] = value.strip().strip("\"'")
        return args

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                try:
                    result = tool["func"](**args)
                    return json.dumps(result, ensure_ascii=False)
                except TypeError as exc:
                    logger.log_event("AGENT_ERROR", {"code": "TOOL_ARGUMENT_ERROR", "tool": tool_name, "args": args, "error": str(exc)})
                    return json.dumps({"error": "invalid_arguments", "detail": str(exc)})
                except Exception as exc:
                    logger.log_event("AGENT_ERROR", {"code": "TOOL_RUNTIME_ERROR", "tool": tool_name, "error": str(exc)})
                    return json.dumps({"error": "tool_runtime_error", "detail": str(exc)})

        logger.log_event("AGENT_ERROR", {"code": "HALLUCINATED_TOOL", "tool": tool_name})
        return json.dumps({"error": "tool_not_found", "tool": tool_name})
