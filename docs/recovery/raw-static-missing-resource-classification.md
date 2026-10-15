# Raw As-Is Missing Resource Classification

Date: 2026-05-24
Updated: 2026-05-29 (historical report; superseded by release-facing `as-is` classification)

## Scope

This is a historical pre-alignment report for the old `exports/static-site/raw-as-is`
build. The current release-facing classification lives in
`docs/recovery/as-is-missing-resource-classification.md` for
`exports/static-site/as-is`.

## Cleanup Applied

Provider-artifact cleanup completed 2026-05-24:
- Deleted 10 `_missing/*.html` files for numeric counter paths and ad/PHP pages.
- Restored 8 range-finder dropdown option values to plain numerics (5, 10, 15, 20, 25, 30, 60, 90).
- Build script `replace_option` fixed to skip non-URL-shaped form values.
- Reproduction report updated: missing_note_count now 14.
- Validation: 0 broken local references across 1,121 local references.

## Missing-Resource Note Classification

Total: 24 notes

| Category | Count |
| --- | ---: |
| provider-artifact | 10 |
| owner-file-candidate | 8 |
| site-decoration | 1 |
| unrecovered-article | 5 |

### provider-artifact

- `http://bullseyepistol.com/10`
  - Note page: `_missing/10-dddeccdd5cb8.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/15`
  - Note page: `_missing/15-660eebcd71f2.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/20`
  - Note page: `_missing/20-c318374985e8.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/25`
  - Note page: `_missing/25-85096db8f086.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/30`
  - Note page: `_missing/30-78eb3178ee88.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/5`
  - Note page: `_missing/5-758b40269cfd.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/60`
  - Note page: `_missing/60-4dfc07e1a614.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/90`
  - Note page: `_missing/90-d2ac878e9d2a.html`
  - Reason: Numeric path; consistent with a click-counter or ad-tracking artifact.
- `http://bullseyepistol.com/advertise1.php`
  - Note page: `_missing/advertise1-78e21d87aa3a.html`
  - Reason: Dynamic PHP page; advertising or affiliate rotation, no archived content.
- `http://bullseyepistol.com/advertise3.htm`
  - Note page: `_missing/advertise3-0b18881e9430.html`
  - Reason: Advertising/affiliate page; referenced by advertise article, no Wayback capture.

### owner-file-candidate

- `http://bullseyepistol.com/Handicap.exe`
  - Note page: `_missing/handicap-7484292b1789.html`
  - Reason: Windows executable; league handicap scoring software linked from Il-Mo pages.
- `http://bullseyepistol.com/ILMOScorecard.pdf`
  - Note page: `_missing/ilmoscorecard-01fe217fa642.html`
  - Reason: Il-Mo league scorecard PDF; owner-supplied document.
- `http://bullseyepistol.com/MidSeasonScorecard.pdf`
  - Note page: `_missing/midseasonscorecard-42931eb5c518.html`
  - Reason: Il-Mo mid-season scorecard PDF; owner-supplied document.
- `http://bullseyepistol.com/NewShooter.pdf`
  - Note page: `_missing/newshooter-f3c546da02da.html`
  - Reason: New shooter orientation PDF; owner-supplied document.
- `http://bullseyepistol.com/POM2004.zip`
  - Note page: `_missing/pom2004-a62f6cff85b9.html`
  - Reason: 2004 league data archive; owner-supplied binary.
- `http://bullseyepistol.com/SignupForm.pdf`
  - Note page: `_missing/signupform-8676ce5174d2.html`
  - Reason: League signup form PDF; owner-supplied document.
- `http://bullseyepistol.com/TeamAdmin2004.zip`
  - Note page: `_missing/teamadmin2004-128edb1ffa1e.html`
  - Reason: 2004 team administration archive; owner-supplied binary.
- `http://bullseyepistol.com/piasaapp.pdf`
  - Note page: `_missing/piasaapp-705191d33daf.html`
  - Reason: PIASA application PDF; owner-supplied document.

### site-decoration

- `http://bullseyepistol.com/fadebar3.jpg`
  - Note page: `_missing/fadebar3-0a91f60bdd85.html`
  - Reason: Navigation fade-bar image; site chrome with no article content.

### unrecovered-article

- `http://bullseyepistol.com/chaptr10.htm`
  - Note page: `_missing/chaptr10-da5a41e17b63.html`
  - Reason: Variant URL for a chapter article; chapter10 was recovered via a different URL.
- `http://bullseyepistol.com/gilhebar.htm`
  - Note page: `_missing/gilhebar-dc3fdfa15b80.html`
  - Reason: Content page not captured in selected baseline/overlay; identity unclear.
- `http://bullseyepistol.com/help.htm`
  - Note page: `_missing/help-3fb6f0f5598b.html`
  - Reason: Site help page; not present in selected Wayback captures.
- `http://bullseyepistol.com/perchamp.htm`
  - Note page: `_missing/perchamp-598c5bcd9713.html`
  - Reason: Likely a Camp Perry championship results page; not captured in selected captures.
- `http://bullseyepistol.com/statoffice.htm`
  - Note page: `_missing/statoffice-5c600d56e16b.html`
  - Reason: State office page; not present in selected Wayback captures.

## Unresolved Rewrite Classification

Total pages with unresolved rewrites: 48
Total unresolved refs: 1005
  - External links (correct behavior, no recovery gap): 914
  - Internal missing (same files as missing-note catalogue): 91

| Category | Pages | Internal refs | External refs |
| --- | ---: | ---: | ---: |
| external-only | 28 | 0 | 421 |
| mixed | 13 | 76 | 493 |
| internal-missing | 7 | 15 | 0 |

**Finding:** 914 of 1005 unresolved refs (91 %) are external links correctly
left unrewritten. The remaining 91 internal refs point to the same 14 URLs
already catalogued in the missing-note section above.

### Pages with internal-missing refs only

- `articles/other-recovered-articles/advertise-and-support-this-tremendous-resource/index.html`
  - `http://bullseyepistol.com/advertise1.php`
- `articles/other-recovered-articles/league-forms/index.html`
  - `http://bullseyepistol.com/ILMOScorecard.pdf`
  - `http://bullseyepistol.com/MidSeasonScorecard.pdf`
  - `http://bullseyepistol.com/NewShooter.pdf`
  - `http://bullseyepistol.com/SignupForm.pdf`
- `articles/other-recovered-articles/scorekeeping-software/index.html`
  - `http://bullseyepistol.com/Handicap.exe`
  - `http://bullseyepistol.com/POM2004.zip`
  - `http://bullseyepistol.com/TeamAdmin2004.zip`
- `shared/scripts/header1.js`
  - `http://bullseyepistol.com/advertise3.htm`
- `shared/scripts/header2.js`
  - `http://bullseyepistol.com/fadebar3.jpg`
- `shared/scripts/header4.js`
  - `http://bullseyepistol.com/chaptr10.htm`
  - `http://bullseyepistol.com/gilhebar.htm`
  - `http://bullseyepistol.com/perchamp.htm`
  - `http://bullseyepistol.com/statoffice.htm`
- `shared/scripts/header5.js`
  - `http://www.bullseyepistol.com/fadebar3.jpg`

### Pages with mixed internal + external refs (sample)

- `index.html` — 8 internal, 29 external
  - internal: `http://www.bullseyepistol.com/10`
  - internal: `http://www.bullseyepistol.com/15`
  - internal: `http://www.bullseyepistol.com/20`
  - internal: `http://www.bullseyepistol.com/25`
  - internal: `http://www.bullseyepistol.com/30`
  - internal: `http://www.bullseyepistol.com/5`
  - internal: `http://www.bullseyepistol.com/60`
  - internal: `http://www.bullseyepistol.com/90`
- `pages/input-fields/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/jquery-pngfix-pack/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/screen7/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/scripts/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/superfish/index.html` — 6 internal, 42 external
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/tournament0/index.html` — 2 internal, 2 external
  - internal: `http://www.bullseyepistol.com/bubba.wav`
  - internal: `http://www.bullseyepistol.com/help.htm`
- `pages/tournamentz/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/tyenter/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/tyhelp/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/tylewis/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/typix/index.html` — 6 internal, 42 external
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://www.bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
- `pages/util-functions/index.html` — 6 internal, 42 external
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/input-fields.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/scripts.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/superfish.js`
  - internal: `http://bullseyepistol.com/generalAppC/javascripts/mydomaincom/util-functions.js`
  - internal: `http://bullseyepistol.com/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`

## Findings Summary

- **No content recovery gap in the unresolved-rewrite set.** The 914 external refs
  are correctly preserved as external links. No additional Wayback downloads are needed.
- **10 provider-artifact missing notes** (8 numeric counter paths + 2 ad/PHP pages)
  can be removed from the raw as-is output in a later cleanup slice without losing
  historical content.
- **8 owner-file-candidate missing notes** (PDFs, executables, archives) represent
  files the site owner may have locally. No Wayback capture exists; owner input is
  needed before treating these as unrecoverable.
- **5 unrecovered-article missing notes** represent content pages not present in
  the selected baseline/overlay captures. These are genuine historical gaps.
- **1 site-decoration missing note** (`fadebar3.jpg`) is a nav chrome image with no
  article content; low impact.

## Recommended Follow-Up Slices

1. **Provider-artifact cleanup:** Remove the 10 provider-artifact missing notes from
   the raw as-is output and update the reproduction report.
2. **Owner-file request:** Ask the site owner whether the 8 PDFs, executables, and
   archives are available locally for inclusion.
3. **Unrecovered-article acknowledgement:** Record the 5 unrecovered article URLs as
   permanent historical gaps in the handoff document.
