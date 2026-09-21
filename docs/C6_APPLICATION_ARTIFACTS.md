# C6 Application Artifacts

The Application Factory now has a private runtime artifact layer. It reuses the repository's existing job-application-assistant templates and rules while keeping candidate data outside Git.

## Pipeline

QUALIFIED -> PLANNED -> DRAFTED -> REVIEWED -> ATS_VERIFIED -> READY_FOR_USER_SUBMISSION -> SUBMITTED -> OUTCOME_CAPTURED

For a stored application, `ApplicationArtifactService.generate()` creates private:
- CV LaTeX source
- cover-letter LaTeX source
- ATS verification JSON
- reviewer JSON
- optional CV/cover-letter PDFs when `lualatex`/ `xelatex` are installed.

`finalize()` creates a SHA-256 manifest for the final pack. `submit()` requires the human approval gate and records the exact artifact versions, channel, timestamp and confirmation reference.

ATS verification is deliberately a verification aid, not a claim that a particular employer's ATS behaves identically.

No automatic submission or outbound email is performed.

## Grounding

Generation reads only the private profile, captured opportunity and assessment. Missing requirements stay visible as ATS gaps. Company claims are not invented.

## Interview handoff

The Interview Command Centre is a separate state object built from the application, opportunity and private evidence. It stores evidence-backed questions/answers, stage, interviewer feedback and outcome.
