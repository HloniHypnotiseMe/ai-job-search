"""Outcome capture and Winner Effect learning loop."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

FINAL={"hired","offer_declined","rejected","no_response","withdrawn"}

def record_application_outcome(app:dict[str,Any], outcome:dict[str,Any])->dict[str,Any]:
    status=str(outcome.get("status","")).strip().lower()
    if status not in FINAL: raise ValueError("unsupported final outcome")
    updated=dict(app); plan=dict(updated.get("plan") or {})
    payload=dict(outcome); payload["recorded_at"]=datetime.now(timezone.utc).isoformat()
    plan["outcome"]=payload; plan["status"]="OUTCOME_CAPTURED"; updated["plan"]=plan; updated["status"]=status
    return updated

def record_interview_outcome(interview:dict[str,Any], outcome:dict[str,Any])->dict[str,Any]:
    updated=dict(interview); updated["outcome"]=dict(outcome); updated["status"]="OUTCOME_CAPTURED"; return updated

def learning_signals(applications:list[dict[str,Any]],opportunities:list[dict[str,Any]],interviews:list[dict[str,Any]],skill_gaps:list[dict[str,Any]])->dict[str,Any]:
    source={}
    roles={}
    for o in opportunities:
        source_name=o.get("source") or "unknown"
        source.setdefault(source_name,{"opportunities":0,"applications":0,"interviews":0,"outcomes":0})
        source[source_name]["opportunities"]+=1
        roles[str(o.get("title") or "unknown")]=roles.get(str(o.get("title") or "unknown"),0)+1
    by_opp={a.get("opportunity_id"):a for a in applications}
    for o in opportunities:
        a=by_opp.get(o.get("id"))
        if a:
            source[o.get("source") or "unknown"]["applications"]+=1
    for i in interviews:
        app=next((a for a in applications if a.get("id")==i.get("application_id")),None)
        if app:
            opp=next((o for o in opportunities if o.get("id")==app.get("opportunity_id")),None)
            source[(opp or {}).get("source") or "unknown"]["interviews"]+=1
    outcomes=[a for a in applications if (a.get("status") or "").lower() in FINAL]
    for a in outcomes:
        opp=next((o for o in opportunities if o.get("id")==a.get("opportunity_id")),None)
        source[(opp or {}).get("source") or "unknown"]["outcomes"]+=1
    recurring={}
    for g in skill_gaps:
        skill=str(g.get("skill") or "").strip()
        if skill: recurring[skill]=recurring.get(skill,0)+1
    submitted=[a for a in applications if (a.get("status") or "").lower() in {"submitted","applied","interview","offer","hired","rejected","no_response","offer_declined"}]
    interviews_count=len(interviews)
    return {
      "version":"1.0","applications":len(applications),"submitted_applications":len(submitted),
      "interviews":interviews_count,"final_outcomes":len(outcomes),
      "application_to_interview_percent":round(interviews_count/len(submitted)*100) if submitted else 0,
      "interview_to_final_percent":round(len(outcomes)/interviews_count*100) if interviews_count else 0,
      "source_performance":source,
      "recurring_skill_gaps":sorted(recurring.items(),key=lambda x:(-x[1],x[0])),
      "role_demand":sorted(roles.items(),key=lambda x:(-x[1],x[0])),
      "winner_effect":{"target_win":"Improve the next application/interview cycle using recorded evidence.","proof":[f"{len(outcomes)} outcomes, {interviews_count} interviews, {len(recurring)} recurring skill gaps."],"next_win":"Use the highest-frequency evidence gap to produce a verified skill artifact."}
    }
