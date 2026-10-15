# Canonical Navigation Refinement

Date: 2026-05-23

## Scope

Analyze the `87` canonical articles currently placed in `Other Recovered
Articles` and identify which can be grouped with provenance-backed evidence.

This report does not change generated static output, canonical article bodies,
raw archive data, EPUB output, or DB plans.

## Recommendation

Implement enhanced raw-article browsing as an additive layer.

Keep the current exact recovered homepage navigation as the primary authority.
Add a separate enhanced browse surface for recovered series and topic groups
that are backed by article IDs, article titles, internal links, or recovered
index evidence.

Reason:

- The current homepage-exact model is an explicit decision and should not be
  silently replaced.
- All `87` fallback articles can be assigned to evidence-backed candidate
  groups.
- Several groups are clearly subordinate to homepage-listed parent articles,
  especially `amuprfil` and `wong`.
- The enhanced layer can improve browsing without changing article content or
  removing the existing fallback trace.

## Evidence Sources

- Raw article export report:
  `exports/static-site/raw/_raw-export-report.json`
- Canonical article records:
  `content/canonical/articles/*.json`
- Canonical article index:
  `content/canonical/articles.index.json`
- Current output audit:
  `docs/recovery/output-audit-report.md`

Evidence types used:

- Direct internal links from canonical records.
- Stable article ID prefixes and numeric sequence.
- Article titles that identify a series.
- Recovered topic-index links from `alphadex`.
- Existing homepage-listed parent articles.

## Placement Summary

| Candidate group | Count | Confidence | Evidence |
| --- | ---: | --- | --- |
| AMU Marksmanship Training Guide | 14 | High | `chapter*` IDs, ordered chapter titles, `alphadex` USAMU links, `chapter2` links to `annex2` |
| NRA Conventional Pistol Rules | 17 | High | `rulebook*` IDs and ordered section titles |
| AMU Champion Profiles | 7 | High | Direct links from homepage-listed `amuprfil` |
| Wong Vision Topics | 8 | High | Direct links from homepage-listed `wong` |
| Il-Mo League | 10 | High | `im*`/`ilmo` IDs and shared Il-Mo titles |
| Camp Perry / National Matches | 7 | High | `per*` IDs, Camp Perry/National Matches titles, cross-links from `perryfaq` to `perinfo` |
| Ron Porter Fundamentals | 8 | High | `ron*` IDs and repeated `Fundamentals Series` titles |
| Dave Salyer Articles | 4 | Medium | `salyer*` IDs and relation to existing `salyer1`/`salyer5` homepage placements |
| Companion Articles | 2 | Medium | About-author or alternate-version relationship to homepage-listed articles |
| Site / Reference / General Index | 10 | Medium | Site utility/reference titles and `alphadex` links |

All `87` fallback articles are accounted for by these groups.

## Candidate Groups

### AMU Marksmanship Training Guide

Candidate parent surface: `amucover` under `Perfecting Technique`.

Articles:

- `chapterf`: FOREWORD
- `chapter0`: ELEMENTS OF PISTOL SHOOTING
- `chapter1`: ATTAINING A MINIMUM ARC OF MOVEMENT
- `chapter2`: SIGHT ALIGNMENT
- `chapter3`: TRIGGER CONTROL
- `chapter4`: ESTABLISHING A SYSTEM
- `chapter5`: TECHNIQUE OF SLOW FIRE
- `chapter6`: TECHNIQUE OF SUSTAINED FIRE
- `chapter7`: MENTAL DISCIPLINE
- `chapter8`: PHYSICAL CONDITIONING
- `chapter9`: DIET AND HEALTH OF THE PISTOL SHOOTER
- `chapter10`: ALCOHOL, COFFEE, TOBACCO AND DRUGS
- `annex2`: OPTICAL PROPERTIES OF THE EYE
- `glossary`: GLOSSARY OF TERMS

Evidence:

- The IDs and titles form a stable chapter sequence.
- `alphadex` links repeatedly label these pages as USAMU material.
- `chapter2` links to `annex2` as an annex.

### NRA Conventional Pistol Rules

Articles:

- `rulebook`: CONVENTIONAL PISTOL RULES
- `rulebook1`: 1. NRA COMPETITION
- `rulebook2`: 2. ELIGIBILITY OF COMPETITORS
- `rulebook3`: 3. EQUIPMENT AND AMMUNITION
- `rulebook4`: 4. TARGETS
- `rulebook5`: 5. POSITIONS
- `rulebook6`: 6. RANGE STANDARDS
- `rulebook7`: 7. COURSES OF FIRE
- `rulebook8`: 8. TIME LIMITS
- `rulebook9`: 9. TOURNAMENT CONDITIONS
- `rulebook10`: 10. RANGE COMMANDS AND OPERATIONS
- `rulebook14`: 14. SCORING AND MARKING
- `rulebook15`: 15. DECISION OF TIES
- `rulebook16`: 16. CHALLENGES AND PROTESTS
- `rulebook17`: 17. NATIONAL RECORDS
- `rulebook18`: 18. COMPETITOR'S RESPONSIBILITIES
- `rulebook19`: 19. NATIONAL PISTOL CLASSIFICATION

Evidence:

- The IDs and titles form an ordered recovered rulebook sequence.
- Missing sections between `10` and `14` should remain absent, not invented.

### AMU Champion Profiles

Candidate parent surface: `amuprfil` under `Biography and History`.

Articles:

- `profile1`: FOREWORD
- `profile2`: FREDERICK J. KEIFER
- `profile3`: OSCAR K. WEINMEISTER, SR.
- `profile4`: SFC. BONNIE D. HARMON
- `profile5`: SFC. HARLAND V. RENNOLDS
- `profile6`: CPT ROBERT L. MERRITT
- `profile7`: MSG. AUBREY E. SMITH

Evidence:

- `amuprfil` directly links all seven profile articles.
- The raw as-is static report already detects this as a sub-article group.

### Wong Vision Topics

Candidate parent surface: `wong` under `Technical Information`.

Articles:

- `wong1`: Bullseye Shooting for the Eyecare Professional
- `wong2`: ABBE Values of Shooting Glasses
- `wong3`: Eyeglass Prescription Innaccuracies
- `wong4`: The Eye Exam at 20 Feet
- `wong5`: Red Dot Focusing Position
- `wong6`: Using Obsolete RX Glasses for Shooting
- `wong7`: Keeping Focused
- `wongbio`: About the Author

Evidence:

- `wong` directly links all eight articles.
- The raw as-is static report already detects this as a sub-article group.

### Il-Mo League

Articles:

- `ilmo`: Il-Mo Indoor Pistol League
- `imadmin`: Il-Mo Executive Officers
- `imforms`: League Forms
- `imhist`: Il-Mo History
- `imnews`: Il-Mo News
- `imprev`: Il-Mo Previous Season Standings
- `imrecord`: Il-Mo Records
- `imsoft`: Scorekeeping Software
- `imstand`: Il-Mo Current Season Standings
- `imteams`: Il-Mo Current Teams

Evidence:

- Shared `im*` IDs and Il-Mo titles identify a coherent league section.
- `imforms`, `imprev`, and `imsoft` contain recovered internal resource links
  already represented in the raw article static report.

### Camp Perry / National Matches

Articles:

- `perenter`: How to Enter the National Matches
- `perhist`: A History of the National Matches
- `perinfo`: Lodging, Dining and Entertainment
- `permem`: Memories of Camp Perry
- `perryfaq`: Camp Perry Frequently Asked Questions
- `perrysrv`: Camp Perry Survival Guide
- `pertriv`: Camp Perry Trivia

Evidence:

- Shared `per*` IDs and titles identify a Camp Perry / National Matches group.
- `perryfaq` links to `perinfo`.
- `alphadex` links to `perinfo` and `perryfaq`.

### Ron Porter Fundamentals

Articles:

- `ron1`: Fundamentals Series: Stance
- `ron2`: Fundamentals Series: Grip
- `ron3`: Fundamentals Series: Breath Control
- `ron4`: Fundamentals Series: Aiming & Sight Alignment
- `ron5`: Fundamentals Series: Trigger Control
- `ron6`: Fundamentals Series: Follow-Through
- `ron7`: Fundamentals Series: Red Dot Scopes
- `ronbio`: About the Author

Evidence:

- Shared `ron*` IDs.
- Seven titles use `Fundamentals Series`; `ronbio` is the companion author page.

### Dave Salyer Articles

Articles:

- `salyer2`: An Explanation of Area Aiming
- `salyer3`: Trigger Control and Aiming Area
- `salyer4`: Master Sustained Fire with Effective Practice
- `salyer6`: About the Author

Evidence:

- Shared `salyer*` IDs.
- Existing homepage sections already place `salyer1` and `salyer5`.

Open point:

- These should likely appear as a Dave Salyer related-articles group rather than
  being forced into one existing homepage section, because existing Salyer pages
  span `Shooting Psychology` and `Technical Information`.

### Companion Articles

Articles:

- `mikelav2`: About the Author
- `savino`: Outdoor Bullseye Pistol Shooting

Evidence:

- `mikelav2` is an author companion to homepage-listed `mikelav1`.
- `savino` appears related to homepage-listed `savino2`, but the relation needs
  implementation-time care because both are article pages rather than a clear
  parent/subarticle pair.

### Site / Reference / General Index

Articles:

- `advertise`: Advertise and Support this Tremendous Resource
- `alphadex`: Website Topic Index
- `legal`: Terms and Conditions
- `links`: Links to Other Sites
- `records`: The NRA's National Records
- `other`: Other Popular Disciplines
- `techo`: Technical Data for Pistol Shooters
- `why`: About this Website...
- `visualize`: Zen in Visualization of Fundamentals
- `zins1`: Fundamentals Series: Trigger Control

Evidence:

- `alphadex` is a recovered topic index and links to many canonical articles.
- `links`, `records`, `other`, and `techo` are reference/index-style resources.
- `why`, `advertise`, and `legal` are site-support pages.
- `visualize` is likely related to Zen content, and `zins1` is likely related to
  Brian Zins fundamentals content, but neither has enough direct parent evidence
  to force into an existing homepage section without marking the placement as
  inferred.

## Implementation Path

Recommended next implementation slice:

Add an enhanced browse layer to the raw article static site.

Constraints:

- Preserve the exact recovered homepage sections.
- Do not remove the existing `Other Recovered Articles` provenance concept
  without recording how every former fallback article is now placed.
- Mark enhanced groups as recovered/inferred browsing aids, not original
  homepage navigation.
- Keep canonical article body content unchanged.
- Keep generated output reproducible from `content/canonical` and
  `content/assets`.

Suggested output behavior:

- Keep `index.html` homepage-exact.
- Add or update a browse page, such as `articles.html`, with enhanced groups.
- For direct parent groups, show child links under the parent article:
  `amuprfil`, `wong`, and possibly `amucover`.
- For sequence groups, preserve numeric/order semantics.
- For medium-confidence groups, either label as `Related recovered articles` or
  keep them in a clearly separated enhanced section.

## Acceptance For The Next Slice

- Canonical static output still validates with `0` broken local references.
- Exact recovered homepage navigation remains available.
- `87` fallback articles are either placed in enhanced groups or explicitly
  retained in a residual fallback with reason.
- Export report records the enhanced navigation model and group counts.
- No raw as-is static, EPUB, or DB output behavior changes unless separately
  requested.
