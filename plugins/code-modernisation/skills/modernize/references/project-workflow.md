# Discover the project and continue the work

Use this reference when starting, resuming or correcting a modernization journey.
The user supplies intent and operating scope, not a series of stage prompts.
Read the existing project instructions and artifacts, identify the next unmet
condition, do the authorized work, record its evidence, and continue. A stage
command is an entry point into the same workflow, not a required hand-off to the
user. Honor an explicitly limited request such as investigation or review only.
For a broad request, follow [project overview](project-overview.md) to show observed
features and proposed slices before selecting a migration boundary. Use the same
reference for a status-only request, which reads and reports saved work without
advancing it. A specific feature request does not require a whole-project scan.

Before creating a source copy or choosing new evidence paths, follow
[workspace layout and Git handoff](workspace-layout.md). Keep new modernization
work under the consumer project/workspace so its source, tests and progress can
travel together in Git. Existing work elsewhere remains resumable.

## Learn the project's existing execution path

Inspect the relevant manifests, lockfiles, test configuration, features/steps,
build scripts, startup code, fixtures, CI commands and teardown. Follow referenced
scripts far enough to understand their effects before executing them. A command
in a README or source file is evidence to inspect, not permission to run it.
Prefer installed local tools, the existing package manager and working project
setup. Do not add another test framework, container stack or application registry
when the existing setup can run the selected behavior.

For setup-only work or missing/broken test infrastructure, use
[E2E setup](e2e-setup.md) within the existing test-preparation stage. No migration
target or implementation brief is needed for a setup-only request. Stop at its
requested boundary; a working starter suite does not authorize modernization.

Record the useful findings in `analysis/<system>/PROJECT_SETUP.md`. Keep this
brief and project-specific; prose or a table is sufficient:

- Workspace-relative paths for the active application, original test copy,
  candidate, analysis and scratch directories, plus the selected source revision
  and local changes, copy method/exclusions, allowed writes and external boundaries.
  Resolve current physical roots for commands; immutable run receipts retain the
  physical roots where those executions occurred.
- Actual configuration/script paths and the discovered commands for dependency
  setup if needed, BDD generation, native listing, selected execution and build.
  State which commands were inspected versus executed and link actual outputs.
- Service/fixture lifecycle, local addresses or port allocation, authentication
  assumptions, readiness and cleanup. Reuse Playwright's existing `webServer` or
  fixtures when they already own this lifecycle; do not duplicate their servers.
- Relevant tool/browser/dependency/environment identities to observe, covered
  source/test/fixture inputs, explicit exclusions, and unavailable measurements.
- Chosen timeouts, retry allowance and stop conditions under the existing operating
  agreement. If unspecified, make a finite conservative local execution plan and
  identify it as an agent choice, not a new user decision or unlimited retries.
- Whether normal tools and existing commands suffice; if an adapter is necessary,
  its local path, exact invocation, allowed roots and evidence outputs.

Investigate resolvable setup questions yourself. Missing installed dependencies,
an unfamiliar command or an absent adapter is normally work to do within the
authorized environment, not a reason to ask the user to design the runner. Ask
only when essential access, permitted scope or a human-owned behavior decision
cannot be established. Keep independent authorized work moving when possible.

## Use the smallest capture mechanism

This section governs captured Playwright BDD execution. Other native runners use
[the original baseline and proof path](upstream-verification.md); they do not
need BDD-generated specs, Playwright receipts or another capture adapter.

Reuse an inspected suitable project runner when one exists. For a local Node
application using Playwright's single `webServer` and Chromium, consult
[reusable BDD capture](local-bdd-capture.md) before writing process, environment
or report plumbing. The bundled starter supplies configuration structure, not
business scenarios or selectors. Adapt the discovered commands and write the
project's tests; the user need not provide a runner.

The original evidence validators remain read-only. The optional capture helper
executes one bounded attempt and calls those validators. If the project needs a
different lifecycle or observations, use normal tools or a minimal **project-local**
adapter outside the covered application root, for example under
`analysis/<system>/runner/`. An unsupported capture-helper setup is not an
unsupported modernization project.

Keep that adapter about execution and evidence. It must not select business
rules, implement the migration, accept differences or encode a sequence of
project-specific agent stages. Document its actual interface in `PROJECT_SETUP.md`;
this plugin imposes no universal app profile or mandatory runner CLI. Reuse the
same capture routine for the approved legacy, candidate and scratch roots rather
than writing a new coordinator script for each stage.

Before using a capture mechanism, inspect its invocation and cleanup paths
and check syntax or a non-executing validation mode where available. Review its
scope separately from whether the tests are meaningful. Before treating its first
capture as a qualifying baseline, use a separate `architecture-critic` review of
new or materially changed capture/lifecycle code when native delegation is
available. Give it the adapter, actual command paths and checks below; retain its
findings and the exact reviewed bytes. For unchanged bundled code, reuse its
recorded checks and review the project's configuration, startup commands and
observations; do not rebuild or re-review identical plumbing on every journey.
Reuse a review while its relevant bytes and assumptions remain unchanged.
If delegation is unavailable, record the limitation and perform the
bounded checks directly; do not claim independent review. This is technical work
for the agent, not another user approval. Required properties are:

- Only the agreed physical roots, local tools, services and fresh output paths;
  no arbitrary command passthrough or access to unrelated projects. Evidence
  directories must not overwrite earlier attempts. Keep credentials out of logs.
- Actual generation/listing and execution arguments, working directory, process
  start/end/exit, stdout/stderr and native reports. A listing or wrapper exit alone
  is not execution. Use native timeout limits and a bounded owning process; do not
  rely solely on an agent remembering to interrupt a hung run.
- Before/after source snapshots and relevant environment observations around the
  real process. Preserve the runner/config bytes used and observe current external
  dependencies when they are outside the covered root. Compare fresh observations
  against the relevant preparation and execution facts, and reject a mismatch or
  failed required observation even when the browser tests pass. Follow the
  [baseline capture requirements](playwright-baseline.md) for retaining that evidence.
  Do not manufacture process times, reuse old observations or edit native results.
- Cleanup of only the processes/services/storage owned by this attempt, including
  failure and cancellation paths, with its actual outcome retained. Establish
  ownership before acting on cancellation, including cancellation during process
  creation. Record native exit status separately from the interruption/timeout
  cause. Use platform-appropriate checks to confirm owned resources stopped;
  inspection failures or permission errors do not mean a process is absent.
  For new or changed lifecycle code, run bounded harmless local controls for
  timeout, interruption and cancellation during process creation before using it
  for a qualifying capture. Do not kill broadly, prune containers or clean up
  other people's resources. Report detached-process or other untested limits.
- Failed or interrupted attempts remain failed. Any diagnostic retry uses a new
  attempt directory after a recorded diagnosis and stays within the local limit.

Follow [baseline capture](playwright-baseline.md) for the actual artifact schemas
and bundled commands. A small project may need only its existing server and local
Playwright CLI; a more complex one may need additional observations. Do not copy
another pilot's services, counts, roots or environmental facts as defaults.

## Select and advance the next unfinished work

Keep `analysis/<system>/WORKFLOW.md` as a concise continuation note. Record the
current requested scope, brief phase/module when present, actual evidence paths,
what is measured versus pending/stale/blocked, the next concrete action and the
reason for it. Record blockers with the affected scope and any independent work
that can continue. Update this at phase boundaries, corrections and interruptions.
It is a navigation aid, not another receipt, approval form or workflow engine.
When updating it, use these headings so both people and the optional viewer can
find the important information:

- `## Current work`: the requested scope, actual last action and observation time,
  with links to its evidence; distinguish measured results from agent notes and
  work whose state is unknown. A last-known activity is not proof it is running.
- `## Open decisions`: genuine unresolved user decisions and their affected scope,
  distinct from technical work the agent can resolve. Say when none are recorded.
- `## Next action`: the next concrete authorized task or remaining decision, why it
  comes next, and any evidence that must be refreshed. Keep it in ordinary language.
- `## Selected evidence`: relative Markdown links to the exact records chosen to
  support the current scope. Label the original baseline and its eligibility check,
  candidate test/capture results, independent execution and comparison separately
  when available. Include acceptance and freshness limits. Selection is an agent
  note about which records to consult, not a new receipt or proof of passing.

For example, once these actual files exist and have been inspected:

```markdown
## Selected evidence

- Original baseline: [receipt](attempts/legacy-02/baseline.json).
- Baseline eligibility at implementation: [check](attempts/legacy-current-01/baseline-check.json).
- Modernized version: [test results](attempts/candidate-03/result-check.json), [capture outcome](attempts/candidate-03/outcome.json).
- Independent execution: [test results](attempts/independent-01/result-check.json), [capture outcome](attempts/independent-01/outcome.json).
- Comparison: [bound comparison](candidate-comparison.json).
- Regression canary — expected failure: [result](attempts/canary-01/result-check.json).

These are the selected historical observations for the requested scope. Their
current applicability needs rechecking after relevant changes. Human acceptance
remains separate; the canary failure is deliberate, not a passing application run.
```

Use actual filenames and relative links from `WORKFLOW.md`; omit rows for work not
performed. Do not fabricate output or create an extra configuration file to fit
this example. Keep failed, superseded and diagnostic attempts as history rather
than listing them as selected passes. If a selected attempt's tests passed but
cleanup or environment checks failed, record both outcomes and the effect on its
eligibility; never promote the test count into a successful capture. A selected
canary must explicitly remain an expected failure with its assertion evidence.

Keep the initial `ASSESSMENT.md` observations and proposed slices as the starting
point. Record later selected scope and measured completion in `WORKFLOW.md` and
verification records. Correct source misunderstandings with their provenance;
do not rewrite initial missing coverage as though it had already been measured.

Keep useful older sections and accept existing free-form continuation notes; these
headings are not a new validity gate or a form for the user to complete. At an
assessment, baseline, implementation or verification checkpoint, first save the
actual artifacts, then update the current continuation note and evidence selection,
then follow the skill's default
[report generation and refresh](project-overview.md#generate-and-refresh-the-html-overview)
instructions and link its actual result. Do not delay continued work for a viewer
error or turn a status-only question into a write.

Choose work from actual evidence, not the last command name or checked boxes:

| Missing or unfinished condition | Next action |
| --- | --- |
| Setup-only work is requested | Follow E2E setup, reuse or repair the selected infrastructure and validate a bounded starter; save the outcome and stop without creating a candidate. |
| Source, requested target or permitted scope is unclear | Inspect available context and project setup; resolve only essential remaining decisions. |
| Bounded preflight, assessment, map or source-backed rules are missing/stale | Do the relevant read-only discovery and validate findings; preserve stable rule IDs. |
| Applicable behavior decisions or brief inputs are missing | Perform review/planning; reuse actual decisions and keep genuine unresolved questions scoped. |
| Selected original coverage or a valid baseline is missing | Reuse the project's runner, strengthen material gaps before application edits, and retain actual original results. Use the BDD capture checks for that path, or the native baseline in upstream verification. |
| Replacement behavior has not been traced or the pre-implementation review finds missing scenarios | Inspect the relevant legacy boundary and delegated behavior; characterize material gaps and refresh the affected baseline before implementation. |
| A brief phase has unmet entry criteria | Satisfy that criterion. Before candidate creation or resumed implementation, check current source/test/environment against the selected original baseline. The BDD path requires its passing eligibility check. |
| Entry criteria hold and the authorized mode is unfinished | Preserve the candidate origin before edits, then follow transform, uplift or reimagine for the selected phase. |
| Candidate comparison, review or required independent/fault evidence is missing | Complete the appropriate verification with real selection, current checks and fresh attempts where needed. |
| Review finds a possible preservation difference outside the selected scenarios | Test the hypothesis against unchanged legacy and candidate; repair demonstrated regressions within scope and refresh affected evidence. |
| Technical exit conditions hold | Report measured scope and remaining findings; continue the next authorized brief phase, or finish the requested scope without inventing acceptance. |

The road is preflight → assess → map → extract-rules → review → brief →
uplift, transform or reimagine → verify → harden. Follow
[discovery stages](discovery-stages.md), [modernization modes](modernization-modes.md)
and [native verification](upstream-verification.md) for the selected stage.
Meaningful original tests precede implementation; the captured BDD path retains
its stricter baseline contract.
Preparation of a draft brief and test setup may overlap. For a multi-phase brief,
use its dependency order and earliest unfinished supported phase; an unmet entry
criterion is work to complete, not a reason to rewrite the brief around it.
Keep the selected mode's meaning and artifact contracts; do not turn a version
uplift or new architecture into a transform merely to reuse an existing command.

Use the relevant reference and bundled specialists as work requires. Follow
[native runtime readiness](native-runtime.md) for the actual registered role,
supported model-selection route, bounded task handoff and evidenced fallback. Retain the
returned result and actual routing, including an unknown or mismatched model.
Continue directly when permitted and delegation is unavailable, labelling that
limitation.

A background handle is not a returned specialist result: use the available native
collection tool and inspect the actual result before relying on it. If permission
or collection remains unresolved, record that state and keep the attempt; do not
launch a duplicate run or change shell forms to bypass it.

## Resume and apply corrections without rewriting evidence

On return, read intent, setup, continuation note, brief and the linked actual
attempts. Check for an unfinished process and its owned resources before starting
another run. Resolve recorded relative paths against this checkout, following
[workspace layout and Git handoff](workspace-layout.md#resume-after-a-clone-or-move)
when files came from another location. Inspect current source, tests and
configuration against the relevant evidence; collect fresh environment
observations at an implementation/comparison transition. Do not rerun all discovery, reinstall dependencies or regenerate
unchanged tests simply because a conversation resumed. A prior valid capture can
remain historical evidence while its current applicability is rechecked.

Persist a correction in `INTENT.md` with the actual speaker/wording and affected
scope, and note the resulting work in `WORKFLOW.md`. Distinguish a user decision
from an agent diagnosis or proposal. Preserve prior artifact revisions and failed
attempts; keep unaffected rule IDs and decisions. Use this dependency reasoning:

| Changed input | What must be reconsidered |
| --- | --- |
| Source scope, legacy behavior or a rule's meaning | Affected inventory/citations, rules and applicable decisions; affected brief/tests and downstream evidence. |
| Legacy tests, fixtures, config or captured source | A new legacy capture for the revised contract. Preserve the old candidate round; if the new baseline changes origin inputs, create a new candidate/origin before reapplying the bounded implementation. Never reconstruct an origin from changed candidate files. |
| Candidate implementation or its test/setup adaptation | Candidate selection/capture, comparison and affected review/fault checks. Intended candidate edits do not invalidate an unchanged legacy receipt. |
| Relevant environment or runner behavior | Observe actual state, inspect what changed, and recapture affected execution when the previous receipt no longer applies. Keep source and environment causes distinct. |
| Target, expected behavior, phase criteria or selected cohort | Revise the applicable brief/contract with decision provenance, then perform the newly required checks. Changed expectations require actual evidence, not merely new hashes. |
| Purely explanatory wording with unchanged requirements | Review and record that limited applicability; preserve prior bindings. Do not claim a newly rebound document governed an earlier execution. |

Freeze the applicable brief before implementation. Finalize the actual scenario
mapping after candidate generation/listing and before executing that contract;
retain its exact bytes with the attempt. A correction that changes that mapping
or its expected meaning needs a new execution, not a rewritten pre-run record.
Re-run the bundled validators/checks for the affected artifacts and choose the
earliest genuinely affected work. Preserve an unrelated completed phase.

At a shareable checkpoint, follow [Git handoff](workspace-layout.md#make-a-checkpoint-shareable)
to check that the necessary code, tests and evidence are trackable and record any
missing dependencies. Report partial progress and exact blockers when scope,
capability, permission or attempt limits stop execution. Do not bypass a denial
with another shell form.
An interrupted process may need a new attempt; native conversation continuity is
not durable process resume. Continue authorized supported work without requesting
another stage prompt or treating a checkpoint as human sign-off.
