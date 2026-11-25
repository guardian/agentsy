# Getting started

## Requirements

- Copilot CLI or VS Code with Copilot Agent chat and plugin support, plus a
  working model connection.
- Access to the Guardian Agentsy repository for marketplace installation.
- Python 3.9+ and Node.js available as `python3` and `node` in the agent's
  execution environment. The optional E2E probe and auth helpers need Node 22+.
- A POSIX environment for the runtime helpers. Windows-native execution is
  unsupported.

Installing the plugin does not install Python or Node. The agent checks their
availability in the shell used for helpers and can reuse existing version-manager
installations. In a container, include these prerequisites in its setup so they
survive recreation. See [runtime troubleshooting](troubleshooting.md#a-runtime-is-missing).

A migration also needs the application's build tools and appropriate test runner.
The agent reuses existing native suites; browser tests need their browser tooling,
and the bundled BDD path uses Playwright BDD. The
[small review example](examples.md#try-a-small-review) needs no browser setup.
Use your project's approved execution environment; plugin consumers are not
required to adopt this plugin repository's development container.

## Install from Agentsy

Consumers can install through Copilot without checking out either repository or
installing the `agentsy` command. Copilot downloads and manages the plugin.

### Copilot CLI

Register the marketplace, then install the plugin:

```sh
copilot plugin marketplace add guardian/agentsy
copilot plugin install editorial-tools-modernisation.code-modernisation@agentsy
```

If Agentsy or your development environment already registered the `agentsy`
marketplace, run only the install command. The
[Agentsy README](https://github.com/guardian/agentsy#plugin-marketplace) describes
its marketplace; GitHub documents
[direct marketplace registration and installation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing).

Open your application folder and start `copilot`. No `--plugin-dir` argument is
needed for an installed plugin.

### VS Code

VS Code discovers plugins installed through Copilot CLI in the same environment.
Open **Chat: Open Customizations → Plugins** and confirm
`editorial-tools-modernisation.code-modernisation` is enabled for the intended
Copilot harness and workspace.

To install without using the CLI:

1. Open **Chat: Open Customizations**, then **Browse → Configure Marketplaces**
   from the source menu.
2. Add `guardian/agentsy` as a marketplace.
3. Browse that marketplace, select `editorial-tools-modernisation.code-modernisation`
   and choose **Install**.

See [VS Code's plugin installation guidance](https://code.visualstudio.com/docs/agent-customization/agent-plugins)
for the controls available in your version. In a remote or container window,
install in that environment so the Copilot session can load the plugin and its
runtimes.

## Install from a local package

Extract the supplied uncompressed `code-modernisation-0.4.0.tar` archive; its
accompanying `.tar.sha256` file provides the checksum for verification:

```sh
tar -xf code-modernisation-0.4.0.tar
```

Its plugin root is `plugins/editorial-tools-modernisation.code-modernisation/`,
the directory containing `plugin.json`. Keep its relative file layout intact and
store it separately from your application.

In VS Code, run **Chat: Install Plugin from Source** and enter the absolute path
to that plugin root. In Copilot CLI, open your application folder and load it with:

```sh
copilot --plugin-dir "/absolute/path/to/plugins/editorial-tools-modernisation.code-modernisation"
```

The agent checks the loaded package's runtime files and helper availability. A
source checkout is only needed when developing the plugin.

## Start a session

Start a fresh Copilot chat in your application folder. In CLI, send:

```text
/editorial-tools-modernisation.code-modernisation:modernize-start Assess this project and recommend a small first modernisation.
```

In VS Code, select the plugin's `modernize-start` entry from the `/` picker and
include your request. Use the entry displayed by your client if its formatting
differs.

Normal client permission prompts still apply. The model is chosen through your
client; the plugin has no required provider or fixed model.

## Make your request

An assessment request stops at findings and recommendations. A migration request
can continue through tests, implementation and verification within your scope:

> Migrate the search form from Angular to React, preserving its current behaviour.

Name the feature, target and constraints you care about. The agent discovers
commands, reuses suitable tests and prepares missing coverage. You own unresolved
behavior decisions and final acceptance.

The agent saves work under `analysis/<project>/`, prepares a runnable original
copy in `legacy/<project>/` and writes the changed version under `modernized/`,
using the selected mode's folder convention. See the
[project walkthrough](project-walkthrough.md) for the layout and handoff.

After an update, refresh the installed plugin and start a new chat. CLI installs
can be updated with `copilot plugin update editorial-tools-modernisation.code-modernisation`.
For a supplied package, install the replacement directory; an existing cache
does not automatically track edits to the original copy.
