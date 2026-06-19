# Terminology Schema

## Standard baseline

Terminology assets must be at least as expressive as TBX.
Use TBX / ISO 30042 as the standard exchange baseline and TBX-Basic
as the default interoperable export target.
TBX-Min is acceptable only as a fallback export profile,
not as the internal design target.

TMX is translation memory and XLIFF is localization-package exchange.
They may reference or consume terms,
but they are not the canonical termbase format for this skill.

## Termbase layers

Use a shared, scoped termbase plus job-local deltas.
Multiple translated documents should share the same applicable termbase layer
instead of creating isolated document glossaries.

Resolution order:

```text
document override -> job override -> project/product/domain -> client -> global
```

Global entries are only for universal, non-confidential concepts.
Client, domain, product, project,
and job terms must carry explicit scope
so terminology does not leak across customers or domains.

Jobs must not mutate approved global/client termbases directly.
They write `termbase.delta.jsonl`; approved deltas can later be promoted.

## Required files

| File | Role |
| --- | --- |
| `termbase.job.json` | Canonical resolved concept-level termbase for the job. |
| `termbase.delta.jsonl` | Append-only proposals, conflicts, overrides, waivers, and promotion requests. |
| `termbase.tbx` | Standard exchange export generated from the canonical JSON. |
| `terminology-review.tsv` | Lossy flattened review view; never canonical. |

`termbase.tbx` must export every canonical source term, preferred target,
allowed variant, and forbidden target as TBX term sections
where the selected profile permits it.
If the selected TBX profile cannot preserve workflow metadata or examples,
ship `termbase.tbx` plus the exact JSON sidecar path `termbase.job.json`;
`termbase.job.json` remains the canonical lossless job termbase.

## Canonical JSON contract

`termbase.job.json` must use BCP-47 language tags and concept-level entries:

```json
{
  "schema_version": "enterprise-termbase-v2",
  "standard_basis": {
    "primary": "TBX ISO 30042",
    "export_targets": ["TBX-Basic"],
    "lossless_for_key_fields": true
  },
  "termbase_id": "enterprise-zh-en",
  "source_locale": "zh-Hans",
  "target_locale": "en-US",
  "entries": [
    {
      "concept_id": "c-release-0001",
      "entry_id": "t-gray-release-zh-en",
      "status": "approved",
      "scope": {
        "level": "client",
        "client_id": "example-client",
        "domain": "enterprise-saas-release-management",
        "project_id": "admin-docs"
      },
      "source": {
        "term": "灰度发布",
        "language": "zh-Hans",
        "part_of_speech": "noun",
        "term_type": "fullForm"
      },
      "target": {
        "preferred": "phased rollout",
        "language": "en-US",
        "allowed_variants": ["phased release"],
        "forbidden": [
          {
            "term": "gray release",
            "match_mode": "case_insensitive",
            "reason": "Literal false friend in release-management context.",
            "severity": "blocking"
          }
        ]
      },
      "context": {
        "definition": "A controlled release to a limited population before broad availability.",
        "usage_note": "Use for software rollout strategy, not image processing.",
        "positive_examples": [
          {
            "source": "本次灰度发布仅面向内部员工。",
            "target": "This phased rollout is limited to internal employees.",
            "reason": "Software release context."
          }
        ],
        "negative_examples": [
          {
            "source": "图片灰度处理完成后再发布。",
            "bad_target": "phased rollout",
            "correct_guidance": "This is image grayscale processing, not release management.",
            "reason": "Same surface form, wrong domain."
          }
        ]
      },
      "provenance": {
        "created_by": "translation-terminologist",
        "created_at": "2026-06-18",
        "evidence_refs": ["terminology-brief.json#terms[0]"]
      },
      "maintenance": {
        "revision": 1,
        "owner": "terminology",
        "reviewer": "customer-subject-matter-expert",
        "approval_status": "approved",
        "reliability": {
          "code": 5,
          "confidence": "high"
        },
        "last_reviewed_at": "2026-06-18"
      }
    }
  ],
  "conflicts": []
}
```

Allowed entry `status` values:

- `approved`
- `candidate`
- `conflict`
- `forbidden`
- `needs_confirmation`
- `deprecated`
- `rejected`

## Delta JSONL contract

Each line in `termbase.delta.jsonl` is an immutable event.

Allowed operations:

- `propose_term`
- `approve_term`
- `reject_term`
- `add_forbidden`
- `raise_conflict`
- `resolve_conflict`
- `add_document_override`
- `waive_term_violation`
- `promote_to_global`
- `supersede_entry`

Required event fields:

- `event_id`
- `op`
- `job_id`
- `doc_id`
- `concept_id` or `source_term`
- `scope`
- `evidence_ref`
- `submitted_by`
- `status`

Merge by `concept_id` plus scope, not by source term alone.
Different targets in the same scope create a conflict.
Approved entries are superseded by new records, not overwritten in place.

## TBX mapping

| JSON field | TBX-compatible mapping |
| --- | --- |
| `concept_id` | `conceptEntry/@id` |
| `scope.domain` / `subject` | `descrip type="subjectField"` |
| `context.definition` | `descrip type="definition"` |
| source/target language blocks | `langSec xml:lang` |
| term text | `termSec/term` |
| `part_of_speech` | `termNote type="partOfSpeech"` |
| `term_type` | `termNote type="termType"` |
| `status` / `approval_status` | `admin` or TBX-compatible term note |
| `reliability.code` | reliability data category |
| contexts/examples | `descrip type="context"` or profile-compatible sidecar |
| provenance | `transacGrp`, `admin`, or note fields |

## Review TSV

`terminology-review.tsv` must use this header:

```text
concept_id	entry_id	scope	status	source_term	preferred_target	allowed_variants	forbidden_targets	context_note	positive_example	negative_example	conflict_id	blocking	evidence_refs
```

The TSV is for human review and diffs only.
TSV edits must become delta events;
do not merge TSV edits directly into canonical JSON.

## Blocking QA conditions

- Unscoped approved terms.
- Missing concept id, language, definition, context, examples, provenance,
  approval status, or reliability for approved terms.
- Conflicting preferred targets in the same scope.
- Forbidden target appears in the translation.
- Applicable approved term is missing without a waiver.
- `conflict`, `candidate`, or `needs_confirmation` terms affect final text.
- Job override lacks approval or explicit waiver.
- TBX/TSV exports do not match canonical JSON.
