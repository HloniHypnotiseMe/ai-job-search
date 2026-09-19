from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Win:
    target: str
    proof: list[str] = field(default_factory=list)
    next_win: str = ""


@dataclass
class Proof:
    kind: str
    statement: str
    source: str = ""
    captured_at: str = field(default_factory=utc_now)


@dataclass
class Mission:
    id: str
    objective: str
    stage: str = "AUDIT"
    status: str = "ACTIVE"
    win: Win | None = None
    evidence: list[Proof] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
