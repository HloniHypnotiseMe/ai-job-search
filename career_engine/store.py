import json
import os
import tempfile
from pathlib import Path
from typing import Any


class CareerStore:
    """Private filesystem-backed career state. Personal data never belongs in Git."""

    COLLECTIONS = {
        "profile": "profile.json",
        "opportunities": "opportunities.json",
        "applications": "applications.json",
        "interviews": "interviews.json",
        "followups": "followups.json",
        "skill_gaps": "skill-gaps.json",
        "wins": "win-ledger.json",
        "missions": "missions.json",
        "settings": "settings.json",
        "mail_signals": "mail-signals.json",
    }

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

    def collection(self, key: str, default: Any = None) -> Any:
        name = self.COLLECTIONS[key]
        return self.read_json(name, [] if default is None else default)

    def put_collection(self, key: str, value: Any) -> None:
        self.write_json(self.COLLECTIONS[key], value)

    def dashboard(self) -> dict[str, Any]:
        opportunities = self.collection("opportunities", [])
        applications = self.collection("applications", [])
        interviews = self.collection("interviews", [])
        followups = self.collection("followups", [])
        skill_gaps = self.collection("skill_gaps", [])
        missions = self.collection("missions", [])
        wins = self.collection("wins", [])
        return {
            "profile": self.collection("profile", {}),
            "opportunities": opportunities,
            "applications": applications,
            "interviews": interviews,
            "followups": followups,
            "skill_gaps": skill_gaps,
            "missions": missions,
            "wins": wins,
            "summary": {
                "opportunities": len(opportunities),
                "applications": len(applications),
                "interviews": len(interviews),
                "followups": len(followups),
                "skill_gaps": len(skill_gaps),
                "active_missions": sum(1 for x in missions if x.get("status") == "ACTIVE"),
                "proven_wins": len(wins),
            },
        }
