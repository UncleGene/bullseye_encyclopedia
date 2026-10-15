# Output Audit Report

Date: 2026-10-15

## Summary

| Output | Validation | Main Counts | Improvement Signal |
| --- | --- | --- | --- |
| As-is static | pass | 524 files; 1093 local refs | 18 suppressed internal URLs; 43 unresolved-rewrite pages |
| Raw static | pass | 150 articles; 165 assets | 0 fallback articles; 7 missing artifacts |
| EPUB | pass | 150 chapters; 160 assets | 59 suppressed internal resource links; 0 unresolved internal links |

Finding counts:

- Blocking: `0`
- Candidate: `3`
- Deferred: `0`

## Output Paths

- As-is static: `exports/static-site/as-is`
- Raw static: `exports/static-site/raw`
- EPUB: `exports/ebook/bullseye-pistol.epub`

## Findings

- `candidate` / `raw-static`: Raw article site missing artifacts (7 unrecovered internal resources are centralized in the Missing Artifacts page.) Next: Keep the centralized catalogue with source-backed descriptions and treat these files as permanent gaps unless supplied outside Wayback later.
- `candidate` / `as-is-static`: As-is permanent non-Wayback file gaps are identified (8 suppressed owner-file candidates, 6 unrecovered article URLs, 2 provider artifacts.) Next: Treat the owner-file candidates as permanent non-Wayback gaps unless files are supplied out-of-band, and keep the other suppressed URLs as explicit gaps or artifacts.
- `candidate` / `as-is-static`: As-is unresolved rewrites are now mostly residual provider-era artifacts (43 pages have unresolved rewrites; 691 external refs and 11 unique hosting-template internal URLs dominate the internal set.) Next: Keep pruning limited to release-facing provider placeholder pages and use the remaining inventory as a documented preservation artifact unless a narrower cleanup target emerges.

## Open Questions

Blocking: none.

Routed:

- None.

Deferred:

- Should a DB import/export contract be defined? Postponed until explicit user request.
- Should public URL redirects or canonical public URLs be assigned? Deferred until a public rebuild or redirect-map slice.

## Recommended Next Slice

Explicit user selection

Reason: Release-facing static and EPUB behavior is aligned and external epubcheck validation passed; DB work, custom domains, and redirects remain deferred until requested.

## Source Reports

- Raw reproduction: `exports/static-site/as-is/_reproduction-report.json`
- Raw validation: `exports/static-site/as-is/_validation-report.json`
- Canonical export: `exports/static-site/raw/_raw-export-report.json`
- Canonical validation: `exports/static-site/raw/_validation-report.json`
- EPUB export: `exports/ebook/_ebook-export-report.json`
