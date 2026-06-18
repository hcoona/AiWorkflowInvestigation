#!/usr/bin/env python
"""Prepare or run Copilot CLI evals for the enterprise translation plugin."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "enterprise-translation-team"
EVALS = SKILL / "evals" / "evals.json"
CHECKER = SKILL / "scripts" / "check_translation_outputs.py"
AGENT_BY_CASE = {
    "structured-markdown-translation": "enterprise-translation-team:translation-linguist",
    "terminology-glossary-conflict": "enterprise-translation-team:translation-terminologist",
    "mqm-review-json": "enterprise-translation-team:translation-reviser",
    "final-qa-contract": "enterprise-translation-team:translation-qa-engineer",
    "negative-no-durable-wiki-write": "enterprise-translation-team:translation-workflow-lead",
}
REVIEW_AGENTS = [
    "enterprise-translation-team:translation-positive-reviewer",
    "enterprise-translation-team:translation-negative-reviewer",
]
REVIEW_MODEL = "gpt-5.5"


def load_cases() -> list[dict]:
    return json.loads(EVALS.read_text(encoding="utf-8"))["evals"]


def select_cases(case_id: str | None) -> list[dict]:
    cases = load_cases()
    if case_id is None:
        return cases
    selected = [case for case in cases if case["id"] == case_id]
    if not selected:
        raise ValueError(f"Unknown eval case: {case_id}")
    return selected


def copy_inputs(case: dict, run_dir: Path) -> None:
    for relative in case.get("files", []):
        source = SKILL / relative
        target = run_dir / relative
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def build_workspace(workspace: Path | None) -> Path:
    if workspace is not None:
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace.resolve()
    return Path(tempfile.mkdtemp(prefix="enterprise-translation-evals-")).resolve()


def needs_grading(case: dict) -> bool:
    return bool(
        case.get("expected_files")
        or case.get("forbidden_created_paths")
        or case.get("required_response_patterns")
        or case.get("forbidden_response_patterns")
    )


def last_verdict(text: str) -> str:
    for line in reversed([line.strip() for line in text.splitlines()]):
        if line.startswith("PASS"):
            return "PASS"
        if line.startswith("BLOCK"):
            return "BLOCK"
    return "UNKNOWN"


def run_review_gates(case: dict, case_dir: Path, model: str) -> list[dict]:
    results: list[dict] = []
    prompt = (
        f"Review eval case {case['id']} for the enterprise-translation-team plugin. "
        "Inspect run-manifest.json, response.txt, grading output, and outputs if present. "
        "Return PASS only if the run satisfies the eval prompt, expected output, "
        "assertions, and safety constraints. Return BLOCK with material findings otherwise."
    )
    for agent in REVIEW_AGENTS:
        command = [
            "copilot",
            "--agent",
            agent,
            "--model",
            REVIEW_MODEL,
            "-C",
            str(case_dir),
            "--plugin-dir",
            str(ROOT),
            "-p",
            prompt,
            "--allow-tool=read",
            "--allow-tool=search",
            "--silent",
        ]
        completed = subprocess.run(
            command,
            cwd=case_dir,
            text=True,
            capture_output=True,
            check=False,
        )
        safe_agent = agent.replace(":", "__")
        output_path = case_dir / f"review-gate-{safe_agent}.txt"
        output_path.write_text(completed.stdout, encoding="utf-8")
        (case_dir / f"review-gate-{safe_agent}.stderr.txt").write_text(
            completed.stderr,
            encoding="utf-8",
        )
        verdict = last_verdict(completed.stdout)
        results.append(
            {
                "agent": agent,
                "returncode": completed.returncode,
                "verdict": verdict,
                "output": str(output_path),
            }
        )
    return results


def run_case(
    case: dict,
    workspace: Path,
    mode: str,
    model: str,
    explicit_agent: str | None,
    baseline: str,
    review_gates: bool,
) -> dict:
    run_name = baseline if mode == "copilot" else "dry-run"
    case_dir = workspace / case["id"] / run_name
    if case_dir.exists():
        shutil.rmtree(case_dir)
    outputs = case_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    copy_inputs(case, case_dir)

    manifest = {
        "case": case["id"],
        "mode": mode,
        "model": model,
        "review_gate_model": REVIEW_MODEL,
        "baseline": baseline,
        "review_gates": review_gates,
        "plugin_root": str(ROOT),
        "run_dir": str(case_dir),
        "expected_files": case.get("expected_files", []),
        "prompt": case["prompt"],
    }
    (case_dir / "run-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if mode == "dry-run":
        return {"case": case["id"], "status": "prepared", "run_dir": str(case_dir)}

    agent = explicit_agent or (AGENT_BY_CASE.get(case["id"]) if baseline == "with-plugin" else None)
    prompt = (
        f"{case.get('baseline_prompt') if baseline == 'no-plugin' else case['prompt']}\n\n"
        "Work only in the current directory. "
        "Write requested files under the existing outputs directory. "
        "Do not modify files outside the current directory. "
        "Do not use network access or shell commands."
    )
    command = ["copilot"]
    if agent:
        command.extend(["--agent", agent])
    command.extend(
        [
            "--model",
            model,
            "-C",
            str(case_dir),
            "-p",
            prompt,
            "--allow-tool=read",
            "--allow-tool=write",
            "--allow-tool=edit",
            "--allow-tool=search",
            "--deny-tool=execute",
            "--deny-tool=shell",
            "--silent",
        ]
    )
    if baseline == "with-plugin":
        command[command.index("-p"):command.index("-p")] = ["--plugin-dir", str(ROOT)]

    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=case_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    response = case_dir / "response.txt"
    response.write_text(result.stdout, encoding="utf-8")
    (case_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    (case_dir / "timing.json").write_text(
        json.dumps({"duration_ms": duration_ms}, indent=2),
        encoding="utf-8",
    )
    if result.returncode != 0:
        return {
            "case": case["id"],
            "status": "copilot-failed",
            "returncode": result.returncode,
            "run_dir": str(case_dir),
        }

    if needs_grading(case):
        check = subprocess.run(
            [
                sys.executable,
                str(CHECKER),
                "--evals",
                str(EVALS),
                "--case",
                case["id"],
                "--outputs",
                str(outputs),
                "--run-dir",
                str(case_dir),
                "--response",
                str(response),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        (case_dir / "grading-stdout.txt").write_text(check.stdout, encoding="utf-8")
        (case_dir / "grading-stderr.txt").write_text(check.stderr, encoding="utf-8")
        if check.returncode != 0:
            return {
                "case": case["id"],
                "status": "grading-failed",
                "returncode": check.returncode,
                "run_dir": str(case_dir),
            }

    gate_results: list[dict] = []
    if review_gates and baseline == "with-plugin":
        gate_results = run_review_gates(case, case_dir, model)
        if any(
            gate["returncode"] != 0 or gate["verdict"] != "PASS"
            for gate in gate_results
        ):
            return {
                "case": case["id"],
                "status": "review-gate-failed",
                "review_gates": gate_results,
                "run_dir": str(case_dir),
            }

    return {
        "case": case["id"],
        "status": "passed",
        "review_gates": gate_results,
        "run_dir": str(case_dir),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare or run enterprise translation plugin eval cases."
    )
    parser.add_argument("--mode", choices=["dry-run", "copilot"], default="dry-run")
    parser.add_argument("--baseline", choices=["with-plugin", "no-plugin"], default="with-plugin")
    parser.add_argument("--case", help="Eval case id. Defaults to all cases.")
    parser.add_argument("--workspace", type=Path, help="Disposable eval workspace.")
    parser.add_argument("--agent", help="Override namespaced Copilot custom agent.")
    parser.add_argument("--model", default="gpt-5.5", help="Copilot model for eval runs.")
    parser.add_argument(
        "--skip-review-gates",
        action="store_true",
        help="Skip GPT-5.5 positive/negative review gates for copilot mode.",
    )
    args = parser.parse_args(argv)

    workspace = build_workspace(args.workspace)
    results = [
        run_case(
            case,
            workspace,
            args.mode,
            args.model,
            args.agent,
            args.baseline,
            args.mode == "copilot" and not args.skip_review_gates,
        )
        for case in select_cases(args.case)
    ]
    summary = {"workspace": str(workspace), "results": results}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if any(result["status"] not in {"prepared", "passed"} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
