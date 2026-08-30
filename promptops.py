"""Provider-independent PromptOps helpers for versioning and regression tests."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

INJECTION_PATTERNS = (
    r"ignore (all|any|the) previous instructions",
    r"reveal (the )?(system|developer) prompt",
    r"show (me )?your hidden instructions",
    r"bypass (the )?(rules|guardrails|policy)",
)


def prompt_fingerprint(template: str, variables: list[str]) -> str:
    payload = json.dumps({"template": template, "variables": sorted(variables)}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def detect_prompt_injection(text: str) -> list[str]:
    lower = (text or "").lower()
    return [pattern for pattern in INJECTION_PATTERNS if re.search(pattern, lower)]


def validate_output_schema(output: dict[str, Any], schema: dict[str, type]) -> list[str]:
    errors: list[str] = []
    for key, expected_type in schema.items():
        if key not in output:
            errors.append(f"missing field: {key}")
        elif not isinstance(output[key], expected_type):
            errors.append(f"field {key} must be {expected_type.__name__}")
    return errors


@dataclass(frozen=True)
class PromptExperimentResult:
    name: str
    passed: int
    failed: int
    total: int
    pass_rate: float


def run_regression_cases(
    name: str,
    renderer,
    cases: list[dict[str, Any]],
) -> PromptExperimentResult:
    passed = 0
    for case in cases:
        rendered = renderer(case.get("variables", {}))
        required = case.get("required_substrings", [])
        forbidden = case.get("forbidden_substrings", [])
        ok = all(text in rendered for text in required) and all(text not in rendered for text in forbidden)
        if ok:
            passed += 1
    total = len(cases)
    failed = total - passed
    return PromptExperimentResult(
        name=name,
        passed=passed,
        failed=failed,
        total=total,
        pass_rate=(passed / total) if total else 1.0,
    )


def compare_experiments(baseline: PromptExperimentResult, candidate: PromptExperimentResult) -> dict[str, float | bool]:
    delta = candidate.pass_rate - baseline.pass_rate
    return {"pass_rate_delta": delta, "regressed": delta < 0}
