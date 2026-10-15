# Recovery Handoff

Last updated: 2026-10-15

## Objective

Recover `bullseyepistol.com` articles and assets from Wayback with completeness prioritized over speed. Preserve raw evidence, deduplicate bytes, recover article images, detect the prior site engine, and keep the content model suitable for ebook, static HTML, and DB-backed outputs.

The static HTML output is a first-class restoration artifact with two release-facing tracks: an `as-is` copy of recovered pages/chrome that can be deployed anywhere, and a `raw` normalized article site generated from canonical article records.

## Source Of Truth

- Inventory manifest: `archive/raw/wayback/manifests/20260522T135739Z-inventory.json`
- Baseline analysis: `docs/recovery/wayback-baseline-analysis.md`
- Current state: `docs/current-state.md`
- Requirements: `docs/requirements.md`
- Roadmap: `docs/roadmap.md`

## Session Boundary Envelope

- Git state: the project is tracked on `main`, with `origin` at `git@github.com:UncleGene/bullseye_encyclopedia.git`. Initial import: `133323e`. Use `git status` and the latest commit alongside manifests for continuity.
- Active docs: `docs/current-state.md`, `docs/requirements.md`, `docs/roadmap.md`, `docs/recovery/canonical-navigation-refinement.md`, `docs/recovery/output-audit-report.md`, `docs/recovery/output-improvement-audit.md`, `docs/recovery/ebook-export-contract.md`, `docs/recovery/ebook-export-report.md`, `docs/recovery/canonical-static-site-report.md`, `docs/recovery/raw-static-site-report.md`, `docs/recovery/normalization-report.md`, `docs/recovery/site-engine-analysis.md`.
- Active scripts: `tools/audit_outputs.py`, `tools/build_ebook.py`, `tools/build_canonical_static_site.py`, `tools/validate_static_site.py`, `tools/normalize_articles.py`, `tools/wayback_backup.py`, `tools/wayback_recover_images.py`, `tools/recover_static_dependencies.py`.
- Last completed planning step: release-facing artifact policy updated in goals, requirements, roadmap, ebook contract, validation plan, recovery spec, and current state.
- Final artifact bundle directory: `exports/final`
- Last completed release gates: EPUBCheck 5.4.0 passed with zero errors and warnings; PDF structural and sampled visual QA passed without export changes. See `docs/recovery/ebook-export-report.md` and `docs/recovery/pdf-export-report.md`.
- Latest publication evidence: workflow run `38814095608` succeeded for `0b22bcd`; historical root and `/raw/` returned HTTP 200 with expected relative version links. See `docs/recovery/github-pages.md`.
- Next intended step: select further work explicitly; DB import/export remains deferred.
- Suggested next skill: `minime-implementation-step-selector`.
- Open-question status: release-facing missing-artifact UX, `as-is` output missing-resource suppression, and EPUB resource eligibility are implemented. The latest GitHub Pages layout is historical `as-is` at root and article `raw` at `/raw/`, with cross-links and a recovered banner on the article site; see `docs/recovery/github-pages.md`. Deferred questions remain for owner-provided files, custom domains and original-domain redirects, DB import/export, and historical-version authority if later snapshot conflicts affect output.

## Selected Periods

Download and preserve these baseline/overlay months:

- `201009`: primary completeness baseline.
- `201502`: article overlay.
- `202303`: recent article overlay.
- `202501`: recent mixed overlay.
- `202508`: recent mixed overlay and asset overlay.

## Current Download State

Initial full selected-period raw backup:

- Manifest: `archive/raw/wayback/manifests/20260522T141108Z-backup.json`
- Selected captures: `884`
- Successful: `280`
- Failed: `604`
- Failure mode was mostly Wayback connection refusal after a burst of requests, not confirmed missing content.

First slower retry, interrupted after checkpointing:

- Manifest: `archive/raw/wayback/manifests/20260522T142631Z-backup.json`
- Selected from prior failures: `604`
- Checkpointed records: `70`
- Successful: `57`
- Failed: `13`

Final combined selected-period raw backup:

- Manifest: `archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json`
- Selected captures: `884`
- Successful: `884`
- Failed: `0`
- Article candidates: `473`
- Assets: `387`
- Active/dynamic evidence: `20`
- Non-content evidence: `4`

Final combined article-image recovery:

- Manifest: `archive/raw/wayback/manifests/20260522T-combined-image-recovery.json`
- Unique recovered article-image records: `809`
- Failed image downloads: `0`
- Unresolved references: `7`
- Unresolved references are external counter URLs: `http://counter.digits.com/wc/-d/4/bullseyepistol`

Raw styling/fidelity repair:

- Broad asset repair manifest: `archive/raw/wayback/manifests/20260523T071345Z-backup.json`
- Targeted `imheader1.js` repair manifest: `archive/raw/wayback/manifests/20260523T073107Z-backup.json`
- The repair restored hardlinked JavaScript blobs that were accidentally modified by an earlier generated-output rewrite.
- Current checksum audit result: `0` mismatched blob references across the combined raw backup and image recovery manifests.

## Resume Procedure

The selected-period raw backup is complete. To inspect or verify manifests:

```sh
find archive/raw/wayback/manifests -maxdepth 1 -name '*-backup.json' -type f | sort
```

Inspect backup progress:

```sh
python3 -c "import json,glob,os; \
for p in sorted(glob.glob('archive/raw/wayback/manifests/*-backup.json'))[-10:]: \
 d=json.load(open(p)); print(os.path.basename(p), d.get('selected_count'), d.get('status_counts'), len(d.get('records', [])))"
```

The old retry commands remain useful if new periods are added. If Wayback refuses connections, increase `--sleep` to `3` or `5` and continue. Do not mark refused connections as missing content until slower retries have also failed.

## Deduplicated Storage Contract

- Downloaded bytes are stored under `archive/raw/wayback/blobs/sha256/<prefix>/<sha256>`.
- Per-capture files under `archive/raw/wayback/files/<run>/<period>/...` are hardlinks to blobs when possible.
- Manifest fields `sha256`, `blob_path`, `local_path`, and `storage_mode` prove deduplication and recoverability.
- Do not replace this with period-only asset copies.

## Permanent Historical Gaps

These URLs were referenced on the site but are absent from all selected baseline/overlay captures.
No additional Wayback downloads are expected to resolve them. Treat as permanent gaps.

- `http://bullseyepistol.com/chaptr10.htm` — variant URL for a chapter article; chapter10 was recovered via a different URL.
- `http://bullseyepistol.com/gilhebar.htm` — content page not captured in selected baseline/overlay; identity unclear.
- `http://bullseyepistol.com/help.htm` — site help page; not present in selected Wayback captures.
- `http://bullseyepistol.com/perchamp.htm` — likely a Camp Perry championship results page; not captured.
- `http://bullseyepistol.com/statoffice.htm` — state office page; not present in selected Wayback captures.

Under the release-facing policy, these should be centralized in the `raw`
site's `Missing Artifacts` section and avoided in the `as-is`, EPUB, and PDF
reader surfaces where practical. These are classified as `unrecovered-article`
in `docs/recovery/as-is-missing-resource-classification.md`.

## Owner-File Candidates

These URLs were linked from article content but have no Wayback capture. They are likely
owner-supplied files (PDFs, executables, archives) that were served from the host but never
crawled.

- `http://bullseyepistol.com/Handicap.exe` — Windows executable; league handicap scoring software linked from Il-Mo pages.
- `http://bullseyepistol.com/ILMOScorecard.pdf` — Il-Mo league scorecard PDF.
- `http://bullseyepistol.com/MidSeasonScorecard.pdf` — Il-Mo mid-season scorecard PDF.
- `http://bullseyepistol.com/NewShooter.pdf` — New shooter orientation PDF.
- `http://bullseyepistol.com/POM2004.zip` — 2004 league data archive.
- `http://bullseyepistol.com/SignupForm.pdf` — League signup form PDF.
- `http://bullseyepistol.com/TeamAdmin2004.zip` — 2004 team administration archive.
- `http://bullseyepistol.com/piasaapp.pdf` — PIASA application PDF.

Under the release-facing policy, these belong in the `raw` site's `Missing
Artifacts` section as permanent non-Wayback gaps unless files are later supplied out-of-band.
Classification: `owner-file-candidate` in `docs/recovery/as-is-missing-resource-classification.md`.
Recovery is currently unavailable. If any of these files are later supplied out-of-band, place them in `archive/owner-files/` and re-run the raw article and as-is build scripts to replace the missing-artifact entries or omitted links with local links where appropriate.

## Pending Work

1. External EPUB validation is complete for the current edition. Re-run `epubcheck exports/final/bullseye-pistol.epub` after future EPUB changes.
2. Define the DB import/export contract only after explicit user request.

## Completed Normalization / Raw Site Work

- Normalization report: `docs/recovery/normalization-report.md`
- Raw static site report: `docs/recovery/raw-static-site-report.md`
- Canonical static site report: `docs/recovery/canonical-static-site-report.md`
- Ebook export contract: `docs/recovery/ebook-export-contract.md`
- Ebook export report: `docs/recovery/ebook-export-report.md`
- Canonical navigation refinement report: `docs/recovery/canonical-navigation-refinement.md`
- Shared output audit report: `docs/recovery/output-audit-report.md`
- Shared output audit machine report: `exports/output-audit/_output-audit-report.json`
- As-is missing-resource classification report: `docs/recovery/as-is-missing-resource-classification.md`
- As-is missing-resource classification machine report: `exports/output-audit/as-is-missing-resource-classification.json`
- Canonical article records: `150`
- Page shell records: `27`
- Article asset records: `165`
- Current as-is static files written: `524`
- Current as-is output directory: `exports/static-site/as-is`
- Obsolete pre-rename export directories `exports/static-site/canonical` and `exports/static-site/raw-as-is` have been removed.
- Raw as-is structure: articles under `articles/<canonical-section>/<article-or-subgroup>/index.html`, subarticles under `articles/<canonical-section>/<parent-article>/<sub-article>/index.html`, article images in `images/` beside the grouped article page, site-wide images under `shared/images/`, and page-local script copies under `_scripts/` beside each page.
- Raw as-is grouping source: canonical homepage sections plus parent/child article links from canonical article records.
- Raw as-is detected subgroups: `technical-information/vision-topics` and `biography-and-history/army-marksmanship-unit-champion-profiles`.
- Raw as-is image counts: `161` article-specific image files and `295` shared image files.
- Raw as-is duplicate-byte check: `161` of `161` same-name article/shared image pairs are hardlinks to the same inode.
- As-is static validation: `0` broken local references across `1,102` local references
- Raw as-is JavaScript syntax validation: `0` bad page-local scripts across `295` checked files.
- As-is styling/fidelity correction rewrites JavaScript/CSS-generated references, preserves query strings/fragments, cleans stale output before rebuild, uses page-local `_scripts/` copies for historical script-generated chrome, skips HTML captures masquerading as JavaScript, prunes MyDomain-style provider placeholder captures from the release-facing output, and uses silent local `_missing` image placeholders plus report-only URL tracking for unrecovered internal references.
- As-is classification after pruning: `17` suppressed internal URLs, `44` pages with unresolved rewrites, `692` external unresolved refs, and `33` unique internal unresolved URLs (`11` hosting-template artifacts, `8` owner-file candidates, `6` decorative assets, `5` unrecovered articles, `2` provider artifacts, `1` unrecovered media file).
- Current raw article site pages written: `150`
- Current raw article site validation: `0` broken local references across `1,530` local references from a fresh 2026-05-29 validation run
- Current raw article site output directory: `exports/static-site/raw`
- Raw-site `missing-artifacts.html` now includes concise descriptions reconstructed from the referring article content plus backlinks to the source article page.
- Ebook output: `exports/ebook/bullseye-pistol.epub`
- Ebook export report: `exports/ebook/_ebook-export-report.json`
- Current ebook output contains `150` article chapters, `160` embedded recovered image assets, `0` broken local EPUB package references, `0` legacy pre-wrapped chapters, `0` hard-wrap candidates, `0` visible asset-ID image captions, `59` suppressed internal non-article resource links, `0` unresolved internal links, and `0` non-reader-safe packaged resources.
- Final artifact bundle files: `exports/final/bullseye-pistol.epub`, `exports/final/bullseye-pistol.pdf`, `exports/final/bullseye-pistol-raw-site.zip`, `exports/final/bullseye-pistol-as-is-site.zip`
- Shared output audit artifacts were regenerated on 2026-05-29 for the `raw` / `as-is` naming and EPUB reader-safety policy.
- Canonical navigation refinement has already been applied as enhanced browsing in the current raw article site candidate; it is no longer the next slice.

## Preliminary Site Engine Finding

Preliminary report: `docs/recovery/site-engine-analysis.md`

Current conclusion: the site appears to be a static hand-maintained `.htm` site, originally or historically authored with Microsoft FrontPage Express and later edited by hand/WordPad.
