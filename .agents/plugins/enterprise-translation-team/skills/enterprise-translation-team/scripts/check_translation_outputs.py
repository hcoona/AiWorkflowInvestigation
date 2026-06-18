#!/usr/bin/env python
"""Validate enterprise translation skill eval outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_CATEGORIES = {
    "Accuracy",
    "Fluency",
    "Terminology",
    "Style",
    "Locale",
    "Non-translation",
}
ALLOWED_SEVERITIES = {"Major", "Minor", "Neutral"}
TERM_HEADER = "source_term\ttarget_term\tstatus\tnotes"


def load_eval_case(evals_path: Path, case_id: str) -> dict:
    data = json.loads(evals_path.read_text(encoding="utf-8"))
    for case in data.get("evals", []):
        if case.get("id") == case_id:
            return case
    raise ValueError(f"Unknown eval case: {case_id}")


def require_file(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"Missing expected file: {path}")
    if not path.is_file():
        raise AssertionError(f"Expected a file, got: {path}")
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise AssertionError(f"Expected non-empty file: {path}")
    return content


def check_review_json(path: Path) -> None:
    payload = json.loads(require_file(path))
    issues = payload.get("issues")
    if not isinstance(issues, list):
        raise AssertionError("review.json must contain an issues array")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("review.json must contain a summary object")
    required = {
        "segment_id",
        "category",
        "severity",
        "source_quote",
        "target_quote",
        "explanation",
        "proposed_fix",
    }
    for index, issue in enumerate(issues, start=1):
        missing = required.difference(issue)
        if missing:
            raise AssertionError(
                f"review.json issue {index} is missing fields: {sorted(missing)}"
            )
        if issue["category"] not in ALLOWED_CATEGORIES:
            raise AssertionError(
                f"review.json issue {index} has invalid category: {issue['category']}"
            )
        if issue["severity"] not in ALLOWED_SEVERITIES:
            raise AssertionError(
                f"review.json issue {index} has invalid severity: {issue['severity']}"
            )
        for field in required:
            if not str(issue[field]).strip():
                raise AssertionError(
                    f"review.json issue {index} has empty field: {field}"
                )
    expected_counts = {
        "major": sum(1 for issue in issues if issue["severity"] == "Major"),
        "minor": sum(1 for issue in issues if issue["severity"] == "Minor"),
        "neutral": sum(1 for issue in issues if issue["severity"] == "Neutral"),
    }
    for key, expected in expected_counts.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"review.json summary.{key} must be {expected}, got {summary.get(key)!r}"
            )


def check_terminology_tsv(path: Path) -> None:
    content = require_file(path)
    first_line = content.splitlines()[0] if content.splitlines() else ""
    if first_line != TERM_HEADER:
        raise AssertionError(
            f"terminology.tsv header must be {TERM_HEADER!r}, got {first_line!r}"
        )


def require_contains(content: str, needle: str, label: str) -> None:
    if needle not in content:
        raise AssertionError(f"{label} must contain {needle!r}")


def check_markdown(path: Path) -> None:
    content = require_file(path)
    if "TODO" in content:
        raise AssertionError(f"Markdown output contains TODO marker: {path}")
    if path.name == "qa.md" and "Files checked" not in content:
        raise AssertionError("qa.md must include a 'Files checked' section")


def check_structured_translation(path: Path) -> None:
    content = require_file(path)
    for protected in [
        "`v2.4.0`",
        "{customer_id}",
        "https://example.com/admin",
        "`region`",
        "`featureFlag`",
        '"featureFlag": "translation-preview"',
    ]:
        require_contains(content, protected, "translation.md")
    if "| --- | --- |" not in content:
        raise AssertionError("translation.md must preserve the source table shape")
    if "```json" not in content:
        raise AssertionError("translation.md must preserve the JSON code fence")
    if "产品发布说明" in content or "目标部署区域" in content:
        raise AssertionError("translation.md contains untranslated Chinese prose")


def check_terminology_content(path: Path) -> None:
    content = require_file(path)
    statuses = {line.split("\t")[2] for line in content.splitlines()[1:] if "\t" in line}
    for status in ["conflict", "forbidden", "needs-confirmation"]:
        if status not in statuses:
            raise AssertionError(f"terminology.tsv must include a {status} entry")
    for forbidden in ["gray release", "grayscale release"]:
        require_contains(content, forbidden, "terminology.tsv")


def check_mqm_content(path: Path) -> None:
    payload = json.loads(require_file(path))
    issues = payload["issues"]
    if not any(issue["severity"] == "Major" for issue in issues):
        raise AssertionError("review.json must include at least one Major issue")
    if not any(issue["category"] in {"Accuracy", "Terminology"} for issue in issues):
        raise AssertionError("review.json must include Accuracy or Terminology issues")


def check_qa_content(path: Path) -> None:
    content = require_file(path)
    lowered = content.casefold()
    for required in ["files checked", "major"]:
        if required not in lowered:
            raise AssertionError(f"qa.md must mention {required!r}")
    if "human" not in lowered and "subject-matter" not in lowered:
        raise AssertionError("qa.md must call out human or subject-matter review")


def check_case_specific(case_id: str, outputs: Path) -> None:
    if case_id == "structured-markdown-translation":
        check_structured_translation(outputs / "translation.md")
    elif case_id == "terminology-glossary-conflict":
        check_terminology_content(outputs / "terminology.tsv")
    elif case_id == "mqm-review-json":
        check_mqm_content(outputs / "review.json")
    elif case_id == "final-qa-contract":
        check_qa_content(outputs / "qa.md")


def check_forbidden_paths(case: dict, run_dir: Path | None) -> None:
    if run_dir is None:
        if case.get("forbidden_created_paths"):
            raise AssertionError("--run-dir is required for forbidden path checks")
        return
    for relative in case.get("forbidden_created_paths", []):
        forbidden = run_dir / relative
        if forbidden.exists():
            raise AssertionError(f"Forbidden path was created: {forbidden}")


def check_response_patterns(case: dict, response_path: Path | None) -> None:
    required = case.get("required_response_patterns", [])
    forbidden = case.get("forbidden_response_patterns", [])
    if not required and not forbidden:
        return
    if response_path is None:
        raise AssertionError("--response is required for response pattern checks")
    response = response_path.read_text(encoding="utf-8").casefold()
    for pattern in required:
        if pattern.casefold() not in response:
            raise AssertionError(f"Required response pattern not found: {pattern}")
    for pattern in forbidden:
        if pattern.casefold() in response:
            raise AssertionError(f"Forbidden response pattern found: {pattern}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate expected files for an enterprise translation eval case."
    )
    parser.add_argument("--evals", required=True, type=Path, help="Path to evals.json")
    parser.add_argument("--case", required=True, help="Eval case id")
    parser.add_argument("--outputs", required=True, type=Path, help="Output directory")
    parser.add_argument("--run-dir", type=Path, help="Eval run directory")
    parser.add_argument("--response", type=Path, help="Agent response text file")
    args = parser.parse_args(argv)

    case = load_eval_case(args.evals, args.case)
    if not (
        case.get("expected_files")
        or case.get("forbidden_created_paths")
        or case.get("required_response_patterns")
        or case.get("forbidden_response_patterns")
    ):
        raise AssertionError(f"Eval {case['id']} has no objective checks")
    outputs = args.outputs
    for expected in case.get("expected_files", []):
        path = outputs / expected
        if expected == "review.json":
            check_review_json(path)
        elif expected == "terminology.tsv":
            check_terminology_tsv(path)
        elif expected.endswith(".md"):
            check_markdown(path)
        else:
            require_file(path)
    check_case_specific(case["id"], outputs)
    check_forbidden_paths(case, args.run_dir)
    check_response_patterns(case, args.response)

    print(
        json.dumps(
            {"case": case["id"], "checked_files": case.get("expected_files", [])},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
