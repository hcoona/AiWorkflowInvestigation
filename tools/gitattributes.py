#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "gitattributes.pkl"
TARGET = ROOT / ".gitattributes"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def pkl_config() -> dict[str, Any]:
    completed = run(["pkl", "eval", "--root-dir", str(ROOT), "--format", "json", str(SOURCE)])
    if completed.returncode != 0:
        print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(completed.returncode)
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        print(f"{SOURCE.relative_to(ROOT)}: pkl did not render valid JSON: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(value, dict):
        print(f"{SOURCE.relative_to(ROOT)}: expected a JSON object", file=sys.stderr)
        raise SystemExit(1)
    return value


def string_list(config: dict[str, Any], key: str) -> list[str]:
    value = config.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        print(f"{SOURCE.relative_to(ROOT)}: {key} must be a list of non-empty strings", file=sys.stderr)
        raise SystemExit(1)
    duplicates = sorted({item for item in value if value.count(item) > 1})
    if duplicates:
        print(f"{SOURCE.relative_to(ROOT)}: {key} contains duplicate patterns: {', '.join(duplicates)}", file=sys.stderr)
        raise SystemExit(1)
    return value


def render(config: dict[str, Any]) -> str:
    header = string_list(config, "header")
    default_attributes = string_list(config, "defaultAttributes")
    text_patterns = string_list(config, "textPatterns")
    verbatim_patterns = string_list(config, "verbatimPatterns")
    binary_patterns = string_list(config, "binaryPatterns")

    overlap = sorted(set(text_patterns).intersection(binary_patterns))
    if overlap:
        print(
            f"{SOURCE.relative_to(ROOT)}: patterns cannot be both text and binary: {', '.join(overlap)}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    lines: list[str] = [f"# {line}" for line in header]
    lines.extend(default_attributes)
    lines.append("")
    lines.extend(f"{pattern} text" for pattern in text_patterns)
    if verbatim_patterns:
        lines.append("")
        lines.extend(f"{pattern} -text" for pattern in verbatim_patterns)
    if binary_patterns:
        lines.append("")
        lines.extend(f"{pattern} binary" for pattern in binary_patterns)
    lines.append("")
    return "\n".join(lines)


def matches_pattern(path: str, pattern: str) -> bool:
    if "/" in pattern:
        return fnmatch.fnmatchcase(path, pattern)
    return fnmatch.fnmatchcase(Path(path).name, pattern)


def listed_files() -> list[str]:
    completed = run(["git", "ls-files", "--cached", "-z"])
    if completed.returncode != 0:
        print(completed.stderr, end="", file=sys.stderr)
        raise SystemExit(completed.returncode)
    return sorted(path for path in completed.stdout.split("\0") if path)


def check_coverage(config: dict[str, Any]) -> bool:
    patterns = (
        string_list(config, "textPatterns")
        + string_list(config, "verbatimPatterns")
        + string_list(config, "binaryPatterns")
    )
    uncovered = [path for path in listed_files() if not any(matches_pattern(path, pattern) for pattern in patterns)]
    if not uncovered:
        return True

    print(
        "The following indexed files are not covered by gitattributes.pkl. "
        "Add a textPatterns or binaryPatterns entry before committing:",
        file=sys.stderr,
    )
    for path in uncovered:
        print(f"- {path}", file=sys.stderr)
    return False


def check() -> int:
    config = pkl_config()
    expected = render(config)
    actual = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
    ok = True
    if actual != expected:
        ok = False
        print(f"{TARGET.relative_to(ROOT)} is not generated from {SOURCE.relative_to(ROOT)}", file=sys.stderr)
        for line in difflib.unified_diff(
            actual.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile=str(TARGET.relative_to(ROOT)),
            tofile=f"{SOURCE.relative_to(ROOT)} (generated)",
        ):
            print(line, end="", file=sys.stderr)
    if not check_coverage(config):
        ok = False
    return 0 if ok else 1


def generate() -> int:
    TARGET.write_text(render(pkl_config()), encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or check .gitattributes from gitattributes.pkl.")
    parser.add_argument("command", choices=("check", "generate"))
    args = parser.parse_args()

    if args.command == "check":
        return check()
    return generate()


if __name__ == "__main__":
    raise SystemExit(main())
