import unittest
from career_engine.application_factory import approve_submission,create_application_plan,record_artifact

class ApplicationFactoryTests(unittest.TestCase):
    def setUp(self):
        self.opportunity={"id":"opp-1","company":"Example","title":"AI Engineer","source_url":"https://example.test/job/1","assessment":{"requirement_matches":["Python"],"evidence_gaps":["Kubernetes"]}}
        self.profile={"experience":[{"title":"AI Engineer","details":"Python systems"}],"projects":[{"name":"C6 Career"}]}
    def test_plan_preserves_evidence_and_requires_human_approval(self):
        p=create_application_plan(self.opportunity,self.profile)
        self.assertEqual(p["status"],"PLANNED"); self.assertIn("Kubernetes",p["evidence_map"]["evidence_gaps"])
        self.assertTrue(p["review_gate"]["human_approval_required"]); self.assertFalse(p["review_gate"]["approved"])
    def test_artifacts_are_versioned(self):
        p=create_application_plan(self.opportunity,self.profile)
        p=record_artifact(p,"cv","cv-v1",evidence=["AI Engineer"])
        self.assertEqual(p["artifacts"]["cv"]["version"],"cv-v1")
        self.assertEqual(p["artifacts"]["cv"]["status"],"READY")
    def test_submission_requires_explicit_approval(self):
        p=create_application_plan(self.opportunity,self.profile)
        p=approve_submission(p,{"cv":"cv-v1","cover_letter":"cl-v1","ats_check":"ats-v1"})
        self.assertTrue(p["review_gate"]["approved"]); self.assertEqual(p["status"],"READY_FOR_USER_SUBMISSION")
        self.assertEqual(p["submission_record"]["artifact_versions"]["cv"],"cv-v1")
if __name__=="__main__": unittest.main()
