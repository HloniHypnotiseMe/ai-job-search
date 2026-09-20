# C6 Opportunity Intelligence

Opportunity Intelligence is the evidence-backed qualification layer between discovery and the Application Factory.

## Contract
Input: canonical opportunity plus the private candidate profile.
Output: deterministic assessment with dimension scores, eligibility/location gates, explicit requirement matches, explicit evidence gaps, candidate evidence references, posting provenance, and Winner Effect Target Win / Proof / Next Win.

## Arsenal boundary
JobOps remains discovery. JobSync remains the candidate tracking boundary. ai-job-search composes this assessment contract and does not duplicate discovery or tracker internals. Company research and salary enrichment remain deeper downstream operations. No automatic application or email sending is performed by assessment.

## Scoring
The baseline mirrors the existing evaluation framework: Technical 30%, Experience 25%, Behavioral 15%, Career Alignment 30%. Location is a gate, not a weighted dimension. Missing profile evidence lowers the result rather than being inferred.

## Lifecycle
DISCOVERED -> ASSESSED -> USER_DECISION -> APPLICATION_FACTORY

An excluded opportunity remains traceable with its gate reason.

## Winner Effect
Every assessment creates a Target Win, Proof tied to the source posting, and a Next Win. An assessment is not itself a career outcome; only evidence-backed completed outcomes belong in the Win Ledger.
