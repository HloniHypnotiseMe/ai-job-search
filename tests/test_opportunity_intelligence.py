import tempfile
import unittest
from career_engine.opportunity_intelligence import assess_opportunity
from career_engine.service import CareerService
from career_engine.store import CareerStore

class OpportunityIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.profile={"location":"Johannesburg, South Africa","work_authorization":"South African citizen","skills":["Python","AI","PostgreSQL"],"technical_skills":["Docker","APIs"],"experience":[{"title":"AI Engineer","details":"Built Python AI APIs and PostgreSQL systems"}],"projects":[{"name":"C6 Career","details":"Built private AI career tooling"}],"career_goals":["AI engineering","automation"],"preferences":["remote","autonomy"]}
        self.job={"id":"job-1","source":"job-ops","source_url":"https://example.test/jobs/1","company":"Example","title":"AI Engineer","location":"Remote South Africa","work_mode":"remote","description":"Build Python AI automation APIs with PostgreSQL.","requirements":["Python","AI","PostgreSQL"]}
    def test_assessment_is_evidence_backed(self):
        r=assess_opportunity(self.job,self.profile)
        self.assertEqual(r["status"],"ASSESSED")
        self.assertEqual(r["gates"]["eligibility"],"PASS")
        self.assertEqual(r["gates"]["location"],"PASS")
        self.assertEqual(r["requirement_matches"],["Python","AI","PostgreSQL"])
        self.assertEqual(r["evidence_gaps"],[])
        self.assertTrue(r["matched_evidence"])
        self.assertEqual(r["provenance"]["source"],"job-ops")
    def test_missing_requirement_is_a_gap(self):
        r=assess_opportunity(dict(self.job,requirements=["Python","Kubernetes"]),self.profile)
        self.assertIn("Kubernetes",r["evidence_gaps"])
        self.assertNotIn("Kubernetes",[x["candidate_evidence"] for x in r["matched_evidence"]])
    def test_hard_gate_excludes_unverified_clearance(self):
        r=assess_opportunity(dict(self.job,description="Requires security clearance and Python."),self.profile)
        self.assertEqual(r["gates"]["eligibility"],"FAIL")
        self.assertEqual(r["disposition"],"EXCLUDED")
    def test_service_persists_assessment(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=CareerService(CareerStore(tmp)); s.save_profile(self.profile)
            job=s.add_opportunity({"title":"AI Engineer","company":"Example","source_url":"https://example.test/jobs/1","description":"Python AI","requirements":["Python"]})
            result=s.assess_opportunity(job["id"])
            self.assertEqual(result["status"],"ASSESSED")
            self.assertEqual(s.opportunities()[0]["assessment"]["status"],"ASSESSED")

if __name__=="__main__":
    unittest.main()
