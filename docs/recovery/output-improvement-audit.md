# Output Improvement Audit

Date: 2026-05-23

Historical note: this audit predates the release-facing `raw` / `as-is`
rename, the centralized `raw` missing-artifacts page, provider-placeholder
pruning in `as-is`, and the EPUB reader-safety policy. Use
`docs/recovery/output-audit-report.md` for current release status.

## Scope

Review the three generated reader outputs before starting DB work:

- As-is static site: `exports/static-site/as-is`
- Raw article static site: `exports/static-site/raw`
- EPUB ebook: `exports/ebook/bullseye-pistol.epub`

DB import/export work is postponed until the user explicitly requests it.

## Current Evidence

Raw as-is static site:

- Validation passed with `0` broken local references across `1,121` local
  references.
- Reproduction report records `24` local missing-resource note pages.
- Reproduction report records `48` pages with unresolved rewrites; most are
  preserved external links, provider-default pages, or explicit local
  missing-resource notes.

Raw article static site:

- Validation passed with `0` broken local references across `1,528` local
  references.
- `150` canonical article pages generated.
- `87` articles are in `Other Recovered Articles` because the current
  canonical navigation preserves the recovered homepage exactly.
- `8` unrecovered internal resources are represented as local missing-note
  pages.

EPUB:

- Built-in EPUB package validation passed.
- `150` article chapters generated.
- `63` raw-index-listed articles are placed under raw-index chapter groups.
- `87` additional recovered articles are included in a final generated group.
- `160` recovered image assets are embedded.
- `0` missing asset records and `0` unsupported asset records.
- `654` local EPUB package references resolve with `0` broken references.
- `33` internal links are preserved as original URL references because they
  point to non-article internal resources or unrecovered files.
- `epubcheck` is not installed locally, so external EPUB validation remains
  a release risk.

## Improvement Candidates

### 1. Shared Output Audit Report

Status: complete. Report: `docs/recovery/output-audit-report.md`. Machine report:
`exports/output-audit/_output-audit-report.json`.

Build a small cross-output audit command that reads existing export reports and
emits one comparison report. It should not change generated outputs.

Value:

- Gives a single release-readiness view across as-is static, raw article static,
  and EPUB.
- Separates true internal gaps from intentionally preserved external links.
- Creates a stable basis for deciding which output to improve next.

Acceptance:

- Report lists output paths, counts, validation status, missing-resource notes,
  fallback/additional article counts, and EPUB unresolved internal links.
- Report explicitly classifies each finding as `blocking`, `candidate`, or
  `deferred`.

### 2. Canonical Navigation Refinement

Status: evidence report complete. Report:
`docs/recovery/canonical-navigation-refinement.md`.

Improve raw-article enhanced browsing without changing canonical article content.
Candidate sources include additional original index pages and proven
parent/child links already present in canonical records.

Value:

- Reduces the `87`-article fallback section.
- Makes series such as rulebook chapters, AMU profiles, Wong vision topics,
  Zen chapters, Perry pages, and Illinois/Missouri League pages easier to
  browse.

Constraints:

- Must not violate the current homepage-exact navigation decision silently.
- Any inferred placement must be provenance-backed and reported.
- The existing exact-homepage navigation should remain available or be clearly
  distinguished from enhanced navigation.

### 3. EPUB Internal Resource Handling

Improve the EPUB handling of internal non-article links.

Value:

- Many of the `33` unresolved internal links point to recovered PDFs, MP3s,
  ZIPs, or non-canonical HTML resources already included in the canonical
  static site resources.
- A supplemental resource manifest or package would make those links more
  useful without forcing unsupported media into the EPUB first pass.

Constraints:

- The EPUB contract currently excludes embedding ZIP, EXE, MP3, PDF, and
  arbitrary HTML resources in the first EPUB pass.
- Any enhancement should either revise the contract explicitly or produce a
  separate supplemental package/report.

### 4. Raw As-Is Missing-Resource Review

Review the `24` local missing-resource notes in the raw as-is site.

Value:

- Separates truly unrecovered historical files from generated noise, external
  provider artifacts, and possible owner-provided-file candidates.
- Reduces ambiguity before any public release.

Constraints:

- Missing files must not be silently replaced.
- Owner-provided files require explicit user input.

## Recommended Next Slice

Start with additive enhanced canonical browse implementation.

Reason:

- The shared output audit is complete and found `0` blocking findings.
- The canonical navigation refinement report accounts for all `87` canonical
  fallback articles.
- The selected implementation path preserves exact recovered homepage
  navigation and adds enhanced groups as a separate browse surface.
