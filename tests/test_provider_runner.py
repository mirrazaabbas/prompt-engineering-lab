import json
import os
import unittest
import urllib.error
from unittest import mock

from provider_runner import OpenAICompatibleRunner, _cost, _optional_int, _transport


class _FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class ProviderRunnerTests(unittest.TestCase):
    def test_validation(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleRunner(model="", endpoint="https://example.com")
        with self.assertRaises(ValueError):
            OpenAICompatibleRunner(model="x", endpoint="not-a-url")
        with self.assertRaises(ValueError):
            OpenAICompatibleRunner(model="x", timeout_seconds=0)

    def test_run_with_injected_transport(self):
        captured = {}

        def transport(request, timeout):
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return json.dumps(
                {
                    "choices": [{"message": {"content": "structured answer"}}],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 8},
                }
            ).encode("utf-8")

        runner = OpenAICompatibleRunner(
            model="test-model",
            endpoint="https://provider.example/v1/chat/completions",
            api_key_env="PROMPT_LAB_TEST_KEY",
            timeout_seconds=5,
            transport=transport,
            input_cost_per_million=1.0,
            output_cost_per_million=2.0,
        )
        with mock.patch.dict(os.environ, {"PROMPT_LAB_TEST_KEY": "secret"}, clear=False):
            result = runner.run("hello")
        self.assertEqual(result.text, "structured answer")
        self.assertEqual(result.provider, "provider.example")
        self.assertEqual(result.input_tokens, 12)
        self.assertEqual(result.output_tokens, 8)
        self.assertEqual(result.cost_usd, 0.000028)
        self.assertEqual(captured["authorization"], "Bearer secret")
        self.assertEqual(captured["timeout"], 5)

    def test_missing_credential_empty_prompt_and_bad_response(self):
        runner = OpenAICompatibleRunner(
            model="test-model",
            api_key_env="PROMPT_LAB_MISSING_KEY",
            transport=lambda request, timeout: b"{}",
        )
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                runner.run("hello")
        with self.assertRaises(ValueError):
            runner.run("   ")
        with mock.patch.dict(os.environ, {"PROMPT_LAB_MISSING_KEY": "x"}, clear=False):
            with self.assertRaises(RuntimeError):
                runner.run("hello")

        invalid = OpenAICompatibleRunner(
            model="test-model",
            api_key_env="PROMPT_LAB_MISSING_KEY",
            transport=lambda request, timeout: b'{"choices":[{"message":{"content":""}}]}',
        )
        with mock.patch.dict(os.environ, {"PROMPT_LAB_MISSING_KEY": "x"}, clear=False):
            with self.assertRaises(RuntimeError):
                invalid.run("hello")

    def test_transport_and_usage_helpers(self):
        request = mock.Mock()
        with mock.patch("urllib.request.urlopen", return_value=_FakeResponse(b"ok")):
            self.assertEqual(_transport(request, 1.0), b"ok")
        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("offline"),
        ):
            with self.assertRaises(RuntimeError):
                _transport(request, 1.0)

        self.assertIsNone(_optional_int(None))
        self.assertEqual(_optional_int("7"), 7)
        with self.assertRaises(RuntimeError):
            _optional_int("nope")
        self.assertIsNone(_cost(None, 2, 1.0, 1.0))
        self.assertEqual(_cost(10, 20, 1.0, 2.0), 0.00005)


if __name__ == "__main__":
    unittest.main()
