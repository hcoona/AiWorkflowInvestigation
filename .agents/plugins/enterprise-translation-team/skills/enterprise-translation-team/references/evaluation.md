# Evaluation Plan

Evaluate this skill before instruction iteration.
Follow the Agent Skills pattern: define prompts and expected outputs,
run each case with and without the skill or against the previous version,
grade assertions with evidence, then iterate only on recurring failures.

## Baselines

Use at least two baselines:

1. No plugin loaded.
2. Current plugin loaded with `--plugin-dir` or local plugin install.

For later iterations, snapshot the previous plugin and compare old versus new.

## GPT-5.5 review gates

Every material step must pass two independent GPT-5.5 review gates:

| Gate | Agent | Blocking threshold |
| --- | --- | --- |
| Positive review | `enterprise-translation-team:translation-positive-reviewer` | Blocks if the stated objective, role boundary, context packet, or eval criterion is not satisfied. |
| Negative review | `enterprise-translation-team:translation-negative-reviewer` | Blocks on schema incompatibility, unsafe permissions, no-op evals, context bloat, Windows/non-interactive failure, or false human sign-off. |

Use the explicit model flag when invoking review gates from Copilot CLI:

```powershell
copilot -C <scratch> --plugin-dir <plugin-root> --agent enterprise-translation-team:translation-positive-reviewer --model gpt-5.5 -p "<review prompt>" --allow-tool=read --allow-tool=search --silent
copilot -C <scratch> --plugin-dir <plugin-root> --agent enterprise-translation-team:translation-negative-reviewer --model gpt-5.5 -p "<review prompt>" --allow-tool=read --allow-tool=search --silent
```

Do not proceed while either review returns `BLOCK`.
After fixing a blocker, rerun both gates on the revised step.

## Public dataset registry

The plugin does not vendor public datasets.
Use these as external benchmark sources
when a real eval run needs standard data:

| Dataset | Best use | Notes |
| --- | --- | --- |
| FLORES-200 | Sentence-level zh-Hans/en translation sanity checks. | Professionally translated benchmark; useful for direction and leakage checks. |
| WMT MQM Human Evaluation | Bilingual review and MQM category/severity behavior. | Includes Chinese-to-English WMT outputs with professional translator annotations. |
| WMT Terminology Task 2023 | Glossary adherence and terminology constraints. | Includes zh-en terminology hints and target terms. |
| MLQE-PE | Post-editing and quality-estimation behavior. | Useful for edit minimality and error resolution checks. |
| ACES | Adversarial accuracy and contrastive error detection. | Useful for reviewer negative cases. |
| BWB/BlonDe | Document-level Chinese-English consistency. | Useful for entity/coreference consistency across segments. |

Do not copy dataset text into this repository by default.
Download to a temporary eval workspace only after checking the dataset license
and the user's authorization.

## Local fixture evals

`evals/evals.json` contains small synthetic fixtures for fast package checks.
They are not a replacement for public dataset runs;
they prove that the skill has stable output contracts
before expensive `copilot -p` evaluation.

## Copilot CLI run shape

Use a disposable workspace outside canonical `raw\` and `wiki\` content.

```powershell
copilot -C <scratch> --plugin-dir <plugin-root> -p "<eval prompt>" --allow-tool=read --allow-tool=write --allow-tool=edit --allow-tool=search --deny-tool=execute --deny-tool=shell --silent
```

When selecting a custom agent directly:

```powershell
copilot -C <scratch> --plugin-dir <plugin-root> --agent enterprise-translation-team:translation-workflow-lead -p "<eval prompt>" --allow-tool=read --allow-tool=write --allow-tool=edit --allow-tool=search --deny-tool=execute --deny-tool=shell --silent
```

Record prompt, plugin version, model, output directory, duration,
and pass/fail evidence.
Avoid using cached plugin installs for A/B tests
unless the cache state is part of the test.

The packaged helper can prepare or run local fixture evals:

```powershell
mise exec -- python scripts\run_copilot_evals.py --mode dry-run
mise exec -- python scripts\run_copilot_evals.py --mode copilot --case mqm-review-json --workspace <scratch>
mise exec -- python scripts\run_copilot_evals.py --mode copilot --baseline no-plugin --case mqm-review-json --workspace <scratch>
```

In `copilot` mode, the helper defaults to enforcing both GPT-5.5 review gates
for `with-plugin` runs.
Use `--skip-review-gates` only when debugging harness mechanics,
not when accepting a skill iteration.

Run it from the plugin root, or prefer the repository task for dry runs:

```powershell
mise run translation-agent-plugin-eval-dry-run
```
