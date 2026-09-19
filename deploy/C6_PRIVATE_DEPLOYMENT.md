# C6 private deployment

Target: jobs.c6group.co.za

## Runtime

Deploy the career portal as a single private service on the C6-controlled VPS path. Coolify may be used as the deployment control plane only after the provider is pinned and the deployment is verified.

Container:
- Dockerfile.career
- port 8787
- health: GET /health

Persistent private volume:
- mount at /data/c6-career
- set CAREER_DATA_DIR=/data/c6-career

Required secrets:
- CAREER_PORTAL_USERNAME
- CAREER_PORTAL_PASSWORD_HASH
- CAREER_PORTAL_COOKIE_SECRET
- C6_MAIL_BASE_URL
- C6_MAIL_API_KEY

## DNS / access

Create the C6 DNS record for jobs.c6group.co.za only after the service is healthy. Put HTTPS in front of port 8787. Do not expose the unauthenticated application port directly to the public internet.

## Release gate

A deployment is not complete until all are true:
1. image/build succeeds;
2. unit tests pass;
3. /health returns healthy;
4. login succeeds with the configured owner credentials;
5. unauthenticated /api/* returns 401;
6. mission creation persists across restart;
7. C6 mail adapter is configured and its endpoint is reachable;
8. no personal data or secrets appear in Git;
9. rollback target is recorded;
10. the private hostname resolves over HTTPS.

## Data protection

The GitHub repository contains code only. Personal CVs, certificates, application records, interview notes, mail signals, generated CVs and cover letters belong on the private persistent volume or another approved private store.
