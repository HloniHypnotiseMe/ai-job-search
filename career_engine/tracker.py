import csv
import os
from pathlib import Path

STATUS_BUCKETS={
    "drafted":"Drafted","applied":"Active","interview":"Interview","offer":"Offer",
    "hired":"Hired","rejected":"Rejected/Closed","no_response":"Rejected/Closed",
    "offer_declined":"Rejected/Closed","withdrawn":"Rejected/Closed",
}

def tracker_path() -> Path:
    return Path(os.getenv("CAREER_WORKSPACE_DIR", ".")).expanduser().resolve() / "job_search_tracker.csv"

def read_tracker() -> list[dict]:
    path=tracker_path()
    if not path.exists(): return []
    with path.open("r",encoding="utf-8",newline="") as handle:
        return list(csv.DictReader(handle))

def summary() -> dict:
    rows=read_tracker()
    buckets={}
    for row in rows:
        status=(row.get("status") or "").strip().lower()
        bucket=STATUS_BUCKETS.get(status,"Rejected/Closed")
        buckets[bucket]=buckets.get(bucket,0)+1
    return {"total":len(rows),"status":buckets,"applications":rows}
