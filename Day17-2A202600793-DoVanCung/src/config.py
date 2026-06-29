from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from model_provider import ProviderConfig, normalize_provider


@dataclass
class LabConfig:
    """Student TODO: define the shared configuration for the lab.

    Hints:
    - Keep paths for the repo root, dataset directory, and state directory.
    - Add compact-memory settings such as threshold and number of messages to keep.
    - Add provider settings for `openai`, `custom`, `gemini`, `anthropic`, `ollama`, and `openrouter`.
    """

    base_dir: Path
    data_dir: Path
    state_dir: Path
    compact_threshold_tokens: int
    compact_keep_messages: int
    model: ProviderConfig
    judge_model: ProviderConfig


def load_config(base_dir: Path | None = None) -> LabConfig:
    """Load environment variables and return a populated LabConfig."""

    root = (base_dir or Path(__file__).resolve().parent.parent).resolve()

    try:
        from dotenv import load_dotenv

        load_dotenv(root / ".env")
    except Exception:
        pass

    state_dir = root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    provider_name = normalize_provider(os.getenv("LLM_PROVIDER", "openai"))
    model_name = os.getenv(
        "LLM_MODEL",
        {
            "openai": "gpt-4.1-mini",
            "custom": "gpt-4.1-mini",
            "gemini": "gemini-2.0-flash",
            "anthropic": "claude-3-5-sonnet-latest",
            "ollama": "llama3.1",
            "openrouter": "openai/gpt-4.1-mini",
        }.get(provider_name, "gpt-4.1-mini"),
    )
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    def provider_config(prefix: str, default_provider: str) -> ProviderConfig:
        current_provider = normalize_provider(os.getenv(f"{prefix}_PROVIDER", default_provider))
        return ProviderConfig(
            provider=current_provider,
            model_name=os.getenv(f"{prefix}_MODEL", model_name),
            temperature=float(os.getenv(f"{prefix}_TEMPERATURE", str(temperature))),
            api_key=os.getenv(f"{prefix}_API_KEY") or None,
            base_url=os.getenv(f"{prefix}_BASE_URL") or None,
        )

    model = provider_config("LLM", provider_name)
    judge_model = provider_config("JUDGE_LLM", os.getenv("JUDGE_LLM_PROVIDER", provider_name))

    return LabConfig(
        base_dir=root,
        data_dir=root / "data",
        state_dir=state_dir,
        compact_threshold_tokens=int(os.getenv("COMPACT_THRESHOLD_TOKENS", "2200")),
        compact_keep_messages=int(os.getenv("COMPACT_KEEP_MESSAGES", "8")),
        model=model,
        judge_model=judge_model,
    )
