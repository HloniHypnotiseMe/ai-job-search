import json
import tempfile
import unittest
from pathlib import Path

from career_engine.service import CareerService
from career_engine.store import CareerStore
from career_engine.discovery import ingest_jobops_export


class DiscoveryIngestionTests(unittest.TestCase):
    def test_jobops_export_is_imported_with_provenance_and_deduped(self):
        payload = {
            "jobs": [
                {
                    "id": "job-1",
                    "source": "JobOps",
                    "source_url": "https://jobs.example/1",
                    "company": "Example Co",
                    "title": "Platform Engineer",
                    "location": "Johannesburg",
                    "work_mode": "hybrid",
                    "description": "Build reliable platforms.",
                },
                {
                    "id": "job-2",
                    "source": "JobOps",
                    "source_url": "https://jobs.example/1",
                    "company": "Example Co",
                    "title": "Platform Engineer",
                },
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / "jobs.json"
            export.write_text(json.dumps(payload), encoding="utf-8")
            service = CareerService(CareerStore(tmp))
            result = ingest_jobops_export(str(export), service)

            self.assertEqual(result["seen"], 2)
            self.assertEqual(result["imported"], 1)
            self.assertEqual(result["skipped_duplicates"], 1)

            opportunity = service.opportunities()[0]
            self.assertEqual(opportunity["source"], "JobOps")
            self.assertEqual(opportunity["provenance"]["adapter"], "job_ops")
            self.assertEqual(opportunity["source_url"], "https://jobs.example/1")


if __name__ == "__main__":
    unittest.main()
