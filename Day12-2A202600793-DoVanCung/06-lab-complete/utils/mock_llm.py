"""Offline mock LLM used for lab deployment without an external API key."""


def ask(question: str) -> str:
    normalized = question.strip()
    if not normalized:
        return "Please send a non-empty question."
    return (
        "Mock response: production deployment should externalize config, "
        "protect endpoints, expose health checks, and keep runtime state out "
        f"of a single process. You asked: {normalized}"
    )
