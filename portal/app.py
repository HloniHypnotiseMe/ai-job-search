import hashlib
import hmac
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from career_engine.service import CareerService
from career_engine.store import CareerStore


HOST = os.getenv("CAREER_PORTAL_HOST", "127.0.0.1")
PORT = int(os.getenv("CAREER_PORTAL_PORT", "8787"))
USERNAME = os.getenv("CAREER_PORTAL_USERNAME", "")
PASSWORD_HASH = os.getenv("CAREER_PORTAL_PASSWORD_HASH", "")
COOKIE_SECRET = os.getenv("CAREER_PORTAL_COOKIE_SECRET", "")


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return "scrypt$%s$%s" % (salt, digest)


def verify_password(password, encoded):
    try:
        algorithm, salt, digest = encoded.split("$", 2)
        if algorithm != "scrypt":
            return False
        candidate = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
        return hmac.compare_digest(candidate, digest)
    except (ValueError, TypeError):
        return False


def signed_session(username):
    return username + "." + hmac.new(COOKIE_SECRET.encode(), username.encode(), hashlib.sha256).hexdigest()


def valid_session(handler):
    expected = signed_session(USERNAME) if USERNAME and COOKIE_SECRET else ""
    for part in handler.headers.get("Cookie", "").split(";"):
        name, _, value = part.strip().partition("=")
        if name == "c6career_session":
            return bool(expected) and hmac.compare_digest(value, expected)
    return False


PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>C6 Career Command Centre</title>
<style>
body{font-family:system-ui;background:#0b1020;color:#edf2f7;margin:0}.wrap{max-width:1220px;margin:auto;padding:28px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}.card{background:#151d32;border:1px solid #2b3652;border-radius:16px;padding:18px;margin:14px 0}
.muted{color:#9aa7bf}.pill{display:inline-block;padding:4px 9px;border-radius:999px;background:#263450;margin-right:5px}
.btn{background:#6ee7b7;border:0;padding:10px 14px;border-radius:10px;cursor:pointer;font-weight:700}
input,textarea,select{background:#0e1528;color:white;border:1px solid #35415e;padding:10px;border-radius:9px;width:100%;box-sizing:border-box}
form{display:grid;gap:10px;max-width:700px}.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.win{border-left:4px solid #6ee7b7}
table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px;border-bottom:1px solid #2b3652}
a{color:#9ee6ff}.section{margin-top:30px}
</style></head><body><div class="wrap">
<h1>🔥 C6 Career Command Centre</h1><p class="muted">Private career engine · Arsenal-first · WIN → ABSORB → VERIFY → SCALE</p>
<div id="app">Loading...</div></div>
<script>
function esc(s){return String(s||"").replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function cards(d){var s=d.summary||{};return "<div class='grid'>"+
["opportunities","applications","interviews","followups","skill_gaps","active_missions","proven_wins"].map(function(k){return "<div class='card'><div class='muted'>"+k.replaceAll("_"," ")+"</div><h2>"+(s[k]||0)+"</h2></div>"}).join("")+"</div>"}
function list(title,rows,fields){var h="<div class='section'><h2>"+title+"</h2><div class='card'>";if(!rows.length)return h+"<p class='muted'>None yet.</p></div></div>";h+="<table><tr>"+fields.map(function(f){return "<th>"+f+"</th>"}).join("")+"</tr>";rows.slice(-20).reverse().forEach(function(r){h+="<tr>"+fields.map(function(f){var v=r[f.toLowerCase().replaceAll(" ","_")];return "<td>"+esc(v)+"</td>"}).join("")+"</tr>"});return h+"</table></div></div>"}
async function post(path,payload){var r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});if(!r.ok){alert((await r.json()).error||"Request failed");return false}return true}
async function createMission(e){e.preventDefault();if(await post("/api/missions",{objective:objective.value.trim()}))load()}
async function addOpportunity(e){e.preventDefault();if(await post("/api/opportunities",{title:op_title.value,company:op_company.value,source_url:op_url.value,location:op_location.value,status:"NEW"}))load()}
async function addApplication(e){e.preventDefault();if(await post("/api/applications",{opportunity_id:app_opp.value,company:app_company.value,role:app_role.value,status:"DRAFT"}))load()}
async function addInterview(e){e.preventDefault();if(await post("/api/interviews",{application_id:int_app.value,stage:int_stage.value,scheduled_at:int_when.value}))load()}
async function load(){var r=await fetch("/api/dashboard");if(r.status===401){location="/login";return}var d=await r.json();var h=cards(d);
h+="<div class='section'><h2>Mission Control</h2><div class='card'><form onsubmit='createMission(event)'><input id='objective' placeholder='Target Win / career objective' required><button class='btn'>Create Mission</button></form></div>";
(d.missions||[]).slice(-10).reverse().forEach(function(x){h+="<div class='card'><span class='pill'>"+esc(x.stage)+"</span><span class='pill'>"+esc(x.status)+"</span><h3>"+esc(x.objective)+"</h3><div class='muted'>Proof: "+((x.evidence||[]).length)+" · Result: "+(Object.keys(x.result||{}).length?"captured":"pending")+"</div></div>"});
h+="</div><div class='section'><h2>Opportunity Intake</h2><div class='card'><form onsubmit='addOpportunity(event)'><div class='row'><input id='op_title' placeholder='Role title' required><input id='op_company' placeholder='Company' required></div><div class='row'><input id='op_url' placeholder='Canonical posting URL' required><input id='op_location' placeholder='Location / remote'></div><button class='btn'>Capture Opportunity</button></form></div></div>";
h+="<div class='section'><h2>Application Factory</h2><div class='card'><form onsubmit='addApplication(event)'><div class='row'><input id='app_opp' placeholder='Opportunity ID' required><input id='app_company' placeholder='Company' required><input id='app_role' placeholder='Role' required></div><button class='btn'>Create Application Record</button></form></div></div>";
h+="<div class='section'><h2>Interview Command Centre</h2><div class='card'><form onsubmit='addInterview(event)'><div class='row'><input id='int_app' placeholder='Application ID' required><input id='int_stage' placeholder='Stage' required><input id='int_when' placeholder='Scheduled time'></div><button class='btn'>Schedule Interview Stage</button></form></div></div>";
h+=list("Opportunities",d.opportunities||[],["Title","Company","Source_url","Status"]);
h+=list("Applications",d.applications||[],["Company","Role","Status"]);
h+=list("Interviews",d.interviews||[],["Application_id","Stage","Status"]);
h+=list("Follow-ups",d.followups||[],["Application_id","Due_at","Status"]);
h+=list("Skill Gaps",d.skill_gaps||[],["Skill","Evidence_gap","Status"]);
h+="<div class='section'><h2>Win Ledger</h2>";if(!(d.wins||[]).length)h+="<div class='card muted'>No evidence-backed wins yet.</div>";(d.wins||[]).slice(-20).reverse().forEach(function(x){h+="<div class='card win'><b>"+esc(x.target)+"</b><div class='muted'>Proof: "+(x.proof||[]).map(esc).join(" · ")+"</div><div>Next win: "+esc(x.next_win)+"</div></div>"});h+="</div>";
document.getElementById("app").innerHTML=h}load();
</script></body></html>"""


LOGIN = """<!doctype html><html><body style="font-family:system-ui;max-width:420px;margin:80px auto;background:#0b1020;color:white;padding:30px">
<h1>🔐 C6 Career</h1><form method="post" action="/login" style="display:grid;gap:12px">
<input name="username" placeholder="Username" required style="padding:12px"><input name="password" type="password" placeholder="Password" required style="padding:12px">
<button style="padding:12px">Sign in</button></form></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_page(self, body, status=200):
        raw = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _require_auth(self):
        if not valid_session(self):
            self.send_json(401, {"error": "authentication_required"})
            return False
        return True

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self.send_json(200, {"status": "healthy", "service": "c6-career-command-centre"})
        if path == "/login":
            return self.send_page(LOGIN)
        if not valid_session(self):
            return self.send_json(401, {"error": "authentication_required"}) if path.startswith("/api/") else self.send_page(LOGIN, 401)
        if path == "/":
            return self.send_page(PAGE)
        if path == "/api/dashboard":
            return self.send_json(200, CareerStore().dashboard())
        if path == "/api/profile":
            return self.send_json(200, CareerService().profile())
        if path == "/api/missions":
            return self.send_json(200, {"missions": CareerService().missions()})
        if path == "/api/intelligence":
            return self.send_json(200, CareerService().career_intelligence())
        if path == "/api/discovery-sources":
            return self.send_json(200, CareerService().discovery_sources())
        return self.send_json(404, {"error": "not_found"})

    def _json_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return None

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/login":
            data = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode())
            user = data.get("username", [""])[0]
            password = data.get("password", [""])[0]
            if user == USERNAME and verify_password(password, PASSWORD_HASH):
                self.send_response(303)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", "c6career_session=" + signed_session(USERNAME) + "; HttpOnly; Secure; SameSite=Strict; Path=/")
                self.end_headers()
                return
            return self.send_page(LOGIN, 401)

        if not self._require_auth():
            return
        data = self._json_body()
        if data is None:
            return self.send_json(400, {"error": "invalid_json"})

        service = CareerService()
        routes = {
            "/api/missions": service.create_mission,
            "/api/opportunities": service.add_opportunity,
            "/api/applications": service.add_application,
            "/api/interviews": service.add_interview,
            "/api/followups": service.add_followup,
            "/api/skill-gaps": service.add_skill_gap,
        }
        fn = routes.get(path)
        try:
            if path == "/api/missions":
                result = fn(data["objective"])
            elif path == "/api/applications/generate":
                result = service.generate_application_artifacts(data["application_id"])
            elif path == "/api/applications/finalize":
                result = service.finalize_application(data["application_id"])
            elif path == "/api/applications/submit":
                result = service.submit_application(data["application_id"], data["channel"], data["confirmation_reference"])
            elif path == "/api/interviews/prepare":
                result = service.prepare_interview(data["application_id"], data["stage"])
            elif path == "/api/applications/outcome":
                result = service.record_application_outcome(data["application_id"], data["outcome"])
            elif path == "/api/interviews/outcome":
                result = service.record_interview_outcome(data["interview_id"], data["outcome"])
            elif path == "/api/mail/signals":
                result = service.propose_mail_signal(data)
            elif path == "/api/discovery/ingest":
                result = service.ingest_discovery_records(data["records"], data["source"])
            elif fn:
                result = fn(data)
            else:
                return self.send_json(404, {"error": "not_found"})
        except (KeyError, ValueError) as exc:
            return self.send_json(400, {"error": str(exc)})
        return self.send_json(201, result)


def main():
    if not (USERNAME and PASSWORD_HASH and COOKIE_SECRET):
        raise SystemExit("CAREER_PORTAL_USERNAME, CAREER_PORTAL_PASSWORD_HASH and CAREER_PORTAL_COOKIE_SECRET are required")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
