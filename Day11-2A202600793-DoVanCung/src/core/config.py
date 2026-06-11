"""
Lab 11 — Configuration & API Key Setup
"""
import os
from pathlib import Path


def load_env_file(path: str | Path = ".env"):
    """Load simple KEY=VALUE entries from a local .env file.

    This avoids hard-coding API keys in source files and does not require an
    extra dependency. Existing environment variables are kept unchanged.
    """
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def setup_api_key():
    """Configure Gemini API access when a key is available.

    The assignment can be run in offline mode with GOOGLE_API_KEY left blank.
    Rule-based guardrails, monitoring, and HITL still run without calling Gemini.
    """
    load_env_file(Path(__file__).resolve().parents[2] / ".env")
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = ""
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
    if os.environ["GOOGLE_API_KEY"]:
        print("API key loaded.")
    else:
        print("GOOGLE_API_KEY is blank. Running offline rule-based sections only.")


# Allowed banking topics (used by topic_filter)
ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
]

# Blocked topics (immediate reject)
BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
