# Prepare or repair an E2E setup

Use this reference for `modernize-setup-tests`, or when an authorized modernization
journey needs test infrastructure. This is preparation within the existing Claude
workflow, not a new modernization stage or controller. A setup-only request needs
a source and bounded test scope, not a migration target or approved implementation
brief. It does not authorize candidate creation, application changes or CI work.

## Discover and reuse

Read the existing intent, setup and workflow records, then inspect the selected
application's build/start commands, package manager, lockfiles, test configuration,
features, steps, fixtures and cleanup. Trace the services and authentication needed
for that scope. Discovery stays read-only; distinguish inspected commands from
executed checks. Preserve suitable existing tests, including tests outside BDD;
other runners use [native verification](upstream-verification.md) rather than the
captured Playwright BDD baseline gate. Preserve useful tests in either path.

Record findings in the existing `PROJECT_SETUP.md`, not another setup manifest:
source revision, permitted writes/services, dependency and auth boundaries,
real-versus-mocked decisions, toolchain needs and commands to validate. Reuse prior
decisions. Mock external dependencies by default; obtain an explicit decision
before running a previously unapproved Guardian service for real. Real means an
isolated local instance, not a deployed service. Ask only for unresolved scope,
access or behavior decisions, not filenames or routine implementation choices.

Use the project's package manager; default to npm only when none exists. Check
the installed application and test-tool requirements separately. Do not upgrade
the legacy runtime, SDK or build system merely to fit a new test stack. Prefer a
compatible, separately pinned test toolchain. If unchanged execution is impossible,
record the concrete blocker instead of changing the application or claiming a
baseline. Docker access, credentials and changes to a devcontainer require their
own established authorization; do not add a host socket or privileges implicitly.

## Plan coverage in small increments

Reuse the assessment's observed features, existing test preparation and the
selected scope. Inspect both user-facing components and relevant routes/services;
do not require a whole-application catalog for a bounded request. Check scenarios,
step definitions and recorded executions separately. A feature file on disk is
authored material, not runnable or verified coverage.

Keep an ordered `## Coverage plan` table in the existing `TEST_PLAN.md`,
`TEST_PROPOSAL.md` or `TEST_PREPARATION.md`. Use a short row per user outcome:

```markdown
## Coverage plan

| Order | Feature / outcome | Why next / dependencies | Test state | Evidence / gaps | Next action |
| --- | --- | --- | --- | --- | --- |
```

Prioritize important journeys and preservation risks, then shared fixtures/steps
and dependency boundaries that make later work cheaper. Give each ordering choice
a brief source-backed reason; do not rank purely by component size or impose a
fixed frontend-first sequence. Priorities are proposals, not human acceptance.

For each selected increment, write/refine its scenarios, wire the steps and run
them together before starting another increment. Reuse useful tests rather than
regenerating them. Record `Planned`, `Authored`, `Runnable`, `Execution recorded`
or `Blocked` as an agent note with the actual paths, result links and remaining
gaps. An execution can fail; record its outcome rather than calling it coverage.
Do not infer a pass from a state label, advance unrequested work or hide gaps to
complete a row. Preserve rule IDs and scope decisions. Update this current plan
without rewriting the historical assessment's initial coverage.

The HTML report shows these tables under Test readiness and keeps their source
links. Multiple plans remain separate; no newest or most favorable one is silently
selected. Existing free-form preparation notes remain usable.

## Prepare the smallest suitable setup

Read the bundled [local E2E recipes](../../../assets/e2e/README.md) before adapting
stack/fixture validation or pan-domain authentication. The working helper modules,
integration patterns, dependency version and safety limits are all provided locally.

Follow [workspace layout](workspace-layout.md): reuse or prepare the runnable
original copy under `legacy/<system>/`, leaving the active application unchanged.
Keep tests, fixtures, configuration and locks inside that tested root; keep evidence
under `analysis/<system>/`. Do not create `modernized/` for a setup-only request.
Preserve an existing test layout. If none exists, an `e2e-tests/` directory inside
the original copy can isolate test dependencies from the application's build.

Reuse existing Playwright configuration and its lifecycle owner. For a single
local Node server, use the [bundled starter and capture](local-bdd-capture.md).
Do not add Testcontainers or a second server controller when the existing setup
already runs the selected behavior. For missing multi-service infrastructure,
follow the [shared-stack command and ownership recipe](../../../assets/e2e/README.md#shared-multi-service-stack)
for `dev:local`, `test`, `test:ci`, `test:ui` and shared runtime connections.
Consider these patterns only where the project needs them:

- Testcontainers with an owned network, readiness checks, bounded startup and
  cleanup on success, failure and interruption. Prefer mapped ports; do not stop
  unrelated services. Bind only the selected source and necessary inputs, not
  the enclosing repository containing analysis or future candidates.
- WireMock for external HTTP boundaries, using one shared image and small
  service-specific fixtures. Do not mock the application behavior being measured.
  Prefer stack-level data/mocks for shared backing state over browser interception
  that bypasses the application's server or hides an integration failure.
- LocalStack only for AWS services actually used. Supply dummy credentials and a
  test region; exclude real profiles, SSO credentials and instance-role access.
  Verify endpoint configuration for the actual SDK, rather than assuming all SDKs
  honor the same environment variables. Refuse remote infrastructure, verify local
  routing, and treat unintended external requests as failures. Dummy credentials
  alone are not network isolation.
- The application's real authentication mechanism with synthetic users, explicit
  permissions and test-only keys. Use pan-domain fixtures only for applications
  that use pan-domain auth. Keep keys and generated state out of Git; never copy
  production cookies, personal data or credentials into fixtures or logs.

Keep generated build/runtime output separate from source and fixtures. Seed after
schema creation and reset mutable data between scenarios. Reuse working tooling,
pin new test dependencies and use the project's tool-version convention. A second
setup request must inspect and reuse these files and decisions, not replace the
suite, recreate the original tree or reinstall unchanged dependencies by default.

## Validate a bounded starter

Reuse existing validation commands. When checks are missing and the stack warrants
them, add small project-local `validate:stack` and `validate:fixtures` scripts;
do not invent a general-purpose runner. Each check must exit nonzero on failure,
use finite timeouts and clean up only resources it owns, including failed startup.
Use the bundled validation helper where appropriate and save its actual
`setup-check.json` output in a fresh attempt directory outside the tested root.
Keep stack, fixture and optional auth checks in separate attempt subdirectories.
Do not hand-author passing receipts or replace the existing baseline capture.

| Check | Required observation |
| --- | --- |
| Scaffold | Locked test dependencies and BDD configuration resolve; generation/listing identifies the intended selection. An empty scaffold is incomplete test setup, even if its command exits zero. |
| Stack | The selected application becomes ready against isolated dependencies; routing is local, logs have no unexplained errors, and owned resources are removed. |
| Fixtures | Required seed data, mock routes and permitted/denied identities match the selected behavior; unexpected unmatched requests and cleanup failures fail the check. |
| Starter tests | A nonempty bounded selection actually executes, including entry-page readiness and a meaningful outcome in the selected feature. Add a negative/permission case where relevant. Retain native results and actual process/cleanup outcomes. |

Use the requested feature; infer a small source-backed starter when scope is clear,
otherwise resolve the missing decision. Follow the
[scenario quality guidance](playwright-baseline.md#scenario-quality). Generate and
list before running; use one worker and zero retries for the starter check. Inspect
application/mock logs as well as assertions, distinguishing expected errors in
negative scenarios from unexplained failures. Fix fixtures or steps from evidence,
not by weakening the behavior under test. Keep failed attempts and bounded retry
decisions visible.

The bundled capture helper supports one local `webServer`, without global setup
or teardown. Testcontainers, multiple services and authentication may need the
existing project runner or a small reviewed adapter following
[execution and lifecycle checks](project-workflow.md#use-the-smallest-capture-mechanism).
Do not remove lifecycle or environment requirements to fit the bundled helper.
This reference does not supply or certify a generic container capture adapter.

## Document the suite

Create a README alongside every new suite, normally `e2e-tests/README.md` inside
the tested root. For an existing suite, update its README in the same change as
the setup, fixtures or commands. Give a newcomer enough information to run the
selected tests and add a feature without reconstructing the setup conversation:

- Purpose, covered scope and where features, steps, fixtures and setup code live.
- Actual prerequisites and installation commands: application/test runtimes,
  package manager, browser and container tooling only where required.
- Implemented commands for starting/stopping the stack, generating and running
  tests, UI mode, isolated runs, validation and viewing results or traces. Map
  existing script names to their roles; document CI only when it already exists.
- Local services, endpoints and real-versus-mocked boundaries; fixture seeding
  and reset; synthetic authentication and permission roles where used.
- Resource ownership and cleanup on success, failure and interruption, including
  which shared services remain running and how their owner stops them.
- How to add a feature and its steps, reuse shared fixtures, supply scenario
  evidence, regenerate specs and run the selected increment. Include common
  setup failures, useful log locations and any remaining gaps.

Use the implemented paths and commands, not unfilled template instructions.

## Save and stop at the requested boundary

Save the discovered commands, dependency choices and actual readiness results in
`PROJECT_SETUP.md`; starter coverage and gaps in `TEST_PREPARATION.md` (or an
existing recognized preparation record); and the next action/evidence links in
`WORKFLOW.md`. Follow the main skill's report checkpoint guidance.
Update the coverage table and link the chosen setup receipts under
`## Selected evidence` before refreshing. The report's Test readiness section
shows the ordered plan, named checks, cleanup and timestamps; unknown or malformed
results remain unverified. Its setup-only continuation prompts do not authorize
application changes or broader test execution.

Report scaffold, stack, fixtures and executed tests separately, marking unavailable
checks as blocked or unverified. Setup readiness is not preservation coverage,
baseline eligibility or human acceptance. A starter run qualifies as baseline
evidence only through the existing [baseline capture and checks](playwright-baseline.md);
the selected migration still needs its coverage review and current entry criteria.

For setup-only work, stop here and suggest the next short request. Do not create a
candidate, migrate code, add CI, commit, push or open a PR without a separate request.
For an already authorized modernization journey, return to its next unmet condition
without requiring another slash command. Reuse unchanged setup, but refresh affected
checks after source, fixture, configuration or environment changes. Old results
remain historical, not fresh observations.

## Reference provenance

All operational instructions are maintained in this package. Use the local
guidance and assets; do not fetch or require another plugin's skills to carry out
the workflow. [NOTICE](../../../NOTICE) records the inspiration and pinned source
revision for attribution, not as an execution dependency.

Mandatory phase PRs, application upgrades, fixed service topology and permissive
retry/no-tests defaults are not adopted. Existing authorization, unchanged-legacy
and evidence rules take precedence. These selected practices are not the complete
Guardian principles.
