# Ebook Export Report

Date: 2026-10-15

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
- Raw-index-listed articles: `95`
- Additional recovered articles not listed on the raw index: `55`

The additional recovered articles are included in evidence-backed groups from
the enhanced canonical browse layer. The EPUB contains `15` chapter groups.

## Results

- Included articles: `150`
- EPUB chapter files: `150`
- Embedded recovered image assets: `160`
- Missing asset records: `0`
- Unsupported asset records: `0`
- Suppressed internal non-article resource links: `59`
- Unresolved internal links: `0`
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
- All `787` local package references inside EPUB XHTML resolve with `0`
  broken references.
- No EPUB chapter uses the legacy pre-wrapped text block.
- No EPUB chapter matches the hard-wrap candidate scan for repeated
  source-line line breaks.
- No EPUB figure caption exposes an internal `asset-...` identifier.
- Built-in validation passed.

EPUBCheck `5.4.0` passed with `0` errors and `0` warnings. The exporter
records its exit code and complete output in
`exports/ebook/_ebook-export-report.json`. The identical final edition at
`exports/final/bullseye-pistol.epub` also passed a separate EPUBCheck run.

The initial external check found `30` navigation errors: section labels were
bare text instead of an `a` or `span` element. The generator now wraps each
section label in `span`; article bodies, ordering, and recovered assets are
unchanged. The existing build command runs EPUBCheck whenever it is on PATH.

Install the external validator on macOS with `brew install epubcheck`.
Run the final-edition check with:

```sh
epubcheck exports/final/bullseye-pistol.epub
```

## Rebuild

Regenerate the ebook from canonical content and recovered local assets:

```sh
python3 tools/build_ebook.py
```
