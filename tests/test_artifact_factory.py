import tempfile, unittest
from career_engine.artifact_factory import ApplicationArtifactService, ats_check, render_cover_letter, render_cv, review_artifacts
from career_engine.service import CareerService
from career_engine.store import CareerStore

class ArtifactFactoryTests(unittest.TestCase):
    def setUp(self):
        self.profile={"name":"Test Candidate","email":"test@example.com","skills":["Python","AI"],"summary":"Evidence-backed engineer.","experience":[{"title":"Engineer","details":"Built Python systems"}],"projects":[{"name":"C6","description":"Career platform"}],"education":["BSc"]}
        self.opp={"id":"o1","company":"Example","title":"AI Engineer","source_url":"https://example.test/job","requirements":["Python","Kubernetes"],"description":"Build AI systems."}
    def test_renderers_are_grounded(self):
        cv=render_cv(self.opp,self.profile); cl=render_cover_letter(self.opp,self.profile)
        self.assertIn("Python",cv); self.assertIn("Example",cl); self.assertNotIn("—",cv+cl)
    def test_ats_reports_gap(self):
        result=ats_check(self.opp,"Python engineer","")
        self.assertEqual(result["status"],"REVIEW_REQUIRED"); self.assertIn("Kubernetes",result["missing_requirements"])
    def test_review_flags_placeholders(self):
        r=review_artifacts(self.opp,self.profile,"[YOUR NAME]","ok")
        self.assertEqual(r["status"],"REVIEW_REQUIRED")
    def test_generate_and_finalize_requires_clean_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=CareerService(CareerStore(tmp)); s.save_profile(self.profile)
            o=s.add_opportunity(dict(self.opp,status="ASSESSED"))
            p=s.create_application_plan(o["id"])
            result=ApplicationArtifactService(s.store).generate(p["id"])
            self.assertIn("cv",result["artifacts"])
            self.assertTrue((s.store.root/"applications").exists())

if __name__=="__main__": unittest.main()
