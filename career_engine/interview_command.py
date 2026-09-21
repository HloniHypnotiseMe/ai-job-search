"""Evidence-backed Interview Command Centre."""
from __future__ import annotations
import uuid
from typing import Any

QUESTION_BANK=[
"Tell me about yourself and why this role fits your experience.",
"Describe a difficult problem you solved.",
"Tell me about a time you worked across teams.",
"What would you do if you lacked a required skill?",
"Why this company and this role?",
"What would success look like in your first six months?",
]

def _evidence(profile:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    for key in ("experience","projects","education","certifications","evidence"):
        value=profile.get(key,[])
        vals=value.values() if isinstance(value,dict) else value if isinstance(value,list) else [value]
        for x in vals:
            if x: out.append({"source":key,"evidence":x})
    return out

def build_interview_prep(application:dict[str,Any],opportunity:dict[str,Any],profile:dict[str,Any],stage:str)->dict[str,Any]:
    requirements=opportunity.get("requirements") or opportunity.get("required_skills") or []
    if isinstance(requirements,str): requirements=[x.strip() for x in requirements.split(",") if x.strip()]
    evidence=_evidence(profile)
    return {
      "id":uuid.uuid4().hex,"application_id":application.get("id"),"company":opportunity.get("company"),
      "role":opportunity.get("title"),"stage":stage,"status":"PREP_REQUIRED",
      "requirements":[str(x) for x in requirements],
      "candidate_evidence":evidence,
      "questions":[{"question":q,"answer":None,"evidence":[],"status":"DRAFT"} for q in QUESTION_BANK],
      "questions_to_ask":[
        "What would success look like in the first six months?",
        "What is the biggest challenge this team is solving now?",
        "How is performance and progression measured in this role?"
      ],
      "feedback":[],"outcome":None,
      "winner_effect":{"target_win":f"Complete the {stage} interview for {opportunity.get('title','role')}",
        "proof":[],"next_win":"Capture interview feedback and outcome."}
    }

def record_answer(prep:dict[str,Any],question:str,answer:str,evidence:list[Any])->dict[str,Any]:
    updated=dict(prep)
    rows=[]
    found=False
    for q in updated.get("questions",[]):
        item=dict(q)
        if item.get("question")==question:
            item.update({"answer":answer,"evidence":list(evidence),"status":"READY"}); found=True
        rows.append(item)
    if not found: raise KeyError(question)
    updated["questions"]=rows; return updated

def record_feedback(prep:dict[str,Any],feedback:str)->dict[str,Any]:
    updated=dict(prep); updated.setdefault("feedback",[]).append(feedback); return updated

def record_outcome(prep:dict[str,Any],outcome:dict[str,Any])->dict[str,Any]:
    updated=dict(prep); updated["outcome"]=dict(outcome); updated["status"]="OUTCOME_CAPTURED"
    updated["winner_effect"]["proof"]=[str(outcome)]; return updated
