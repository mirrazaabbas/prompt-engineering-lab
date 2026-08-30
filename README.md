# Prompt Engineering Lab

[![CI](https://github.com/mirrazaabbas/prompt-engineering-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/mirrazaabbas/prompt-engineering-lab/actions/workflows/ci.yml)
[![Security](https://github.com/mirrazaabbas/prompt-engineering-lab/actions/workflows/security.yml/badge.svg)](https://github.com/mirrazaabbas/prompt-engineering-lab/actions/workflows/security.yml)

A tested PromptOps portfolio project for building reusable prompts, running deterministic regression experiments, detecting prompt-injection signals, comparing prompt versions, and optionally executing prompts through a provider-independent model boundary.

## What it demonstrates

- Validated prompt templates with declared variables.
- Deterministic prompt rendering and regression cases.
- Stable prompt fingerprints for version tracking.
- Prompt-injection pattern detection for untrusted variable content.
- Dataset-backed experiments with pass/fail results.
- A/B regression comparison using pass-rate deltas.
- JSON and escaped HTML experiment reports.
- Provider-independent `PromptRunner` protocol.
- OpenAI-compatible HTTP boundary with injectable transport for credential-free tests.
- Latency, input/output token and optional cost metadata.
- Installable CLI entry points.
- Python 3.10-3.12 CI, linting, coverage, package-build verification and installed-wheel smoke tests.
- CodeQL, dependency audit, CycloneDX SBOM and provenance-backed tagged releases.

## Quick start

```bash
python -m pip install -e .
prompt-experiment sample_experiment.json --json result.json --html result.html
```

The interactive template builder is available as:

```bash
prompt-lab
```

The source checkout also works directly:

```bash
python prompt_lab.py
python experiments.py sample_experiment.json
```

## Prompt library

`prompts.json` currently includes research, professional content, and data-analysis templates. The installed package also contains a built-in default copy of these templates so the interactive CLI remains usable outside the repository checkout.

Each template declares its variables. `build_prompt()` rejects missing or empty values and verifies that no declared placeholders remain unresolved.

## PromptOps experiments

`sample_experiment.json` shows the dataset format:

```json
{
  "template": "Research Assistant",
  "cases": [
    {
      "id": "example",
      "variables": {
        "topic": "RAG",
        "audience": "engineering leaders",
        "output_format": "a concise table"
      },
      "required_substrings": ["RAG"],
      "forbidden_substrings": ["invented citation"]
    }
  ]
}
```

Without a model runner, experiments evaluate the rendered prompt deterministically. With a runner, the same harness evaluates model output and records execution metadata.

## Provider boundary

`provider_runner.py` defines a small `PromptRunner` protocol and an `OpenAICompatibleRunner`. The HTTP transport is injectable, which means unit tests exercise request/response handling without real credentials or live provider calls.

Credentials are read from environment variables only. No API key is committed to this repository.

## Security behavior

Prompt variables are treated as untrusted text. The experiment report surfaces common instruction-injection patterns such as requests to ignore previous instructions or reveal hidden prompts. Detection is a signal for review, not a claim that regex matching alone provides complete prompt-injection defense.

## Quality gates

```bash
python -m pip install --upgrade pip -r requirements-dev.txt build
ruff check .
coverage run -m unittest discover -s tests -v
coverage report --fail-under=80
python -m build
```

CI additionally runs the sample experiment and installs the built wheel in order to smoke-test the packaged modules and CLI.

## Scope and claims

This repository demonstrates transparent PromptOps engineering patterns. It does not claim that simple substring checks or regex injection detection fully evaluate production LLM quality or security. Provider calls are optional, and no live external provider is required for the automated test suite.

## Skills demonstrated

Python · Prompt Engineering · PromptOps · LLM Evaluation · Regression Testing · Prompt Safety · Provider Abstraction · JSON · HTML Reporting · CI/CD · CodeQL · SBOM · Packaging
