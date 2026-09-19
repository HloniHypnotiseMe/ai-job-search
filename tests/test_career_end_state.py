import tempfile
import unittest

from career_engine.service import CareerService
from career_engine.store import CareerStore


class CareerEndStateTests(unittest.TestCase):
    def test_private_career_collections_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = CareerService(CareerStore(tmp))
            profile = service.save_profile({"name": "Candidate", "location": "South Africa"})
            opportunity = service.add_opportunity({
                "title": "AI Engineer",
                "company": "C6",
                "source_url": "https://example.test/job/1",
            })
            application = service.add_application({
                "opportunity_id": opportunity["id"],
                "company": "C6",
                "role": "AI Engineer",
            })
            interview = service.add_interview({
                "application_id": application["id"],
                "stage": "technical",
            })
            followup = service.add_followup({
                "application_id": application["id"],
                "due_at": "2026-09-20T09:00:00Z",
            })
            gap = service.add_skill_gap({
                "skill": "distributed systems",
                "evidence_gap": "No verified production example yet",
            })
            dashboard = service.store.dashboard()
            self.assertEqual(profile["name"], "Candidate")
            self.assertEqual(dashboard["summary"]["opportunities"], 1)
            self.assertEqual(dashboard["summary"]["applications"], 1)
            self.assertEqual(dashboard["summary"]["interviews"], 1)
            self.assertEqual(dashboard["summary"]["followups"], 1)
            self.assertEqual(dashboard["summary"]["skill_gaps"], 1)
            self.assertEqual(interview["status"], "SCHEDULED")
            self.assertEqual(followup["status"], "DRAFT")
            self.assertEqual(gap["status"], "OPEN")

    def test_end_state_reuses_existing_mission_and_win_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = CareerService(CareerStore(tmp))
            mission = service.create_mission("Submit one evidence-backed application")
            service.update_mission(mission["id"], stage="EVIDENCE", proof="Posting captured")
            result = service.prove_mission(
                mission["id"],
                "Evidence pack submitted",
                ["CV PDF", "cover letter", "ATS verification"],
                "Complete interview stage",
            )
            self.assertEqual(result["status"], "PROVEN")
            self.assertEqual(len(service.store.collection("wins")), 1)


if __name__ == "__main__":
    unittest.main()
