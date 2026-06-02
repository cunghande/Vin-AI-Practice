import re
import time
from typing import Any, Dict, Generator, Optional

from src.core.llm_provider import LLMProvider


class ScriptedProvider(LLMProvider):
    """Deterministic provider used for local tests and report generation."""

    def __init__(self):
        super().__init__(model_name="scripted-react-provider")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()
        content = self._respond(prompt, system_prompt or "")
        latency_ms = int((time.time() - start) * 1000)
        tokens = max(1, len((prompt + content).split()))
        return {
            "content": content,
            "usage": {
                "prompt_tokens": max(1, len(prompt.split())),
                "completion_tokens": max(1, len(content.split())),
                "total_tokens": tokens,
            },
            "latency_ms": latency_ms,
            "provider": "scripted",
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        yield self.generate(prompt, system_prompt)["content"]

    def _respond(self, prompt: str, system_prompt: str) -> str:
        if "You are a helpful chatbot" in system_prompt:
            return self._chatbot_answer(prompt)

        lower_prompt = prompt.lower()
        if "explain what a react agent" in lower_prompt:
            return "Thought: This is a conceptual question and no tool is needed.\nFinal Answer: A ReAct agent combines reasoning traces with tool actions so it can observe results before answering."

        if "observation:" not in lower_prompt:
            item = self._extract_item(lower_prompt)
            return f'Thought: I need the product price, stock, and weight.\nAction: get_product_info({{"item_name": "{item}"}})'

        if "discount_percent" not in lower_prompt:
            coupon = self._extract_coupon(lower_prompt)
            return f'Thought: I need the coupon discount before calculating the total.\nAction: get_discount({{"coupon_code": "{coupon}"}})'

        if "shipping_cost" not in lower_prompt:
            item = self._extract_item(lower_prompt)
            quantity = self._extract_quantity(lower_prompt)
            weight = {"iphone": 0.4, "headphones": 0.5, "laptop": 1.8, "keyboard": 0.8}.get(item, 1.0)
            destination = self._extract_destination(lower_prompt)
            return f'Thought: I need shipping for the total package weight.\nAction: calc_shipping({{"weight_kg": {quantity * weight}, "destination": "{destination}"}})'

        if '"result"' not in lower_prompt:
            item = self._extract_item(lower_prompt)
            quantity = self._extract_quantity(lower_prompt)
            price = {"iphone": 799, "headphones": 80, "laptop": 1200, "keyboard": 45}.get(item, 0)
            discount = self._latest_number_after(lower_prompt, "discount_percent")
            shipping = self._latest_number_after(lower_prompt, "shipping_cost")
            expression = f"{quantity}*{price}*(1-{discount}/100)+{shipping}"
            return f'Thought: I have the price, discount, and shipping; now I calculate the total.\nAction: calculator({{"expression": "{expression}"}})'

        result = self._latest_number_after(lower_prompt, '"result"')
        return f"Thought: The calculation is complete.\nFinal Answer: The final total is ${result:.2f}."

    def _chatbot_answer(self, prompt: str) -> str:
        if "coupon" in prompt.lower() or "ship" in prompt.lower():
            return "I estimate the total is about $1000, but I cannot verify stock, coupon, or shipping without tools."
        return "A ReAct agent reasons step by step and can call tools before giving the final answer."

    def _extract_item(self, text: str) -> str:
        for item in ["iphone", "headphones", "laptop", "keyboard"]:
            if item in text:
                return item
        return "iphone"

    def _extract_quantity(self, text: str) -> int:
        match = re.search(r"\b(\d+)\s*(iphone|headphones|laptop|keyboard)", text)
        return int(match.group(1)) if match else 1

    def _extract_coupon(self, text: str) -> str:
        match = re.search(r"(winner|save10|student|none)", text, flags=re.IGNORECASE)
        return match.group(1).upper() if match else "NONE"

    def _extract_destination(self, text: str) -> str:
        for destination in ["Hanoi", "Ho Chi Minh", "Danang", "Da Nang"]:
            if destination.lower() in text:
                return destination
        return "Hanoi"

    def _latest_number_after(self, text: str, key: str) -> float:
        matches = re.findall(rf"{re.escape(key)}[^0-9.-]*(-?\d+(?:\.\d+)?)", text)
        return float(matches[-1]) if matches else 0.0
