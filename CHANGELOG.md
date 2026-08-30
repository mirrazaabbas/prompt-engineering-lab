# Changelog

All notable changes to this project are documented here.

## 1.0.0 - 2026-08-30

### Added
- Dataset-backed PromptOps experiment runner with JSON and HTML reports.
- Prompt fingerprinting and prompt-injection signal detection in experiment results.
- Provider-independent execution protocol and OpenAI-compatible HTTP boundary with injectable transport.
- Latency, token and optional cost metadata for model-backed experiments.
- Installable `prompt-lab` and `prompt-experiment` command-line entry points.
- Python 3.10-3.12 CI with deterministic experiments, package build and installed-wheel smoke tests.
- CodeQL, dependency auditing, CycloneDX SBOM generation and tagged release provenance.

### Security
- Provider tests use injected transports and do not require live credentials.
- Credentials are read only from environment variables and are never stored in the prompt library.
