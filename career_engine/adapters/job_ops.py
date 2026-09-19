"""JobOps discovery adapter.

JobOps is treated as an external discovery capability. This adapter accepts
JSON records produced by JobOps (or a saved export) and normalizes them into
the C6 canonical job shape. It does not reimplement JobOps.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_job(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize one JobOps-style record without inventing candidate facts."""
    source_url = str(record.get("source_url") or record.get("url") or "").strip()
    title = str(record.get("title") or record.get("role") or "").strip()
    company = str(record.get("company") or record.get("company_name") or "").strip()
    location = str(record.get("location") or "").strip()
    description = str(record.get("description") or record.get("job_description") or "").strip()
    source = str(record.get("source") or "job-ops").strip()
    canonical_key = str(
        record.get("canonical_key")
        or f"{company.lower()}|{title.lower()}|{source_url.lower()}"
    )
    return {
        "id": str(record.get("id") or canonical_key),
        "source": source,
        "source_url": source_url,
        "company": company,
        "title": title,
        "location": location,
        "work_mode": str(record.get("work_mode") or record.get("remote") or "").strip(),
        "description": description,
        "posted_at": record.get("posted_at"),
        "first_seen_at": record.get("first_seen_at") or _now(),
        "canonical_key": canonical_key,
        "status": str(record.get("status") or "OPEN"),
        "fit": record.get("fit"),
        "evidence": record.get("evidence") or [],
        "created_at": record.get("created_at") or _now(),
        "updated_at": record.get("updated_at") or _now(),
    }


def normalize_jobs(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_job(record) for record in records]


def load_export(path: str) -> list[dict[str, Any]]:
    """Load a JobOps JSON export; accepts a list or {jobs:[...]} envelope."""
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        payload = payload.get("jobs", [])
    if not isinstance(payload, list):
        raise ValueError("JobOps export must be a JSON list or an object containing jobs")
    return normalize_jobs(payload)
