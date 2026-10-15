# Raw Article Static Site Report

Date: 2026-05-22

## Output

- Directory: `exports/static-site/raw`
- Entry point: `exports/static-site/raw/index.html`
- Generator: `tools/build_canonical_static_site.py`
- Export report: `exports/static-site/raw/_raw-export-report.json`
- Validation report: `exports/static-site/raw/_validation-report.json`

## Model

The raw article static site is a clean article presentation generated from `content/canonical/articles` and `content/assets`.

The navigation model follows the recovered original homepage sections as exactly as possible, with an additional enhanced browse layer for provenance-backed groupings. All articles are now placed without a fallback section.

## Generated Content

- Article pages: `150`
- Homepage-derived sections: `15`
- Enhanced browse groups: `6`
- Fallback section: `0`
- Articles in fallback section: `0`
- Recovered article image assets copied/hardlinked: `165`
- Additional recovered linked resources copied/hardlinked: `21`
- Missing internal linked resources represented in `missing-artifacts.html`: `7`

Additional recovered resources include recovered PDFs and non-article HTML pages referenced from article bodies. They are stored under `exports/static-site/raw/resources`.

Missing internal resources are centralized in `exports/static-site/raw/missing-artifacts.html`. Each entry includes the original URL, a concise description reconstructed from the referring article context, and a backlink to the source article page. The current missing original URLs are:

- `http://bullseyepistol.com/Handicap.exe`
- `http://bullseyepistol.com/ILMOScorecard.pdf`
- `http://bullseyepistol.com/MidSeasonScorecard.pdf`
- `http://bullseyepistol.com/NewShooter.pdf`
- `http://bullseyepistol.com/POM2004.zip`
- `http://bullseyepistol.com/SignupForm.pdf`
- `http://bullseyepistol.com/TeamAdmin2004.zip`
## Validation

Command:

```sh
python3 tools/validate_static_site.py exports/static-site/raw --expect-articles 150 --report exports/static-site/raw/_validation-report.json
```

Result:

- HTML files checked: `168`
- Article pages found: `150`
- Local references checked: `1,530`
- Broken local references: `0`
- External references preserved: `380`
- Overall validation: passed

## Rebuild

Regenerate the export from canonical content and deduplicated raw backup blobs:

```sh
python3 tools/build_canonical_static_site.py --backup archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json
python3 tools/validate_static_site.py exports/static-site/raw --expect-articles 150 --report exports/static-site/raw/_validation-report.json
```
