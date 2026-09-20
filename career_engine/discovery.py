import argparse
import json
from pathlib import Path
from typing import Any

from career_engine.adapters.job_ops import load_export
from career_engine.service import CareerService
from career_engine.store import CareerStore


def ingest_jobops_export(path: str, service: CareerService) -> dict[str, int]:
    """Import a JobOps export into private opportunities without duplicating postings."""
    jobs = load_export(path)
    existing = service.opportunities()
    keys = {str(row.get("canonical_key", "")).strip() for row in existing if row.get("canonical_key")}
    urls = {str(row.get("source_url", "")).strip() for row in existing if row.get("source_url")}
    imported = 0
    skipped = 0

    for job in jobs:
        canonical = str(job.get("canonical_key", "")).strip()
        source_url = str(job.get("source_url", "")).strip()
        if (canonical and canonical in keys) or (source_url and source_url in urls):
            skipped += 1
            continue
        payload: dict[str, Any] = {
            "title": job["title"],
            "company": job["company"],
            "source_url": source_url,
            "location": job.get("location", ""),
            "work_mode": job.get("work_mode", ""),
            "description": job.get("description", ""),
            "posted_at": job.get("posted_at", ""),
            "first_seen_at": job.get("first_seen_at", ""),
            "source": job.get("source", "jobops"),
            "source_id": job.get("id", ""),
            "canonical_key": canonical,
            "status": "NEW",
            "provenance": {
                "adapter": "job_ops",
                "source": job.get("source", "jobops"),
                "source_url": source_url,
            },
        }
        service.add_opportunity(payload)
        if canonical:
            keys.add(canonical)
        if source_url:
            urls.add(source_url)
        imported += 1

    return {"seen": len(jobs), "imported": imported, "skipped_duplicates": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a JobOps JSON export into the private Career Command Centre.")
    parser.add_argument("export", help="Path to a JobOps JSON export")
    parser.add_argument("--data-dir", default=None, help="Private CAREER_DATA_DIR override")
    args = parser.parse_args()

    service = CareerService(CareerStore(args.data_dir))
    result = ingest_jobops_export(args.export, service)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
