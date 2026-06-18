# Output Contracts

## Translation output

Use `translation.md` unless the user requests a different format.

Requirements:

- Preserve Markdown heading levels, list nesting, table dimensions, links,
  images, inline code, code fences, placeholders, and file paths.
- Translate natural-language prose only.
- Do not leave source-language prose untranslated unless marked as protected
  text or unresolved.
- Add translator queries in a separate section only when ambiguity affects
  correctness.

## Terminology output

Use `terminology.tsv` with this header:

```text
source_term	target_term	status	notes
```

Allowed `status` values:

- `approved`
- `candidate`
- `conflict`
- `forbidden`
- `needs-confirmation`

## Review output

Use `review.json` for machine-checkable MQM findings:

```json
{
  "issues": [],
  "summary": {
    "major": 0,
    "minor": 0,
    "neutral": 0
  }
}
```

The top-level array must be named `issues`.
Do not use `findings`.
The `summary` object must include top-level lowercase numeric keys `major`,
`minor`, and `neutral`.
Do not replace them with nested `by_severity` counts.
Each issue category must be one of the exact values in
`references/mqm-taxonomy.md`; do not append subcategories such as
`Accuracy/Mistranslation`.

## QA output

Use `qa.md` with:

- Files checked.
- Deterministic checks and pass/fail results.
- Unresolved major issues.
- Human or subject-matter expert sign-off still required.
