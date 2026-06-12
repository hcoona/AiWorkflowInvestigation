# AI Workflow Investigation

[简体中文](README.zh-Hans.md)

This repository investigates opportunities for AI-enhanced workflows: workflows where AI systems help plan, execute, validate, or coordinate work with human participants.

The focus is on practical software-engineering workflows and adjacent knowledge-work processes. The project explores how AI can collaborate with people across a workflow lifecycle, including plan generation, plan revision from human feedback, partial node execution, human-in-the-loop checkpoints, and confirmation that manually owned steps have been completed.

## Research scope

The investigation includes, but is not limited to:

- AI-generated or AI-modified workflow plans based on human input, constraints, and feedback.
- AI execution of selected workflow nodes where automation is safe, useful, and auditable.
- AI-human interaction patterns for confirming manually completed workflow nodes.
- Workflow state tracking, handoff design, and evidence capture across mixed human/AI execution.
- Reliability, reviewability, and control mechanisms for workflows that include autonomous or semi-autonomous AI steps.

## Intended audience

This repository is written for software engineers evaluating how AI can augment real workflows without turning workflow execution into an opaque automation system. The materials should help engineers reason about architecture, operating models, boundaries of autonomy, and places where human judgment must remain explicit.

## Knowledge organization

The repository is bootstrapped as an LLM-Wiki. Durable synthesis belongs in `wiki/`, curated evidence belongs in `raw/`, and agent operating rules belong in `AGENTS.md`.

Use the declared validation task after durable wiki changes:

```bash
mise run wiki-check
```

## Git hooks

This repository uses [hk](https://hk.jdx.dev/) through mise. The hk `pre-commit`, `check`, and `fix` hooks run the same validation steps, including `check-wiki`, which executes the existing `mise run wiki-check` validation task.
The `.gitattributes` file is generated from `gitattributes.pkl`; hooks also check that indexed files are covered by its explicit text or binary pattern lists.

Install project tools with:

```bash
mise install
```

Install or update git hooks with:

```bash
mise exec -- hk install --mise
```

Run the pre-commit checks manually with:

```bash
mise exec -- hk run pre-commit
```

Run the check-only hook against all files with:

```bash
mise exec -- hk check --all
```

Run checks and configured fixes against all files with:

```bash
mise exec -- hk fix --all
```

Regenerate `.gitattributes` after changing `gitattributes.pkl` with:

```bash
mise run gitattributes-generate
```

## License

This repository is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See [LICENSE](LICENSE) and the official license text at <https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode>.
