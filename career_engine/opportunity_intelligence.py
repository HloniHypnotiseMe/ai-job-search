"""Deterministic, evidence-backed opportunity assessment."""
from __future__ import annotations
import re
from typing import Any

STOP={"and","the","with","for","from","that","this","your","you","our","are","will","have","has","not","but","role","work","years"}

def _text(value: Any) -> str:
    if value is None: return ""
    if isinstance(value,(list,tuple)): return " ".join(_text(x) for x in value)
    if isinstance(value,dict): return " ".join(f"{k} {_text(v)}" for k,v in value.items())
    return str(value)

def _tokens(text: str) -> set[str]:
    return {x for x in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}",text.lower()) if x not in STOP and len(x)>2}

def _evidence(profile: dict[str,Any]) -> dict[str,list[str]]:
    out={}
    for key in ("skills","technical_skills","tools","technologies","experience","projects","education","certifications","evidence"):
        value=profile.get(key,[])
        if isinstance(value,dict):
            for name,detail in value.items(): out.setdefault(str(name),[]).append(f"{key}: {_text(detail)}")
        elif isinstance(value,list):
            for item in value:
                if isinstance(item,dict):
                    label=item.get("name") or item.get("title") or item.get("skill") or key
                    out.setdefault(str(label),[]).append(_text(item))
                elif item: out.setdefault(str(item),[]).append(f"{key}: {_text(item)}")
        elif value: out.setdefault(key,[]).append(_text(value))
    return out

def _matched(job_text: str, profile: dict[str,Any]) -> list[dict[str,str]]:
    jt=_tokens(job_text); out=[]
    for label,sources in _evidence(profile).items():
        if _tokens(label) & jt: out.append({"candidate_evidence":label,"source":sources[0]})
    return out

def _requirements(job:dict[str,Any])->list[str]:
    value=job.get("requirements") or job.get("required_skills") or []
    if isinstance(value,str): return [x.strip() for x in re.split(r"[,;\n]",value) if x.strip()]
    return [str(x).strip() for x in value if str(x).strip()] if isinstance(value,list) else []

def _gate(profile:dict[str,Any],text:str)->tuple[str,str|None]:
    lower=text.lower(); auth=_text(profile.get("citizenship") or profile.get("work_authorization")).lower()
    if re.search(r"\b(?:security clearance|security cleared)\b",lower) and "clearance" not in auth:
        return "FAIL","Posting requires security clearance; no verified clearance evidence is present."
    if re.search(r"\b(?:must be|only) (?:a )?(?:south african|sa) citizen\b",lower) and "citizen" not in auth:
        return "FAIL","Posting states a citizenship requirement that is not verified in the candidate profile."
    return "PASS",None

def _location(profile:dict[str,Any],job:dict[str,Any])->tuple[str,str]:
    constraint=_text(profile.get("location_constraints") or profile.get("constraints")).lower()
    location=_text(job.get("location")).lower(); mode=_text(job.get("work_mode")).lower()
    if "no relocation" in constraint:
        if "remote" in mode or "remote" in location: return "PASS","Remote work is indicated."
        if location and any(x in location for x in ("south africa","johannesburg","pretoria","cape town","durban")):
            return "PASS","Posting location is compatible with the recorded constraint."
        if location: return "FAIL","Posting location appears outside the recorded no-relocation constraint."
    return "PASS","No location conflict is established from available profile evidence."

def assess_opportunity(job:dict[str,Any],profile:dict[str,Any])->dict[str,Any]:
    job_text=" ".join(_text(job.get(k)) for k in ("title","description","requirements","required_skills"))
    matches=_matched(job_text,profile); requirements=_requirements(job)
    evidence_labels=_tokens(" ".join(x["candidate_evidence"] for x in matches))
    req_matches=[r for r in requirements if _tokens(r) & evidence_labels]
    gaps=[r for r in requirements if r not in req_matches]
    technical=min(100,round(len(req_matches)/len(requirements)*100)) if requirements else min(100,len(matches)*15)
    exp=_matched(_text(job.get("title"))+" "+_text(job.get("description")),{"experience":profile.get("experience",[]),"projects":profile.get("projects",[])})
    experience=min(100,len(exp)*20)
    goals=_tokens(_text(profile.get("career_goals") or profile.get("goals")))
    career=min(100,len(goals & _tokens(job_text))*25) if goals else 0
    prefs=_tokens(_text(profile.get("behavioral_preferences") or profile.get("preferences")))
    behavioral=min(100,50+len(prefs & _tokens(job_text))*10) if prefs else 50
    eligibility,eligibility_note=_gate(profile,job_text); location,location_note=_location(profile,job)
    overall=round(technical*.30+experience*.25+behavioral*.15+career*.30)
    if eligibility=="FAIL" or location=="FAIL": disposition="EXCLUDED"
    elif overall>=75: disposition="STRONG_FIT"
    elif overall>=60: disposition="GOOD_FIT"
    elif overall>=45: disposition="MODERATE_FIT"
    elif overall>=30: disposition="WEAK_FIT"
    else: disposition="POOR_FIT"
    return {"version":"1.0","status":"ASSESSED","disposition":disposition,"overall_score":overall,
      "scores":{"technical":technical,"experience":experience,"behavioral":behavioral,"career_alignment":career},
      "gates":{"eligibility":eligibility,"eligibility_note":eligibility_note,"location":location,"location_note":location_note},
      "matched_evidence":matches,"requirement_matches":req_matches,"evidence_gaps":gaps,
      "unverified":["Company research has not been performed.","Claims without a recorded source are not treated as candidate evidence."],
      "provenance":{"job_id":job.get("id"),"source":job.get("source"),"source_url":job.get("source_url")},
      "winner_effect":{"target_win":f"Qualify {job.get('title','role')} at {job.get('company','company')}",
        "proof":[f"Opportunity assessment v1.0 for {job.get('source_url','')}"],
        "next_win":"Review the assessment and decide whether to enter the Application Factory."}}
