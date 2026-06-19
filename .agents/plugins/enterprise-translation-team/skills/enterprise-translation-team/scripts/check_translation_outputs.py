#!/usr/bin/env python
"""Validate enterprise translation skill eval outputs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
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
ALLOWED_TERM_STATUSES = {
    "approved",
    "candidate",
    "conflict",
    "forbidden",
    "needs_confirmation",
    "deprecated",
    "rejected",
}
ALLOWED_DELTA_OPS = {
    "propose_term",
    "approve_term",
    "reject_term",
    "add_forbidden",
    "raise_conflict",
    "resolve_conflict",
    "add_document_override",
    "waive_term_violation",
    "promote_to_global",
    "supersede_entry",
}
ALLOWED_TBX_ADMIN_STATUSES = {
    "admittedTerm-admn-sts",
    "deprecatedTerm-admn-sts",
    "preferredTerm-admn-sts",
    "supersededTerm-admn-sts",
}
ALLOWED_TBX_PARTS_OF_SPEECH = {
    "abbreviation",
    "acronym",
    "adjective",
    "adverb",
    "conjunction",
    "interjection",
    "noun",
    "numeral",
    "particle",
    "phrase",
    "preposition",
    "pronoun",
    "properNoun",
    "verb",
}
ALLOWED_TBX_TERM_NOTE_TYPES = {"administrativeStatus", "partOfSpeech", "termType"}
ALLOWED_TBX_TERM_TYPES = {
    "acronym",
    "abbreviation",
    "fullForm",
    "phrase",
    "shortForm",
    "variant",
}
TBX_NAMESPACE = "urn:iso:std:iso:30042:ed-2"
TERM_REVIEW_HEADER = (
    "concept_id\tentry_id\tscope\tstatus\tsource_term\tpreferred_target\t"
    "allowed_variants\tforbidden_targets\tcontext_note\tpositive_example\t"
    "negative_example\tconflict_id\tblocking\tevidence_refs"
)


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


def require_dict(payload: object, label: str) -> dict:
    if not isinstance(payload, dict):
        raise AssertionError(f"{label} must be an object")
    return payload


def require_list(payload: object, label: str) -> list:
    if not isinstance(payload, list):
        raise AssertionError(f"{label} must be an array")
    return payload


def require_nonempty_string(payload: object, label: str) -> str:
    if not isinstance(payload, str) or not payload.strip():
        raise AssertionError(f"{label} must be a non-empty string")
    return payload


def check_bcp47(value: object, label: str) -> None:
    text = require_nonempty_string(value, label)
    if not all(part and part.replace("-", "").isalnum() for part in text.split("-")):
        raise AssertionError(f"{label} must look like a BCP-47 language tag: {text!r}")


def split_tsv_list(value: str) -> set[str]:
    return {item.strip() for item in value.split(";") if item.strip()}


def entry_scope_text(entry: dict) -> str:
    scope = require_dict(entry.get("scope"), f"{entry.get('concept_id', '<unknown>')}.scope")
    parts = [require_nonempty_string(scope.get("level"), "scope.level")]
    for key in ["client_id", "domain", "project_id", "document_id"]:
        value = scope.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    return ":".join(parts[:2]) + ("/" + "/".join(parts[2:]) if len(parts) > 2 else "")


def entry_target_terms(entry: dict) -> set[str]:
    target = require_dict(entry.get("target"), f"{entry.get('concept_id', '<unknown>')}.target")
    terms = {require_nonempty_string(target.get("preferred"), "target.preferred")}
    terms.update(
        require_nonempty_string(term, "target.allowed_variants[]")
        for term in require_list(target.get("allowed_variants", []), "target.allowed_variants")
    )
    for forbidden in require_list(target.get("forbidden", []), "target.forbidden"):
        forbidden_entry = require_dict(forbidden, "target.forbidden[]")
        terms.add(require_nonempty_string(forbidden_entry.get("term"), "forbidden.term"))
    return terms


def first_example_text(context: dict, key: str, fields: list[str]) -> str:
    examples = require_list(context.get(key), f"context.{key}")
    example = require_dict(examples[0], f"context.{key}[0]")
    for field in fields:
        value = example.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise AssertionError(f"context.{key}[0] must include one of {fields}")


def conflicts_by_concept(termbase: dict) -> dict[str, list[dict]]:
    conflicts: dict[str, list[dict]] = {}
    for conflict in require_list(termbase.get("conflicts", []), "conflicts"):
        conflict_entry = require_dict(conflict, "conflicts[]")
        concept_id = require_nonempty_string(conflict_entry.get("concept_id"), "conflict.concept_id")
        conflicts.setdefault(concept_id, []).append(conflict_entry)
    return conflicts


def entry_is_blocking(entry: dict, concept_conflicts: list[dict]) -> bool:
    status = require_nonempty_string(entry.get("status"), "entry.status")
    if status in {"candidate", "conflict", "needs_confirmation"}:
        return True
    if any(conflict.get("blocking") is True for conflict in concept_conflicts):
        return True
    target = require_dict(entry.get("target"), "entry.target")
    for forbidden in require_list(target.get("forbidden", []), "target.forbidden"):
        forbidden_entry = require_dict(forbidden, "target.forbidden[]")
        if forbidden_entry.get("severity") == "blocking":
            return True
    return False


def check_terminology_review_tsv(path: Path, termbase: dict | None = None) -> None:
    content = require_file(path)
    lines = content.splitlines()
    first_line = lines[0] if lines else ""
    if first_line != TERM_REVIEW_HEADER:
        raise AssertionError(
            f"terminology-review.tsv header must be {TERM_REVIEW_HEADER!r}, "
            f"got {first_line!r}"
        )
    rows = list(csv.DictReader(lines, delimiter="\t"))
    if termbase is None:
        if not rows:
            raise AssertionError("terminology-review.tsv must include at least one data row")
        return
    entries = require_list(termbase.get("entries"), "entries")
    if len(rows) < len(entries):
        raise AssertionError("terminology-review.tsv must include at least one row per termbase entry")
    rows_by_entry = {row.get("entry_id"): row for row in rows}
    conflicts = conflicts_by_concept(termbase)
    for entry in entries:
        entry_id = require_nonempty_string(entry.get("entry_id"), "entry_id")
        concept_id = require_nonempty_string(entry.get("concept_id"), "concept_id")
        row = rows_by_entry.get(entry_id)
        if row is None:
            raise AssertionError(f"terminology-review.tsv missing row for entry_id {entry_id}")
        if row.get("concept_id") != concept_id:
            raise AssertionError(f"terminology-review.tsv row {entry_id} has wrong concept_id")
        if row.get("scope") != entry_scope_text(entry):
            raise AssertionError(f"terminology-review.tsv row {entry_id} has wrong scope")
        if row.get("status") != entry.get("status"):
            raise AssertionError(f"terminology-review.tsv row {entry_id} has wrong status")
        source = require_dict(entry.get("source"), f"{entry_id}.source")
        target = require_dict(entry.get("target"), f"{entry_id}.target")
        context = require_dict(entry.get("context"), f"{entry_id}.context")
        provenance = require_dict(entry.get("provenance"), f"{entry_id}.provenance")
        if row.get("source_term") != source.get("term"):
            raise AssertionError(f"terminology-review.tsv row {entry_id} has wrong source_term")
        if row.get("preferred_target") != target.get("preferred"):
            raise AssertionError(f"terminology-review.tsv row {entry_id} has wrong preferred_target")
        allowed = set(require_list(target.get("allowed_variants", []), "target.allowed_variants"))
        if split_tsv_list(row.get("allowed_variants", "")) != allowed:
            raise AssertionError(f"terminology-review.tsv row {entry_id} allowed_variants mismatch")
        forbidden = {
            require_nonempty_string(item.get("term"), "forbidden.term")
            for item in require_list(target.get("forbidden", []), "target.forbidden")
        }
        if split_tsv_list(row.get("forbidden_targets", "")) != forbidden:
            raise AssertionError(f"terminology-review.tsv row {entry_id} forbidden_targets mismatch")
        for field in ["context_note", "positive_example", "negative_example", "evidence_refs"]:
            if not row.get(field, "").strip():
                raise AssertionError(f"terminology-review.tsv row {entry_id} missing {field}")
        context_note = context.get("usage_note") or context.get("definition")
        if row.get("context_note") != context_note:
            raise AssertionError(f"terminology-review.tsv row {entry_id} context_note mismatch")
        if row.get("positive_example") != first_example_text(context, "positive_examples", ["target"]):
            raise AssertionError(f"terminology-review.tsv row {entry_id} positive_example mismatch")
        if row.get("negative_example") != first_example_text(
            context,
            "negative_examples",
            ["correct_guidance", "reason", "bad_target"],
        ):
            raise AssertionError(f"terminology-review.tsv row {entry_id} negative_example mismatch")
        evidence_refs = set(require_list(provenance.get("evidence_refs"), "provenance.evidence_refs"))
        if not evidence_refs.issubset(split_tsv_list(row.get("evidence_refs", ""))):
            raise AssertionError(f"terminology-review.tsv row {entry_id} evidence_refs mismatch")
        if not require_list(context.get("positive_examples"), "context.positive_examples"):
            raise AssertionError(f"termbase entry {entry_id} missing positive examples")
        if not require_list(context.get("negative_examples"), "context.negative_examples"):
            raise AssertionError(f"termbase entry {entry_id} missing negative examples")
        entry_conflicts = conflicts.get(concept_id, [])
        expected_conflict_ids = {
            require_nonempty_string(conflict.get("conflict_id"), "conflict.conflict_id")
            for conflict in entry_conflicts
        }
        row_conflict_id = row.get("conflict_id", "").strip()
        if expected_conflict_ids and row_conflict_id not in expected_conflict_ids:
            raise AssertionError(f"terminology-review.tsv row {entry_id} conflict_id mismatch")
        if not expected_conflict_ids and row_conflict_id:
            raise AssertionError(f"terminology-review.tsv row {entry_id} has unexpected conflict_id")
        expected_blocking = "true" if entry_is_blocking(entry, entry_conflicts) else "false"
        if row.get("blocking") != expected_blocking:
            raise AssertionError(f"terminology-review.tsv row {entry_id} blocking mismatch")


def check_termbase_json(path: Path) -> dict:
    payload = require_dict(json.loads(require_file(path)), "termbase.job.json")
    if payload.get("schema_version") != "enterprise-termbase-v2":
        raise AssertionError("termbase.job.json schema_version must be enterprise-termbase-v2")
    check_bcp47(payload.get("source_locale"), "source_locale")
    check_bcp47(payload.get("target_locale"), "target_locale")
    standard = require_dict(payload.get("standard_basis"), "standard_basis")
    if "TBX" not in require_nonempty_string(standard.get("primary"), "standard_basis.primary"):
        raise AssertionError("standard_basis.primary must reference TBX")
    entries = require_list(payload.get("entries"), "entries")
    if not entries:
        raise AssertionError("termbase.job.json must include at least one entry")
    seen_concepts: set[str] = set()
    statuses: set[str] = set()
    forbidden_terms: list[str] = []
    for index, raw_entry in enumerate(entries, start=1):
        entry = require_dict(raw_entry, f"entries[{index}]")
        concept_id = require_nonempty_string(entry.get("concept_id"), f"entries[{index}].concept_id")
        if concept_id in seen_concepts:
            raise AssertionError(f"Duplicate concept_id: {concept_id}")
        seen_concepts.add(concept_id)
        require_nonempty_string(entry.get("entry_id"), f"entries[{index}].entry_id")
        status = require_nonempty_string(entry.get("status"), f"entries[{index}].status")
        if status not in ALLOWED_TERM_STATUSES:
            raise AssertionError(f"Invalid term status: {status}")
        statuses.add(status)
        scope = require_dict(entry.get("scope"), f"entries[{index}].scope")
        require_nonempty_string(scope.get("level"), f"entries[{index}].scope.level")
        source = require_dict(entry.get("source"), f"entries[{index}].source")
        target = require_dict(entry.get("target"), f"entries[{index}].target")
        require_nonempty_string(source.get("term"), f"entries[{index}].source.term")
        part_of_speech = require_nonempty_string(
            source.get("part_of_speech"),
            f"entries[{index}].source.part_of_speech",
        )
        if part_of_speech not in ALLOWED_TBX_PARTS_OF_SPEECH:
            raise AssertionError(
                f"Entry {concept_id} part_of_speech is not TBX-Basic compatible: {part_of_speech}"
            )
        term_type = require_nonempty_string(source.get("term_type"), f"entries[{index}].source.term_type")
        if term_type not in ALLOWED_TBX_TERM_TYPES:
            raise AssertionError(f"Entry {concept_id} term_type is not TBX-Basic compatible: {term_type}")
        require_nonempty_string(target.get("preferred"), f"entries[{index}].target.preferred")
        check_bcp47(source.get("language"), f"entries[{index}].source.language")
        check_bcp47(target.get("language"), f"entries[{index}].target.language")
        context = require_dict(entry.get("context"), f"entries[{index}].context")
        require_nonempty_string(context.get("definition"), f"entries[{index}].context.definition")
        positive = require_list(
            context.get("positive_examples"),
            f"entries[{index}].context.positive_examples",
        )
        negative = require_list(
            context.get("negative_examples"),
            f"entries[{index}].context.negative_examples",
        )
        if status == "approved" and (not positive or not negative):
            raise AssertionError(
                f"Approved entry {concept_id} must include positive and negative examples"
            )
        for forbidden in require_list(target.get("forbidden", []), f"entries[{index}].target.forbidden"):
            forbidden_entry = require_dict(forbidden, f"entries[{index}].target.forbidden[]")
            forbidden_terms.append(
                require_nonempty_string(forbidden_entry.get("term"), "forbidden.term")
            )
            require_nonempty_string(forbidden_entry.get("reason"), "forbidden.reason")
        provenance = require_dict(entry.get("provenance"), f"entries[{index}].provenance")
        require_nonempty_string(
            provenance.get("created_by"),
            f"entries[{index}].provenance.created_by",
        )
        if not require_list(provenance.get("evidence_refs"), f"entries[{index}].provenance.evidence_refs"):
            raise AssertionError(f"Entry {concept_id} must include evidence_refs")
        maintenance = require_dict(entry.get("maintenance"), f"entries[{index}].maintenance")
        require_nonempty_string(
            maintenance.get("approval_status"),
            f"entries[{index}].maintenance.approval_status",
        )
        reliability = require_dict(
            maintenance.get("reliability"),
            f"entries[{index}].maintenance.reliability",
        )
        if not isinstance(reliability.get("code"), int):
            raise AssertionError(f"Entry {concept_id} reliability.code must be an integer")
    payload["_checked_statuses"] = sorted(statuses)
    payload["_checked_forbidden_terms"] = forbidden_terms
    return payload


def check_delta_jsonl(path: Path) -> list[dict]:
    lines = [line for line in require_file(path).splitlines() if line.strip()]
    if not lines:
        raise AssertionError("termbase.delta.jsonl must include at least one event")
    events = []
    for index, line in enumerate(lines, start=1):
        event = require_dict(json.loads(line), f"termbase.delta.jsonl line {index}")
        events.append(event)
        op = require_nonempty_string(event.get("op"), f"line {index}.op")
        if op not in ALLOWED_DELTA_OPS:
            raise AssertionError(f"Invalid delta op on line {index}: {op}")
        for field in ["event_id", "job_id", "doc_id", "scope", "evidence_ref", "submitted_by", "status"]:
            if field not in event:
                raise AssertionError(f"Delta line {index} missing {field}")
        if "concept_id" not in event and "source_term" not in event:
            raise AssertionError(f"Delta line {index} must include concept_id or source_term")
    return events


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def namespace_uri(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def require_descendant(root: ET.Element, name: str, label: str) -> None:
    if not any(local_name(element.tag) == name for element in root.iter()):
        raise AssertionError(f"{label} must include {name}")


def check_tbx(path: Path, termbase: dict | None = None) -> None:
    root = ET.fromstring(require_file(path))
    if local_name(root.tag) != "tbx":
        raise AssertionError("termbase.tbx root element must be tbx")
    if namespace_uri(root.tag) != TBX_NAMESPACE:
        raise AssertionError(f"termbase.tbx root namespace must be {TBX_NAMESPACE}")
    if root.get("type") != "TBX-Basic":
        raise AssertionError("termbase.tbx type must be TBX-Basic")
    if root.get("style") not in {"dca", "dct"}:
        raise AssertionError("termbase.tbx style must be dca or dct")
    require_descendant(root, "tbxHeader", "termbase.tbx")
    require_descendant(root, "fileDesc", "termbase.tbx")
    require_descendant(root, "sourceDesc", "termbase.tbx")
    require_descendant(root, "text", "termbase.tbx")
    require_descendant(root, "body", "termbase.tbx")
    concepts = [element for element in root.iter() if local_name(element.tag) == "conceptEntry"]
    if not concepts:
        raise AssertionError("termbase.tbx must include conceptEntry")
    lang_secs = [element for element in root.iter() if local_name(element.tag) == "langSec"]
    term_secs = [element for element in root.iter() if local_name(element.tag) == "termSec"]
    terms = [element for element in root.iter() if local_name(element.tag) == "term"]
    if not lang_secs or not term_secs or not terms:
        raise AssertionError("termbase.tbx must include langSec, termSec, and term")
    for term_note in [element for element in root.iter() if local_name(element.tag) == "termNote"]:
        note_type = term_note.get("type")
        value = (term_note.text or "").strip()
        if note_type not in ALLOWED_TBX_TERM_NOTE_TYPES:
            raise AssertionError(f"Invalid TBX-Basic termNote type: {note_type!r}")
        if note_type == "partOfSpeech" and value not in ALLOWED_TBX_PARTS_OF_SPEECH:
            raise AssertionError(f"Invalid TBX-Basic partOfSpeech value: {value!r}")
        if note_type == "administrativeStatus" and value not in ALLOWED_TBX_ADMIN_STATUSES:
            raise AssertionError(f"Invalid TBX-Basic administrativeStatus value: {value!r}")
        if note_type == "termType" and value not in ALLOWED_TBX_TERM_TYPES:
            raise AssertionError(f"Invalid TBX-Basic termType value: {value!r}")
    if termbase is None:
        return
    concepts_by_id = {
        require_nonempty_string(concept.get("id"), "conceptEntry.id"): concept
        for concept in concepts
    }
    for entry in require_list(termbase.get("entries"), "entries"):
        concept_id = require_nonempty_string(entry.get("concept_id"), "entry.concept_id")
        concept = concepts_by_id.get(concept_id)
        if concept is None:
            raise AssertionError(f"termbase.tbx missing conceptEntry {concept_id}")
        concept_terms = {
            (term.text or "").strip()
            for term in concept.iter()
            if local_name(term.tag) == "term" and (term.text or "").strip()
        }
        source = require_dict(entry.get("source"), f"{concept_id}.source")
        required_terms = {require_nonempty_string(source.get("term"), "source.term")}
        required_terms.update(entry_target_terms(entry))
        missing = required_terms.difference(concept_terms)
        if missing:
            raise AssertionError(
                f"termbase.tbx conceptEntry {concept_id} missing canonical terms: {sorted(missing)}"
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


def check_terminology_content(path: Path, delta_path: Path) -> dict:
    payload = check_termbase_json(path)
    if "approved" not in payload["_checked_statuses"]:
        raise AssertionError("termbase.job.json must include an approved entry")
    if not {"conflict", "needs_confirmation"}.intersection(payload["_checked_statuses"]):
        raise AssertionError(
            "termbase.job.json must represent glossary conflicts as conflict or needs_confirmation"
        )
    conflicts = require_list(payload.get("conflicts"), "conflicts")
    if not conflicts:
        raise AssertionError("termbase.job.json must include a non-empty conflicts array")
    for forbidden in ["gray release", "grayscale release"]:
        if forbidden not in payload["_checked_forbidden_terms"]:
            raise AssertionError(f"termbase.job.json must include forbidden term: {forbidden}")
    events = check_delta_jsonl(delta_path)
    if not any(event.get("op") == "raise_conflict" for event in events):
        raise AssertionError("termbase.delta.jsonl must include a raise_conflict event")
    return payload


def check_mqm_content(path: Path) -> None:
    payload = json.loads(require_file(path))
    issues = payload["issues"]
    if not any(issue["severity"] == "Major" for issue in issues):
        raise AssertionError("review.json must include at least one Major issue")
    if not any(issue["category"] in {"Accuracy", "Terminology"} for issue in issues):
        raise AssertionError("review.json must include Accuracy or Terminology issues")


NEGATIVE_QA_POLARITY = {
    " no ",
    " not ",
    " none ",
    " absent",
    " acceptable",
    " accepted",
    " clean",
    " pass ",
    " passed",
    " resolved",
}


def require_failure_line(content: str, needle: str, words: set[str], label: str) -> None:
    candidate_lines = [
        line.casefold()
        for line in content.splitlines()
        if needle.casefold() in line.casefold()
    ]
    if not candidate_lines:
        raise AssertionError(f"qa.md must name {label}: {needle}")
    for line in candidate_lines:
        padded = f" {line} "
        if any(marker in padded for marker in NEGATIVE_QA_POLARITY):
            continue
        if any(word in line for word in words):
            return
    raise AssertionError(f"qa.md must mark {label} as an unresolved/blocking failure: {needle}")


def check_qa_content(path: Path, run_dir: Path | None) -> None:
    content = require_file(path)
    lowered = content.casefold()
    for required in [
        "files checked",
        "major",
        "blocking",
        "forbidden",
        "conflict",
        "unresolved",
        "termbase.job.json",
        "termbase.tbx",
        "terminology-review.tsv",
    ]:
        if required not in lowered:
            raise AssertionError(f"qa.md must mention {required!r}")
    if "human" not in lowered and "subject-matter" not in lowered:
        raise AssertionError("qa.md must call out human or subject-matter review")
    if run_dir is None:
        raise AssertionError("--run-dir is required for final-qa-contract package checks")
    package = run_dir / "evals" / "files" / "qa-package"
    translation = require_file(package / "translation.md")
    termbase = check_termbase_json(package / "termbase.job.json")
    forbidden_hits = [
        term
        for term in termbase["_checked_forbidden_terms"]
        if term.casefold() in translation.casefold()
    ]
    if not forbidden_hits:
        raise AssertionError("final-qa-contract fixture must contain a forbidden terminology hit")
    for term in forbidden_hits:
        require_failure_line(
            content,
            term,
            {"appears", "blocking", "fail", "forbidden", "present", "violation"},
            "forbidden terminology hit",
        )
    open_conflicts = [
        require_dict(conflict, "conflicts[]")
        for conflict in require_list(termbase.get("conflicts"), "conflicts")
        if conflict.get("status") == "open" and conflict.get("blocking") is True
    ]
    if not open_conflicts:
        raise AssertionError("final-qa-contract fixture must contain an open blocking conflict")
    for conflict in open_conflicts:
        conflict_id = require_nonempty_string(conflict.get("conflict_id"), "conflict.conflict_id")
        require_failure_line(
            content,
            conflict_id,
            {"blocking", "conflict", "open", "unresolved"},
            "unresolved conflict",
        )
    review = json.loads(require_file(package / "review.json"))
    major_issues = [
        require_dict(issue, "review.json issue")
        for issue in require_list(review.get("issues"), "review.json.issues")
        if issue.get("severity") == "Major"
    ]
    if not major_issues:
        raise AssertionError("final-qa-contract fixture must contain a Major MQM issue")
    for issue in major_issues:
        target_quote = require_nonempty_string(issue.get("target_quote"), "issue.target_quote")
        proposed_fix = require_nonempty_string(issue.get("proposed_fix"), "issue.proposed_fix")
        try:
            require_failure_line(
                content,
                target_quote,
                {"blocking", "fail", "major", "mqm", "unresolved"},
                "unresolved Major MQM issue",
            )
            continue
        except AssertionError:
            require_failure_line(
                content,
                proposed_fix,
                {"blocking", "fail", "major", "mqm", "unresolved"},
                "unresolved Major MQM issue",
            )


def check_case_specific(case_id: str, outputs: Path, run_dir: Path | None) -> None:
    if case_id == "structured-markdown-translation":
        check_structured_translation(outputs / "translation.md")
    elif case_id == "terminology-glossary-conflict":
        payload = check_terminology_content(
            outputs / "termbase.job.json",
            outputs / "termbase.delta.jsonl",
        )
        check_tbx(outputs / "termbase.tbx", payload)
        check_terminology_review_tsv(outputs / "terminology-review.tsv", payload)
    elif case_id == "mqm-review-json":
        check_mqm_content(outputs / "review.json")
    elif case_id == "final-qa-contract":
        check_qa_content(outputs / "qa.md", run_dir)


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
        elif expected == "termbase.job.json":
            check_termbase_json(path)
        elif expected == "termbase.delta.jsonl":
            check_delta_jsonl(path)
        elif expected == "termbase.tbx":
            check_tbx(path)
        elif expected == "terminology-review.tsv":
            check_terminology_review_tsv(path)
        elif expected.endswith(".md"):
            check_markdown(path)
        else:
            require_file(path)
    check_case_specific(case["id"], outputs, args.run_dir)
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
