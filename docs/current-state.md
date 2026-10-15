# Current State

Date: 2026-10-15

## Current Slice

PDF release QA passed on 2026-10-15: structural checks cover all `574` pages and `150` article destinations; sampled visual review found no export defect. The PDF already follows the missing-resource policy, so its bytes are unchanged. Evidence and review limits are recorded in `docs/recovery/pdf-export-report.md`. External EPUB validation also remains complete: EPUBCheck 5.4.0 passed with zero errors and warnings.

## Status

- Workspace was empty when planning began.
- The highest priority remains local preservation of all recoverable Wayback content.
- User clarified that the site is primarily a collection of articles with minimal active content, and articles should be stored without unnecessary site chrome.
- Wayback inventory run `20260522T135739Z` found `15,809` deduped captures from `96,074` CDX records.
- September 2010 is the best article-plus-asset completeness baseline found so far; February 2015, March 2023, January 2025, and August 2025 are candidate overlays.
- Selected baseline/overlay raw backup is complete: `884` selected captures, `884` successful, `0` failed.
- Article image recovery is complete for the selected backup: `809` unique recovered article-image records, `0` failed downloads, `7` unresolved external counter references.
- Deduplicated storage is active: `1,693` successful file references share `536` unique SHA-256 blobs, with `0` missing blob references.
- Site-engine detection now identifies the site as static HTML authored with Microsoft FrontPage/WordPad after scanning `493` recovered HTML files.
- Canonical normalization has produced `150` article records, `27` page shell records, and `165` article asset records.
- Current as-is output is `exports/static-site/as-is`.
- Final single-file release artifacts are collected under `exports/final`.
- As-is static site reproduction has produced `524` selected files under the release path after pruning provider-template placeholder pages from the release-facing export.
- The `as-is` static site uses a canonical-grouped deployable layout: article pages under `articles/<canonical-section>/<article-or-subgroup>/index.html`, subarticles under `articles/<canonical-section>/<parent-article>/<sub-article>/index.html`, article-specific recovered images in `images/` beside the grouped article page, and site-wide images under `shared/images/`.
- Current `as-is` grouping includes `10` top-level canonical sections and `2` detected sub-article groups: `technical-information/vision-topics` and `biography-and-history/army-marksmanship-unit-champion-profiles`.
- `As-is` structured image convenience copies are hardlinked where possible; current check shows `161` of `161` same-name article/shared image pairs share the same inode.
- `As-is` static validation now passes with `0` broken local references across `1,102` local references; `295` page-local scripts pass `node --check`.
- A checksum repair pass restored accidentally modified hardlinked JavaScript blobs; current combined raw and image manifests audit with `0` mismatched blob references.
- Current raw article site output is `exports/static-site/raw`.
- Obsolete pre-rename export directories `exports/static-site/canonical` and `exports/static-site/raw-as-is` have been removed.
- Raw article site export has produced `150` article pages under the release path.
- Fresh validation on 2026-05-29 passed with `0` broken local references across `1,530` local references (`168` HTML files).
- Current raw article site uses exact recovered homepage navigation plus enhanced browse groups with `0` unplaced articles; profile1–7 appear as sub-items under `amuprfil` in "Biography and History", and wong1–7+wongbio appear as sub-items under `wong` in "Technical Information", matching raw-site subdirectory structure.
- Current raw article site includes `165` recovered article assets, `21` additional recovered linked resources, and `7` entries in `missing-artifacts.html` for unrecovered owner-file links.
- Each raw-site missing-artifact entry now includes a concise description reconstructed from the referring article block plus a backlink to that article.
- Ebook export contract is documented at `docs/recovery/ebook-export-contract.md`; it now requires only EPUB-reader-safe packaged resources.
- Current EPUB has `150` included article chapters in `15` groups (`9` raw-index groups plus `6` generated groups for additional recovered articles), `160` embedded recovered image assets, `0` non-reader-safe packaged resources, `0` broken local EPUB package references, `59` suppressed internal non-article resource links, and `0` unresolved internal links.
- Current final artifact bundle contains `bullseye-pistol.epub`, `bullseye-pistol.pdf`, `bullseye-pistol-raw-site.zip`, and `bullseye-pistol-as-is-site.zip`.
- EPUB article formatting uses canonical HTML-derived paragraphs and inline recovered figures; export report verifies `0` legacy pre-wrapped chapters, `0` hard-wrap candidates, and `0` visible asset-ID image captions.
- Shared output audit report exists at `docs/recovery/output-audit-report.md` with machine output at `exports/output-audit/_output-audit-report.json`.
- As-is missing-resource classification exists at `docs/recovery/as-is-missing-resource-classification.md` with machine output at `exports/output-audit/as-is-missing-resource-classification.json`.
- The release-facing `as-is` build now prunes `12` provider-template placeholder captures that rendered as MyDomain pages rather than Bullseye content.
- Enhanced browse layer is complete in `exports/static-site/raw/articles.html`; it shows evidence-backed groups plus a `Recovered Homepage Articles` section with profile and Wong sub-articles indented under their parents; `0` broken local references.
- Canonical article titles for `amuprfil` and `profile1`–`profile7` corrected from all-caps article-body text to proper-case names with roles sourced from parent article link text (e.g., "Frederick J. Kiefer, International Coordinator USAMU").
- User preference: completeness is preferred to speed; downloads should be staggered and retried instead of treated as one fast scrape.
- User preference: asset storage must avoid duplicate bytes across dumps; use content-addressed blobs with per-capture references or hardlinks.
- User preference: article images must be found, saved locally, and recoverable, with unresolved image references explicitly reported.
- User preference: detect and record the prior site engine/platform from recovered evidence.
- User preference: because the original appears to be a manual/static HTML site, one produced artifact must be a good navigable static website that can be deployed as-is anywhere.
- User preference: `as-is` static output should not be flat; group articles in folders, place article images in each article folder, and place site-wide images in a shared images folder.
- User preference: `as-is` article grouping should follow logical top-page groups and sub-article groups, similar to canonical groups such as `Technical Information / Vision Topics`.
- User preference: release-facing names should be `raw` for the normalized article site and `as-is` for the historical full-page reproduction.
- User preference: missing artifacts should be visible in a dedicated `Missing Artifacts` section of the `raw` site for possible future recovery; other reader outputs should avoid mentioning missing artifacts where practical.
- User preference: EPUB must package only resources that common e-readers can open.
- User preference: DB import/export work is postponed until explicitly requested.

## Open Questions

Release-facing artifact alignment is implemented for `raw`, `as-is`, and EPUB. External EPUB validation has passed; DB work and public URL policy remain deferred.

Deferred or routed questions:

- Historical baseline authority: deferred until conflicting snapshots affect generated output; current selected baseline/overlay set remains the working source.
- Alternate hostnames: `www.bullseyepistol.com` is already included; any additional old subdomains, CDN hosts, or provider preview domains require owner input or a new inventory slice.
- Non-public assets outside Wayback: route to the new `raw` site's `Missing Artifacts` section. Recovery is currently unavailable; only later out-of-band supplied files would change that.
- Public URL policy: deferred until a public rebuild or redirect-map slice; current static outputs remain self-contained generated artifacts.
- Article-body/chrome patterns: first pass uses recovered `ARTICLE BEGINS/ENDS` markers and page-shell evidence; broaden only if a later normalization pass finds articles without reliable markers.
- Ebook cover: deferred; a later pass may add a designed cover image.
- Raw article site missing-artifact section: implemented with article backlinks and source-backed descriptions.
- As-is output missing-resource presentation: implemented as silent suppression in reader-facing pages, with `17` internal missing URLs retained only in the report. Classification now breaks them down into `8` non-Wayback owner-file gaps, `5` unrecovered article URLs, `2` provider artifacts, `1` hosting-template artifact, and `1` decorative image.
- As-is unresolved rewrite inventory: classified. It contains `44` pages, `692` external refs, and `33` unique internal URLs; `11` hosting-template artifact URLs dominate the internal side.
- EPUB internal non-article resource handling: implemented as reader-safe suppression; `59` such links are omitted from active EPUB navigation and retained only in the export report.
- DB import/export contract: postponed until the user explicitly requests DB work.

- PDF export has produced `exports/pdf/bullseye-pistol.pdf` — `574` pages, `150` articles, `162` resolved image references, and `15` topic groups; built with WeasyPrint 68.1 using `tools/build_pdf.py`. The identical final edition passed structural and sampled visual QA, with `838` working local link annotations and no generated missing-resource notices. See `docs/recovery/pdf-export-report.md`.

## Next Step

EPUBCheck and PDF QA are complete for the current editions. Select any further release or presentation work explicitly; DB import/export remains deferred. See `docs/recovery/ebook-export-report.md` and `docs/recovery/pdf-export-report.md` for evidence and review limits.

## Continuation / Handoff

Use `docs/recovery/handoff.md` as the session-independent recovery handoff. It records the inventory manifest, selected periods, completed backup manifests, deduplicated storage contract, and pending work.

## Recent Decisions

- Use a three-layer repository structure: immutable archive, normalized canonical content, generated exports.
- Treat raw Wayback retrieval as preservation work, not as the final publishing format.
- Keep ebook, static site, and DB engine outputs downstream of the same canonical content layer.
- Canonical records are article-first; raw captures preserve complete pages, but normalized article bodies should omit recurring site chrome.
- Raw backup storage is content-addressed by SHA-256 to avoid duplicate asset bytes across period dumps and retry runs.
- Backup speed is secondary to completeness and recoverability.
- Static HTML output is a first-class restoration artifact, not just a demo export.
- Static HTML output has two required release-facing tracks: `as-is` recovered site reproduction and `raw` normalized article site.
- The raw article site should preserve recovered original homepage sections where possible, keep enhanced provenance-backed browsing, and centralize unavailable internal resources in `Missing Artifacts`.
- Ebook export contract targets EPUB 3 and must include only e-reader-openable package resources; non-reader-safe supplemental resources are report/static-site concerns, not EPUB package content.
- Ebook ordering should use the raw recovered index page's generic topic order and chapter grouping, not the canonical static fallback section as the ordering authority.
- Open questions must be classified as blocking, deferred, or routed before implementation starts.
- DB import/export contract is deferred until the user explicitly requests DB work.
