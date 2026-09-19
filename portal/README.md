# C6 Private Career Command Centre

Private browser control surface for the ai-job-search workflow.

Personal career data is stored outside the repository via CAREER_DATA_DIR. Authentication is environment-backed. Session cookies are signed and marked HttpOnly, Secure and SameSite=Strict. Put the service behind HTTPS and a private C6 access boundary before exposing it at jobs.c6group.co.za.

Run:
python3 tools/hash_career_password.py 'your-password'
python3 portal/server.py

Required: CAREER_PORTAL_USERNAME, CAREER_PORTAL_PASSWORD_HASH, CAREER_PORTAL_COOKIE_SECRET.
