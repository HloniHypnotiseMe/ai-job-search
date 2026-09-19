import json
import os
import tempfile
from pathlib import Path
from typing import Any
from .tracker import summary as tracker_summary


class CareerStore:
    """Private, filesystem-backed career state; the repository contains no personal data."""

    def __init__(self, root: str | None = None):
        self.root = Path(root or os.getenv("CAREER_DATA_DIR", "./.career-private")).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / name

    def read_json(self, name: str, default: Any) -> Any:
        path = self._path(name)
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def write_json(self, name: str, value: Any) -> None:
        path = self._path(name)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(self.root), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(value, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def dashboard(self) -> dict[str, Any]:
        return {
            "profile": self.read_json("profile.json", {}),
            "missions": self.read_json("missions.json", []),
            "wins": self.read_json("win-ledger.json", []),
            "settings": self.read_json("settings.json", {}),
            "tracker": tracker_summary(),
        }
