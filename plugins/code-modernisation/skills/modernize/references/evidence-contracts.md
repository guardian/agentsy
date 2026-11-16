# Discovery and modernization evidence

## Project overview

`build_report.py --analysis /absolute/analysis/system` reads saved analysis and
prints JSON without writing files or running models, application code, tests or
validators. Adding `--write-report` creates or refreshes only that directory's
generated `REPORT.html`; it refuses an unrelated existing report. The directory
must already exist for a write. Exit 0 means collection succeeded, not that tests
passed; exit 2 means the request or write failed.

After a successful write, JSON additionally includes `report.written: true`,
the actual `report.path` and the generated file's `report.sha256`. Read-only
collection omits this result. The workflow creates the view after assessment and
refreshes at saved checkpoints by default, while honoring opt-out and keeping
status-only requests read-only.

The feature table comes from `ASSESSMENT.md` under `Observed features and suggested
slices`. `WORKFLOW.md` sections `Current work`, `Open decisions` and `Next action`
supply the continuation summary; `Selected evidence` supplies relative Markdown
links identifying the records chosen for the current scope. Selection is an agent
note, not a validation result. The view distinguishes selected evidence from
historical attempts and retains missing or unsupported selection limits. Older
free-form records remain available without invented summaries. `topology.json`
supplies a bounded structure/flow view when its
supported tree is present. Known saved result filenames supply historical outcomes
and counts. Their source, test and environment inputs are not revalidated.

The agent saves actual artifacts, updates current scope/decisions/selection/next
action, then renders the checkpoint. `ASSESSMENT.md` retains the initial discovery
observations; it is not rewritten into a completion report. Recognized preparation
documents are `TEST_PLAN.md`, `TEST_PROPOSAL.md` and `TEST_PREPARATION.md`, including
nested paths within the bounded analysis scan. Their notes describe preparation,
not executed tests. Preserve the full relative path in links and display labels
so different attempts' documents are not conflated by basename.

The evidence view distinguishes native test results from producer-reported outcomes
and detailed attempt checks, including environment and cleanup. An opaque producer
pass does not fill missing lifecycle details; those remain unknown. A passing test cohort inside a failed
capture remains a failed capture; counts alone cannot promote it to a qualifying
baseline. Expected-failure canaries remain distinct from clean application runs.
Neither evidence selection nor its display establishes current applicability or
human acceptance. See the agent's [continuation format](project-workflow.md#select-and-advance-the-next-unfinished-work).

The bundled capture writes `results-check.json`; the collector also accepts the
older `result-check.json`. Both are associated with sibling `outcome.json`,
`baseline.json` and native results. The capture outcome identifies
`kind: "playwright-capture-outcome"` and `schemaVersion: 1`. Its `checks` object
records execution, cleanup, service closure, after-snapshot, after-environment,
environment stability, result validation, baseline validation and helper integrity
as strict booleans when observed. The top-level
`postExecutionEvidenceComplete` records completion of the after-execution source
and environment observations; it is not a receipt or validation pass by itself.
The report requires all ten details for a recorded attempt pass; explicit failures,
errors or cancellation cannot be overridden by the producer's aggregate pass.
Missing, malformed or unsupported details cannot establish a pass. Older aggregate
outcomes retain their producer claim with unknown details; the report does not
backfill new checks into old evidence. Historical adapter lifecycle fields remain
supported separately.

`baseline-check.json` does not identify whether the checked source was original,
modernized or an independent copy. Its report label is therefore **Source/test
baseline check (role unclassified)**. Directory names and free-text selection
notes do not supply that missing role. The original-test card stays partial when
only preparation notes or these unclassified checks are available; inspect the
linked source evidence to determine which application was tested. This display
limit neither changes the validator contract nor adds project configuration.

Topology uses `root` nodes with `id`, `name` and `kind`; edges use `source`, `target`
and `kind`, and flows use `name` plus ordered `steps` containing `label` and `nodes`.
Older `from`/`to`/`type` edges and `id`/`action`/`nodeId` flow fields can be normalized
for display with warnings. This does not rewrite or validate the source map.
Unsupported fields and unresolved references must remain visible limits rather
than silently empty relationships. New artifacts follow the
[canonical format example](review-and-brief.md#produce-real-brief-inputs).
Suggested continuation requests use the analysis path relative to the consumer
project, not a machine-specific absolute path.

The report labels record availability separately from recorded outcomes. Modification
times offer possible-staleness hints, not a current source or environment check.
Known documents are read as literal text; the HTML view formats Markdown through
the pinned offline renderer and retains the original text. JSON stays literal;
external resources are never loaded. Exact local evidence-selection links receive
a bounded availability read before related results can be grouped; that does not
validate their contents or follow a receipt's source/environment references.
Unknown files are not embedded. Reads
exclude linked/special files, cap each artifact at 512 KiB and display document text
up to 65,536 characters. Breadth-first artifact scanning is bounded to 200 known result
files, 100 nested preparation documents, six levels, 500 directories and 5,000 entries
per directory, excluding candidate/source and dependency trees.
Skipped or unsupported inputs remain visible as limitations. This is an overview,
not a complete archive, secret scanner or approval mechanism.

See [progress and continuation](../../../docs/user/progress.md) for user requests.

## Test readiness records

The report reads `## Coverage plan` tables from recognized test-preparation
documents, including nested records. It preserves their ordering, source links
and agent-maintained state, with up to 100 rows per table. Authored and runnable
tests are not inferred to have executed; multiple plans are not silently merged
or promoted over one another. These plans are separate from the historical
assessment and from helper results.

The bundled [local validation helper](../../../assets/e2e/validation.mjs) writes
`setup-check.json` for a fresh `stack`, `fixtures` or `auth` attempt. Its contract is:

- `kind: "e2e-setup-check"` and integer `formatVersion: 1`.
- `startedAt` and `completedAt`: ordered, timezone-qualified observation times.
- `checks`: 1 to 100 uniquely named assertions, each with an `outcome` of
  `passed`, `failed`, `timed-out` or `not-run`.
- `cleanup.outcome`: the separate outcome of owned-resource cleanup verification.
- `passed`: a strict boolean, true only if every check and cleanup passed.

Use actual helper output, not hand-authored receipts. A failed detail overrides
an aggregate pass; missing, malformed or unsupported fields do not establish a
pass. Test counts and mapped-case fields are ignored for setup receipts. They
cannot satisfy a baseline gate, establish a tested source role or assert human
acceptance. Keys, cookies and raw response bodies do not belong in these records.

The additive report `testing` field holds `coveragePlans` and `setupChecks`.
The HTML Test readiness section shows selected setup evidence first, retaining
other attempts and explicit cleanup failures. The collector never executes
probes, refreshes their observations or authenticates them. See the bundled
[integration and auth recipes](../../../assets/e2e/README.md) for lifecycle boundaries,
cooperative timeout limits and application-specific assertions.

## Discovery validation

Run the bundled validator after saving or updating `inventory.json` and
`rules.json`. It imports only the bundled inventory helper and reads selected
source; it does not execute the analyzed application or modify files.

```sh
/absolute/plugin/scripts/validate_discovery.py \
  --source /absolute/source \
  --inventory /absolute/analysis/inventory.json \
  --rules /absolute/analysis/rules.json
```

Use the inventory's original `--module` and `--include-tests` options. If a prior
rules artifact exists, add `--previous-rules /absolute/previous-rules.json` to
check that prior IDs are retained. The skill saves the actual JSON result as
`validation.json` where artifact writes are permitted, following the shared
[exact output capture guidance](native-runtime.md#preserve-helper-output).
Keep raw stdout, stderr and the observed exit separate from analysis; preserve
earlier attempts when rechecking corrected findings.

Checks include strict JSON parsing, inventory structure/counts and equality to a
fresh source inventory, rule structure/status and unique IDs, safe in-scope source
paths, inclusive line ranges, and literal excerpts within those lines. Citations
are hash-checked against the inventory. A requested rule needs a separate requested
change; its citations describe legacy context, not implementation of the request.
A candidate may preserve observed behavior and a separate requested change.

- Exit **0**: implemented checks passed; inspect warnings too.
- Exit **1**: validation defects, such as changed source or mismatched citations.
- Exit **2**: unreadable/invalid inputs or unavailable source inventory.

Redacted excerpts remain explicitly unverified. A narrow heuristic warns about
current limitations beginning with an unavailable/null digest claim when a digest
is present. It is not general prose validation. Output does not echo source text
or supplied artifact values; this is not a secret scanner.

`checksPassed` does not establish rule meaning, governing path conditions,
complete coverage, runtime results, delegation, human acceptance, or semantic ID
continuity. The source read is not an atomic snapshot or a runtime sandbox.
Playwright BDD baseline guidance is available separately. Report auditing below
checks results; the baseline evidence helper additionally checks the technical
prerequisite for later implementation.

## Native Playwright result checks

`check_playwright_results.py` compares an actual native JSON listing captured
before execution with the native execution report and actual process exit code:

```sh
/absolute/plugin/scripts/check_playwright_results.py \
  --selection /absolute/selection.json \
  --report /absolute/results.json \
  --runner-exit-code 0
```

Obtain reports using the project's installed Playwright CLI and its native
[JSON reporter](https://playwright.dev/docs/test-reporters#json-reporter). The
selection is `test --list --reporter=json`; it normally contains skipped outcome
placeholders and no execution results. Those placeholders are not executed skips.

The checker requires a nonempty unique selection, matching test/project identities
and source coordinates, consistent counters, successful runner exit, and exactly
one clean passed attempt per selected case. It rejects missing/additional cases,
actual skips, expected failures, flaky outcomes, retries, and global/result/step
errors. Exit 0 passes those checks, 1 reports defects, and 2 reports unreadable or
invalid JSON. It validates relevant report fields, not the entire Playwright schema.

Output includes counts and input hashes, without echoing test payloads. Supplied
reports and exit codes are unauthenticated. Hashes identify the supplied bytes;
they do not bind source/environment identities or prove BDD provenance, meaningful
assertions, coverage, or acceptance. The skill's baseline guidance requires those
separate checks. No application is executed by this helper.


## Bound baseline evidence

`baseline_evidence.py` links a passing native run to source/test/fixture identity,
its measured process interval, supplied environment observations, and preserved
evidence files. Its subcommands read inputs and emit JSON; they do not execute
tests, inspect running services, modify application code, or write output files.
Save their actual output using the same capture guidance, without rewriting JSON
or substituting a wrapped terminal transcript for a raw JSON artifact.

Use a separate attempt directory under `analysis/<system>/` and retain the link
from `INTENT.md`. Keep that directory outside the source root, or explicitly
exclude its output subtree. See [workspace layout](workspace-layout.md) for the original, candidate and analysis roots.

### Capture the inputs

After generating BDD specs and preparing the authorized harness, capture the
before-run snapshot:

```sh
/absolute/plugin/scripts/baseline_evidence.py snapshot \
  --root /absolute/physical-source \
  --exclude node_modules
```

Capture the emitted JSON as `before.json` outside the covered source tree. Repeat
`--exclude` for each justified canonical relative file/subtree. These are exact
paths, not globs; overlapping/duplicate exclusions are invalid and there are no
implicit exclusions. Application files, configuration, feature/step/fixture files,
dependency locks, and generated BDD specs must remain represented. Exclusions
must not conceal an input that needs to be compared. The discovery inventory's
extension/directory filters make it unsuitable as this complete snapshot.

Preserved external provenance files establish historical bytes, not the current
state of their original locations or services. A relevant external dependency
must have its current identity measured in environment facts or be materialized
under the covered root. Declaring a copied runner or fixture file as provenance
alone does not detect later changes to the original external input.

Pass a resolved physical root; the helper scans every included regular file. It
records relative paths, SHA-256, four-digit octal modes, explicit exclusions,
capture start/completion times and `treeSha256`. Symlink path components, included
symlinks and special files are rejected; resolve a `legacy/<system>` symlink before
passing its physical root. Included linked content must be materialized and its
provenance retained. Evidence paths must also be physical (use `/private/tmp`
instead of the macOS `/tmp` symlink). Two
scans and per-file identity checks detect observed changes during capture; they
are not an atomic filesystem snapshot.

The default consumer layout places both tested trees inside one project:
`legacy/<system>/` and `modernized/<system>/<module>/`, with evidence in
`analysis/<system>/`. Pass those application roots, not their enclosing project
directory. The comparison still rejects equal or nested roots. The enclosing
repository's Git metadata and progress writes then sit outside both code snapshots.
No new implicit exclusions or relaxed evidence checks are introduced. On a new
clone, keep historical absolute-root receipts unchanged and record new attempts
for the current physical paths and environment.

Collect relevant actual environment observations through scoped normal tools.
Use this schema for both `environment-before.json` and, later, a separately
observed `environment-current.json`:

```json
{
  "schemaVersion": 1,
  "observedAt": "2026-10-23T10:00:00Z",
  "facts": {
    "nodeVersion": "observed version",
    "browserIdentity": "observed version or digest"
  },
  "limitations": []
}
```

The displayed values illustrate the shape; never copy them as measurements.
`facts` must be a nonempty JSON object with stable, relevant observations chosen
for the project. Include build/runtime settings, tool/browser versions, image
identities and fixture setup as relevant. State unavailable measurements and
their effect on reuse; omit credentials and secrets. Facts equality does not
establish their truth or completeness. An image tag or configuration file alone
does not prove the state of a running service.

Run the selected tests with native JSON results, preserving the native listing
and result as `selection.json` and `results.json`. Record the actual process
start, completion, and exit code in exactly this `process.json` shape:

```json
{
  "schemaVersion": 1,
  "exitCode": 0,
  "startedAt": "2026-10-23T10:01:00Z",
  "completedAt": "2026-10-23T10:03:00Z"
}
```

Use actual UTC measurements, not these example values. The process interval must
contain the native report's entire interval, including setup/teardown. Record
cleanup separately. After process completion, repeat the snapshot command with
the same exclusions and save `after.json`. The before and after snapshots must
match in root, membership, bytes, modes and scope.

### Assemble and check the record

```sh
/absolute/plugin/scripts/baseline_evidence.py record \
  --directory /absolute/attempt \
  --before before.json --after after.json \
  --runner process.json --environment environment-before.json \
  --selection selection.json --report results.json \
  --provenance runner.py
```

Input names are canonical relative paths within `--directory`. `--provenance` is
optional and repeatable for additional preserved files; use the runner example
only when that actual file is present. The helper automatically includes the
before-snapshot file among provenance references. Save the emitted receipt as
`baseline.json` in the attempt directory so its relative references still resolve.

The receipt has `schemaVersion: 1` and `kind: "playwright-bdd-baseline"`. It embeds
the before-run `snapshot` and binds all evidence references with `path` and
`sha256`: `provenance.references`, execution selection/report/process,
`execution.beforeSnapshot`, `execution.afterSnapshot`, and the environment record.
Captured receipts require both snapshot references; the preserved before file
must equal the embedded snapshot. `execution` also carries the actual exit
code and interval; `environment.facts` carries the recorded observations.
`limitations` and `blockers` retain distinct evidence gaps. Receipt assembly
validates the capture inputs; it does not issue implementation eligibility.

Observe the current environment through the normal tools, then check:

```sh
/absolute/plugin/scripts/baseline_evidence.py check \
  --baseline /absolute/attempt/baseline.json \
  --root /absolute/physical-source \
  --environment /absolute/attempt/environment-current.json
```

Save actual output as `baseline-check.json`. Checks cover:

- The complete current declared file set, scope, modes and hashes match the
  captured physical root and snapshots.
- Linked selection/results satisfy the native Playwright checker, and the
  referenced process record matches the receipt's actual exit and interval.
- Native report roots, project test directories, config identity and selected
  spec paths agree between listing and execution and refer to covered source
  inputs. A passing report for an unrelated or excluded test file cannot qualify.
- Capture chronology brackets execution: the before snapshot completes before
  the process starts, and the after snapshot starts after it completes. The
  hash-bound before file must also equal the receipt's embedded snapshot.
- The before environment observation predates execution; the current observation
  follows it, meets the configured age limit and has exactly the same declared
  facts. Timestamps more than five seconds in the future fail.
- Bound artifact bytes remain unchanged during checking and no recorded blocker
  remains.

Native `config.rootDir` and every project `testDir` must be canonical absolute
POSIX paths inside the captured root and outside excluded subtrees. If a native
`configFile` is supplied, it must name a covered regular file; absent/null config
paths remain explicit. Each selected spec path must name a covered file under
its test project's directory. A spec path may be canonical absolute or relative
to the native `rootDir`; `./` and `../` components are rejected. Listing and result
must agree on these roots, config path, project mapping and resolved spec paths.
This verifies the native source linkage, not the meaning of generated BDD tests.

The check requires a separately collected current observation no older than five
minutes by default. `--max-environment-age-seconds` accepts a positive integer for
an explicitly justified operating window and appears in the output as
`maxEnvironmentAgeSeconds`. This is a technical freshness policy, not a supplied
Guardian rule. Copying old facts and refreshing their timestamp is not measurement.
The helper checks declared chronology and age, not the truth of the observation;
the invoking workflow must observe again immediately before reuse. Do not extend
the window, alter comparisons, or remove relevant facts merely to force a pass.

Exit **0** and `eligibleForImplementation: true` mean these technical checks
passed. Exit **1** reports stale, missing or blocked evidence; exit **2** reports
malformed/unreadable inputs. `checksPassed` reflects the same technical result.
The output includes individual checks (including `reportSourcesBound`), native
counts, input hashes, errors and limits. Omitting `--environment` still audits
other evidence but cannot pass.

Historical evidence may be retained with `provenance.kind: "historical-import"`
and a nonempty `blockers` list; it is never eligible. Capturing files now cannot
retroactively supply a before-run snapshot for an earlier result. A new captured
attempt establishes a new eligible receipt without rewriting the old evidence.
An incomplete historical receipt may omit its before-snapshot reference; this
exception does not apply to captured receipts.

Run the check before creating an implementation candidate or entering a later
`uplift`, `transform`, or `reimagine` stage. A brief/planning discussion can
continue while gaps are resolved. Once a candidate exists, its intended changes
have a separate identity; they do not invalidate the legacy result merely because
its source differs. Candidate behavioral verification is a subsequent stage.

This helper does not authenticate reports, timestamps, process records, or
environment facts. It does not prove BDD provenance, adequate exclusions, correct
assertions, full coverage, accepted behavior, or behavioral equivalence. It is
read-only, supplies no OS write lock, and cannot prevent changes after checking.
These limits remain visible even when the technical result passes.

## Candidate comparison

`compare_candidate.py` checks the retained behavioral cohort across separately
captured legacy and candidate runs. Before implementation, save a candidate-origin
snapshot with the same complete files, hashes, modes and exclusions as the passing
legacy tree, at a distinct nonoverlapping physical root. Later candidate edits are
expected; preserve that pre-edit origin and capture the candidate's own run.

The contract binds the exact legacy receipt, candidate-origin snapshot and brief
bytes, and maps every selected native spec/project identity exactly once on each
side. Give each mapping a stable behavior ID, concrete retained expectation and
an account of selector/fixture adaptations. Candidate spec IDs, file coordinates,
code and selectors may differ. The helper checks membership and identity, not
whether assertion changes preserve meaning. Review those changes separately.

```sh
/absolute/plugin/scripts/compare_candidate.py \
  --contract /absolute/contract.json --brief /absolute/MODERNIZATION_BRIEF.md \
  --legacy /absolute/legacy/baseline.json --legacy-root /physical/legacy \
  --legacy-environment /absolute/legacy/environment-current.json \
  --candidate /absolute/candidate/evidence.json --candidate-root /physical/candidate \
  --candidate-environment /absolute/candidate/environment-current.json \
  --origin /absolute/candidate-origin.json
```

Each receipt must independently pass current source/report/environment checks;
candidate and legacy environments may differ but must each match their own run.
The original snapshot must precede candidate execution and retain the legacy scope.
The current environment observation age defaults to 300 seconds. An explicit
`--max-environment-age-seconds` needs the same operational rationale as the baseline
helper; copying timestamps or widening the window to force a pass is invalid.

Exit 0 means the implemented comparison checks passed, 1 means stale or inconsistent
evidence, and 2 means malformed/unreadable inputs. Inspect `checksPassed`,
`runs.legacy`, `runs.candidate`, `mappedCases`, `treeIdentities`, input hashes,
errors, tool limits and `declaredLimitations`. See the exact contract schema and
capture sequence in [implementation and verification](implementation-and-verification.md).

The read-only helper neither runs applications nor authenticates measurements.
A pass is scoped technical evidence, not business acceptance, full equivalence or
upstream `PROVEN`. Independent review, fresh verification and a meaningful scratch
canary remain separate workflow checks. New or intentionally changed behavior can
use separate suites and explicit decisions; it must not silently replace retained
cases in this comparison.
