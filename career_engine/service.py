import uuid
from typing import Any

from .contracts import Mission
from .opportunity_intelligence import assess_opportunity
from .application_factory import create_application_plan
from .sop_soms import advance, capture_proof, close_with_win, acceptance_record
from .store import CareerStore


class CareerService:
    def __init__(self, store: CareerStore | None = None):
        self.store = store or CareerStore()

    def missions(self) -> list[dict]:
        return self.store.collection("missions", [])

    def create_mission(self, objective: str) -> dict:
        mission = Mission(id=uuid.uuid4().hex, objective=objective)
        rows = self.missions()
        rows.append(mission.to_dict())
        self.store.put_collection("missions", rows)
        return mission.to_dict()

    def update_mission(
        self,
        mission_id: str,
        stage: str | None = None,
        proof: str | None = None,
        result: dict | None = None,
    ) -> dict:
        rows = self.missions()
        for row in rows:
            if row["id"] != mission_id:
                continue
            mission = Mission(**row)
            if stage:
                advance(mission, stage, result=result)
            elif result:
                mission.result.update(result)
            if proof:
                capture_proof(mission, "execution", proof)
            self.store.put_collection("missions", [
                mission.to_dict() if x["id"] == mission_id else x for x in rows
            ])
            return mission.to_dict()
        raise KeyError(mission_id)

    def prove_mission(self, mission_id: str, target: str, proof: list[str], next_win: str) -> dict:
        rows = self.missions()
        for row in rows:
            if row["id"] == mission_id:
                mission = Mission(**row)
                close_with_win(mission, target, proof, next_win)
                self.store.put_collection("missions", [
                    mission.to_dict() if x["id"] == mission_id else x for x in rows
                ])
                wins = self.store.collection("wins", [])
                wins.append(mission.win.__dict__)
                self.store.put_collection("wins", wins)
                return acceptance_record(mission)
        raise KeyError(mission_id)

    def _add(self, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        payload.setdefault("id", uuid.uuid4().hex)
        rows = self.store.collection(key, [])
        rows.append(payload)
        self.store.put_collection(key, rows)
        return payload

    def profile(self) -> dict[str, Any]:
        return self.store.collection("profile", {})

    def save_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        self.store.put_collection("profile", profile)
        return profile

    def opportunities(self) -> list[dict[str, Any]]:
        return self.store.collection("opportunities", [])

    def applications(self) -> list[dict[str, Any]]:
        return self.store.collection("applications", [])

    def interviews(self) -> list[dict[str, Any]]:
        return self.store.collection("interviews", [])

    def followups(self) -> list[dict[str, Any]]:
        return self.store.collection("followups", [])

    def skill_gaps(self) -> list[dict[str, Any]]:
        return self.store.collection("skill_gaps", [])

    def assess_opportunity(self, opportunity_id: str) -> dict[str, Any]:
        rows = self.opportunities()
        profile = self.profile()
        for row in rows:
            if row["id"] == opportunity_id:
                assessment = assess_opportunity(row, profile)
                updated = dict(row)
                updated["assessment"] = assessment
                updated["status"] = "ASSESSED"
                self.store.put_collection("opportunities", [
                    updated if x["id"] == opportunity_id else x for x in rows
                ])
                return assessment
        raise KeyError(opportunity_id)

    def add_opportunity(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("title", "company", "source_url")
        if any(not str(payload.get(k, "")).strip() for k in required):
            raise ValueError("title, company and source_url are required")
        payload.setdefault("status", "NEW")
        return self._add("opportunities", payload)

    def create_application_plan(self, opportunity_id: str) -> dict[str, Any]:
        for opportunity in self.opportunities():
            if opportunity["id"] == opportunity_id:
                if opportunity.get("status") not in ("ASSESSED", "QUALIFIED"):
                    raise ValueError("opportunity must be assessed before creating an application plan")
                plan = create_application_plan(opportunity, self.profile(), opportunity.get("assessment"))
                self._add("applications", {
                    "id": plan["id"], "opportunity_id": opportunity_id,
                    "company": plan["company"], "role": plan["role"],
                    "status": plan["status"], "plan": plan,
                })
                return plan
        raise KeyError(opportunity_id)

    def add_application(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("opportunity_id", "company", "role")
        if any(not str(payload.get(k, "")).strip() for k in required):
            raise ValueError("opportunity_id, company and role are required")
        payload.setdefault("status", "DRAFT")
        return self._add("applications", payload)

    def add_interview(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("application_id", "stage")
        if any(not str(payload.get(k, "")).strip() for k in required):
            raise ValueError("application_id and stage are required")
        payload.setdefault("status", "SCHEDULED")
        return self._add("interviews", payload)

    def add_followup(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("application_id", "due_at")
        if any(not str(payload.get(k, "")).strip() for k in required):
            raise ValueError("application_id and due_at are required")
        payload.setdefault("status", "DRAFT")
        return self._add("followups", payload)

    def add_skill_gap(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("skill", "evidence_gap")
        if any(not str(payload.get(k, "")).strip() for k in required):
            raise ValueError("skill and evidence_gap are required")
        payload.setdefault("status", "OPEN")
        return self._add("skill_gaps", payload)
