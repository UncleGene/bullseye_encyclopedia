# PDF Release Check

Date: 2026-10-15

## Edition and scope

Checked `exports/final/bullseye-pistol.pdf` against the working edition at
`exports/pdf/bullseye-pistol.pdf`, the canonical article index, and
`exports/pdf/_pdf-export-report.json`. This closes the PDF QA portion of M5;
it does not mark all presentation or publishing work complete.

Both PDF copies are identical. SHA-256:
`359e07754d8561d2246e9d1ccb2e6c72bca7bf3d02dfea05cee2ecf54cbb6985`.

## Structural results

- Poppler `pdfinfo` and pypdf confirm `574` letter-size pages. The former
  `575`-page status statement was stale.
- All `150` eligible canonical articles appear exactly once in the export
  order, in the existing `15` topic groups.
- Every article has a named chapter destination, and each destination page
  contains that article's canonical title.
- All `838` PDF link annotations resolve to local destinations; there are
  `0` broken destinations and `0` external URI annotations.
- The export report records `162` resolved image references out of `162`.
  Sampled illustrated pages contain embedded image resources.
- Poppler's bounding-box extraction found no words outside page boundaries
  across all `574` pages. This is a structural check, not a substitute for
  visual review of every page.

## Visual review

Rendered pages with `pdftoppm` and inspected pages `1`, `2`, `7`, `151`,
`358`, `378`, `440`, `483`, `486`, `554`, and `574`. These cover the title
page, contents, illustrated prose, a long training article, profiles, vision
topics, rules, league forms, unavailable-resource references, fixed-width
records, and the final article.

The sampled pages show readable text, intact images and tables, consistent
headers and page numbers, and no observed clipping or overlap. The records
table extends slightly beyond the usual body margin but remains readable
inside the page. Visual review was sampled; every page was not inspected.

## Missing-resource policy and release notes

The PDF export report retains `33` unresolved internal-resource link records.
These are references to non-article resources, including recovered resources
and unrecovered files; the count is not a count of missing articles.

The exporter strips non-article link targets from article bodies and omits
unresolved internal resources from generated reference lists, retaining their
labels as original article text where present. The full PDF text contains no
generated `Missing Artifacts`, `missing resource`, `not recovered`, or
`[Image:` notices. League forms and old season results retain their original
descriptive text without active download links. This matches the R4 policy
of avoiding reader-facing missing-resource pages while retaining report
evidence.

Historical omissions remain documented in `handoff.md` and in the raw site's
`Missing Artifacts` catalogue. Downloadable league forms, software, and old
results are not restored by this PDF check. No historical content was
substituted or rewritten. Article titles and bylines remain canonical-source
values; this check does not establish their editorial accuracy.

## Verification and disposition

Used Poppler `pdfinfo`, `pdftotext -bbox`, `pdftotext -layout`, and
`pdftoppm`; pypdf checked article destinations and link annotations against
the current export report and canonical article set. Python byte comparison
and SHA-256 confirmed the two editions match.

No PDF export defect was confirmed, so no generator or PDF bytes were
changed. Raw archives, canonical records, recovered assets, and existing
topic order remain unchanged. Further release work should be scoped
separately; DB work and public URL policy remain deferred.
