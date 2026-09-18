Agentsy
=======

Support and empower engineers' use of Agentic AI.

## Features

Agentsy exposes features from this checkout inside a devcontainer. It currently
supports scripts and GitHub Copilot CLI instructions.

```bash
agentsy list
agentsy list --type instructions
agentsy enable script openai-copilot
agentsy enable instructions writing-style.instructions.md
agentsy disable instructions writing-style.instructions.md
```

`enable` creates an absolute symlink from the feature in this checkout to the
location used by the devcontainer:

| Type | Destination |
|---|---|
| Script | `~/.local/bin/<name>` |
| Instructions | `~/.copilot/instructions/<filename>` |

Running the same `enable` or `disable` command more than once is safe. Agentsy
will not replace an existing path that points elsewhere, and it will only
remove links to features in the current checkout.

Run `agentsy` without arguments in an interactive terminal to open the feature
manager. Use the Up and Down arrow keys to select a feature, Space to enable or
disable it, and `q` or Esc to exit. The interface shows `[x]` for enabled
features and `[!]` when an existing destination prevents Agentsy from managing
a feature. It has no dependencies beyond Bash and an ANSI-compatible terminal.

### Available features

#### Instructions

##### Writing style instructions

The `writing-style.instructions.md` instructions give Copilot guidance for
plain repository documentation, comments, commit messages, and pull request
descriptions.

#### Scripts

##### OpenAI-backed Copilot CLI

The `openai-copilot` script runs GitHub Copilot CLI against a supported OpenAI
model using Copilot's BYOK support. It requires `copilot` on `PATH` and
`OPENAI_API_KEY` in the environment.

```bash
openai-copilot <model_id> [copilot_args...]
```

Supported model IDs are `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, and
`gpt-6-astra`.

## Devcontainer setup

External devcontainer setup tooling is responsible for cloning this repository
to `~/agentsy` and placing the root `agentsy` entrypoint on `PATH`. Feature links
continue to use the files in that checkout, so updating the checkout also
updates every enabled feature.

## Development

### TUI style guide

The repository's terminal output conventions are documented in
[`STYLE_GUIDE.md`](STYLE_GUIDE.md). This style guide is implemented in
[terminal-style.sh](scripts/lib/terminal-style.sh).

### Validation

Run the dependency-free shell tests and ShellCheck with:

```bash
tests/agentsy-test.sh
shellcheck agentsy scripts/openai-copilot scripts/lib/*.sh tests/*.sh
```
