# Raw Static Site Reproduction Report

Date: 2026-05-23

## Purpose

Produce a deployable `as-is` copy of the recovered website, preserving original page layout/chrome where possible while rewriting recovered internal dependencies to local files.

## Inputs

- Raw backup manifest: `archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json`
- Article image recovery manifest: `archive/raw/wayback/manifests/20260522T-combined-image-recovery.json`
- Static dependency manifests:
  - `archive/raw/wayback/manifests/20260522T210905Z-static-dependencies.json`
  - `archive/raw/wayback/manifests/20260522T211825Z-static-dependencies.json`
  - `archive/raw/wayback/manifests/20260522T212117Z-static-dependencies.json`
  - `archive/raw/wayback/manifests/20260522T212351Z-static-dependencies.json`
  - `archive/raw/wayback/manifests/20260522T212800Z-static-dependencies.json`
  - `archive/raw/wayback/manifests/20260522T213255Z-static-dependencies.json`
- Repair manifests included in the current rebuild:
  - `archive/raw/wayback/manifests/20260523T071345Z-backup.json`
  - `archive/raw/wayback/manifests/20260523T073107Z-backup.json`

## Output

- Static site directory: `exports/static-site/as-is`
- Reproduction report: `exports/static-site/as-is/_reproduction-report.json`
- Validation report: `exports/static-site/as-is/_validation-report.json`
- Files written: `524`
- Entry page: `exports/static-site/as-is/index.html`

## Directory Structure

The `as-is` export is intentionally not flat. It follows canonical homepage groups and detected parent/sub-article groups:

- Top-level article pages: `exports/static-site/as-is/articles/<canonical-section>/<article-or-subgroup>/index.html`
- Sub-article pages: `exports/static-site/as-is/articles/<canonical-section>/<parent-article>/<sub-article>/index.html`
- Article-specific recovered images: `images/` beside the grouped article page
- Page-local script copies: `_scripts/` beside each generated page
- Site-wide images: `exports/static-site/as-is/shared/images/`
- Site-wide styles/scripts/files retained from selected captures: `exports/static-site/as-is/shared/`

Current structure counts:

- Top-level canonical sections: `10`
- Detected sub-article groups: `2`
- Article-specific image files: `161`
- Shared image files: `295`
- Page-local JavaScript files checked: `295`

Detected sub-article groups:

- `articles/technical-information/vision-topics/` for `wong` and its `wong1`-`wong7`/`wongbio` child pages.
- `articles/biography-and-history/army-marksmanship-unit-champion-profiles/` for `amuprfil` and its `profile1`-`profile7` child pages.

When the same recovered image appears in both an article folder and `shared/images`, the exporter uses hardlinks where the filesystem permits it. Current check: `161` of `161` same-name article/shared image pairs share the same inode, so the structured convenience copies do not duplicate bytes locally.

## Internal Dependency Recovery

The raw-site builder recursively surfaced missing internal dependencies. Recovery passes downloaded additional assets/pages, including the `tournament.bullseyepistol.com` page and the tournament-related page/assets that were successfully archived.

Current release-facing export behavior suppresses missing-resource prose from reader pages. The reproduction report records `17` suppressed internal URLs, and unresolved rewrite inventory is retained only in the machine report.

Permanent or historically unresolved internal URLs include:

- `http://bullseyepistol.com/Handicap.exe`
- `http://bullseyepistol.com/ILMOScorecard.pdf`
- `http://bullseyepistol.com/MidSeasonScorecard.pdf`
- `http://bullseyepistol.com/NewShooter.pdf`
- `http://bullseyepistol.com/POM2004.zip`
- `http://bullseyepistol.com/SignupForm.pdf`
- `http://bullseyepistol.com/TeamAdmin2004.zip`
- `http://www.bullseyepistol.com/bubba.wav`
- `http://www.bullseyepistol.com/help.htm`
- `http://www.bullseyepistol.com:80/arpc.gif`
- `http://www.bullseyepistol.com:80/canton.gif`
- `http://www.bullseyepistol.com:80/dbgc.gif`
- `http://www.bullseyepistol.com:80/delaware.gif`
- `http://www.bullseyepistol.com:80/piasaapp.pdf`
- `http://www.bullseyepistol.com:80/wlgc.gif`

Current suppressed internal URLs are listed in `exports/static-site/as-is/_reproduction-report.json` under `silent_missing_internal_urls`.

External unresolved links remain as outbound links and are not required for local site reproduction.

## Styling / Fidelity Correction

The raw-site builder was corrected after review showed the `as-is` presentation could render with off styling or stale links.

Corrections made:

- Rebuilds now clear `exports/static-site/as-is` before generation so stale timestamped HTML cannot remain from older runs.
- Generated HTML, JavaScript, and CSS files are unlinked before writing so hardlinked archive blobs cannot be mutated by generated-output rewrites.
- JavaScript-generated layout/link references are rewritten along with HTML references. This matters because original pages use `header*.js` to write major header, sidebar, quickstart, and article chrome.
- Scripts referenced by pages are emitted as page-local `_scripts/` copies. This preserves the original script-generated chrome while making relative asset URLs resolve correctly from each page directory.
- Captured `.js` URLs whose Wayback payload is actually HTML, such as parked-provider/MyDomain default pages, are not emitted as executable page scripts.
- Dynamic JavaScript image prefixes used by the original ad/sidebar chrome, such as `premium1.jpg?v=" + rand`, are rewritten to local `shared/images` paths without applying HTML-style rewrites to JavaScript source.
- Rewritten local links preserve query strings and anchor fragments.
- URL-encoded filenames are written with decoded filesystem names so browser and validator path resolution agree.
- Missing internal resources are suppressed from reader-facing pages where practical, using silent local placeholders for missing images and report-only tracking for omitted internal URLs.
- Release-facing cleanup prunes MyDomain/provider-template placeholder captures from the published `as-is` tree while leaving archive evidence untouched.

During this correction, a checksum audit found hardlinked JavaScript blobs that had been accidentally modified by the previous generated-output rewrite. The affected blobs were repaired from Wayback:

- Broad repair manifest: `archive/raw/wayback/manifests/20260523T071345Z-backup.json`
- Targeted `imheader1.js` repair manifest: `archive/raw/wayback/manifests/20260523T073107Z-backup.json`

Post-repair checksum audit: `0` mismatched blob references across the combined raw backup and article-image recovery manifests.

## Validation

- Verified `exports/static-site/as-is/index.html` exists.
- Verified core local dependencies such as `header.js`, `banner1.jpg`, and `bp.ico` exist.
- Verified recovered internal dependency variants collapse across `http`, `https`, `www`, `:80`, and `.htm/.html`.
- Verified structured article sample:
  - `exports/static-site/as-is/articles/tools-of-the-trade/the-benefits-of-custom-anatomical-grips/index.html`
  - `exports/static-site/as-is/articles/tools-of-the-trade/the-benefits-of-custom-anatomical-grips/images/funggun.jpg`
  - `exports/static-site/as-is/articles/technical-information/vision-topics/index.html`
  - `exports/static-site/as-is/articles/technical-information/vision-topics/bullseye-shooting-for-the-eyecare-professional/index.html`
  - `exports/static-site/as-is/articles/technical-information/vision-topics/images/wong.jpg`
- Verified raw export has `0` broken local references across `1,102` local references:

```sh
python3 tools/validate_static_site.py exports/static-site/as-is --report exports/static-site/as-is/_validation-report.json
```

- Verified all page-local JavaScript files parse:

```sh
python3 - <<'PY'
from pathlib import Path
import subprocess
bad = []
for p in Path('exports/static-site/as-is').rglob('_scripts/*.js'):
    r = subprocess.run(['node', '--check', str(p)], capture_output=True, text=True)
    if r.returncode:
        bad.append(str(p))
print(len(bad))
PY
```

Result: `0` bad scripts across `295` checked files.
