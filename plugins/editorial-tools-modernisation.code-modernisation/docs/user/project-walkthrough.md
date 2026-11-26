# Modernize a local project in VS Code

This example uses an Angular application called `catalogue-app` and a search-form
migration to React. Substitute your application and desired change. Follow the
[installation requirements](getting-started.md) first. The agent reuses suitable
native tests or prepares meaningful coverage before implementation; Playwright
BDD is the bundled browser-testing path.

## Open your existing application

Open the application repository in VS Code and install the plugin from its
separate directory. Start a new Agent chat with your configured model.

```text
catalogue-app/
├── .git/
├── src/
└── e2e/          # Existing tests and setup, if present
```

Use your usual branch workflow. The agent prepares modernization folders as the
work needs them.

## Start with a short request

Select `modernize-start` and ask for an assessment:

```text
/editorial-tools-modernisation.code-modernisation modernize-start Assess this Angular application for migration to React and recommend a small first step.
```

The agent inspects the project, records features and existing coverage, recommends
starting slices and links an HTML report. Choose a slice in ordinary conversation:

> Migrate the search form first, preserving its current behaviour.

You can also request that migration directly. The agent discovers setup, reuses
suitable tests, fills relevant gaps, measures original behavior, implements a
separate candidate and verifies it. Essential behavior decisions remain yours.

## Keep the work in your project repository

The agent uses this layout:

```text
catalogue-app/
├── .git/
├── src/                              # Existing active application
├── e2e/
├── legacy/
│   └── catalogue/                    # Runnable original copy
│       ├── src/
│       └── e2e/                      # Original characterization tests
├── modernized/
│   └── catalogue/
│       └── search/                   # Runnable candidate and retained tests
└── analysis/
    └── catalogue/
        ├── INTENT.md                 # Goal and actual decisions
        ├── PROJECT_SETUP.md          # Commands, environment and locations
        ├── ASSESSMENT.md             # Initial findings and suggested slices
        ├── WORKFLOW.md               # Current work, evidence and next action
        ├── TEST_PLAN.md              # Preparation and coverage notes
        ├── VERIFICATION.md           # Results and limits
        ├── REPORT.html               # Generated overview
        └── attempts/                 # Saved execution evidence
```

Records appear as their work happens. Tests live inside the relevant runnable
application tree; preparation notes record their coverage and gaps. The agent may
reuse an existing preparation filename and links its actual location.

`catalogue` is a short project name, reused across features and sessions. The
folders follow the Claude plugin's project-root layout. This port uses a real
original copy so the original and candidate remain physically separate. A
runnable copy may contain the whole application even when only one feature is
being changed.

Existing application files stay in place. If the default folder names conflict
with your project, the agent preserves them and records a suitable alternative.
Existing work elsewhere can continue from its saved locations.

This example uses transform's `modernized/<project>/<module>/` path. Uplift keeps
the complete working copy in `modernized/<project>-uplifted/`; reimagine puts its
approved services under `modernized/<project>-reimagined/<service>/`. These mode
names follow the original plugin and let its proof checks identify the work.

## Review progress and results

Open `analysis/catalogue/REPORT.html` or select `modernize-status`:

> Show the saved position in `analysis/catalogue/`.

The result points to actual tests, candidate code, evidence, gaps and next steps.
The report separates the initial assessment from current work and selected runs
from previous attempts. See [progress and continuation](progress.md) for reading
readiness and verification results.

After verification and your acceptance, integrating the candidate into the active
application is a separate requested step.

## Share progress through Git

Use the application's existing repository and review the files needed for handoff:
original and candidate source, tests, configuration, analysis records and required
shareable evidence. Exclude dependencies, generated builds, caches and secrets
with targeted ignore rules. Keep the modernization folders trackable.

An ordinary request can prepare the review:

> Save the current position and prepare a commit of the modernization work so a teammate can continue. Don't push yet.

Push through your normal Git workflow. If required evidence must remain outside
Git, record where a teammate can retrieve it. The HTML page alone cannot replace
source, test code and execution records.

## Continue yourself or hand over to a teammate

Open the application repository at the branch containing the saved work. Install
the plugin separately, start a fresh chat and select `modernize-start`:

> Resume the saved work in `analysis/catalogue/`.

The agent uses project-relative continuation paths, preserves earlier findings and
decisions, and checks what changed. A different checkout or environment requires
fresh observations before earlier evidence can support a current pass. Original
receipts retain their original execution facts.
