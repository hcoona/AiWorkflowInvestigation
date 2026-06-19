---
name: enterprise-translation-team
description: Coordinates role-based AI agents for enterprise professional Chinese-English document translation, including terminology, first-pass translation, bilingual MQM revision, QA, context compression, and eval-driven iteration. Use when the user asks for Chinese-English business, technical, legal, product, or enterprise documentation translation workflows.
license: CC-BY-NC-SA-4.0
compatibility: Designed for GitHub Copilot CLI with custom agents and project/plugin skills.
---

# Enterprise Translation Team

## Purpose

Use this skill when an AI agent, not a human translator,
must execute or design an enterprise Chinese-English document translation
workflow.
The goal is a controlled production line: compact context packets,
role-specialized agents, structured handoffs, deterministic QA,
and explicit human sign-off boundaries.

## Operating rules

1. Establish evaluation criteria before iterating on prompts, skills,
   or agent profiles.
   Use `evals/evals.json` as the local eval manifest
   and `references/evaluation.md` for public dataset guidance.
2. Use role agents when available: `translation-workflow-lead`,
   `translation-terminologist`, `translation-linguist`, `translation-reviser`,
   and `translation-qa-engineer`.
   When loaded from this plugin,
   Copilot CLI may list them with the plugin namespace,
   for example `enterprise-translation-team:translation-workflow-lead`.
3. For every material step,
   run independent positive
   and negative review gates with GPT-5.5 reviewer agents.
   Do not proceed while either gate returns `BLOCK`.
4. Send each role a compact task packet instead of the whole conversation.
   Use `references/context-packet.md` as the packet template.
5. Preserve source document structure unless the user explicitly asks
   for adaptation.
   Read `references/output-contracts.md` before generating files.
6. Use MQM-style review findings for bilingual revision.
   Read `references/mqm-taxonomy.md` before grading errors.
7. Treat AI review as a quality gate, not a regulated human approval.
   Escalate legal, medical, financial, compliance,
   or publication-sensitive uncertainty to a human or subject-matter expert.
8. Do not write to `raw\`, durable `wiki\`,
   or `wiki\log.jsonl` merely because a translation task was performed.
   Only update repository knowledge
   when the user explicitly requests durable wiki maintenance.

## Default workflow

1. **Intake**: identify language direction, audience, domain, risk level,
   files, output format, confidentiality constraints, terminology assets, and
   acceptance criteria.
2. **Evaluation gate**: choose relevant eval cases and assertions before
   changing skill or agent instructions.
3. **Terminology pass**: maintain a TBX-compatible concept-level termbase,
   extract job deltas, resolve conflicts, and enforce forbidden translations,
   acronyms, product names, placeholders, context examples, and approvals.
4. **Translation or post-edit pass**: translate only natural-language content
   while preserving Markdown, code, links, placeholders, numbers, and tables.
5. **Independent bilingual revision**: compare source and target, record
   MQM-style issues, and propose targeted fixes.
6. **Post-edit and reconciliation**: apply approved fixes and produce a
   resolved/unresolved issue report.
7. **Final QA**: run deterministic checks first, including termbase/schema,
   forbidden-term, and TBX export checks, then summarize subjective residual
   risks.
8. **Delivery package**: provide final files, `termbase.job.json`,
   `termbase.delta.jsonl`, `termbase.tbx`, `terminology-review.tsv`,
   QA report, and unresolved questions.

## Minimal role handoff

When delegating to a custom agent, include only:

- Objective and owned scope.
- Source and target language direction.
- Input paths or excerpt identifiers.
- Required output paths and format.
- Glossary and style constraints relevant to that role.
- Validation command or checklist.
- Prior role outputs needed for this step.
- Explicit non-goals.

Read `references/roles.md` for detailed role boundaries.
Read `references/terminology-schema.md` before creating, updating, exporting,
or QA-checking terminology assets.

## Available scripts

- `scripts/check_translation_outputs.py` validates expected eval output files,
  review JSON shape, termbase JSON/TBX/TSV contracts, and basic Markdown
  deliverables.

Run scripts from the skill directory root.
Example:

```powershell
mise exec -- python scripts\check_translation_outputs.py --evals evals\evals.json --case mqm-review-json --outputs path\to\outputs
```

## Iteration rule

Do not add more instructions just because an output feels imperfect.
First compare with a baseline, grade assertions with evidence,
identify the smallest generalizable failure pattern,
then edit the skill or agent profile.
