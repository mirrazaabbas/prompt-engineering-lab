# AI platform compatibility

The prompt library and template renderer work fully offline. Rendered prompts can optionally be sent through the shared `AIClient` interface to OpenAI/OpenAI-compatible APIs, Anthropic Claude, or Google Gemini.

## Offline verification

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -c "import prompt_lab; assert len(prompt_lab.load_prompts()) >= 3"
```

No API key is required for these checks.

## Provider selection

```bash
# OpenAI or OpenAI-compatible
export AI_PROVIDER=openai
export AI_API_KEY="YOUR_KEY"
export AI_MODEL="YOUR_CHAT_MODEL"
# Optional: export AI_BASE_URL="https://provider.example/v1"
```

```bash
# Anthropic Claude
export AI_PROVIDER=anthropic
export AI_API_KEY="YOUR_KEY"
export AI_MODEL="YOUR_CLAUDE_MODEL"
```

```bash
# Google Gemini
export AI_PROVIDER=gemini
export AI_API_KEY="YOUR_KEY"
export AI_MODEL="YOUR_GEMINI_MODEL"
```

## Run a rendered prompt on the selected provider

```bash
python - <<'PY'
from ai_features import run_prompt
from ai_platform import create_ai_client

prompt = "Create a concise implementation plan for a reliable RAG assistant."
print(run_prompt(prompt, create_ai_client()))
PY
```

Provider selection is entirely environment-driven, so prompt templates stay vendor-independent.
