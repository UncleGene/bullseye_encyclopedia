#!/usr/bin/env python3
"""Audit generated reader outputs and rank follow-up improvement candidates."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_RAW_REPRODUCTION_REPORT = Path("exports/static-site/as-is/_reproduction-report.json")
DEFAULT_RAW_VALIDATION_REPORT = Path("exports/static-site/as-is/_validation-report.json")
DEFAULT_CANONICAL_EXPORT_REPORT = Path("exports/static-site/raw/_raw-export-report.json")
DEFAULT_CANONICAL_VALIDATION_REPORT = Path("exports/static-site/raw/_validation-report.json")
DEFAULT_EBOOK_EXPORT_REPORT = Path("exports/ebook/_ebook-export-report.json")
DEFAULT_AS_IS_CLASSIFICATION_REPORT = Path("exports/output-audit/as-is-missing-resource-classification.json")
DEFAULT_JSON_OUT = Path("exports/output-audit/_output-audit-report.json")
DEFAULT_MARKDOWN_OUT = Path("docs/recovery/output-audit-report.md")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required report is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validation_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "passed": bool(report.get("passed")),
        "html_file_count": report.get("html_file_count"),
        "article_page_count": report.get("article_page_count"),
        "local_reference_count": report.get("local_reference_count"),
        "external_reference_count": report.get("external_reference_count"),
        "broken_local_reference_count": len(report.get("broken_local_references") or []),
    }


def count_report_value(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, (list, tuple, set, dict)):
        return len(value)
    raise TypeError(f"Cannot count report value of type {type(value).__name__}")


def ebook_check(report: dict[str, Any], name: str) -> dict[str, Any] | None:
    for check in report.get("validation", {}).get("checks", []):
        if check.get("name") == name:
            return check
    return None


def add_finding(
    findings: list[dict[str, Any]],
    *,
    output: str,
    classification: str,
    title: str,
    evidence: str,
    next_action: str,
) -> None:
    findings.append(
        {
            "output": output,
            "classification": classification,
            "title": title,
            "evidence": evidence,
            "next_action": next_action,
        }
    )


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    raw_reproduction = load_json(Path(args.raw_reproduction_report))
    raw_validation = load_json(Path(args.raw_validation_report))
    canonical_export = load_json(Path(args.canonical_export_report))
    canonical_validation = load_json(Path(args.canonical_validation_report))
    ebook_export = load_json(Path(args.ebook_export_report))
    as_is_classification = load_json(Path(args.as_is_classification_report)) if Path(args.as_is_classification_report).exists() else {}

    raw_missing_notes = raw_reproduction.get("missing_notes") or {}
    raw_silent_missing_urls = raw_reproduction.get("silent_missing_internal_urls") or []
    raw_missing_rewrites = raw_reproduction.get("missing_rewrites") or {}
    raw_unresolved_pages = raw_reproduction.get("pages_with_unresolved_local_rewrites")
    raw_unresolved_page_count = count_report_value(raw_unresolved_pages)
    raw_missing_rewrite_page_count = count_report_value(raw_missing_rewrites)
    canonical_missing = canonical_export.get("missing_internal_references") or []
    ebook_unresolved = ebook_export.get("unresolved_internal_links") or []
    ebook_local_refs = ebook_check(ebook_export, "local_package_references_resolve") or {}
    ebook_prewrap = ebook_check(ebook_export, "no_legacy_prewrapped_chapters") or {}
    ebook_hard_wrap = ebook_check(ebook_export, "no_hard_wrap_candidates") or {}
    ebook_asset_id_captions = ebook_check(ebook_export, "no_visible_asset_id_captions") or {}
    epubcheck = ebook_check(ebook_export, "epubcheck_available") or ebook_check(ebook_export, "epubcheck")
    as_is_suppressed_by_category = as_is_classification.get("suppressed_by_category") or {}
    as_is_internal_unresolved_by_category = as_is_classification.get("internal_unresolved_by_category") or {}
    as_is_external_unresolved_ref_count = as_is_classification.get("external_unresolved_ref_count")

    findings: list[dict[str, Any]] = []

    for output, report in (
        ("as-is-static", raw_validation),
        ("raw-static", canonical_validation),
    ):
        summary = validation_summary(report)
        if not summary["passed"] or summary["broken_local_reference_count"]:
            add_finding(
                findings,
                output=output,
                classification="blocking",
                title="Static validation failure",
                evidence=f"{summary['broken_local_reference_count']} broken local references; passed={summary['passed']}",
                next_action="Fix broken local references before any release or further polish work.",
            )

    if not ebook_export.get("validation", {}).get("passed"):
        add_finding(
            findings,
            output="ebook",
            classification="blocking",
            title="EPUB package validation failure",
            evidence="Built-in EPUB validation did not pass.",
            next_action="Fix EPUB packaging before improving content or navigation.",
        )

    if canonical_export.get("unplaced_article_count", 0):
        add_finding(
            findings,
            output="raw-static",
            classification="candidate",
            title="Raw article-site fallback section is large",
            evidence=f"{canonical_export['unplaced_article_count']} articles are in Other Recovered Articles.",
            next_action="Evaluate provenance-backed enhanced navigation while preserving the exact-homepage navigation model.",
        )

    if canonical_missing:
        add_finding(
            findings,
            output="raw-static",
            classification="candidate",
            title="Raw article site missing artifacts",
            evidence=f"{len(canonical_missing)} unrecovered internal resources are centralized in the Missing Artifacts page.",
            next_action="Keep the centralized catalogue with source-backed descriptions and treat these files as permanent gaps unless supplied outside Wayback later.",
        )

    if raw_missing_notes or raw_silent_missing_urls:
        add_finding(
            findings,
            output="as-is-static",
            classification="candidate",
            title="As-is permanent non-Wayback file gaps are identified",
            evidence=(
                f"{as_is_suppressed_by_category.get('owner-file-candidate', 0)} suppressed owner-file candidates, "
                f"{as_is_suppressed_by_category.get('unrecovered-article', 0)} unrecovered article URLs, "
                f"{as_is_suppressed_by_category.get('provider-artifact', 0)} provider artifacts."
            ),
            next_action="Treat the owner-file candidates as permanent non-Wayback gaps unless files are supplied out-of-band, and keep the other suppressed URLs as explicit gaps or artifacts.",
        )

    if raw_missing_rewrite_page_count or raw_unresolved_page_count:
        add_finding(
            findings,
            output="as-is-static",
            classification="candidate",
            title="As-is unresolved rewrites are now mostly residual provider-era artifacts",
            evidence=(
                f"{raw_unresolved_page_count} pages have unresolved rewrites; "
                f"{as_is_external_unresolved_ref_count if as_is_external_unresolved_ref_count is not None else 'n/a'} external refs and "
                f"{as_is_internal_unresolved_by_category.get('hosting-template-artifact', 0)} unique hosting-template internal URLs dominate the internal set."
            ),
            next_action="Keep pruning limited to release-facing provider placeholder pages and use the remaining inventory as a documented preservation artifact unless a narrower cleanup target emerges.",
        )

    if ebook_unresolved:
        add_finding(
            findings,
            output="ebook",
            classification="candidate",
            title="EPUB unresolved internal links remain after reader-safe suppression",
            evidence=f"{len(ebook_unresolved)} internal links still cannot be resolved to included chapters or assets.",
            next_action="Review whether any remaining unresolved links should be normalized to article targets or excluded from chapter reference lists.",
        )

    if epubcheck and not epubcheck.get("passed"):
        add_finding(
            findings,
            output="ebook",
            classification="deferred",
            title="External EPUB validation unavailable",
            evidence=str(epubcheck.get("risk") or "epubcheck did not pass or is unavailable."),
            next_action="Run epubcheck before public release when available locally.",
        )

    report = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "inputs": {
            "raw_reproduction_report": str(args.raw_reproduction_report),
            "raw_validation_report": str(args.raw_validation_report),
            "canonical_export_report": str(args.canonical_export_report),
            "canonical_validation_report": str(args.canonical_validation_report),
            "ebook_export_report": str(args.ebook_export_report),
            "as_is_classification_report": str(args.as_is_classification_report),
        },
        "outputs": {
            "as_is_static": {
                "output": raw_reproduction.get("output"),
                "files_written": raw_reproduction.get("files_written"),
                "article_specific_image_count": raw_reproduction.get("article_specific_image_count"),
                "missing_note_count": len(raw_missing_notes),
                "silent_missing_internal_url_count": len(raw_silent_missing_urls),
                "suppressed_by_category": as_is_suppressed_by_category,
                "pages_with_unresolved_local_rewrites": raw_unresolved_page_count,
                "missing_rewrite_page_count": raw_missing_rewrite_page_count,
                "internal_unresolved_by_category": as_is_internal_unresolved_by_category,
                "external_unresolved_ref_count": as_is_external_unresolved_ref_count,
                "validation": validation_summary(raw_validation),
            },
            "raw_static": {
                "output": canonical_export.get("output"),
                "article_count": canonical_export.get("article_count"),
                "asset_count": canonical_export.get("asset_count"),
                "linked_resource_count": canonical_export.get("linked_resource_count"),
                "missing_internal_reference_count": len(canonical_missing),
                "unplaced_article_count": canonical_export.get("unplaced_article_count"),
                "navigation_model": canonical_export.get("navigation_model"),
                "validation": validation_summary(canonical_validation),
            },
            "ebook": {
                "output": ebook_export.get("output"),
                "included_article_count": ebook_export.get("included_article_count"),
                "raw_index_listed_article_count": ebook_export.get("raw_index_listed_article_count"),
                "not_raw_index_listed_article_count": ebook_export.get("not_raw_index_listed_article_count"),
                "embedded_asset_count": ebook_export.get("embedded_asset_count"),
                "missing_asset_count": len(ebook_export.get("missing_assets") or []),
                "unsupported_asset_count": len(ebook_export.get("unsupported_assets") or []),
                "suppressed_internal_resource_link_count": len(ebook_export.get("suppressed_internal_resource_links") or []),
                "unresolved_internal_link_count": len(ebook_unresolved),
                "validation_passed": bool(ebook_export.get("validation", {}).get("passed")),
                "local_package_reference_count": ebook_local_refs.get("local_reference_count"),
                "broken_package_reference_count": len(ebook_local_refs.get("broken_references") or []),
                "legacy_prewrapped_chapter_count": len(ebook_prewrap.get("chapters") or []),
                "hard_wrap_candidate_count": len(ebook_hard_wrap.get("chapters") or []),
                "visible_asset_id_caption_count": len(ebook_asset_id_captions.get("captions") or []),
                "epubcheck": epubcheck,
            },
        },
        "findings": findings,
        "finding_counts": {
            "blocking": sum(1 for finding in findings if finding["classification"] == "blocking"),
            "candidate": sum(1 for finding in findings if finding["classification"] == "candidate"),
            "deferred": sum(1 for finding in findings if finding["classification"] == "deferred"),
        },
        "open_questions": {
            "blocking": [],
            "routed": [],
            "deferred": [
                {
                    "question": "Should a DB import/export contract be defined?",
                    "reason": "Postponed until explicit user request.",
                },
                {
                    "question": "Should public URL redirects or canonical public URLs be assigned?",
                    "reason": "Deferred until a public rebuild or redirect-map slice.",
                },
                {
                    "question": "Should external epubcheck validation be required?",
                    "reason": "Deferred until epubcheck is installed locally or available in release tooling.",
                },
            ],
        },
        "recommended_next_slice": {
            "name": "EPUB external validation",
            "reason": "Release-facing static and EPUB behavior is aligned, unresolved internal EPUB links are now suppressed from reader-facing output, and the main remaining release gate is external epubcheck validation.",
        },
    }
    return report


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = "| " + " | ".join(rows[0]) + " |"
    divider = "| " + " | ".join("---" for _ in rows[0]) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join([header, divider, body])


def write_markdown(report: dict[str, Any], path: Path) -> None:
    outputs = report["outputs"]
    findings = report["findings"]
    rows = [
        ["Output", "Validation", "Main Counts", "Improvement Signal"],
        [
            "As-is static",
            "pass" if outputs["as_is_static"]["validation"]["passed"] else "fail",
            f"{outputs['as_is_static']['files_written']} files; {outputs['as_is_static']['validation']['local_reference_count']} local refs",
            f"{outputs['as_is_static']['silent_missing_internal_url_count']} suppressed internal URLs; {outputs['as_is_static']['pages_with_unresolved_local_rewrites']} unresolved-rewrite pages",
        ],
        [
            "Raw static",
            "pass" if outputs["raw_static"]["validation"]["passed"] else "fail",
            f"{outputs['raw_static']['article_count']} articles; {outputs['raw_static']['asset_count']} assets",
            f"{outputs['raw_static']['unplaced_article_count']} fallback articles; {outputs['raw_static']['missing_internal_reference_count']} missing artifacts",
        ],
        [
            "EPUB",
            "pass" if outputs["ebook"]["validation_passed"] else "fail",
            f"{outputs['ebook']['included_article_count']} chapters; {outputs['ebook']['embedded_asset_count']} assets",
            f"{outputs['ebook']['suppressed_internal_resource_link_count']} suppressed internal resource links; {outputs['ebook']['unresolved_internal_link_count']} unresolved internal links",
        ],
    ]

    finding_lines = []
    for finding in findings:
        finding_lines.append(
            f"- `{finding['classification']}` / `{finding['output']}`: {finding['title']} "
            f"({finding['evidence']}) Next: {finding['next_action']}"
        )

    output_path_lines = [
        f"- As-is static: `{outputs['as_is_static']['output']}`",
        f"- Raw static: `{outputs['raw_static']['output']}`",
        f"- EPUB: `{outputs['ebook']['output']}`",
    ]
    open_questions = report["open_questions"]
    routed_lines = [
        f"- {item['question']} Route: {item['route']}."
        for item in open_questions["routed"]
    ] or ["- None."]
    deferred_lines = [
        f"- {item['question']} {item['reason']}"
        for item in open_questions["deferred"]
    ] or ["- None."]

    body = f"""# Output Audit Report

Date: {report['generated_at'][:10]}

## Summary

{markdown_table(rows)}

Finding counts:

- Blocking: `{report['finding_counts']['blocking']}`
- Candidate: `{report['finding_counts']['candidate']}`
- Deferred: `{report['finding_counts']['deferred']}`

## Output Paths

{chr(10).join(output_path_lines)}

## Findings

{chr(10).join(finding_lines) if finding_lines else '- No findings.'}

## Open Questions

Blocking: none.

Routed:

{chr(10).join(routed_lines)}

Deferred:

{chr(10).join(deferred_lines)}

## Recommended Next Slice

{report['recommended_next_slice']['name']}

Reason: {report['recommended_next_slice']['reason']}

## Source Reports

- Raw reproduction: `{report['inputs']['raw_reproduction_report']}`
- Raw validation: `{report['inputs']['raw_validation_report']}`
- Canonical export: `{report['inputs']['canonical_export_report']}`
- Canonical validation: `{report['inputs']['canonical_validation_report']}`
- EPUB export: `{report['inputs']['ebook_export_report']}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-reproduction-report", default=str(DEFAULT_RAW_REPRODUCTION_REPORT))
    parser.add_argument("--raw-validation-report", default=str(DEFAULT_RAW_VALIDATION_REPORT))
    parser.add_argument("--canonical-export-report", default=str(DEFAULT_CANONICAL_EXPORT_REPORT))
    parser.add_argument("--canonical-validation-report", default=str(DEFAULT_CANONICAL_VALIDATION_REPORT))
    parser.add_argument("--ebook-export-report", default=str(DEFAULT_EBOOK_EXPORT_REPORT))
    parser.add_argument("--as-is-classification-report", default=str(DEFAULT_AS_IS_CLASSIFICATION_REPORT))
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--markdown-out", default=str(DEFAULT_MARKDOWN_OUT))
    args = parser.parse_args()

    report = build_audit(args)
    json_out = Path(args.json_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, Path(args.markdown_out))

    print(f"JSON report: {json_out}")
    print(f"Markdown report: {args.markdown_out}")
    print(f"Blocking findings: {report['finding_counts']['blocking']}")
    print(f"Candidate findings: {report['finding_counts']['candidate']}")
    print(f"Deferred findings: {report['finding_counts']['deferred']}")
    return 0 if report["finding_counts"]["blocking"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
