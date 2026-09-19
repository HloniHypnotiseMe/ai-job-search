import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from career_engine.adapters.job_ops import load_export, normalize_job
from career_engine.adapters.jobsync import JobSyncAdapter
from career_engine.adapters.interview_handbook import InterviewHandbookAdapter
from career_engine.adapters.coding_interview_university import CodingInterviewUniversityAdapter
from career_engine.adapters.c6_mail import C6MailAdapter


class AdapterTests(unittest.TestCase):
    def test_job_ops_normalizes_canonical_job(self):
        job = normalize_job({"url": "https://example.test/job/1", "title": "Engineer", "company": "C6"})
        self.assertEqual(job["source"], "job-ops")
        self.assertEqual(job["source_url"], "https://example.test/job/1")
        self.assertEqual(job["company"], "C6")

    def test_job_ops_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "jobs.json")
            path.write_text(json.dumps({"jobs": [{"title": "Analyst", "company": "C6"}]}), encoding="utf-8")
            self.assertEqual(len(load_export(str(path))), 1)

    def test_jobsync_snapshot_is_interchange_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "jobsync.json")
            path.write_text(json.dumps({"applications": [{"company": "C6"}]}), encoding="utf-8")
            rows = JobSyncAdapter(str(path)).application_records(JobSyncAdapter(str(path)).import_snapshot())
            self.assertEqual(rows[0]["company"], "C6")

    def test_read_only_learning_adapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guide.md").write_text("binary search interview", encoding="utf-8")
            self.assertEqual(InterviewHandbookAdapter(tmp).find("binary"), ["guide.md"])
            self.assertEqual(CodingInterviewUniversityAdapter(tmp).find("interview"), ["guide.md"])

    def test_mail_requires_endpoint(self):
        with self.assertRaises(ValueError):
            C6MailAdapter().send(to=["test@example.com"], subject="x")

    @patch("career_engine.adapters.c6_mail.request.urlopen")
    def test_mail_requires_sent_confirmation(self, mocked):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"status":"sent","message_id":"abc"}'
        mocked.return_value = Response()
        result = C6MailAdapter("https://mail.example").send(to=["test@example.com"], subject="Hello")
        self.assertEqual(result["status"], "sent")


if __name__ == "__main__":
    unittest.main()
