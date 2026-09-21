"""South African job-source boundary.

JobOps remains the discovery engine. This module records source policy, provenance,
freshness and dedupe without creating a second scraper.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import hashlib

SOUTH_AFRICA_SOURCES={
 "job_ops":{"kind":"aggregator_adapter","country":"ZA","active":True},
 "careerjunction":{"kind":"external_source","country":"ZA","active":True},
 "pnet":{"kind":"external_source","country":"ZA","active":True},
 "linkedin":{"kind":"external_source","country":"ZA","active":True},
 "employer_ats":{"kind":"canonical_employer_source","country":"ZA","active":True},
}

def source_registry()->dict[str,dict[str,Any]]:
    return {k:dict(v) for k,v in SOUTH_AFRICA_SOURCES.items()}

def canonical_key(record:dict[str,Any])->str:
    raw="|".join(str(record.get(k,"")).strip().lower() for k in ("company","title","location","source_url"))
    return hashlib.sha256(raw.encode()).hexdigest()

def normalize_source_record(record:dict[str,Any],source:str)->dict[str,Any]:
    if source not in SOUTH_AFRICA_SOURCES: raise ValueError(f"unsupported discovery source: {source}")
    now=datetime.now(timezone.utc).isoformat()
    out=dict(record); out["source"]=source; out["country"]="ZA"; out["canonical_key"]=record.get("canonical_key") or canonical_key(record)
    out["provenance"]={"source":source,"captured_at":now,"attribution_required":True}
    out.setdefault("status","NEW"); return out

def ingest_records(records:list[dict[str,Any]],source:str,existing:list[dict[str,Any]]|None=None)->tuple[list[dict[str,Any]],dict[str,int]]:
    rows=list(existing or []); seen={x.get("canonical_key") for x in rows}; added=0; duplicates=0
    for record in records:
        item=normalize_source_record(record,source)
        if item["canonical_key"] in seen: duplicates+=1; continue
        rows.append(item); seen.add(item["canonical_key"]); added+=1
    return rows,{"added":added,"duplicates":duplicates,"captured_at":datetime.now(timezone.utc).isoformat()}
