import unittest
from career_engine.interview_command import build_interview_prep, record_answer, record_feedback, record_outcome

class InterviewCommandTests(unittest.TestCase):
    def setUp(self):
        self.profile={"experience":[{"title":"Engineer","details":"Python"}],"projects":[{"name":"C6"}]}
        self.opp={"id":"o1","company":"Example","title":"AI Engineer","requirements":["Python","AI"]}
        self.app={"id":"a1"}
    def test_build_maps_requirements_and_evidence(self):
        p=build_interview_prep(self.app,self.opp,self.profile,"technical")
        self.assertEqual(p["status"],"PREP_REQUIRED"); self.assertIn("Python",p["requirements"]); self.assertTrue(p["candidate_evidence"])
    def test_answer_feedback_outcome_loop(self):
        p=build_interview_prep(self.app,self.opp,self.profile,"technical")
        q=p["questions"][0]["question"]
        p=record_answer(p,q,"Evidence-backed answer",[{"source":"experience","id":"x"}])
        p=record_feedback(p,"Strong example; tighten result.")
        p=record_outcome(p,{"result":"completed","feedback":"Strong example"})
        self.assertEqual(p["status"],"OUTCOME_CAPTURED"); self.assertTrue(p["feedback"])

if __name__=="__main__": unittest.main()
