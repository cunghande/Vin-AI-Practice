"""Storage skeleton for benchmark artifacts."""

from pathlib import Path


class LocalArtifactStore:
    """Small local store for reports and trace exports."""

    def __init__(self, root: Path = Path("reports")) -> None:
        # Resolve the project root dynamically (storage.py is in src/multi_agent_research_lab/services/)
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.root = project_root / root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_text(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path
