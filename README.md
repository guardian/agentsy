Agentsy
=======

Support and empower engineers' use of Agentic AI.

## Scripts

### OpenAI-backed Copilot CLI

Runs GitHub Copilot CLI against an OpenAI GPT-5.6 model using Copilot's BYOK support. It requires `copilot` on `PATH`
and `OPENAI_API_KEY` in the environment.

To install it in a dev container, first authenticate GitHub CLI with access to this repository, then run:

```bash
AGENTSY_REF=kc/openai bash -o pipefail -c 'gh api -H "Accept: application/vnd.github.raw+json" "/repos/guardian/agentsy/contents/scripts/install-openai-copilot?ref=$AGENTSY_REF" | bash'
```

This installs the command at `~/.local/bin/openai-copilot` and its support library under `~/.local/lib/agentsy`.
If `~/.local/bin` is not on `PATH`, the installer prints the line to add to the current shell's startup file. Rerun
the command to update the installation from the latest `kc/openai`. `AGENTSY_REF` ensures the installer and the files
it installs all come from the same branch; it defaults to `main` when omitted.

Run the installed command from any directory:

```bash
openai-copilot <model_id> [copilot_args...]
```

When working in this repository, it can also be run without installing:

```bash
scripts/openai-copilot <model_id> [copilot_args...]
```

Supported model IDs are `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`.

## Development

### TUI style guide

The repository's terminal output conventions are documented in [`STYLE_GUIDE.md`](STYLE_GUIDE.md). This style guide is
implemented in [terminal-style.sh](scripts/lib/terminal-style.sh).
