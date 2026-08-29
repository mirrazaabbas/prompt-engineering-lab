import json
import re
from pathlib import Path
from typing import Any

PROMPTS_FILE = Path(__file__).resolve().with_name("prompts.json")
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")


def load_prompts(path: Path = PROMPTS_FILE) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Prompt library not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Prompt library contains invalid JSON: {exc}") from exc

    if not isinstance(data, list) or not data:
        raise ValueError("Prompt library must be a non-empty JSON array.")

    for index, prompt in enumerate(data, 1):
        if not isinstance(prompt, dict):
            raise ValueError(f"Prompt entry {index} must be an object.")
        for field in ("name", "description", "template", "variables"):
            if field not in prompt:
                raise ValueError(f"Prompt entry {index} is missing '{field}'.")
        if not isinstance(prompt["variables"], list) or not all(isinstance(v, str) and v for v in prompt["variables"]):
            raise ValueError(f"Prompt entry {index} has invalid variables.")
        placeholders = set(PLACEHOLDER_RE.findall(prompt["template"]))
        declared = set(prompt["variables"])
        if placeholders != declared:
            raise ValueError(
                f"Prompt '{prompt['name']}' variable mismatch: template={sorted(placeholders)}, declared={sorted(declared)}"
            )
    return data


def build_prompt(template: dict[str, Any], values: dict[str, str]) -> str:
    expected = set(template["variables"])
    missing = expected - set(values)
    if missing:
        raise ValueError(f"Missing values for: {', '.join(sorted(missing))}")

    cleaned = {key: str(values[key]).strip() for key in expected}
    empty = [key for key, value in cleaned.items() if not value]
    if empty:
        raise ValueError(f"Values cannot be empty for: {', '.join(sorted(empty))}")

    prompt = template["template"]
    for key in expected:
        prompt = prompt.replace("{" + key + "}", cleaned[key])

    unresolved = PLACEHOLDER_RE.findall(prompt)
    if unresolved:
        raise ValueError(f"Unresolved template variables: {', '.join(sorted(set(unresolved)))}")
    return prompt


def choose_template(prompts: list[dict[str, Any]]) -> dict[str, Any]:
    print("\nPrompt Engineering Lab\n")
    for index, prompt in enumerate(prompts, start=1):
        print(f"{index}. {prompt['name']} — {prompt['description']}")

    while True:
        try:
            choice = int(input("\nChoose a template: "))
            if 1 <= choice <= len(prompts):
                return prompts[choice - 1]
        except (ValueError, EOFError):
            pass
        print("Please enter a valid number.")


def main() -> None:
    try:
        prompts = load_prompts()
        selected = choose_template(prompts)
        values = {}
        for variable in selected["variables"]:
            values[variable] = input(f"{variable.replace('_', ' ').title()}: ")
        final_prompt = build_prompt(selected, values)
    except (ValueError, EOFError, KeyboardInterrupt) as exc:
        raise SystemExit(f"Error: {exc}") from exc

    print("\n--- Generated Prompt ---\n")
    print(final_prompt)


if __name__ == "__main__":
    main()
