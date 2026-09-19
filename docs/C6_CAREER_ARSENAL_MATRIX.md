# C6 Career Arsenal Matrix

The career system is a composed system. `ai-job-search` is not allowed to duplicate capabilities that already exist in the Arsenal.

## Role of each career repository

| Repository | Capability | Role in C6 Career |
|---|---|---|
| `job-ops` | multi-board discovery, fit scoring, CV tailoring, application tracking | Discovery + search operations adapter |
| `jobsync` | application tracker, resume management, AI matching, contacts, question bank, MCP | Candidate workspace / tracking adapter |
| `ai-job-search` | setup → scrape → rank → apply → interview → outcome → upskill | Career orchestration + execution engine |
| `tech-interview-handbook` | curated technical/behavioral interview preparation | Interview knowledge source |
| `coding-interview-university` | structured CS/algorithm study plan | Technical upskilling source |

## C6 services around the repositories

| Capability | C6 boundary |
|---|---|
| Mail | C6-Mail-Services |
| Automation | n8n / DIESEL CONNECT |
| Scheduling | Cal.com |
| Knowledge/context | Context-Hub / OpenViking |
| Documents/signing | Documenso / Docuseal where needed |
| Analytics | approved C6 analytics provider after runtime verification |
| Auth/private access | C6 private deployment boundary |
| Deployment | approved C6 deployment control plane after pin + health verification |

## Non-goals

- Do not fork five repositories into one giant codebase.
- Do not duplicate JobOps discovery inside ai-job-search if an adapter can consume it.
- Do not duplicate JobSync's tracker if it is the selected tracker store.
- Do not use Gmail as the mail architecture.
- Do not use Notion as the career memory architecture.
- Do not auto-apply.

## Composition model

JOB SOURCES → JOB-OPS DISCOVERY → AI-JOB-SEARCH RANK/DECIDE → JOBSYNC/PRIVATE TRACKER → APPLICATION FACTORY → C6 MAIL → INTERVIEW PREP → OUTCOME → UPSKILL → WIN LEDGER

The exact runtime provider is selected by the C6 Arsenal registry and verified before activation. Repository presence alone does not mean a provider is production-ready.

## Selection rule

1. Find existing Arsenal provider.
2. Inspect its actual code/config/runtime contract.
3. Prefer reuse through an adapter.
4. Keep provider-specific details outside the career domain model.
5. Verify with a real test.
6. Record evidence in the SOP/SOMS acceptance record.

## Interview composition

`tech-interview-handbook` supplies curated interview knowledge and `coding-interview-university` supplies structured technical study material. They are reference corpora, not application databases.

The interview engine should create role-specific preparation plans from the actual job description, candidate evidence and identified gaps.

## Winner Effect integration

Every stage must produce a measurable next win: discovery → qualified opportunity; application → submitted evidence pack; interview → completed stage + feedback; offer → documented offer; rejection → extracted lesson / next adjustment; upskill → demonstrated evidence of the new capability.

The Win Ledger records only evidence-backed wins.
