import os
import tempfile
import unittest
from pathlib import Path
from career_engine.tracker import summary

class TrackerTests(unittest.TestCase):
    def test_tracker_summary_reads_private_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,"job_search_tracker.csv").write_text(
                "date,company,role,status\n2026-09-19,Example,Engineer,interview\n",
                encoding="utf-8",
            )
            old=os.environ.get("CAREER_WORKSPACE_DIR")
            os.environ["CAREER_WORKSPACE_DIR"]=tmp
            try:
                result=summary()
                self.assertEqual(result["total"],1)
                self.assertEqual(result["status"]["Interview"],1)
            finally:
                if old is None: os.environ.pop("CAREER_WORKSPACE_DIR",None)
                else: os.environ["CAREER_WORKSPACE_DIR"]=old

if __name__=="__main__": unittest.main()
