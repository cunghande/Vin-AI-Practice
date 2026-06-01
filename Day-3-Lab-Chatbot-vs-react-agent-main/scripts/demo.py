import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv

from src.agent.agent import ReActAgent
from src.core.fake_provider import ScriptedProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.core.openai_provider import OpenAIProvider
from src.tools import get_tools


def build_provider():
    load_dotenv(PROJECT_ROOT / ".env")
    provider = os.getenv("DEFAULT_PROVIDER", "scripted").lower()
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")

    if provider == "openai":
        return OpenAIProvider(model_name=model, api_key=os.getenv("OPENAI_API_KEY"))
    if provider in {"google", "gemini"}:
        return GeminiProvider(model_name=model or "gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
    if provider == "local":
        return LocalProvider(model_path=os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf"))
    return ScriptedProvider()


def main() -> None:
    question = " ".join(sys.argv[1:]) or "I want 2 headphones with coupon SAVE10 shipped to Hanoi. What is the total?"
    agent = ReActAgent(build_provider(), get_tools(), max_steps=6)
    answer = agent.run(question)
    print(answer)


if __name__ == "__main__":
    main()
