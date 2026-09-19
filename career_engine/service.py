import uuid
from .contracts import Mission
from .sop_soms import advance, capture_proof, close_with_win, acceptance_record
from .store import CareerStore


class CareerService:
    def __init__(self, store: CareerStore | None = None):
        self.store = store or CareerStore()

    def missions(self) -> list[dict]:
        return self.store.read_json("missions.json", [])

    def create_mission(self, objective: str) -> dict:
        mission = Mission(id=uuid.uuid4().hex, objective=objective)
        rows = self.missions()
        rows.append(mission.to_dict())
        self.store.write_json("missions.json", rows)
        return mission.to_dict()

    def update_mission(self, mission_id: str, stage: str | None = None, proof: str | None = None, result: dict | None = None) -> dict:
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
            self.store.write_json("missions.json", [mission.to_dict() if x["id"] == mission_id else x for x in rows])
            return mission.to_dict()
        raise KeyError(mission_id)

    def prove_mission(self, mission_id: str, target: str, proof: list[str], next_win: str) -> dict:
        rows = self.missions()
        for row in rows:
            if row["id"] == mission_id:
                mission = Mission(**row)
                close_with_win(mission, target, proof, next_win)
                self.store.write_json("missions.json", [mission.to_dict() if x["id"] == mission_id else x for x in rows])
                wins = self.store.read_json("win-ledger.json", [])
                wins.append(mission.win.__dict__)
                self.store.write_json("win-ledger.json", wins)
                return acceptance_record(mission)
        raise KeyError(mission_id)
