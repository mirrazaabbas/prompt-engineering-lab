"""Optional cross-platform execution for rendered prompt templates."""
from __future__ import annotations

from ai_platform import AIClient


def run_prompt(prompt: str, client: AIClient) -> str:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string.")
    system = (
        "Follow the supplied prompt faithfully. Do not claim external actions, browsing, tool use, or "
        "facts that are not available in the conversation or prompt context."
    )
    return client.generate(system, prompt)
