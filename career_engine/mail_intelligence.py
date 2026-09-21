"""C6 Mail career signal parser.

This is intentionally proposal-only. It never changes career state and never sends mail.
An inbound transport such as n8n/C6 Mail webhook may pass normalized message events here.
"""
from __future__ import annotations
import re
from typing import Any

PATTERNS=[
 ("offer",r"\b(offer|congratulations.*offer|pleased to offer)\b"),
 ("interview",r"\b(interview|phone screen|technical interview|assessment|schedule.*call)\b"),
 ("rejection",r"\b(unfortunately|not moving forward|regret to inform|rejected|unsuccessful)\b"),
 ("application_received",r"\b(application.*received|thank you for applying|application submitted)\b"),
 ("follow_up",r"\b(follow.?up|checking in|application status)\b"),
]

def classify_message(subject:str,body:str)->dict[str,Any]:
    text=(subject+"\n"+body).lower()
    matches=[name for name,pattern in PATTERNS if re.search(pattern,text,re.I)]
    signal=matches[0] if matches else "unknown"
    return {"signal":signal,"signals":matches,"confidence":"high" if len(matches)==1 else "review","requires_user_confirmation":True}

def propose_update(message:dict[str,Any],applications:list[dict[str,Any]])->dict[str,Any]:
    classification=classify_message(str(message.get("subject","")),str(message.get("body","")))
    candidate=[]
    hay=(str(message.get("subject",""))+" "+str(message.get("body",""))).lower()
    for app in applications:
        label=f"{app.get('company','')} {app.get('role','')}".strip().lower()
        if label and any(token in hay for token in label.split() if len(token)>3): candidate.append(app.get("id"))
    return {"classification":classification,"candidate_application_ids":candidate,"proposal_only":True,"action":"present_to_user_for_confirmation"}
