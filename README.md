Agentsy
=======

Support and empower engineers' use of Agentic AI.

## Instructions

### Writing style instructions

The [`writing-style.instructions.md`](instructions/writing-style.instructions.md)
instructions give Copilot guidance for plain repository documentation, comments,
commit messages, and pull request descriptions.

## Scripts

### OpenAI-backed Copilot CLI

Runs GitHub Copilot CLI against a supported OpenAI model using Copilot's BYOK support. It requires `copilot` on `PATH`
and `OPENAI_API_KEY` in the environment.

```bash
scripts/openai-copilot <model_id> [copilot_args...]
```

Supported model IDs are `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, and `gpt-6-astra`.

## Development

### TUI style guide

The repository's terminal output conventions are documented in [`STYLE_GUIDE.md`](STYLE_GUIDE.md). This style guide is
implemented in [terminal-style.sh](scripts/lib/terminal-style.sh).
