"""Private application artifact generation, review, ATS checks, and immutable packs.

The repository contains only the orchestration code. Candidate data and generated
documents are written under CAREER_DATA_DIR and never committed to Git.
"""
from __future__ import annotations
import hashlib, json, re, shutil, subprocess
from pathlib import Path
from typing import Any

from .application_factory import record_artifact, approve_submission

STOP={"and","the","with","for","from","that","this","your","you","our","are","will","have","has","not","but","role","work","years","into","their","they","what","who","how"}

def slug(value:str)->str:
    value=re.sub(r"[^A-Za-z0-9]+","_",value.lower()).strip("_")
    return re.sub(r"_+","_",value)

def _text(v:Any)->str:
    if v is None:return ""
    if isinstance(v,list):return " ".join(_text(x) for x in v)
    if isinstance(v,dict):return " ".join(f"{k} {_text(x)}" for k,x in v.items())
    return str(v)

def _items(profile:dict[str,Any], keys:tuple[str,...])->list[str]:
    out=[]
    for key in keys:
        v=profile.get(key,[])
        vals=v.values() if isinstance(v,dict) else v if isinstance(v,list) else [v]
        for item in vals:
            if not item: continue
            if isinstance(item,dict):
                label=item.get("name") or item.get("title") or item.get("skill") or ""
                detail=item.get("details") or item.get("description") or item.get("summary") or item.get("evidence") or ""
                out.append(f"{label}: {detail}".strip(": "))
            else: out.append(str(item))
    return out

def latex(value:str)->str:
    s=str(value or "")
    replacements={"\\":r"\textbackslash{}", "&":r"\&","%":r"\%","$":r"\$","#":r"\#","_":r"\_","~":r"\textasciitilde{}","^":r"\textasciicircum{}"}
    for a,b in replacements.items(): s=s.replace(a,b)
    return s

def _evidence(profile:dict[str,Any])->list[str]:
    return _items(profile,("experience","projects","education","certifications","evidence"))

def _skills(profile:dict[str,Any])->list[str]:
    return _items(profile,("skills","technical_skills","tools","technologies"))

def _first(profile:dict[str,Any],*keys:str)->str:
    for k in keys:
        if profile.get(k): return str(profile[k])
    return ""

def render_cv(opportunity:dict[str,Any],profile:dict[str,Any])->str:
    company=latex(opportunity.get("company",""))
    role=latex(opportunity.get("title",""))
    name=latex(_first(profile,"name","full_name") or "Candidate")
    first,last=(name.split(" ",1)+[""])[:2] if " " in name else (name,"")
    contact=profile.get("contact",{}) if isinstance(profile.get("contact"),dict) else {}
    email=latex(contact.get("email") or profile.get("email",""))
    phone=latex(contact.get("phone") or profile.get("phone",""))
    location=latex(contact.get("location") or profile.get("location",""))
    linkedin=contact.get("linkedin") or profile.get("linkedin","")
    github=contact.get("github") or profile.get("github","")
    summary=latex(_first(profile,"summary","profile_statement") or f"Evidence-backed professional targeting the {role} role at {company}.")
    skills=_skills(profile)[:7]
    evidence=_evidence(profile)
    education=_items(profile,("education",))
    exp=_items(profile,("experience",))
    def bullets(rows,limit):
        return "\n".join(f"    \\item {{{latex(x)}}}" for x in rows[:limit]) or "    \\item {Verified experience details are maintained in the private candidate profile.}"
    return f"""\\documentclass[11pt,a4paper,sans]{{moderncv}}
\\moderncvstyle{{banking}}
\\moderncvcolor{{blue}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[scale=0.80]{{geometry}}
\\AtEndPreamble{{\\hypersetup{{pdfpagemode=UseNone}}}}
\\name{{{latex(first)}}}{{{latex(last)}}}
\\address{{{location}}}{{}}{{}}
\\phone[mobile]{{{phone}}}
\\email{{{email}}}
\\extrainfo{{\\href{{{latex(linkedin)}}}{{LinkedIn}}, \\href{{{latex(github)}}}{{GitHub}}}}
\\begin{{document}}
\\makecvtitle
\\vspace{{4pt}}
\\small{{{summary}}}
\\section{{Core Competencies}}
\\begin{{itemize}}
{bullets(skills,7)}
\\end{{itemize}}
\\section{{Professional Experience}}
\\begin{{itemize}}
{bullets(exp,6)}
\\end{{itemize}}
\\section{{Education}}
\\begin{{itemize}}
{bullets(education,4)}
\\end{{itemize}}
\\section{{Selected Evidence}}
\\begin{{itemize}}
{bullets(evidence,5)}
\\end{{itemize}}
\\end{{document}}
"""

def render_cover_letter(opportunity:dict[str,Any],profile:dict[str,Any])->str:
    company=latex(opportunity.get("company",""))
    role=latex(opportunity.get("title",""))
    name=latex(_first(profile,"name","full_name") or "Candidate")
    contact=profile.get("contact",{}) if isinstance(profile.get("contact"),dict) else {}
    email=latex(contact.get("email") or profile.get("email",""))
    phone=latex(contact.get("phone") or profile.get("phone",""))
    summary=latex(_first(profile,"summary","profile_statement") or "My background provides evidence-backed experience relevant to this role.")
    exp=_items(profile,("experience","projects"))
    bullets="\n".join(f"    \\item \\textbf{{Evidence:}} {latex(x)}" for x in exp[:3])
    return f"""\\documentclass[]{{cover}}
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}\\fancyhf{{}}
\\rfoot{{Page \\thepage}}\\thispagestyle{{empty}}\\renewcommand{{\\headrulewidth}}{{0pt}}
\\begin{{document}}
\\namesection{{}}{{\\Huge{{{name}}}}{{ {email} | {phone} }}}
\\currentdate{{\\today}}
\\lettercontent{{Dear Hiring Manager,}}
\\lettercontent{{I am applying for the {role} position at {company}. {summary}}}
\\lettercontent{{The strongest evidence I would bring to this role includes:}}
{{\\raggedright\\fontspec[Path = OpenFonts/fonts/raleway/]{{Raleway-Medium}}\\fontsize{{11pt}}{{13pt}}\\selectfont
\\begin{{itemize}}
{bullets}
\\end{{itemize}}\\par}}
\\lettercontent{{I have kept this application grounded in the evidence available in my private candidate record. I would welcome the opportunity to discuss how that experience maps to the requirements of the role.}}
\\lettercontent{{I look forward to hearing from you.}}
\\begin{{flushright}}\\closing{{Kind regards,}}\\signature{{{name}}}\\end{{flushright}}
\\end{{document}}
"""

def _tokens(text:str)->set[str]:
    return {x for x in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}",text.lower()) if x not in STOP}

def ats_check(opportunity:dict[str,Any],cv_text:str,cover_text:str)->dict[str,Any]:
    requirements=opportunity.get("requirements") or opportunity.get("required_skills") or []
    if isinstance(requirements,str): requirements=[x.strip() for x in re.split(r"[,;\n]",requirements) if x.strip()]
    corpus=_tokens(cv_text+" "+cover_text)
    rows=[{"requirement":str(r),"matched":bool(_tokens(str(r)) & corpus)} for r in requirements]
    matched=sum(1 for x in rows if x["matched"])
    missing=[x["requirement"] for x in rows if not x["matched"]]
    coverage=round(matched/len(rows)*100) if rows else 100
    return {"version":"1.0","status":"PASS" if not missing else "REVIEW_REQUIRED","coverage_percent":coverage,"requirements":rows,"missing_requirements":missing,"notes":["ATS verification is lexical/structural; it does not certify employer-specific ATS behavior."]}

def review_artifacts(opportunity:dict[str,Any],profile:dict[str,Any],cv_text:str,cover_text:str)->dict[str,Any]:
    evidence=" ".join(_evidence(profile)).lower()
    combined=cv_text+" "+cover_text
    issues=[]
    for marker in ("[YOUR","[FIRST","[LAST","[COMPANY","[ROLE"):
        if marker.lower() in combined.lower(): issues.append({"type":"placeholder","message":f"Unresolved template marker: {marker}"})
    if "—" in combined: issues.append({"type":"style","message":"Em dash found; replace with punctuation."})
    for number in re.findall(r"\\b\\d+(?:\\.\\d+)?%?",combined):
        if number not in evidence and number not in {"1","2","3","4","5","6","7"}:
            issues.append({"type":"grounding_review","message":f"Numeric claim requires evidence check: {number}"})
    return {"version":"1.0","status":"PASS" if not issues else "REVIEW_REQUIRED","issues":issues,"human_review_required":True}

def _sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _compile(source:Path,engine:str)->Path|None:
    if not shutil.which(engine): return None
    cwd=source.parent
    subprocess.run([engine,"-interaction=nonstopmode",source.name],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    pdf=source.with_suffix(".pdf")
    return pdf if pdf.exists() else None

class ApplicationArtifactService:
    def __init__(self,store):
        self.store=store
    def generate(self,application_id:str)->dict[str,Any]:
        apps=self.store.collection("applications",[])
        row=next((x for x in apps if x.get("id")==application_id),None)
        if not row: raise KeyError(application_id)
        plan=row.get("plan") or {}
        opp=next((x for x in self.store.collection("opportunities",[]) if x.get("id")==row.get("opportunity_id")),{})
        profile=self.store.collection("profile",{})
        if not profile: raise ValueError("candidate profile is required before generating application artifacts")
        root=self.store.root/"applications"/slug(f"{opp.get('company','company')}_{opp.get('title','role')}")
        root.mkdir(parents=True,exist_ok=True)
        cv=render_cv(opp,profile); cover=render_cover_letter(opp,profile)
        cvp=root/"cv_v1.tex"; clp=root/"cover_letter_v1.tex"
        cvp.write_text(cv,encoding="utf-8"); clp.write_text(cover,encoding="utf-8")
        ats=ats_check(opp,cv,cover); review=review_artifacts(opp,profile,cv,cover)
        (root/"ats_v1.json").write_text(json.dumps(ats,indent=2)+"\n",encoding="utf-8")
        (root/"review_v1.json").write_text(json.dumps(review,indent=2)+"\n",encoding="utf-8")
        cvpdf=_compile(cvp,"lualatex"); clpdf=_compile(clp,"xelatex")
        artifacts={"cv":cvp,"cover_letter":clp,"ats_check":root/"ats_v1.json"}
        if cvpdf: artifacts["cv_pdf"]=cvpdf
        if clpdf: artifacts["cover_letter_pdf"]=clpdf
        plan=record_artifact(plan,"cv","v1","READY",["private candidate profile"])
        plan=record_artifact(plan,"cover_letter","v1","READY",["private candidate profile","captured posting"])
        plan=record_artifact(plan,"ats_check","v1",ats["status"],ats["missing_requirements"])
        plan=record_artifact(plan,"final_pack","v1","REVIEW_REQUIRED",[])
        plan["review"]=review
        row["plan"]=plan; row["status"]="REVIEWED" if review["status"]=="PASS" else "REVIEW_REQUIRED"
        self.store.put_collection("applications",apps)
        return {"application_id":application_id,"directory":str(root),"artifacts":{k:str(v) for k,v in artifacts.items()},"ats":ats,"review":review}

    def finalize(self,application_id:str)->dict[str,Any]:
        apps=self.store.collection("applications",[])
        row=next((x for x in apps if x.get("id")==application_id),None)
        if not row: raise KeyError(application_id)
        plan=row.get("plan") or {}
        if plan.get("review",{}).get("status")!="PASS": raise ValueError("application review must pass before finalization")
        root=self.store.root/"applications"/slug(f"{row.get('company','company')}_{row.get('role','role')}")
        manifest=[]
        for name in ("cv_v1.tex","cover_letter_v1.tex","ats_v1.json","review_v1.json"):
            p=root/name
            if p.exists(): manifest.append({"file":name,"sha256":_sha(p)})
        pack={"version":"1.0","application_id":application_id,"files":manifest,"immutable":True}
        (root/"final_pack_v1.json").write_text(json.dumps(pack,indent=2)+"\n",encoding="utf-8")
        plan=record_artifact(plan,"final_pack","v1","READY",[x["sha256"] for x in manifest])
        plan["final_pack"]=pack; row["plan"]=plan; row["status"]="READY_FOR_USER_SUBMISSION"
        self.store.put_collection("applications",apps)
        return pack

    def submit(self,application_id:str,channel:str,confirmation_reference:str)->dict[str,Any]:
        apps=self.store.collection("applications",[])
        row=next((x for x in apps if x.get("id")==application_id),None)
        if not row: raise KeyError(application_id)
        plan=row.get("plan") or {}
        versions={k:v.get("version") for k,v in plan.get("artifacts",{}).items() if k in ("cv","cover_letter","ats_check","final_pack")}
        if not plan.get("review_gate",{}).get("approved"): raise ValueError("human approval is required before submission")
        if not plan.get("final_pack"): raise ValueError("final pack must be finalized before submission")
        plan["submission_record"]={"submitted":True,"submitted_at":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),"channel":channel,"artifact_versions":versions,"confirmation_reference":confirmation_reference}
        plan["status"]="SUBMITTED"; row["plan"]=plan; row["status"]="SUBMITTED"
        self.store.put_collection("applications",apps)
        return plan["submission_record"]
