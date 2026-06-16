#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "wiki",
    "wiki/overview.md",
    "wiki/log.jsonl",
    "wiki/_system/log-event.schema.json",
    "wiki/_templates/README.md",
    "wiki/_templates/sources/page.md",
    "wiki/_templates/analyses/answer-memo.md",
    "wiki/_templates/analyses/topic-faq.md",
    "wiki/_templates/analyses/decision-memo.md",
    "wiki/_templates/analyses/playbook-checklist.md",
    "wiki/_templates/entities/page.md",
    "wiki/_templates/concepts/page.md",
    "wiki/_templates/hubs/page.md",
    "wiki/analyses",
    "wiki/sources",
    "wiki/concepts",
    "wiki/entities",
    "wiki/hubs",
]

ALLOWED_PAGE_TYPES = {"source", "entity", "concept", "analysis", "overview", "hub"}
ALLOWED_STATUSES = {"seed", "active", "stale", "superseded", "archived"}
ALLOWED_EDIT_POLICIES = {"update", "reconcile", "supersede", "frozen"}
ALLOWED_BODY_CONTRACTS = {
    "analysis-answer-memo",
    "analysis-topic-faq",
    "analysis-decision-memo",
    "analysis-playbook-checklist",
    "source",
    "concept",
    "entity",
    "hub",
    "overview",
}
ALLOWED_FRONTMATTER_FIELDS = {
    "schema_version",
    "page_type",
    "title",
    "status",
    "created",
    "updated",
    "summary",
    "maintenance",
    "validation",
    "tags",
}
ALLOWED_EVIDENCE_TYPES = {"raw", "wiki", "external", "repo", "session", "user"}
PRIMARY_SOURCE_EVIDENCE_TYPES = {"raw", "external", "session", "user"}
BANNED_FRONTMATTER_FIELDS = {
    "depends_on",
    "used_by",
    "supersedes",
    "superseded_by",
    "evidence",
    "claims",
    "provenance",
    "confidence",
}
FORBIDDEN_DEPENDENCY_HEADINGS = {
    "Source pages and dependencies",
    "Known downstream dependencies",
    "来源页面与依赖关系",
    "已知下游依赖",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_error(errors: list[str], path: Path | str, message: str) -> None:
    errors.append(f"{path}: {message}")


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        add_error(errors, rel(path), f"must be UTF-8: {exc}")
        return ""


def durable_wiki_pages() -> list[Path]:
    pages: list[Path] = []
    for path in sorted((ROOT / "wiki").rglob("*.md")):
        if path.name == "AGENTS.md":
            continue
        parts = path.relative_to(ROOT / "wiki").parts
        if parts[0].startswith("_"):
            continue
        pages.append(path)
    return pages


def scalar_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", frontmatter, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if not value:
        return None
    return value.strip("\"'")


def nested_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^  {re.escape(key)}:\s*(.*?)\s*$", frontmatter, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if not value:
        return None
    return value.strip("\"'")


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[str, str]:
    text = read_text(path, errors)
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not match:
        add_error(errors, rel(path), "must start with YAML frontmatter delimited by ---")
        return "", text
    return match.group(1), match.group(2)


def check_required_paths(errors: list[str]) -> None:
    for required in REQUIRED_PATHS:
        path = ROOT / required
        if not path.exists():
            add_error(errors, required, "required path is missing")


def check_log_schema(errors: list[str]) -> None:
    schema_path = ROOT / "wiki/_system/log-event.schema.json"
    if not schema_path.exists():
        return
    try:
        json.loads(read_text(schema_path, errors))
    except json.JSONDecodeError as exc:
        add_error(errors, rel(schema_path), f"must contain valid JSON: {exc}")


def check_log_jsonl(errors: list[str]) -> None:
    path = ROOT / "wiki/log.jsonl"
    if not path.exists():
        return
    event_ids: set[str] = set()
    for line_number, line in enumerate(read_text(path, errors).splitlines(), start=1):
        if not line.strip():
            add_error(errors, f"{rel(path)}:{line_number}", "blank lines are not allowed")
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            add_error(errors, f"{rel(path)}:{line_number}", f"must be valid JSON: {exc}")
            continue

        for key in ("schema_version", "id", "timestamp", "type", "summary", "changed_paths"):
            if key not in event:
                add_error(errors, f"{rel(path)}:{line_number}", f"missing required field {key!r}")

        event_id = event.get("id")
        if isinstance(event_id, str):
            if event_id in event_ids:
                add_error(errors, f"{rel(path)}:{line_number}", f"duplicate event id {event_id!r}")
            event_ids.add(event_id)
        else:
            add_error(errors, f"{rel(path)}:{line_number}", "field 'id' must be a string")

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, str) or not re.match(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$", timestamp
        ):
            add_error(errors, f"{rel(path)}:{line_number}", "field 'timestamp' must be UTC ISO-8601 ending in Z")

        changed_paths = event.get("changed_paths")
        if not isinstance(changed_paths, list) or not all(isinstance(item, str) for item in changed_paths):
            add_error(errors, f"{rel(path)}:{line_number}", "field 'changed_paths' must be a list of strings")
        elif not changed_paths:
            add_error(errors, f"{rel(path)}:{line_number}", "field 'changed_paths' must contain at least one path")
        else:
            for changed_path in changed_paths:
                if changed_path.startswith("/") or changed_path.startswith("../") or "/../" in changed_path:
                    add_error(errors, f"{rel(path)}:{line_number}", f"changed path must be relative: {changed_path!r}")
                if not changed_path.startswith("wiki/"):
                    add_error(errors, f"{rel(path)}:{line_number}", f"changed path must stay under wiki/: {changed_path!r}")


def check_frontmatter(path: Path, frontmatter: str, errors: list[str]) -> None:
    required_scalars = ["schema_version", "page_type", "title", "status", "created", "updated", "summary"]
    for key in required_scalars:
        if scalar_value(frontmatter, key) is None:
            add_error(errors, rel(path), f"missing non-empty frontmatter field {key!r}")

    if not re.search(r"^maintenance:\s*$", frontmatter, re.MULTILINE):
        add_error(errors, rel(path), "missing frontmatter object 'maintenance'")
    if not re.search(r"^validation:\s*$", frontmatter, re.MULTILINE):
        add_error(errors, rel(path), "missing frontmatter object 'validation'")
    if not re.search(r"^tags:\s*\n(?:  - .+\n?)+", frontmatter, re.MULTILINE):
        add_error(errors, rel(path), "frontmatter field 'tags' must contain at least one list item")

    schema_version = scalar_value(frontmatter, "schema_version")
    if schema_version != "2":
        add_error(errors, rel(path), "schema_version must be 2")

    page_type = scalar_value(frontmatter, "page_type")
    if page_type not in ALLOWED_PAGE_TYPES:
        add_error(errors, rel(path), f"page_type must be one of {sorted(ALLOWED_PAGE_TYPES)}")

    status = scalar_value(frontmatter, "status")
    if status not in ALLOWED_STATUSES:
        add_error(errors, rel(path), f"status must be one of {sorted(ALLOWED_STATUSES)}")

    for key in ("created", "updated"):
        value = scalar_value(frontmatter, key)
        if value is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            add_error(errors, rel(path), f"{key} must use YYYY-MM-DD")

    edit_policy = nested_value(frontmatter, "edit_policy")
    if edit_policy not in ALLOWED_EDIT_POLICIES:
        add_error(errors, rel(path), f"maintenance.edit_policy must be one of {sorted(ALLOWED_EDIT_POLICIES)}")

    body_contract = nested_value(frontmatter, "body_contract")
    if body_contract not in ALLOWED_BODY_CONTRACTS:
        add_error(errors, rel(path), f"validation.body_contract must be one of {sorted(ALLOWED_BODY_CONTRACTS)}")

    if page_type == "analysis" and body_contract and not body_contract.startswith("analysis-"):
        add_error(errors, rel(path), "analysis pages must use an analysis-* body contract")
    elif page_type and page_type != "analysis" and body_contract and body_contract != page_type:
        add_error(errors, rel(path), "non-analysis pages must match page_type and validation.body_contract")

    for banned in sorted(BANNED_FRONTMATTER_FIELDS):
        if re.search(rf"^{re.escape(banned)}:", frontmatter, re.MULTILINE):
            add_error(errors, rel(path), f"frontmatter must not contain body-provenance field {banned!r}")

    top_level_fields = {
        match.group(1)
        for match in re.finditer(r"^([A-Za-z_][A-Za-z0-9_]*):", frontmatter, re.MULTILINE)
    }
    for field in sorted(top_level_fields - ALLOWED_FRONTMATTER_FIELDS):
        add_error(errors, rel(path), f"unexpected top-level frontmatter field {field!r}")


def check_h1_free(path: Path, body: str, errors: list[str]) -> None:
    in_fence = False
    for line_number, line in enumerate(body.splitlines(), start=1):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#\s+", line):
            add_error(errors, f"{rel(path)} body line {line_number}", "durable wiki bodies must not contain H1 headings")


def check_body_provenance(path: Path, body: str, errors: list[str]) -> None:
    section = "## 证据与限制"
    index = body.find(section)
    if index == -1:
        add_error(errors, rel(path), f"missing final {section!r} section")
        return

    appendix = body[index:]
    if re.search(r"^##\s+", appendix[len(section) :], re.MULTILINE):
        add_error(errors, rel(path), f"{section!r} must be the final level-2 section")

    for heading in ("### 证据单元", "### 支撑的主张"):
        heading_index = appendix.find(heading)
        if heading_index == -1:
            add_error(errors, rel(path), f"missing {heading!r} table")
            continue
        rest = appendix[heading_index:]
        next_heading = rest.find("\n### ", 1)
        subsection = rest if next_heading == -1 else rest[:next_heading]
        if not re.search(r"^\|.+\|\n\|\s*:?-{3,}:?\s*\|", subsection, re.MULTILINE):
            add_error(errors, rel(path), f"{heading!r} must contain a Markdown table")


def evidence_unit_types(body: str) -> list[str]:
    section = "## 证据与限制"
    section_index = body.find(section)
    if section_index == -1:
        return []

    appendix = body[section_index:]
    heading = "### 证据单元"
    heading_index = appendix.find(heading)
    if heading_index == -1:
        return []

    rest = appendix[heading_index:]
    next_heading = rest.find("\n### ", 1)
    subsection = rest if next_heading == -1 else rest[:next_heading]

    types: list[str] = []
    for line in subsection.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "类型" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells:
            types.append(cells[0].strip("`"))
    return types


def check_evidence_units(path: Path, frontmatter: str, body: str, errors: list[str]) -> None:
    types = evidence_unit_types(body)
    for evidence_type in types:
        if evidence_type not in ALLOWED_EVIDENCE_TYPES:
            add_error(
                errors,
                rel(path),
                f"evidence unit type must be one of {sorted(ALLOWED_EVIDENCE_TYPES)}: {evidence_type!r}",
            )

    if scalar_value(frontmatter, "page_type") == "source" and not any(
        evidence_type in PRIMARY_SOURCE_EVIDENCE_TYPES for evidence_type in types
    ):
        add_error(
            errors,
            rel(path),
            "source pages must include at least one primary evidence unit of type "
            f"{sorted(PRIMARY_SOURCE_EVIDENCE_TYPES)}",
        )


def check_forbidden_dependency_sections(path: Path, body: str, errors: list[str]) -> None:
    for heading in sorted(FORBIDDEN_DEPENDENCY_HEADINGS):
        if re.search(rf"^#+\s+{re.escape(heading)}\s*$", body, re.MULTILINE):
            add_error(errors, rel(path), f"forbidden manual dependency section {heading!r}")


def check_links(path: Path, body: str, errors: list[str]) -> None:
    for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", body):
        target = target.strip()
        if not target or target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target):
            continue
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        resolved = (path.parent / path_part).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            add_error(errors, rel(path), f"link escapes repository root: {target}")
            continue
        if not resolved.exists():
            add_error(errors, rel(path), f"broken relative link: {target}")


def check_durable_pages(errors: list[str]) -> None:
    for path in durable_wiki_pages():
        frontmatter, body = parse_frontmatter(path, errors)
        check_frontmatter(path, frontmatter, errors)
        check_h1_free(path, body, errors)
        check_body_provenance(path, body, errors)
        check_evidence_units(path, frontmatter, body, errors)
        check_forbidden_dependency_sections(path, body, errors)
        check_links(path, body, errors)


def main() -> int:
    errors: list[str] = []
    check_required_paths(errors)
    check_log_schema(errors)
    check_log_jsonl(errors)
    check_durable_pages(errors)

    if errors:
        print("wiki-check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("wiki-check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
