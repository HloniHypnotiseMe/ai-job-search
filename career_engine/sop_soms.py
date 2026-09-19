from dataclasses import asdict
from typing import Any
from .contracts import Mission, Proof, Win, utc_now

STAGES = ["AUDIT", "EVIDENCE", "DIAGNOSE", "RECOMMEND", "SELECT", "EXECUTE", "MEASURE", "RE-AUDIT", "PROVE"]


def advance(mission: Mission, stage: str, *, result: dict[str, Any] | None = None) -> Mission:
    if stage not in STAGES:
        raise ValueError(f"Unknown SOP/SOMS stage: {stage}")
    mission.stage = stage
    mission.updated_at = utc_now()
    if result:
        mission.result.update(result)
    return mission


def capture_proof(mission: Mission, kind: str, statement: str, source: str = "") -> Mission:
    mission.evidence.append(Proof(kind=kind, statement=statement, source=source))
    mission.updated_at = utc_now()
    return mission


def close_with_win(mission: Mission, target: str, proof: list[str], next_win: str) -> Mission:
    mission.win = Win(target=target, proof=proof, next_win=next_win)
    mission.stage = "PROVE"
    mission.status = "PROVEN"
    mission.updated_at = utc_now()
    return mission


def acceptance_record(mission: Mission) -> dict[str, Any]:
    """SOMS acceptance chain: promised work must have capability, execution, measurement and proof."""
    return {
        "mission_id": mission.id,
        "objective": mission.objective,
        "stage": mission.stage,
        "status": mission.status,
        "evidence_count": len(mission.evidence),
        "has_result": bool(mission.result),
        "has_win": mission.win is not None,
        "record": asdict(mission),
    }
