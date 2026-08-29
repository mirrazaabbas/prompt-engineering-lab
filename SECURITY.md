# Security Policy

## Supported branch

The `main` branch is the actively maintained version of this portfolio project.

## Reporting a vulnerability

Do not publish credentials, private prompt content, personal data, or actionable exploit details in a public issue. Use GitHub private vulnerability reporting when available. Otherwise, open a minimal issue without sensitive reproduction details until a private channel is established.

## Security principles

- Never commit API keys, tokens, passwords, or private prompt data.
- Treat prompt variables and future model output as untrusted input.
- Validate prompt-template structure and declared variables before rendering.
- Keep secrets outside prompt templates and repository files.
- Do not use prompt wording to claim capabilities or evidence that the underlying system does not have.
