import json
import tempfile
import unittest
from pathlib import Path

import prompt_lab


class PromptLabTests(unittest.TestCase):
    def test_load_and_build(self):
        prompts = prompt_lab.load_prompts()
        self.assertGreaterEqual(len(prompts), 3)
        first = prompts[0]
        values = {variable: "test value" for variable in first["variables"]}
        rendered = prompt_lab.build_prompt(first, values)
        self.assertNotIn("{", rendered)

    def test_missing_and_empty_values(self):
        template = prompt_lab.load_prompts()[0]
        with self.assertRaises(ValueError):
            prompt_lab.build_prompt(template, {})
        with self.assertRaises(ValueError):
            prompt_lab.build_prompt(template, {v: "" for v in template["variables"]})

    def test_invalid_prompt_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(bad)

            mismatch = Path(tmp) / "mismatch.json"
            mismatch.write_text(json.dumps([{
                "name": "X",
                "description": "X",
                "template": "Hello {name}",
                "variables": ["topic"],
            }]), encoding="utf-8")
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(mismatch)


if __name__ == "__main__":
    unittest.main()
