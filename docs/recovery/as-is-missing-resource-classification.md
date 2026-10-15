# As-Is Missing Resource Classification

Date: 2026-05-29

## Scope

Classifies the reader-suppressed internal missing URLs and the unresolved rewrite pages
in `exports/static-site/as-is`. This is an analysis report only.

## Suppressed Internal URLs

Total suppressed internal URLs: 18

| Category | Count |
| --- | ---: |
| provider-artifact | 2 |
| hosting-template-artifact | 1 |
| owner-file-candidate | 8 |
| site-decoration | 1 |
| unrecovered-article | 6 |

### provider-artifact

- `http://bullseyepistol.com/advertise1.php`
  - Reason: Dynamic PHP page; advertising or affiliate rotation, no archived content.
- `http://bullseyepistol.com/advertise3.htm`
  - Reason: Advertising or affiliate page referenced by site chrome, not article content.

### hosting-template-artifact

- `http://bullseyepistol.com/tournamentz.htm`
  - Reason: Recovered as a MyDomain placeholder page rather than Bullseye content; pruned from the release-facing as-is build.

### owner-file-candidate

- `http://bullseyepistol.com/Handicap.exe`
  - Reason: Windows executable for league handicap scoring; likely owner-supplied.
- `http://bullseyepistol.com/ILMOScorecard.pdf`
  - Reason: Il-Mo league scorecard PDF; likely owner-supplied.
- `http://bullseyepistol.com/MidSeasonScorecard.pdf`
  - Reason: Il-Mo mid-season scorecard PDF; likely owner-supplied.
- `http://bullseyepistol.com/NewShooter.pdf`
  - Reason: New shooter orientation PDF; likely owner-supplied.
- `http://bullseyepistol.com/piasaapp.pdf`
  - Reason: PIASA application PDF; likely owner-supplied.
- `http://bullseyepistol.com/POM2004.zip`
  - Reason: League data archive; likely owner-supplied.
- `http://bullseyepistol.com/SignupForm.pdf`
  - Reason: League signup form PDF; likely owner-supplied.
- `http://bullseyepistol.com/TeamAdmin2004.zip`
  - Reason: Team administration archive; likely owner-supplied.

### site-decoration

- `http://bullseyepistol.com/fadebar3.jpg`
  - Reason: Navigation fade-bar image; site chrome with no article value.

### unrecovered-article

- `http://bullseyepistol.com/brianbio.htm`
  - Reason: Author biography linked from an article header; absent from the Wayback inventory.
- `http://bullseyepistol.com/gilhebar.htm`
  - Reason: Linked content page not present in the selected baseline or overlay captures.
- `http://bullseyepistol.com/help.htm`
  - Reason: Help page linked by recovered content but not captured in the selected baseline.
- `http://bullseyepistol.com/perchamp.htm`
  - Reason: Likely Camp Perry championship page not present in the selected captures.
- `http://bullseyepistol.com/statoffice.htm`
  - Reason: State office page linked by recovered content but not captured in the selected baseline.
- `http://bullseyepistol.com/wong8.htm`
  - Reason: Related Wong article linked from an article header; absent from the Wayback inventory.

## Unresolved Rewrite Pages

Total pages with unresolved rewrites: 43
Total external unresolved refs: 691
Total internal unresolved refs: 69

| Page bucket | Pages |
| --- | ---: |
| external-only | 24 |
| mixed | 10 |
| internal-only | 9 |

### Internal unresolved URL inventory

Unique internal unresolved URLs: 32

| Category | Unique URLs | Reference Count |
| --- | ---: | ---: |
| provider-artifact | 2 | 2 |
| hosting-template-artifact | 11 | 47 |
| owner-file-candidate | 8 | 8 |
| site-decoration | 6 | 7 |
| unrecovered-media | 1 | 1 |
| unrecovered-article | 4 | 4 |

### Internal unresolved: provider-artifact

- `http://bullseyepistol.com/advertise1.php`
  - Refs: 1
  - Pages: `articles/site-reference-general-index/advertise-and-support-this-tremendous-resource/index.html`
  - Reason: Dynamic PHP page; advertising or affiliate rotation, no archived content.
- `http://bullseyepistol.com/advertise3.htm`
  - Refs: 1
  - Pages: `shared/scripts/header1.js`
  - Reason: Advertising or affiliate page referenced by site chrome, not article content.

### Internal unresolved: hosting-template-artifact

- `http://www.bullseyepistol.com:80/generalAppC/javascripts/mydomaincom/input-fields.js`
  - Refs: 7
  - Pages: `pages/945ecf10693ad5cae76c2d8f13e34e66/index.html`, `pages/input-fields/index.html`, `pages/jquery-pngfix-pack/index.html` (+4 more)
  - Reason: Leftover registrar-hosting template JavaScript, not Bullseye article content.
- `http://www.bullseyepistol.com:80/generalAppC/javascripts/mydomaincom/jquery.pngFix.pack.js`
  - Refs: 7
  - Pages: `pages/945ecf10693ad5cae76c2d8f13e34e66/index.html`, `pages/input-fields/index.html`, `pages/jquery-pngfix-pack/index.html` (+4 more)
  - Reason: Leftover registrar-hosting template JavaScript, not Bullseye article content.
- `http://www.bullseyepistol.com:80/generalAppC/javascripts/mydomaincom/scripts.js`
  - Refs: 7
  - Pages: `pages/945ecf10693ad5cae76c2d8f13e34e66/index.html`, `pages/input-fields/index.html`, `pages/jquery-pngfix-pack/index.html` (+4 more)
  - Reason: Leftover registrar-hosting template JavaScript, not Bullseye article content.
- `http://www.bullseyepistol.com:80/generalAppC/javascripts/mydomaincom/superfish.js`
  - Refs: 7
  - Pages: `pages/945ecf10693ad5cae76c2d8f13e34e66/index.html`, `pages/input-fields/index.html`, `pages/jquery-pngfix-pack/index.html` (+4 more)
  - Reason: Leftover registrar-hosting template JavaScript, not Bullseye article content.
- `http://www.bullseyepistol.com:80/generalAppC/javascripts/mydomaincom/util-functions.js`
  - Refs: 7
  - Pages: `pages/945ecf10693ad5cae76c2d8f13e34e66/index.html`, `pages/input-fields/index.html`, `pages/jquery-pngfix-pack/index.html` (+4 more)
  - Reason: Leftover registrar-hosting template JavaScript, not Bullseye article content.
- `http://www.bullseyepistol.com:80/generalAppC/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1`
  - Refs: 7
  - Pages: `pages/945ecf10693ad5cae76c2d8f13e34e66/index.html`, `pages/input-fields/index.html`, `pages/jquery-pngfix-pack/index.html` (+4 more)
  - Reason: Registrar-hosting template asset, not part of the recovered Bullseye content set.
- `http://www.bullseyepistol.com/tournamentz.htm`
  - Refs: 1
  - Pages: `pages/tournament0/index.html`
  - Reason: Recovered as a MyDomain placeholder page rather than Bullseye content; pruned from the release-facing as-is build.
- `http://www.bullseyepistol.com/tyenter.gif`
  - Refs: 1
  - Pages: `pages/tournament4/index.html`
  - Reason: Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.
- `http://www.bullseyepistol.com:80/tyhelp.jpg`
  - Refs: 1
  - Pages: `pages/tournamentk/index.html`
  - Reason: Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.
- `http://www.bullseyepistol.com:80/tylewis.jpg`
  - Refs: 1
  - Pages: `pages/tournamentk/index.html`
  - Reason: Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.
- `http://www.bullseyepistol.com/typix.gif`
  - Refs: 1
  - Pages: `pages/tournament0/index.html`
  - Reason: Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.

### Internal unresolved: owner-file-candidate

- `http://bullseyepistol.com/Handicap.exe`
  - Refs: 1
  - Pages: `articles/il-mo-league/scorekeeping-software/index.html`
  - Reason: Windows executable for league handicap scoring; likely owner-supplied.
- `http://bullseyepistol.com/ILMOScorecard.pdf`
  - Refs: 1
  - Pages: `articles/il-mo-league/league-forms/index.html`
  - Reason: Il-Mo league scorecard PDF; likely owner-supplied.
- `http://bullseyepistol.com/MidSeasonScorecard.pdf`
  - Refs: 1
  - Pages: `articles/il-mo-league/league-forms/index.html`
  - Reason: Il-Mo mid-season scorecard PDF; likely owner-supplied.
- `http://bullseyepistol.com/NewShooter.pdf`
  - Refs: 1
  - Pages: `articles/il-mo-league/league-forms/index.html`
  - Reason: New shooter orientation PDF; likely owner-supplied.
- `http://www.bullseyepistol.com:80/piasaapp.pdf`
  - Refs: 1
  - Pages: `pages/pi-g/index.html`
  - Reason: PIASA application PDF; likely owner-supplied.
- `http://bullseyepistol.com/POM2004.zip`
  - Refs: 1
  - Pages: `articles/il-mo-league/scorekeeping-software/index.html`
  - Reason: League data archive; likely owner-supplied.
- `http://bullseyepistol.com/SignupForm.pdf`
  - Refs: 1
  - Pages: `articles/il-mo-league/league-forms/index.html`
  - Reason: League signup form PDF; likely owner-supplied.
- `http://bullseyepistol.com/TeamAdmin2004.zip`
  - Refs: 1
  - Pages: `articles/il-mo-league/scorekeeping-software/index.html`
  - Reason: Team administration archive; likely owner-supplied.

### Internal unresolved: site-decoration

- `http://www.bullseyepistol.com:80/arpc.gif`
  - Refs: 1
  - Pages: `pages/tournamenty/index.html`
  - Reason: Club-logo image used as page decoration or navigation, not article content.
- `http://www.bullseyepistol.com:80/canton.gif`
  - Refs: 1
  - Pages: `pages/tournamenty/index.html`
  - Reason: Club-logo image used as page decoration or navigation, not article content.
- `http://www.bullseyepistol.com:80/dbgc.gif`
  - Refs: 1
  - Pages: `pages/tournamenty/index.html`
  - Reason: Club-logo image used as page decoration or navigation, not article content.
- `http://www.bullseyepistol.com:80/delaware.gif`
  - Refs: 1
  - Pages: `pages/tournamenty/index.html`
  - Reason: Club-logo image used as page decoration or navigation, not article content.
- `http://bullseyepistol.com/fadebar3.jpg`
  - Refs: 2
  - Pages: `shared/scripts/header2.js`, `shared/scripts/header5.js`
  - Reason: Navigation fade-bar image; site chrome with no article value.
- `http://www.bullseyepistol.com:80/wlgc.gif`
  - Refs: 1
  - Pages: `pages/tournamenty/index.html`
  - Reason: Club-logo image used as page decoration or navigation, not article content.

### Internal unresolved: unrecovered-media

- `http://www.bullseyepistol.com/bubba.wav`
  - Refs: 1
  - Pages: `pages/tournament0/index.html`
  - Reason: Standalone audio file referenced by tournament pages; not present in the selected captures.

### Internal unresolved: unrecovered-article

- `http://bullseyepistol.com/gilhebar.htm`
  - Refs: 1
  - Pages: `shared/scripts/header4.js`
  - Reason: Linked content page not present in the selected baseline or overlay captures.
- `http://www.bullseyepistol.com/help.htm`
  - Refs: 1
  - Pages: `pages/tournament0/index.html`
  - Reason: Help page linked by recovered content but not captured in the selected baseline.
- `http://bullseyepistol.com/perchamp.htm`
  - Refs: 1
  - Pages: `shared/scripts/header4.js`
  - Reason: Likely Camp Perry championship page not present in the selected captures.
- `http://bullseyepistol.com/statoffice.htm`
  - Refs: 1
  - Pages: `shared/scripts/header4.js`
  - Reason: State office page linked by recovered content but not captured in the selected baseline.

## Findings Summary

- `as-is` suppresses `18` internal missing URLs from reader-facing pages.
- The unresolved rewrite inventory contains `32` unique internal URLs and `691` external references.
- Hosting-template artifacts account for `11` unique internal unresolved URLs and are concentrated in provider-generated `pages/*` captures.
- Owner-file candidates account for `8` suppressed URLs and should be the first owner-recovery request set.

## Recommended Follow-Up Slices

1. **Owner-file recovery request:** Ask the site owner for the 8 PDFs, ZIPs, and EXE files still missing from recovery.
2. **As-is provider-artifact cleanup:** Decide whether provider-hosting template pages and decorative unresolved assets should remain in the as-is export or be pruned from future builds.
3. **Historical-gap acknowledgement:** Keep the unrecovered article/media URLs in handoff and audit docs as explicit historical gaps.
