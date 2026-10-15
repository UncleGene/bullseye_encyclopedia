# Ebook Export Contract

Date: 2026-05-23

## Summary

The ebook export produces one reader-facing ebook from the normalized
canonical article layer. The first contract targets an EPUB 3 artifact
because it can carry structured chapters, local images, internal links, and
metadata while remaining independent of a specific reading device.

The ebook is downstream of `content/canonical` and `content/assets`. It is
not an editing surface: generated files under `exports/ebook` must be
reproducible from canonical records, recovered assets, and this contract.

## Inputs

- Canonical article index: `content/canonical/articles.index.json`.
  Authority: defines the complete set of article records eligible for ebook
  inclusion.
- Canonical article records: `content/canonical/articles/*.json`.
  Required fields for inclusion are `id`, `title`, `body`, `status`,
  `original_urls`, and `provenance`. Optional fields such as `byline`,
  `published_at`, `updated_at`, `context`, `assets`, `images`, and `links`
  must be preserved when present.
- Asset index: `content/assets/assets.index.json`.
  Authority: maps article asset IDs to local recovered files, media type,
  checksum, status, and provenance.
- Raw recovered index page:
  `archive/raw/wayback/files/20260522T143136Z/202508/article_candidate/www.bullseyepistol.com/20250818003737-index-5fffb450c2814c7e.html`.
  Authority for first-pass ebook ordering and chapter grouping. The ebook
  must preserve the generic topic order and chapter labels from this raw
  index page.
- Raw article static export report:
  `exports/static-site/raw/_raw-export-report.json`.
  Supporting reference only. It may be used as a parsed cache of raw-index
  links when its `homepage_source` matches the raw index page, but it is not
  the ordering authority.

Input constraints:

- Include canonical records with `status` of `recovered` or `partial`.
  Partial records must be visibly marked in generated metadata and in the
  provenance appendix.
- Exclude page shells unless a later requirement promotes a shell to a
  canonical article.
- Use local recovered assets only. Do not link to Wayback-hosted images or
  scripts for normal ebook reading.
- Preserve original URLs and capture provenance in metadata or appendix
  form; do not discard it during export.
- Treat missing, substituted, or excluded assets as report-level recovery
  evidence. The reader-facing EPUB should avoid missing-resource prose unless
  the omission affects comprehension of the article text.

## Outputs

Primary output:

- `exports/ebook/bullseye-pistol.epub`: one EPUB 3 file containing the
  article collection.

Supporting generated output:

- `exports/ebook/_ebook-export-report.json`: machine-readable report with
  input manifest paths, included article count, skipped records, embedded
  asset count, missing asset notes, generated chapter order, and validation
  results.
- `exports/ebook/provenance.html`: human-readable provenance appendix also
  embedded in the EPUB.

Completeness guarantee:

- The ebook includes every eligible canonical article from
  `content/canonical/articles.index.json` unless the export report records a
  specific skip reason.
- The ebook embeds every article image asset whose canonical asset record has
  a recovered local file and an EPUB-reader-safe media type.
- The ebook reports every missing, unsupported, or intentionally excluded
  asset/resource with the article ID, original URL when available, and reason.

## Ordering And Structure

- Use the raw recovered index page for first-pass ebook ordering.
- Preserve the generic topic order from the raw index page, currently:
  `Introductory Information`, `Tools of the Trade`, `Perfecting Technique`,
  `Shooting Psychology`, `Zen in the Art of Shooting`, `The Reference Room`,
  `Biography and History`, `Technical Information`, and `General Firearms
  Information`.
- Preserve article order inside each raw-index topic from the raw index page.
- Treat each raw-index topic as an ebook chapter group. The generated ebook
  may render these as EPUB sections or parts, but their labels and order come
  from the raw index page.
- Each canonical article linked from the raw index page becomes a chapter
  entry under its raw-index chapter group.
- Eligible canonical articles not linked from the raw index page must still be
  included for completeness in a generated final appendix group named
  `Additional Recovered Articles Not Listed on the Raw Index`, sorted by
  article title and then canonical ID. The export report must mark these as
  not raw-index-listed.
- Article titles use canonical `title`. If title is missing, use the
  canonical ID with an explicit missing-title note.
- Byline and recovered publication/update dates appear below the chapter
  title when present.
- Internal article links should point to the corresponding ebook chapter when
  the target canonical article is known. Unknown or unavailable internal links
  are omitted from reader-facing link lists where practical and recorded in the
  export report.
- External links remain outbound links and are listed in the provenance
  appendix.

## Metadata

Minimum ebook metadata:

- Title: `Bullseye Pistol`
- Subtitle or description: recovered article collection from
  `bullseyepistol.com`
- Language: `en`
- Creator/contributor: recovered by provenance, with article-level authors
  retained per chapter when available
- Source domain: `bullseyepistol.com`
- Build timestamp
- Canonical article count
- Asset count
- Source manifest paths used for the build

The generator must not invent publication dates, authors, or rights
statements. Unknown values remain absent or explicitly unknown.

## Asset Handling

- Embed recovered JPEG, PNG, GIF, and SVG assets when referenced by included
  articles and present locally.
- Preserve alt text or nearby caption text when available in canonical body
  content.
- Use stable generated asset filenames derived from canonical asset IDs, not
  original URL basenames alone.
- If multiple articles reference the same canonical asset ID, store one ebook
  asset file and reference it from each chapter.
- Do not embed recovered supplemental PDFs, MP3s, ZIPs, arbitrary HTML files,
  EXE files, or other non-reader-safe resources in the EPUB package. They may
  be represented in machine reports and in the `raw` static site's `Missing
  Artifacts` or resources area, but not inside the EPUB.
- Multiple chapters referencing the same excluded or unavailable resource share
  one report entry where possible.

## Error Cases

- Missing canonical article index: fail with a message naming the missing
  path.
- Malformed article or asset JSON: fail and record the path and parse error.
- Article listed in the index but missing on disk: fail unless the export
  report records an explicit skipped-record reason.
- Article body missing or empty: include only when `status` is `partial`, and
  mark the chapter and report entry as partial.
- Asset record references a missing local file: continue the export, omit the
  asset, and record an explicit missing-asset note.
- Recovered asset or linked-resource media type is unsupported by the EPUB
  pass: continue the export, omit it from the package, and record an
  unsupported-resource note.
- Internal link cannot be mapped to a canonical article or EPUB-safe resource:
  omit it from reader-facing EPUB output where practical and record the
  unresolved link in the report.
- Duplicate canonical IDs or duplicate chapter output paths: fail; reruns
  must not produce ambiguous chapters.
- EPUB validation failure: fail the release gate and keep the validation
  error in `_ebook-export-report.json`.

## Idempotency And Rebuild Rules

- Re-running the ebook export with unchanged canonical inputs must produce
  the same chapter order, same generated internal IDs, and same report
  counts, except for build timestamp and validation timing fields.
- The generator may clean `exports/ebook` before rebuilding. It must not
  modify files under `archive` or `content`.
- Generated output is disposable and must not become the source of truth.

## Validation

Minimum validation for the implementation slice:

- Confirm the EPUB exists at `exports/ebook/bullseye-pistol.epub`.
- Confirm `_ebook-export-report.json` exists and reports the same included
  article count as the eligible canonical article count.
- Confirm the report records the raw index page used for ordering and the
  ordered raw-index chapter groups.
- Confirm every embedded asset path in the EPUB report exists inside the
  EPUB package.
- Confirm the EPUB package manifest contains only XHTML, CSS, JPEG, PNG, GIF,
  SVG, and required EPUB container/package metadata.
- Confirm every omitted or unsupported asset has an explicit report entry.
- Confirm internal links to included articles resolve to EPUB chapter targets.
- Run an EPUB structural validator when available. If no validator is
  installed locally, record the unavailable validator as a release risk and
  still run the project-level report checks.
- Spot-check at least three chapters against source canonical records:
  one with assets, one without assets, and one partial or provenance-heavy
  article if present.

## Non-Goals

- No PDF, MOBI, Kindle-specific, print-layout, or cover-design work.
- No editorial rewriting, modernization, or author attribution invention.
- No DB schema or seed implementation.
- No change to canonical article extraction rules.
- No attempt to restore active forms, counters, widgets, scripts, or dynamic
  behavior inside the ebook.
- No use of Wayback-hosted dependencies for normal reading.
- No embedding of PDFs, MP3s, ZIPs, EXE files, arbitrary HTML files, or other
  non-reader-safe supplemental formats.

## Open Questions

No open question blocks the first EPUB implementation.

Deferred questions:

- Cover: a later pass may add a designed cover image. That later decision must
  choose between recovered historical artwork and a new preservation-oriented
  cover.

## Related Decisions

- `docs/project-goals.md`: multi-target publishing readiness requires a
  single ebook, static site, and DB-backed path from canonical content.
- `docs/requirements.md`: R4 requires ebook, static site, and DB export
  schemas before implementation and generated outputs under `exports`.
- `docs/recovery/content-structure.md`: ebook mapping treats raw-index
  topics as chapter groups, articles as chapter entries, assets as embedded
  media, and provenance as appendix or metadata.
- `docs/current-state.md`: ebook ordering uses the raw recovered index page's
  generic topic order and chapter grouping.
