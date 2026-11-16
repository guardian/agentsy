# Troubleshooting

## The plugin or command is missing

In VS Code, use **Chat: Open Customizations → Plugins** to check that
`code-modernisation` is enabled for the intended workspace and agent. Confirm
plugin support is enabled, then start a fresh chat and select the command from
the `/` picker. See [getting started](getting-started.md#vs-code) and
[VS Code's plugin guidance](https://code.visualstudio.com/docs/agent-customization/agent-plugins#troubleshooting).

In CLI, `--plugin-dir` must name the folder containing `plugin.json`. Quote paths
containing spaces. If you updated source files, refresh the installed copy;
client caches may still contain older files.

## A helper has no execute permission

The workflow checks the actual loaded package and can repair missing execute bits
on verified helpers. For manual diagnosis, use the loaded path reported by the
agent, which may differ from the source checkout:

```sh
plugin_dir="/absolute/path/to/loaded/plugin"
python3 "$plugin_dir/scripts/check_installation.py" --plugin-root "$plugin_dir"
```

The check verifies runtime file identities and invokes helper help commands. If
it reports `repairEligible: true`, the supported repair is:

```sh
python3 "$plugin_dir/scripts/check_installation.py" --plugin-root "$plugin_dir" --repair-execute-bits
```

This repairs only missing executable modes on the allowlisted files. For missing
or mismatched content, refresh the complete package from a trusted source.

## A command is denied or a runtime is missing

Check the actual permission request and grant the access appropriate to your
task. Preserve the failing command and error if access remains unavailable.
The agent must respect a denial rather than switch execution methods to bypass it.

Make `python3` and `node` available in the client's execution environment and
retry readiness. Application dependencies, browser tooling and service access
are separate requirements for test execution. Use
[supported scope](supported-scope.md) to identify the relevant boundary.

## No specialist ran, or the model is unknown

Specialist execution depends on the client's available delegation tools. Supported
VS Code Local/BYOK sessions can inherit the parent's model; CLI tasks use explicit
selection where supported. The agent should record what actually ran and identify
unknown routing.

Refresh the plugin and start a new chat if instructions appear outdated. You
should not need to supply specialist sequences or hardcode a model. Permitted
work may continue in the main session when delegation is unavailable, with its
independence limitation recorded.

## Verification says evidence is stale

Source, test, dependency, browser or environment changes can affect a baseline.
Have the agent inspect what changed and refresh the necessary measurements.
Keep earlier receipts as records of their original runs.

## The report is missing or out of date

The agent creates the report after assessment and refreshes it at saved
checkpoints. Reload the browser page after regeneration. For a refresh request:

> Refresh the HTML report for `analysis/catalogue/`.

Use your actual analysis directory. This rebuilds the view without rerunning
verification. A status-only request reads saved work and does not refresh it.

If rendering fails, continue using the saved Markdown and evidence. An empty
section can mean the corresponding work is unrecorded. See
[progress and continuation](progress.md) for report semantics.

## Report a problem

Include plugin/client versions, the request, exact error, relevant output paths
and any manual steps needed. Share only relevant records, with application
secrets and personal data removed.
