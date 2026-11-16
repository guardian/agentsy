# Commands and conversation

For most work, select `modernize-start` and describe the outcome in the same chat
message. The agent follows the relevant stages and saves its progress.

| Client      | Entry command                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| Copilot CLI | `/code-modernisation:modernize-start`                                                                  |
| VS Code     | Select the plugin's `modernize-start` entry; clients may display `/code-modernisation modernize-start` |

## Short requests

- **Assess:** “Assess this project and recommend a small first modernisation.”
- **Review:** “Review the checkout module and propose tests that protect its
  current behaviour. Stop before implementation.”
- **Migrate:** “Migrate the search form from Angular to React, preserving its
  current behaviour.”

Use the open application folder or supply a source path. Include constraints such
as “Keep the current URLs” or “Stop after the brief.” The plugin discovers setup
and chooses the appropriate helpers and specialists.

## Correct, pause and continue

Use ordinary follow-ups:

> Focus on the search form first. Leave the results list unchanged.

> That behaviour is a bug we want to fix; record it as an intentional change.

> Pause here and save what remains to be done.

> Resume the saved work in `analysis/catalogue/`.

A correction updates the affected plan and checks while preserving unrelated
work and earlier results. In a new chat, select `modernize-start` with the resume
request. The agent reads saved records and checks what changed.

## Other entry commands

| Command                   | Purpose                                                                |
| ------------------------- | ---------------------------------------------------------------------- |
| `modernize-setup-tests`   | Prepare or repair Playwright BDD setup and a small starter suite       |
| `modernize-status`        | Read saved progress, gaps, open decisions and the next action          |
| `modernize-preflight`     | Check source completeness, boundaries and build/test readiness         |
| `modernize-assess`        | Assess structure, debt, risks and modernization options                |
| `modernize-map`           | Map calls, data relationships, entry points and user flows             |
| `modernize-extract-rules` | Extract source-backed behavior rules and data objects                  |
| `modernize-review`        | Review behavior findings and record your decisions                     |
| `modernize-brief`         | Create or update the implementation brief                              |
| `modernize-uplift`        | Move to an exact newer version of the same stack, preserving structure |
| `modernize-transform`     | Implement a separate candidate after decisions and baseline checks     |
| `modernize-reimagine`     | Design and scaffold an approved architecture from retained intent      |
| `modernize-verify`        | Compare candidate behavior with the original and report gaps           |
| `modernize-harden`        | Review security risks and prepare reviewed remediation patches         |

Use the same client prefix as `modernize-start`. These entries let you request a
particular phase; a later entry still checks its prerequisites. A migration
request can continue across supported phases without another command from you.
`modernize-status` reads saved work without advancing it.

Uplift needs the exact source and target versions. Reimagine needs your decisions
on essential or dropped capabilities and approval of the concrete architecture
before scaffolding. Pending scaffold tests remain unfinished behavior. Hardening
produces findings and proposed patches; applying them is a separate decision.

## Prepare tests first

Select `modernize-setup-tests` and describe the feature to exercise:

```text
/code-modernisation modernize-setup-tests Prepare the E2E setup for this application's search form. Reuse existing tests and stop before migration.
```

In CLI, use `/code-modernisation:modernize-setup-tests` with the same request.
No migration target is needed. The agent discovers dependencies and authentication,
reuses suitable infrastructure, prepares the original test copy and executes a
bounded starter suite. It records the commands, results, coverage gaps and next
action, then refreshes the report. Repeating the request reuses existing work.

Guardian-informed recipes include stack and fixture probes, incremental
feature/step planning and optional pan-domain auth. These are bundled locally;
no other skill installation is required. Test-library dependencies are installed
in the project's test setup when needed.

Setup-only work ends after preparation and validation. It does not change the
application, create a candidate, add CI or publish work. The starter establishes
setup readiness; a migration still needs adequate coverage and a current baseline.
Normal modernization uses the same preparation guidance when necessary.

For multi-service stacks, the agent uses the project's lifecycle and a suitable
capture integration. The bundled capture helper supports one local web server.
See [supported scope](supported-scope.md) and the report's
[Test readiness section](progress.md#test-readiness).

## Where results go

The default folders are inside your application's repository:

| Folder                                       | Contents                                                     |
| -------------------------------------------- | ------------------------------------------------------------ |
| `analysis/<project>/`                        | Findings, decisions, progress, report and shareable evidence |
| `legacy/<project>/`                          | Runnable original copy and prepared tests                    |
| `modernized/<project>/<module>/`             | Transform candidate and its tests                            |
| `modernized/<project>-uplifted/`             | Whole working copy for a same-stack uplift                   |
| `modernized/<project>-reimagined/<service>/` | Services in the approved replacement architecture            |

The agent creates these as needed and links the actual locations. `INTENT.md`
holds the goal and decisions; `PROJECT_SETUP.md` records commands and environment;
`WORKFLOW.md` identifies current work, selected evidence and the next action.
Assessment, brief, test and verification records provide the supporting detail.

`REPORT.html` brings these records together. Ask “Refresh the HTML report from the
saved records” to rebuild just the view, or ask to omit HTML. See
[progress and continuation](progress.md) for reviewing results and returning later.
