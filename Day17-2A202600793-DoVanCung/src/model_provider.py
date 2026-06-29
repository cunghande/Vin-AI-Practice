from __future__ import annotations

from dataclasses import dataclass
import os
from importlib import import_module


@dataclass
class ProviderConfig:
    """Student TODO: define the provider configuration shared by the agents.

    Required providers for this lab:
    - openai
    - custom (OpenAI-compatible base URL)
    - gemini
    - anthropic
    - ollama
    - openrouter
    """

    provider: str
    model_name: str
    temperature: float
    api_key: str | None = None
    base_url: str | None = None


def normalize_provider(value: str) -> str:
    """Map provider aliases to the canonical provider names."""

    normalized = (value or "").strip().lower()
    aliases = {
        "anthorpic": "anthropic",
        "openai-compatible": "custom",
        "open_ai": "openai",
        "google": "gemini",
        "gpt": "openai",
    }
    return aliases.get(normalized, normalized or "openai")


def build_chat_model(config: ProviderConfig):
    """Instantiate the real chat model for the selected provider.

    The lab runs happily in offline mode, so this helper is only used when the
    optional provider SDKs are installed and an API key / base URL is available.
    """

    provider = normalize_provider(config.provider)
    temperature = config.temperature
    model_name = config.model_name

    if provider == "openai":
        module = import_module("langchain_openai")
        return module.ChatOpenAI(model=model_name, temperature=temperature, api_key=config.api_key)
    if provider == "custom":
        module = import_module("langchain_openai")
        kwargs = {"model": model_name, "temperature": temperature}
        if config.api_key:
            kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return module.ChatOpenAI(**kwargs)
    if provider == "gemini":
        module = import_module("langchain_google_genai")
        kwargs = {"model": model_name, "temperature": temperature}
        if config.api_key:
            kwargs["google_api_key"] = config.api_key
        return module.ChatGoogleGenerativeAI(**kwargs)
    if provider == "anthropic":
        module = import_module("langchain_anthropic")
        kwargs = {"model": model_name, "temperature": temperature}
        if config.api_key:
            kwargs["anthropic_api_key"] = config.api_key
        return module.ChatAnthropic(**kwargs)
    if provider == "ollama":
        module = import_module("langchain_ollama")
        kwargs = {"model": model_name, "temperature": temperature}
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return module.ChatOllama(**kwargs)
    if provider == "openrouter":
        module = import_module("langchain_openrouter")
        kwargs = {"model": model_name, "temperature": temperature}
        if config.api_key:
            kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return module.ChatOpenRouter(**kwargs)
    raise ValueError(f"Unsupported provider: {config.provider}")
