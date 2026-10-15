# Ebook Export Report

Date: 2026-05-23

## Output

- EPUB: `exports/ebook/bullseye-pistol.epub`
- Export report: `exports/ebook/_ebook-export-report.json`
- Provenance appendix: `exports/ebook/provenance.html`
- Generator: `tools/build_ebook.py`
- Contract: `docs/recovery/ebook-export-contract.md`

## Ordering

The ebook uses the raw recovered index page as the ordering and chapter-group
authority:

- Raw index: `archive/raw/wayback/files/20260522T143136Z/202508/article_candidate/www.bullseyepistol.com/20250818003737-index-5fffb450c2814c7e.html`
- Raw-index-listed articles: `63`
- Additional recovered articles not listed on the raw index: `87`

The additional recovered articles are included for completeness in a generated
final appendix group named `Additional Recovered Articles Not Listed on the Raw
Index`.

## Results

- Included articles: `150`
- EPUB chapter files: `150`
- Embedded recovered image assets: `160`
- Missing asset records: `0`
- Unsupported asset records: `0`
- Unresolved internal links preserved as original URL references: `33`
- Visible asset-ID image captions: `0`

## Validation

Command:

```sh
python3 tools/build_ebook.py
```

Result:

- EPUB exists.
- EPUB `mimetype` entry is first.
- `META-INF/container.xml` exists.
- `OEBPS/content.opf` exists.
- `OEBPS/nav.xhtml` exists.
- All report-listed embedded assets exist inside the EPUB package.
- All report-listed chapter files exist inside the EPUB package.
- All `654` local package references inside EPUB XHTML resolve with `0`
  broken references.
- No EPUB chapter uses the legacy pre-wrapped text block.
- No EPUB chapter matches the hard-wrap candidate scan for repeated
  source-line line breaks.
- No EPUB figure caption exposes an internal `asset-...` identifier.
- Built-in validation passed.

`epubcheck` is not installed locally, so full external EPUB structural
validation remains a release risk. The exporter records that risk in
`exports/ebook/_ebook-export-report.json`.

## Rebuild

Regenerate the ebook from canonical content and recovered local assets:

```sh
python3 tools/build_ebook.py
```
