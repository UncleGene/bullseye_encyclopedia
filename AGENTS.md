# Bullseye Recovery Project Guide

## Project

Recover and preserve `bullseyepistol.com` content after provider takedown, then normalize it so it can feed multiple presentation formats: a single ebook, a static HTML site, and a DB-backed content engine.

## Operating Priorities

1. Preserve recoverable source material locally before rewriting or modernizing it.
2. Keep the recovery structure presentation-neutral.
3. Retain provenance for every raw page, canonical article, asset, and derived content record.
4. Separate immutable raw archive data from normalized canonical content and generated exports.

## Skill Routing

MiniMe skills are optional in this project. Use judgment: work directly,
keep the Completion Gates below, and run the full MiniMe gate chain (doc-sync,
scope, simplifier, reviewer, decision prompts) only when the user asks for it.
The table below names the skill to reach for when one is wanted.

| Work type | Owning skill | Gate |
|---|---|---|
| Requirements | `minime-requirements-manager` | Acceptance criteria must be verifiable |
| Feature or domain spec | `minime-project-spec` | Inputs, outputs, errors, non-goals, and open questions recorded |
| Roadmap and milestones | `minime-project-milestone` | Each milestone has done criteria and release gates |
| Validation plan | `minime-validation-planner` | Tests or manual checks cover provenance, completeness, idempotency, and failure cases |
| Implementation slice selection | `minime-implementation-step-selector` | Next slice is small, end-to-end, and traceable |
| Code review | `minime-code-reviewer` | Findings first, ordered by severity |
| Simplification pass | `minime-code-simplifier` | No speculative abstraction beyond documented needs |
| Completion verification | `minime-verification-gate` | Evidence exists before completion is claimed |

## Completion Gates

- Recovery commands must be idempotent: reruns update manifests without duplicating canonical records.
- Every downloaded file must retain source URL, Wayback timestamp, retrieval URL, HTTP status, content type, checksum, and retrieval time.
- Every normalized article must trace to one or more raw captures.
- Canonical article bodies must exclude recurring site chrome unless it carries article meaning, ordering, taxonomy, or provenance.
- Generated ebook, static site, and DB outputs must be reproducible from `content/canonical` plus `content/assets`.
- Missing or ambiguous assets must be recorded explicitly instead of silently replaced.
