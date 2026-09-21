import unittest
from career_engine.outcomes import learning_signals, record_application_outcome
from career_engine.discovery_sources import ingest_records, source_registry
from career_engine.mail_intelligence import classify_message, propose_update

class CareerIntelligenceTests(unittest.TestCase):
    def test_outcome_learning(self):
        apps=[{"id":"a1","opportunity_id":"o1","status":"rejected"},{"id":"a2","opportunity_id":"o2","status":"interview"}]
        opps=[{"id":"o1","source":"pnet","title":"Engineer"},{"id":"o2","source":"pnet","title":"Engineer"}]
        data=learning_signals(apps,opps,[{"application_id":"a2"}],[{"skill":"Kubernetes","evidence_gap":"no evidence"},{"skill":"Kubernetes","evidence_gap":"no evidence"}])
        self.assertEqual(data["final_outcomes"],1); self.assertEqual(data["recurring_skill_gaps"][0],("Kubernetes",2))
    def test_sources_dedupe_and_provenance(self):
        self.assertIn("pnet",source_registry())
        records=[{"company":"A","title":"Engineer","source_url":"https://x/1"}]
        rows,stats=ingest_records(records,"pnet"); rows,stats2=ingest_records(records,"pnet",rows)
        self.assertEqual(stats["added"],1); self.assertEqual(stats2["duplicates"],1); self.assertEqual(rows[0]["country"],"ZA")
    def test_mail_is_proposal_only(self):
        c=classify_message("Interview invitation","We would like to schedule a technical interview.")
        self.assertEqual(c["signal"],"interview"); self.assertTrue(c["requires_user_confirmation"])
        p=propose_update({"subject":"Example Engineer interview","body":"Interview invitation from Example."},[{"id":"a1","company":"Example","role":"Engineer"}])
        self.assertTrue(p["proposal_only"])
    def test_outcome_requires_canonical_final_status(self):
        with self.assertRaises(ValueError): record_application_outcome({"id":"a1"},{"status":"maybe"})

if __name__=="__main__": unittest.main()
