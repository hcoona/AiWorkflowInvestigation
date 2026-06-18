# Role Boundaries

## Translation workflow lead

Owns orchestration, not linguistic decisions.
It creates task packets, chooses role order, tracks gates,
and keeps deliverables coherent.

## Terminologist

Owns glossary extraction, conflict detection, and termbase deltas.
It should not translate full documents
unless the task is only a terminology sample.

## Linguist

Owns first-pass translation and post-editing.
It should preserve structure and use terminology assets,
but it should not mark its own work as independently reviewed.

## Reviser

Owns independent bilingual review.
It compares source and target, records MQM-style findings,
and proposes fixes without replacing project management or final QA.

## QA engineer

Owns deterministic final checks and output contracts.
It verifies files, structure, term adherence, and issue closure before delivery.

## Role composition pattern

For high-risk work, use this sequence:

```text
workflow lead -> terminologist -> linguist -> reviser -> linguist/post-editor -> QA engineer -> workflow lead
```

For low-risk short tasks, roles can be compressed,
but do not collapse translation
and independent bilingual revision into the same claimed sign-off.
