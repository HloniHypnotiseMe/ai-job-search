import hashlib, hmac, json, os, secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from career_engine.service import CareerService
from career_engine.store import CareerStore

HOST=os.getenv("CAREER_PORTAL_HOST","127.0.0.1")
PORT=int(os.getenv("CAREER_PORTAL_PORT","8787"))
USERNAME=os.getenv("CAREER_PORTAL_USERNAME","")
PASSWORD_HASH=os.getenv("CAREER_PORTAL_PASSWORD_HASH","")
COOKIE_SECRET=os.getenv("CAREER_PORTAL_COOKIE_SECRET","")

def password_hash(password, salt=None):
    salt=salt or secrets.token_hex(16)
    digest=hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()
    return "scrypt$%s$%s"%(salt,digest)

def verify_password(password, encoded):
    try:
        algorithm,salt,digest=encoded.split("$",2)
        if algorithm!="scrypt": return False
        candidate=hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()
        return hmac.compare_digest(candidate,digest)
    except ValueError: return False

def signed_session(username):
    return username+"."+hmac.new(COOKIE_SECRET.encode(),username.encode(),hashlib.sha256).hexdigest()

def valid_session(handler):
    expected=signed_session(USERNAME) if USERNAME and COOKIE_SECRET else ""
    for part in handler.headers.get("Cookie","").split(";"):
        name,_,value=part.strip().partition("=")
        if name=="c6career_session": return bool(expected) and hmac.compare_digest(value,expected)
    return False

PAGE="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>C6 Career Command Centre</title><style>body{font-family:system-ui;background:#0b1020;color:#edf2f7;margin:0}.wrap{max-width:1180px;margin:auto;padding:28px}.card{background:#151d32;border:1px solid #2b3652;border-radius:16px;padding:20px;margin:14px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.muted{color:#9aa7bf}.pill{display:inline-block;padding:4px 9px;border-radius:999px;background:#263450}.btn{background:#6ee7b7;border:0;padding:10px 14px;border-radius:10px;cursor:pointer;font-weight:700}input{background:#0e1528;color:white;border:1px solid #35415e;padding:10px;border-radius:9px;width:100%;box-sizing:border-box}form{display:grid;gap:10px;max-width:560px}.win{border-left:4px solid #6ee7b7}</style></head><body><div class="wrap"><h1>🔥 C6 Career Command Centre</h1><p class="muted">Private career engine · SOP/SOMS · WIN → ABSORB → VERIFY → SCALE</p><div id="app">Loading...</div></div><script>
function esc(s){return String(s||"").replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
async function load(){var r=await fetch("/api/dashboard");if(r.status===401){location="/login";return}var d=await r.json(),m=d.missions||[],w=d.wins||[];var h="<div class='grid'><div class='card'><div class='muted'>Missions</div><h2>"+m.length+"</h2></div><div class='card'><div class='muted'>Proven wins</div><h2>"+w.length+"</h2></div><div class='card'><div class='muted'>Active</div><h2>"+m.filter(function(x){return x.status==="ACTIVE"}).length+"</h2></div></div>";h+="<div class='card'><h2>Career Mission Control</h2><form onsubmit='createMission(event)'><input id='objective' placeholder='Objective / target win' required><button class='btn'>Create Mission</button></form></div>";m.forEach(function(x){h+="<div class='card'><span class='pill'>"+esc(x.stage)+"</span> <span class='pill'>"+esc(x.status)+"</span><h3>"+esc(x.objective)+"</h3><div class='muted'>Proof captured: "+((x.evidence||[]).length)+" · Result: "+(Object.keys(x.result||{}).length?"yes":"pending")+"</div></div>"});h+="<div class='card'><h2>Win Ledger</h2>";if(!w.length)h+="<p class='muted'>No proven wins yet.</p>";w.forEach(function(x){h+="<div class='card win'><b>"+esc(x.target)+"</b><div class='muted'>Proof: "+(x.proof||[]).map(esc).join(" · ")+"</div><div>Next win: "+esc(x.next_win)+"</div></div>"});h+="</div>";document.getElementById("app").innerHTML=h}
async function createMission(e){e.preventDefault();var objective=document.getElementById("objective").value.trim();await fetch("/api/missions",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({objective:objective})});load()}load();
</script></body></html>"""

LOGIN="""<!doctype html><html><body style="font-family:system-ui;max-width:420px;margin:80px auto;background:#0b1020;color:white;padding:30px"><h1>🔐 C6 Career</h1><form method="post" action="/login" style="display:grid;gap:12px"><input name="username" placeholder="Username" required style="padding:12px"><input name="password" type="password" placeholder="Password" required style="padding:12px"><button style="padding:12px">Sign in</button></form></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def send_json(self,status,value):
        body=json.dumps(value).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def send_page(self,body,status=200):
        raw=body.encode();self.send_response(status);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health": return self.send_json(200,{"status":"healthy","service":"c6-career-command-centre"})
        if path=="/login": return self.send_page(LOGIN)
        if not valid_session(self): return self.send_json(401,{"error":"authentication_required"}) if path.startswith("/api/") else self.send_page(LOGIN,401)
        if path=="/": return self.send_page(PAGE)
        if path=="/api/dashboard": return self.send_json(200,CareerStore().dashboard())
        if path=="/api/missions": return self.send_json(200,{"missions":CareerService().missions()})
        return self.send_json(404,{"error":"not_found"})
    def do_POST(self):
        path=urlparse(self.path).path
        length=int(self.headers.get("Content-Length","0"));body=self.rfile.read(length)
        if path=="/login":
            data=parse_qs(body.decode());user=data.get("username",[""])[0];password=data.get("password",[""])[0]
            if user==USERNAME and verify_password(password,PASSWORD_HASH):
                self.send_response(303);self.send_header("Location","/");self.send_header("Set-Cookie","c6career_session="+signed_session(USERNAME)+"; HttpOnly; Secure; SameSite=Strict; Path=/");self.end_headers();return
            return self.send_page(LOGIN,401)
        if not valid_session(self): return self.send_json(401,{"error":"authentication_required"})
        if path=="/api/missions":
            try: data=json.loads(body or b"{}")
            except json.JSONDecodeError: return self.send_json(400,{"error":"invalid_json"})
            objective=str(data.get("objective","")).strip()
            if not objective: return self.send_json(400,{"error":"objective_required"})
            return self.send_json(201,CareerService().create_mission(objective))
        return self.send_json(404,{"error":"not_found"})

def main():
    if not (USERNAME and PASSWORD_HASH and COOKIE_SECRET): raise SystemExit("CAREER_PORTAL_USERNAME, CAREER_PORTAL_PASSWORD_HASH and CAREER_PORTAL_COOKIE_SECRET are required")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()

if __name__=="__main__": main()
