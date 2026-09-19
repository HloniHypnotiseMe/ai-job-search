# C6 Career Integration Contract

This is the boundary between the career engine and Arsenal components.

## Job object

Minimum canonical fields: `id`, `source`, `source_url`, `company`, `title`, `location`, `work_mode`, `description`, `posted_at`, `first_seen_at`, `canonical_key`, `status`, `fit`, `evidence`, `created_at`, `updated_at`.

A provider may have additional fields. The canonical career model must not depend on them.

## Candidate evidence

Never represent a claim as candidate fact unless it has a source: CV/resume, employment record, project record, certificate/qualification, portfolio/GitHub, reference, or user-confirmed statement.

AI may summarize or map evidence; it may not manufacture evidence.

## Application

An application links: job → evidence map → CV version → cover letter version → submission event → communications → interview stages → outcome. Every submitted artifact is immutable after submission; revisions create a new version.

## Communication

Career communications are routed through C6-Mail-Services. Passive inbound signals may create a proposed state change, but the system must not silently change an application state without an auditable rule or user confirmation.

## Interview preparation

Consumes job description, company context, candidate evidence, interview stage, prior feedback, relevant Tech Interview Handbook material and relevant Coding Interview University material. Output is preparation plan, evidence stories, technical topics, practice questions, mock interview, feedback and next win.

## Upskill

An upskill mission links market signal → skill gap → learning source → practice/build → proof artifact → re-evaluation. A resource completed without evidence is not treated as a career win.

## Security

Providers receive only the candidate data required for the operation. Secrets remain runtime configuration. Public repository history must contain no personal career records or credentials.
