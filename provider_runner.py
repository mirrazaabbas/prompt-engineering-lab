"""Provider-independent prompt execution boundaries with injectable transport."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

Transport = Callable[[urllib.request.Request, float], bytes]


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model: str
    provider: str
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class PromptRunner(Protocol):
    def run(self, prompt: str) -> ModelResponse: ...


def _transport(request: urllib.request.Request, timeout: float) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"provider request failed: {exc.reason}") from exc


@dataclass
class OpenAICompatibleRunner:
    """Small OpenAI-compatible chat boundary; tests can inject transport and use no credentials."""

    model: str
    endpoint: str = "https://api.openai.com/v1/chat/completions"
    api_key_env: str = "OPENAI_API_KEY"
    timeout_seconds: float = 30.0
    transport: Transport = _transport
    input_cost_per_million: float | None = None
    output_cost_per_million: float | None = None

    def __post_init__(self) -> None:
        parsed = urlparse(self.endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("endpoint must be an absolute HTTP(S) URL")
        if not self.model.strip():
            raise ValueError("model cannot be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    def run(self, prompt: str) -> ModelResponse:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        key = os.getenv(self.api_key_env, "").strip()
        if not key:
            raise RuntimeError(f"missing provider credential in {self.api_key_env}")
        payload = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}]}).encode()
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        raw = self.transport(request, self.timeout_seconds)
        latency = int((time.perf_counter() - started) * 1000)
        try:
            data = json.loads(raw.decode("utf-8"))
            text = data["choices"][0]["message"]["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("provider returned an invalid response") from exc
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("provider returned an empty response")
        usage = data.get("usage") or {}
        input_tokens = _optional_int(usage.get("prompt_tokens"))
        output_tokens = _optional_int(usage.get("completion_tokens"))
        return ModelResponse(
            text=text,
            model=self.model,
            provider=urlparse(self.endpoint).netloc,
            latency_ms=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=_cost(input_tokens, output_tokens, self.input_cost_per_million, self.output_cost_per_million),
        )


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("token usage must be numeric") from exc


def _cost(input_tokens: int | None, output_tokens: int | None, input_rate: float | None, output_rate: float | None) -> float | None:
    if input_tokens is None or output_tokens is None or input_rate is None or output_rate is None:
        return None
    return round((input_tokens * input_rate + output_tokens * output_rate) / 1_000_000, 8)
