"""Read-only adapter for Coding Interview University content."""
from __future__ import annotations

from pathlib import Path


class CodingInterviewUniversityAdapter:
    def __init__(self, root: str):
        self.root = Path(root).expanduser().resolve()

    def exists(self) -> bool:
        return self.root.is_dir()

    def find(self, term: str, limit: int = 20) -> list[str]:
        needle = term.casefold()
        matches: list[str] = []
        for path in self.root.rglob("*"):
            if len(matches) >= limit:
                break
            if not path.is_file() or path.suffix.lower() not in {".md", ".mdx", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if needle in text.casefold():
                matches.append(str(path.relative_to(self.root)))
        return matches
