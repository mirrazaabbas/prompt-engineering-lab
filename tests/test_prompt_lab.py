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

    def test_invalid_prompt_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            bad = folder / "bad.json"
            bad.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(bad)

            empty = folder / "empty.json"
            empty.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(empty)

            non_object = folder / "non-object.json"
            non_object.write_text('["bad"]', encoding="utf-8")
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(non_object)

            missing_field = folder / "missing.json"
            missing_field.write_text(json.dumps([{"name": "X"}]), encoding="utf-8")
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(missing_field)

            invalid_variables = folder / "variables.json"
            invalid_variables.write_text(
                json.dumps(
                    [
                        {
                            "name": "X",
                            "description": "X",
                            "template": "Hello {name}",
                            "variables": "name",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(invalid_variables)

            mismatch = folder / "mismatch.json"
            mismatch.write_text(
                json.dumps(
                    [
                        {
                            "name": "X",
                            "description": "X",
                            "template": "Hello {name}",
                            "variables": ["topic"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(mismatch)

            with self.assertRaises(ValueError):
                prompt_lab.load_prompts(folder / "missing-file.json")


if __name__ == "__main__":
    unittest.main()
