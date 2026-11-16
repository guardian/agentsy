# Reuse local Playwright BDD capture

Use existing suitable project infrastructure first. These optional tools remove
repeated environment, process and evidence plumbing for a local Node application
with one Playwright-managed web server and Chromium on a POSIX host. They do not choose behavior,
write scenarios, approve rules or advance modernization stages.

## Prepare the project

Inspect the actual startup command, configuration, dependency lock, tests and
fixtures. Keep that setup in `PROJECT_SETUP.md`. Author the selected Gherkin and
step assertions from this application's behavior before application changes.

When no suitable BDD configuration exists, adapt
[`assets/playwright-bdd/playwright.config.mjs`](../../../assets/playwright-bdd/playwright.config.mjs)
into the covered project root. Fill in the discovered feature/step locations,
startup command and local address. The starter contains no business scenarios,
selectors or application registry. Keep its explicit browser executable binding
when using the supplied observer; a measured executable must be the configured
one. Inspect fixtures for overrides and document the limit of that observation.

Use installed local dependencies and an installed browser. The capture helper
does not install packages or download browsers. It expects a single local
`webServer` at `http://127.0.0.1:PORT`, no reuse of an existing server, and no additional global
setup/teardown. This uses [Playwright's own lifecycle](https://playwright.dev/docs/test-webserver)
instead of starting a second copy of the application. Review the command and its
effects before execution; loading a project configuration executes project code.

External services, authentication, containers, multiple servers or other required
environment facts need the project's existing adapter or a small extension with
its own checks. Do not remove those requirements just to fit this helper.

## Capture one attempt

Resolve `<plugin-directory>` as described in the skill. Use physical paths and a
new attempt directory under `analysis/<system>/`, outside the covered original
or candidate root as described in [workspace layout](workspace-layout.md). Inspect
the helper's `--help` and keep the exact invocation with the analysis record:

```text
<plugin-directory>/scripts/capture_playwright.py --root <physical-project-root> --attempt <new-attempt-directory> --config <root-relative-config> --url <loopback-url> --browser-executable <installed-Chromium-executable> --exclude node_modules --exclude test-results --timeout-seconds 180
```

Adapt exclusions to the actual project; keep application code, configuration,
locks, features, steps, fixtures and generated BDD specs in the source snapshot.
Installed dependencies are observed separately. Do not exclude changed tests or
source to obtain an eligible result. Use the same selected cases and supported
capture mechanism for legacy, candidate and independent attempts.

The helper retains actual generation, native listing and execution results,
before/after source snapshots, fresh environment observations and cleanup. It
calls the existing result and baseline validators. It preserves failures and
refuses to overwrite attempts; a retry needs a diagnosis and a new directory
within the operating limit. Inspect its summary and actual validator output,
not merely the helper's process exit. Timeout, interruption, missing observations,
changed inputs or incomplete cleanup cannot become a qualifying receipt.

The result validator output is `results-check.json`. `outcome.json`
uses the versioned `playwright-capture-outcome` contract with explicit lifecycle
checks; the report reads both it and older saved formats without inventing missing
checks. A `baseline-check.json` is a source/test check for whichever root was
supplied, not an original-application role declaration. Keep the actual roots and
evidence links clear in the workflow record. The report labels these checks with
an unclassified role; do not rename or rewrite evidence to force a completed card.

Review the project-specific configuration, startup and fixture behavior. Reuse
unchanged bundled code and its recorded checks; do not rebuild the same runner
for every application. New or materially changed lifecycle code still needs the
bounded controls and separate review in [project discovery](project-workflow.md).

## Reuse the evidence

Immediately before candidate creation or resumed implementation, collect a new
observation with `scripts/observe_node_environment.mjs` and run the normal
`baseline_evidence.py check`, following [baseline guidance](playwright-baseline.md).
Use the same installed Node as the captured execution:

```text
<installed-node> <plugin-directory>/scripts/observe_node_environment.mjs --root <physical-project-root> --browser-executable <installed-Chromium-executable> --url <same-loopback-url>
```

Use the same observed scope and installed browser; an old passing receipt alone
does not establish current eligibility. Preserve the actual new observation and
check output without rewriting historical attempts.

These are local observations of declared files and processes. They do not
authenticate evidence, sandbox project code, establish full environment coverage
or prove assertion quality. Keep additional relevant facts and unavailable
measurements explicit. A passing baseline remains separate from business
approval, candidate comparison and final acceptance.
