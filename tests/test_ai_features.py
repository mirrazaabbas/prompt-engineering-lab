from __future__ import annotations

import unittest
from unittest.mock import patch

import ai_features
import ai_platform


class FakeClient:
    def generate(self, system: str, user: str) -> str:
        self.system = system
        self.user = user
        return "Prompt executed successfully."


class AiFeatureTests(unittest.TestCase):
    def test_prompt_execution(self) -> None:
        client = FakeClient()
        result = ai_features.run_prompt("Create a concise AI project plan.", client)
        self.assertEqual(result, "Prompt executed successfully.")
        self.assertIn("project plan", client.user)
        with self.assertRaises(ValueError):
            ai_features.run_prompt("", client)

    def test_provider_response_shapes(self) -> None:
        cases = [
            ("openai", {"choices": [{"message": {"content": "openai ok"}}]}, "openai ok"),
            ("anthropic", {"content": [{"text": "claude ok"}]}, "claude ok"),
            (
                "gemini",
                {"candidates": [{"content": {"parts": [{"text": "gemini ok"}]}}]},
                "gemini ok",
            ),
        ]
        for provider, payload, expected in cases:
            client = ai_platform.HTTPAIClient(
                ai_platform.AIConfig(provider, "key", "model", "https://example.test")
            )
            with patch.object(client, "_post", return_value=payload):
                self.assertEqual(client.generate("system", "user"), expected)


if __name__ == "__main__":
    unittest.main()
