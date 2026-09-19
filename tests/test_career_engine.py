import os
import tempfile
import unittest
from pathlib import Path

from career_engine.service import CareerService
from career_engine.store import CareerStore


class CareerEngineTests(unittest.TestCase):
    def test_mission_lifecycle_records_proof_and_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = CareerService(CareerStore(tmp))
            mission = service.create_mission("Find and prepare one target role")
            service.update_mission(mission["id"], stage="EVIDENCE", proof="Target posting captured")
            service.update_mission(mission["id"], stage="EXECUTE", result={"application_pack": "ready"})
            result = service.prove_mission(mission["id"], "Application ready", ["CV PDF", "cover letter", "ATS check"], "Secure interview")
            self.assertEqual(result["stage"], "PROVE")
            self.assertEqual(result["status"], "PROVEN")
            self.assertTrue(result["has_win"])


if __name__ == "__main__":
    unittest.main()
