<!-- Adapted from Anthropic's code-modernization plugin (Apache-2.0).
Modified for captured Playwright BDD verification.
See [LICENSE](../../../LICENSE) and [NOTICE](../../../NOTICE). -->

# Playwright BDD transformation and verification

Use this reference for an authorized cross-stack rewrite of one selected module
and a scoped candidate check. Follow the completed brief and real entry criteria.
This reference owns the stricter captured Playwright BDD path. Other modes use
[modernization modes](modernization-modes.md), and native report/output proof uses
[upstream verification](upstream-verification.md). A BDD comparison alone does
not produce an upstream `PROVEN` verdict.

## Enter the selected phase

Read `INTENT.md`, the current `MODERNIZATION_BRIEF.md`, relevant source/rules,
reviews and legacy baseline. Use the chosen target and module IDs; select the next
unfinished applicable phase when unambiguous, following
[project discovery and continuation](project-workflow.md). Update `WORKFLOW.md`
with the actual unmet condition and next action; a notes file is not completion.
A module absent from the brief or an
unchosen target requires resolution, not an invented implementation. Inspect
current target toolchain and isolated test setup before starting. Preserve external
callers, off-limits work, requested changes and unresolved behavior decisions.

Existing authorization for that concrete scope is sufficient for routine work.
A human still owns ambiguous requirements, intentional behavioral differences and
final acceptance. Carry actual decisions forward; no repeated gate is needed for
a decision already given. Read [review and brief](review-and-brief.md) when the
plan needs correction. Continue independent preparation while genuine blockers
are resolved; do not silently relax a criterion to proceed.

Immediately before candidate creation, collect fresh environment observations and
run the legacy `baseline_evidence.py check` from
[baseline guidance](playwright-baseline.md). Require exit 0 and
`eligibleForImplementation: true`, plus applicable phase decisions. Its current
checks are a technical prerequisite, not permission or an operating-system lock.
If legacy execution is unavailable, retained traces may inform planning but do not
satisfy this captured path's live BDD requirement. Report the missing prerequisite;
do not switch evidence paths to disguise a failed or stale check.

When resuming an existing candidate, inspect its current diff and latest evidence
before continuing. Do not discard valid implementation work or recreate its origin
just because a new conversation began. Unverified edits need the appropriate new
candidate checks; source/test changes to the legacy contract need the affected
new baseline and candidate round described in the continuation reference.

## Preserve the origin, then implement

Create `modernized/<system>/<module>/` inside the consumer project/workspace from
the prepared passing `legacy/<system>/` tree, including its tests and required
configuration. Follow [workspace layout](workspace-layout.md) for existing paths,
copy exclusions and Git handoff. A whole-project candidate is allowed when the
selected slice depends on its harness or remaining legacy modules; keep the actual
application change bounded. Both tested roots remain distinct nonoverlapping
subdirectories, even though they share the enclosing repository. Do not implement
in the legacy baseline or overwrite the existing application files. Record the
physical root; do not follow included symlinks silently.

Before any candidate edits, capture `candidate-origin.json` outside its covered
root using the same explicit exclusions as the legacy snapshot:

```text
<plugin-directory>/scripts/baseline_evidence.py snapshot --root <physical-candidate-root> --exclude <same-excluded-path>
```

Repeat the actual legacy exclusions, or omit `--exclude` if there were none. The
origin must have the same complete file membership, hashes, modes and exclusions
as the legacy snapshot, with a distinct nonoverlapping root. Its capture must
follow the legacy after-snapshot and precede candidate edits and execution.
Do not create it retrospectively from already changed files or rewrite its time.
Record the copy method and source receipt; the helper checks declared identity and
chronology, not whether a copied timestamp is authentic.

Delegate test work to the bundled `test-engineer` when useful and available. Supply
its permitted test/harness/evidence paths, rule decisions and existing contract;
its write/execute tools do not authorize application implementation. Reuse the
passing legacy scenarios. Review candidate-specific selector, fixture and setup
adaptations for unchanged expectation meaning. Preserve separate evidence for
requested differences; do not make the legacy baseline pretend they existed.

Implement the brief's bounded change using target idioms and domain structure.
Keep files outside that scope unchanged except justified recorded integration or
test adaptations. During iteration, use focused checks; before reporting completion,
run the complete selected behavioral contract and relevant build checks. Retain
actual commands/results and earlier attempts. Diagnose within the existing retry
agreement, stop on scope/permission limits, and clean up owned processes/services.

Write `TRANSFORMATION_NOTES.md` outside the captured application root where
practical, or in an explicitly declared output subtree. Record legacy-to-target
file/line mappings per behavior, rule IDs, actual changes and unmigrated code,
intentional differences and their decision provenance, test adaptations, executed
case counts, canary evidence, review findings and remaining work. A notes file is
an account of evidence, not proof by its existence. Do not claim legacy code was
retired when it remains in the delivered candidate.

## Capture candidate execution and map the retained contract

After the last candidate/test edit and BDD generation, capture a native selection,
fresh candidate environment observations and a before-snapshot. Run the complete
selected contract, retain native reports and actual process times/exit code, clean
up, then capture an unchanged after-snapshot. Use the same capture and `record`
procedure as the legacy baseline, saving a separate candidate receipt such as
`candidate/evidence.json`. Candidate and scratch captures inherit the
[adapter review/cleanup](project-workflow.md) and
[fresh environment comparison](playwright-baseline.md) requirements; a passing
browser report alone cannot override failed capture checks.
Reusing this capture schema does not make candidate
code the legacy oracle. Keep the origin's exact exclusions for candidate capture;
do not hide changes by widening the excluded scope. Candidate and legacy may have different physical paths,
native test IDs, selectors, configuration and intended runtime versions; each run
must independently bind its own source and measured environment.

Before execution, prepare an explicit one-to-one mapping between every selected
legacy and candidate scenario, Examples row and project. Native IDs come from
actual listings, not model-generated values. Save the finalized mapping and its
binding hashes in `contract.json`:

```json
{
  "schemaVersion": 1,
  "kind": "preserved-behavior-contract",
  "bindings": {
    "legacyReceiptSha256": "<actual hash of the legacy receipt bytes>",
    "candidateOriginSha256": "<actual hash of candidate-origin.json>",
    "briefSha256": "<actual hash of MODERNIZATION_BRIEF.md>"
  },
  "cases": [
    {
      "id": "CASE-001",
      "expectation": "<retained concrete Given/When/Then and relevant rule IDs>",
      "legacy": {"specId": "<native spec ID>", "projectId": "", "projectName": ""},
      "candidate": {"specId": "<native spec ID>", "projectId": "", "projectName": ""},
      "adaptation": "<unchanged, or precise selector/fixture adaptation and review limits>"
    }
  ],
  "limitations": []
}
```

Use actual native project values; empty strings apply only when the native report
has no project ID/name. Give each mapped case a stable contract ID. Record mocks,
authentication assumptions, assertion scope and known defects in the contract's
limitations and brief. Do not fill placeholders as evidence. Every selected case
must map uniquely on both sides; fewer scenarios with similar titles is not the
same contract. Test additions and deliberately changed expectations need separate
selection/evidence and explicit decisions; they do not silently replace a retained
case. The helper verifies identity/membership, not the truth of expectation prose
or whether a changed assertion is equally strong.

Preserve the exact finalized brief and contract with the attempt before execution,
and bind those real files as receipt provenance where applicable. Before reporting
a comparison, check that its claimed pre-run brief/contract still match those
preserved bytes. A newly authored mapping must not be presented as the contract
that governed a historical run. Use a fresh attempt when its selected cases or
expectation meaning changed; retain prior mappings and outcomes.

Collect new current environment observations for both roots, then invoke:

```text
<plugin-directory>/scripts/compare_candidate.py --contract <contract.json> --brief <MODERNIZATION_BRIEF.md> --legacy <legacy/baseline.json> --legacy-root <physical-legacy-root> --legacy-environment <legacy/environment-current.json> --candidate <candidate/evidence.json> --candidate-root <physical-candidate-root> --candidate-environment <candidate/environment-current.json> --origin <candidate-origin.json>
```

Save actual output as a separate comparison artifact, for example
`candidate-comparison.json`. The default maximum environment observation age is
300 seconds; `--max-environment-age-seconds` requires the same explicit rationale
as baseline checking. Never refresh timestamps or extend the window to force a
pass. Both environment sets must still match their own recorded run; the helper
does not decide whether a planned difference between the two environments is safe.

A passing comparison requires independently current legacy and candidate receipts,
unchanged linked evidence, the matching pre-edit candidate origin, binding to this
brief and a complete unique scenario mapping. Inspect `checksPassed`, the nested
`runs.legacy`/`runs.candidate` checks and counts, `mappedCases`, `treeIdentities`,
errors and limits. The tool only reads evidence and emits JSON. It cannot enforce
an edit boundary, authenticate measurements, inspect assertion meaning or grant
acceptance. A pass is scoped technical evidence, not complete equivalence.

## Independently challenge the result

Ask a separate specialist/session to examine the candidate and tests against the
brief and retained legacy behavior. Use the bundled `architecture-critic` for
read-only source/assertion review; report whether it actually ran. Address Blocker
and High findings within the authorized scope or leave completion explicitly
blocked; preserve the remaining findings. Its read-only review is not a fresh
execution. Ask the critic to trace the replaced boundary from legacy source as
well as the brief: which observable framework or integration behavior changed,
and which of those differences are absent from the authored tests? Passing the
same suite again does not answer that question.

For a suspected preservation gap, obtain a focused characterization on unchanged
legacy and the candidate before deciding that a regression exists. Keep source
inferences distinct from runtime findings. A demonstrated violation of the agreed
preservation contract requires repair within scope or an explicit human decision
to change that contract, regardless of the review's severity label. Do not merely
list it as a Medium finding beside a completion claim. Route new cases through
the existing correction flow: preserve previous attempts, refresh affected legacy
and candidate evidence, and recheck the revised contract before reporting a pass.

Re-run the complete selected contract independently from clean authorized
outputs/setup and retain a new attempt when the scope calls for independent
verification; do not recycle development results as an independent run. Route this
execution through the bundled `test-engineer` using [native delegation](native-runtime.md#select-the-actual-specialist-and-model),
including the selected model. A generic execution task can have a different model
default; use the documented fallback and record actual routing when necessary.

Prove the tests detect a meaningful regression in an isolated scratch candidate,
never by altering legacy or the preserved clean candidate. Change one behavior
that the retained contract is meant to protect, such as a boundary, expected route
or returned result. Run the relevant selected tests and keep the changed-code diff,
native listing/report, actual process outcome and cleanup. Confirm a relevant
behavior assertion failed; a startup error, missing browser or zero executed cases
is not a successful canary. If the fault survives, report the coverage gap and
strengthen/review tests; any changed legacy contract needs a new legacy capture
before it can support a revised comparison. Keep deliberate failures separate from
clean receipts; do not edit a failed report to pass the baseline checker.

If a specialist or runtime capability is unavailable, state the exact gap and
continue permitted work. Do not describe the builder's own review as independent.
The [upstream proof pack](upstream-verification.md) additionally requires its own rule tracing, recorded
output comparisons and at least ten fresh dual-execution inputs. This slice's
comparison and canary do not implement those checks; do not call its result
`PROVEN`, translate it into invented proof-pack evidence or soften missing checks.

## Report and resume accurately

Report the scoped implementation, actual selected/executed/pass/fail counts,
source and test identities, comparison, meaningful canary outcome, independent
review/re-execution status, cleanup, deviations and limitations. Keep human
acceptance separate; never sign the brief or verification on the user's behalf.
Use `VERIFICATION.md` for this narrative if helpful, clearly labelled as the port's
scoped BDD verification rather than output of upstream `proof_pack.py`.

Before regenerating the progress report, update `WORKFLOW.md` with the actual
current scope, remaining decisions and next action. Under `## Selected evidence`,
link the exact baseline, candidate, independent and comparison records chosen for
that scope, plus any deliberate canary result labelled as an expected failure.
Preserve unsuccessful and superseded attempts as history. State test outcomes
separately from capture/environment/cleanup outcomes and retain acceptance limits.
Follow the [continuation record format](project-workflow.md#select-and-advance-the-next-unfinished-work);
no additional user prompt or report configuration is needed.

On continuation, inspect legacy and candidate separately. Resolve project-relative
locations in the current checkout and follow [relocated-work guidance](workspace-layout.md#resume-after-a-clone-or-move)
when a move or clone changes the roots in earlier receipts. Intended candidate
changes do not invalidate the unchanged historical legacy capture. Later source,
test, fixture or environment drift requires checking the affected receipt and
rerunning the appropriate attempt. Contract/brief edits require reviewing their
meaning and re-binding/rechecking; rehashing alone is not approval or a new test.
Preserve failures, prior notes and unresolved decisions. Choose the next useful
authorized action from the brief rather than declaring the phase complete merely
because a folder or notes file exists.
