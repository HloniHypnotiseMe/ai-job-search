"""Evidence-backed application package planning and lifecycle."""
from __future__ import annotations
import uuid
from typing import Any

ARTIFACT_TYPES=("cv","cover_letter","ats_check","final_pack")

def _evidence(profile:dict[str,Any])->list[str]:
    out=[]
    for key in ("experience","projects","education","certifications","evidence"):
        value=profile.get(key,[])
        if isinstance(value,list):
            out.extend(str(x.get("name") or x.get("title") or x) if isinstance(x,dict) else str(x) for x in value)
        elif value: out.append(str(value))
    return out

def create_application_plan(opportunity:dict[str,Any], profile:dict[str,Any], assessment:dict[str,Any]|None=None)->dict[str,Any]:
    assessment=assessment or opportunity.get("assessment") or {}
    return {
      "id":uuid.uuid4().hex,"version":"1.0","status":"PLANNED",
      "opportunity_id":opportunity.get("id"),"company":opportunity.get("company"),
      "role":opportunity.get("title"),"source_url":opportunity.get("source_url"),
      "assessment_snapshot":assessment,
      "evidence_map":{
        "matched_requirements":assessment.get("requirement_matches",[]),
        "evidence_gaps":assessment.get("evidence_gaps",[]),
        "candidate_evidence":_evidence(profile)
      },
      "artifacts":{k:{"status":"NOT_STARTED"} for k in ARTIFACT_TYPES},
      "submission_record":{
        "submitted":False,"submitted_at":None,"channel":None,
        "artifact_versions":{},"confirmation_reference":None
      },
      "review_gate":{
        "human_approval_required":True,
        "approved":False,
        "reason":"Application content must be reviewed before submission."
      },
      "winner_effect":{
        "target_win":f"Submit an evidence-backed application for {opportunity.get('title','role')} at {opportunity.get('company','company')}",
        "proof":["Application plan linked to the captured posting and candidate evidence."],
        "next_win":"Generate and review the CV/cover-letter artifacts, then run ATS verification."
      }
    }

def record_artifact(plan:dict[str,Any], artifact_type:str, version:str, status:str="READY", evidence:list[str]|None=None)->dict[str,Any]:
    if artifact_type not in ARTIFACT_TYPES: raise ValueError("unsupported artifact type")
    updated=dict(plan); artifacts=dict(updated.get("artifacts",{}))
    item=dict(artifacts.get(artifact_type,{})); item.update({"status":status,"version":version,"evidence":evidence or []})
    artifacts[artifact_type]=item; updated["artifacts"]=artifacts; return updated

def approve_submission(plan:dict[str,Any], artifact_versions:dict[str,str])->dict[str,Any]:
    updated=dict(plan); gate=dict(updated.get("review_gate",{})); gate["approved"]=True; updated["review_gate"]=gate
    submission=dict(updated.get("submission_record",{})); submission["artifact_versions"]=dict(artifact_versions); submission["ready"]=True
    updated["submission_record"]=submission; updated["status"]="READY_FOR_USER_SUBMISSION"; return updated
