<!-- Adapted from Anthropic's code-modernization plugin (Apache-2.0).
Modified for native Copilot verification and this port's artifact formats.
See [LICENSE](../../../LICENSE) and [NOTICE](../../../NOTICE). -->

# Independent verification with the upstream proof checks

Use this path for the original plugin's rule tracing, native test results,
recorded output comparison and proof verdicts. Read the pinned
[verification command](../../../upstream/commands/modernize-verify.md) for its
complete evidence format. The main skill's source protection, authorization,
native delegation and report checkpoints govern execution. Never use Claude
tools or an unavailable environment as an excuse to fabricate a result.

The existing Playwright BDD capture/baseline/candidate checks continue to apply
to work using that path. They verify a scoped retained cohort; they do not
replace this proof pack's additional requirements. Other native runners may
supply real JUnit/TRX results or supported raw logs directly. Do not manufacture
XML, test counts or historical outputs to make an unsupported report parse.

## Establish the native original baseline before implementation

This is the shared test-first entry condition for native-runner transformations,
uplifts and reimagining. First inspect the existing tests, runner/configuration,
fixtures and service destinations. Reuse suitable tests and establish the
selected meaningful behavior contract against unchanged application code.
Review material coverage gaps from the source, rules and proposed replacement;
add concrete characterization tests before implementation, then run the complete
selected contract. For uplift include silent-delta sites, preserving unrelated
pre-existing failures separately from the required passing contract.

Keep original source, test/configuration and fixture identities with the actual
run. The framework-neutral snapshot command is available for this purpose:

```text
<plugin-directory>/scripts/baseline_evidence.py snapshot --root <physical-original-test-root> [--exclude <generated-path>]
```

Capture before and after the run, retaining the actual JSON, commands and explicit
exclusions outside the covered root. Use inspected narrow exclusions for generated
output; never exclude relevant application, tests or fixtures to hide a change.
Application source stays unchanged throughout preparation and capture; tests may
be authored before the before-snapshot, not rewritten during execution. Run builds
in the prepared original test copy or a disposable scratch copy, keeping the
preserved source unchanged. Record the exact copy and its source identity.

Retain actual runner command, working directory, tool versions, process exit,
executed case results and original JUnit/TRX/raw log files. Keep failures and
retries in separate attempt directories. A listing, typed result table or model
claim is not execution. Save the evidence links, coverage limits and known
unrelated failures in the existing test plan and `PROJECT_SETUP.md`; uplift also
uses `BASELINE.md` with its real recorded result paths.

For the prepared-original workflow, retain a source snapshot of the actual
`legacy/<system>/` tree before creating or editing the candidate. Reuse the
baseline's saved after-snapshot when it covers that physical root and its tested
inputs. If execution used a scratch copy, retain that copy's own run snapshots
and establish the matching original input identity; never rewrite their roots.
Record the selected original snapshot path alongside the baseline results.
Keep its bytes immutable after first use. Its exclusions must be explicit and
must cover only justified generated/dependency output, not relevant source,
tests, fixtures or configuration.

Require the relevant selected contract to pass before implementation. Recheck
source, tests, configuration, fixtures and relevant environment before reusing
that baseline; refresh affected execution after material changes. The snapshot
alone establishes file identity, not behavior, coverage or an environment match.
When the Playwright BDD path is selected, its stronger captured baseline and
`eligibleForImplementation` checks remain required; do not downgrade to raw
logs to avoid a failed check.

An unavailable executable original permits analysis and planning under the
default requirement, not automatic target-only migration. Upstream's trace-based
fallback requires an actual user decision accepting that weaker scope. Record
the exception and use only real retained traces; it does not create a live
baseline or establish a full proof verdict.

## Identify the work and preserve the claim being checked

Read intent, the brief, original source, actual build/test setup and retained
development evidence. Identify transform modules, uplift units or reimagined
services from their recorded roots: `modernized/<system>/<module>/`,
`modernized/<system>-uplifted/` or `modernized/<system>-reimagined/<service>/`.
A test-harness-only folder is
tooling, not a modernized implementation to claim as proven.

Verify independently of development, with a separate native specialist/session
where available. Inspect service configuration before executing any suite.
Keep the original untouched, build it only in an authorized scratch copy, and
clean only owned generated outputs. Do not repair application/test code during
the independent check; preserve failures and route needed repairs back through
the relevant implementation phase. Preserve prior verification records before
a new run replaces the current `VERIFICATION.md`/`.json` snapshot.

## Trace and execute

Invoke bundled checks from the consumer workspace root using the loaded plugin:

```text
python3 <plugin-directory>/scripts/upstream_checks.py trace <system> --module <module>
```

The dispatcher preserves original helper arguments. Use `--workspace` when
supported to name a different consumer root; read the selected helper's `--help`
for its exact interface. Keep existing `R-001` IDs; the compatibility layer
supports them without changing historical rules. Run tracing again with
`--results <actual-result-directory>` after execution. A named rule only counts
as tested when a passing executed test backs it; notes and skipped tests are not
that evidence. Logs can establish counts, while per-test native results provide
rule-to-execution traceability.

Run the complete selected native suites from clean authorized build outputs.
Retain actual commands, exits, raw logs and supported native result files. For
uplift, use `BASELINE.md`'s exact unit commands and compare per-test outcomes:

```text
python3 <plugin-directory>/scripts/upstream_checks.py baseline analysis/<system>/BASELINE.md --junit <actual-results>
```

The measured original results, retained tests and characterization of silent
deltas are separate uplift checks. Zero executed cases, missing tools and
unreachable fixtures remain failures/gaps. A baseline typed from memory is not
a measured run. A person owns differences and decisions about removed/weakened
tests; the verifier cannot edit those decisions to improve a verdict.

Create an isolated scratch candidate, make one meaningful regression and run
the tests covering it. Retain its diff, real failure output and cleanup. A
startup failure is not a successful canary, and the development canary's notes
do not replace this independent fault check.

## Compare real outputs and challenge with fresh inputs

Preserve development `cases.json`, inputs and legacy outputs. Re-run the new
side and compare with the actual bundled comparison helper:

```text
python3 <plugin-directory>/scripts/upstream_checks.py compare analysis/<system>/equivalence/cases.json --out analysis/<system>/EQUIVALENCE.json
```

For multiple modules, keep each module's cases and fresh cases in its own
equivalence subdirectory. Use the real schema documented in the pinned
[comparison helper](../../../upstream/scripts/compare.py), with relative paths
to captured outputs. Mask only legitimate variability with a recorded reason;
numeric tolerance also needs a concrete rationale. A person owns any
`approvedDifference` or `approvedInputs`; never add one to obtain a passing result.

Choose at least ten fresh accepted inputs not used during development, including
relevant boundaries and ordering. Follow intent for malformed-input/quirk scope.
Run both versions with the same input and driver, retaining real product outputs
under `equivalence/fresh/legacy/` and `fresh/new/`. Group outputs from one input
using its `input` ID in `fresh-cases.json`. Repeated status lines or development
outputs do not count as fresh evidence; the pack checks this. Diagnose refused
inputs and record them in `leftOut`, replacing them to obtain ten valid fresh
inputs when possible. Retain earlier fresh cases and human difference decisions.
Run `compare` on `fresh-cases.json` too. If legacy cannot run, report trace-based
limits; this path cannot produce full `PROVEN` evidence from target-only execution.

## Generate the verdict and continue

Write `analysis/<system>/equivalence/test-runs.json` using the pinned verification
command's schema: actual date, legacy execution/limits, `leftOut`, suite commands
and native result/log paths, and independent canary changes/result paths. Retain
the exact module/unit identity expected by the proof checker. Enter paths and
observations, never hand-enter counts or substitute a model completion message.

```text
python3 <plugin-directory>/scripts/upstream_checks.py proof <system> [<module>] --source-snapshot <saved-original-snapshot.json>
```

`--source-snapshot` is the port's optional source-identity adaptation: it compares
the preserved original with the actual saved preimplementation snapshot instead
of treating every file newer than `PREFLIGHT.md` as a source edit. This allows
test preparation without inventing a fresh preflight date. Use the snapshot
already retained with the original baseline, not a new snapshot of changed code
created to clear a failed check. Never refresh/backdate `PREFLIGHT.md`, edit
snapshot hashes or widen exclusions to force a pass. Missing or mismatched
snapshot inputs remain an explicit failed/gap check. Without this option the
unchanged upstream modification-time check applies, and prepared tests or build
output may be reported as later changes.

The helper computes `PROVEN`, `PARTLY PROVEN` or `NOT PROVEN`, writes
`VERIFICATION.md` and `VERIFICATION.json`, and returns nonzero when proof is
incomplete. Show its actual per-module verdict, reasons, P0 tracing gaps, tooling
exclusions and limitations. Do not reinterpret a scoped BDD pass as this verdict,
soften a failed check, or alter output to make the verdict better. Report the
source-check method and exclusions actually used. File identity does not
authenticate a local snapshot, prove when it was collected, establish the
meaning of tests or verify external environment identity. Keep the real capture
history and stronger BDD checks where applicable; a retrospective snapshot
cannot govern an earlier run.

Record technical outcomes separately from brief decisions and final human
acceptance. Leave sign-off to the named person. Turn each gap into the next
concrete work: restore execution readiness, obtain an actual decision, add missing
characterization, or repair the candidate within its authorized phase. Refresh
the existing HTML report after saving records; do not import the upstream UI.
