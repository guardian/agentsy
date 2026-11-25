* This plugin is and experiment and work in progress

# Code Modernisation for GitHub Copilot

A port of Anthropic's Claude code-modernization workflow to Copilot CLI and
VS Code. Describe a change in chat: the plugin investigates existing behavior,
helps review the rules and plan, establishes tests on the original application,
then implements and verifies a separate modernized version.

The workflow keeps Claude's stage responsibilities, specialist roles and saved
artifacts. An offline HTML report provides the overview and continuation prompts
in place of Claude-specific UI. Selected Guardian Agentsy practices guide E2E
setup, feature coverage, reusable BDD steps and optional pan-domain fixtures.

## Get started

Follow the [installation guide](docs/user/getting-started.md), then select
`modernize-start` in your client's plugin command picker and include your request:

```text
Migrate the search form from Angular to React, preserving its current behaviour.
```

In Copilot CLI, use `/editorial-tools-modernisation.code-modernisation:modernize-start`. In VS Code, select the
plugin's `modernize-start` entry. The plugin discovers project setup and chooses
necessary specialists and checks. You supply the outcome and constraints.

For a small first check, try the bundled [review example](docs/user/examples.md).
For an application journey, use the [project walkthrough](docs/user/project-walkthrough.md).

## Everyday use

| Request | Entry point |
| --- | --- |
| Assess a project, modernize a feature or resume saved work | `modernize-start` |
| Prepare tests without migrating the application | `modernize-setup-tests` |
| Read saved progress and the next action | `modernize-status` |
| Upgrade versions while preserving the stack and structure | `modernize-uplift` |
| Rewrite a selected module for a different stack | `modernize-transform` |
| Design and scaffold a replacement architecture | `modernize-reimagine` |
| Review security findings and proposed patches | `modernize-harden` |

Use ordinary follow-ups to correct scope, record intentional behavior changes or
pause. The [command guide](docs/user/commands.md) also covers review, planning,
transformation and verification entries.

Work stays in your application repository:

```text
analysis/<project>/    # Findings, progress, evidence and REPORT.html
legacy/<project>/      # Runnable original copy and tests
modernized/            # Separate candidates, with a folder for the chosen mode
```

The agent creates the report after assessment and refreshes it at saved
checkpoints. Open it locally in a browser, or continue through chat. See
[progress and continuation](docs/user/progress.md) for sharing work and returning
in a new session.

## Current scope

Meaningful tests on the unchanged original precede implementation. Reuse existing
native suites and supported reports, or prepare Playwright BDD coverage where it
fits the project. The BDD capture checks preserve a selected test cohort; upstream
proof checks additionally assess rule tracing, output comparisons, fresh inputs
and an independent regression canary. Each result keeps its own scope and limits.
You retain behavior decisions and acceptance.

The added uplift, reimagine, hardening and native-report paths still need live
consumer trials. Their availability does not imply complete compatibility with
every application or client.

See [supported scope](docs/user/supported-scope.md) for requirements and limits,
or [troubleshooting](docs/user/troubleshooting.md) for installation and execution
problems.

## License

[Apache 2.0](LICENSE). [NOTICE](NOTICE) records Anthropic and Guardian attribution;
[upstream.lock.json](upstream.lock.json) pins the retained upstream files.
Bundled report dependencies include their own license notices.
