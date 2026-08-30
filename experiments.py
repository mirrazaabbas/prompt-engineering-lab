"""Dataset-backed PromptOps experiments and regression reports."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from prompt_lab import build_prompt, load_prompts
from promptops import detect_prompt_injection, prompt_fingerprint
from provider_runner import PromptRunner


def load_experiment(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to load experiment: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list) or not data["cases"]:
        raise ValueError("experiment must be an object with a non-empty cases list")
    return data


def run_experiment(template: dict[str, Any], cases: list[dict[str, Any]], runner: PromptRunner | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    total_latency = 0
    total_tokens = 0
    total_cost = 0.0
    cost_count = 0
    for index, case in enumerate(cases, 1):
        variables = case.get("variables")
        if not isinstance(variables, dict):
            raise ValueError(f"case {index} variables must be an object")
        prompt = build_prompt(template, {str(k): str(v) for k, v in variables.items()})
        injection_matches = [match for value in variables.values() for match in detect_prompt_injection(str(value))]
        response = runner.run(prompt) if runner is not None else None
        output = response.text if response is not None else prompt
        required = [str(v) for v in case.get("required_substrings", [])]
        forbidden = [str(v) for v in case.get("forbidden_substrings", [])]
        passed = all(value in output for value in required) and all(value not in output for value in forbidden)
        latency = response.latency_ms if response else 0
        tokens = ((response.input_tokens or 0) + (response.output_tokens or 0)) if response else len(prompt.split())
        cost = response.cost_usd if response else None
        total_latency += latency
        total_tokens += tokens
        if cost is not None:
            total_cost += cost
            cost_count += 1
        rows.append({
            "id": str(case.get("id", index)),
            "passed": passed,
            "prompt_fingerprint": prompt_fingerprint(str(template["template"]), list(template["variables"])),
            "injection_patterns": sorted(set(injection_matches)),
            "latency_ms": latency,
            "tokens": tokens,
            "cost_usd": cost,
        })
    passed_count = sum(1 for row in rows if row["passed"])
    return {
        "template": template["name"],
        "fingerprint": prompt_fingerprint(str(template["template"]), list(template["variables"])),
        "cases": rows,
        "total": len(rows),
        "passed": passed_count,
        "pass_rate": round(passed_count / len(rows), 6),
        "average_latency_ms": round(total_latency / len(rows), 3),
        "average_tokens": round(total_tokens / len(rows), 3),
        "average_cost_usd": round(total_cost / cost_count, 8) if cost_count else None,
    }


def compare_results(baseline: dict[str, Any], candidate: dict[str, Any], *, max_pass_rate_drop: float = 0.0) -> dict[str, Any]:
    delta = float(candidate["pass_rate"]) - float(baseline["pass_rate"])
    return {
        "baseline_pass_rate": baseline["pass_rate"],
        "candidate_pass_rate": candidate["pass_rate"],
        "pass_rate_delta": round(delta, 6),
        "regressed": delta < -max_pass_rate_drop,
    }


def to_html(result: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(str(row['id']))}</td><td>{'PASS' if row['passed'] else 'FAIL'}</td><td>{row['latency_ms']}</td><td>{row['tokens']}</td></tr>"
        for row in result["cases"]
    )
    return f"""<!doctype html><meta charset="utf-8"><title>Prompt Experiment</title>
<h1>{html.escape(str(result['template']))}</h1><p>Pass rate: {float(result['pass_rate']):.1%}</p>
<p>Fingerprint: <code>{html.escape(str(result['fingerprint']))}</code></p>
<table border="1" cellpadding="6"><thead><tr><th>Case</th><th>Status</th><th>Latency ms</th><th>Tokens</th></tr></thead><tbody>{rows}</tbody></table>"""


def main() -> None:
    parser = argparse.ArgumentParser(prog="prompt-experiment")
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--prompts", type=Path, default=Path(__file__).resolve().with_name("prompts.json"))
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--html", dest="html_path", type=Path)
    args = parser.parse_args()
    data = load_experiment(args.experiment)
    templates = {str(item["name"]): item for item in load_prompts(args.prompts)}
    name = str(data.get("template"))
    if name not in templates:
        parser.error(f"unknown template: {name}")
    result = run_experiment(templates[name], data["cases"])
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.json_path:
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    if args.html_path:
        args.html_path.write_text(to_html(result), encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
