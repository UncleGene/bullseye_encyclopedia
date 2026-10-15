#!/usr/bin/env python3
"""Stage the historical homepage and article site with same-origin switches."""

import argparse
import os
import re
import shutil
from pathlib import Path


VARIANT_LINK = re.compile(r'(<a\b[^>]*data-site-variant="(raw|as-is)"\s+href=")[^"]*(")')


def stage_site(exports: Path, out: Path) -> None:
    shutil.copytree(exports / "as-is", out)
    shutil.copytree(exports / "raw", out / "raw")
    targets = {"as-is": out / "index.html", "raw": out / "raw/index.html"}
    for page in out.rglob("*.html"):
        def rewrite(match: re.Match[str]) -> str:
            href = Path(os.path.relpath(targets[match[2]], page.parent)).as_posix()
            return match[1] + href + match[3]

        source = page.read_text(encoding="utf-8")
        rewritten = VARIANT_LINK.sub(rewrite, source)
        if rewritten != source:
            page.write_text(rewritten, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path, help="New staging directory")
    args = parser.parse_args()
    stage_site(Path("exports/static-site"), args.out)


if __name__ == "__main__":
    main()
