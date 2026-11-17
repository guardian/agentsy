<!-- Adapted from Anthropic's code-modernization plugin (Apache-2.0).
Modified for native Copilot execution and local evidence.
See [LICENSE](../../../LICENSE) and [NOTICE](../../../NOTICE). -->

# Transform, uplift, reimagine and hardening

Read only the pinned command for the requested mode, then apply these Copilot
adaptations. The main skill governs existing authorization, native delegation,
baseline selection, records and report refresh. Preserve upstream's different
mode meanings; none is an alias for transform. Use the original stage's required
artifacts, without Claude Workflow, telemetry, panes or extra applications.

Keep new work inside the consumer repository. Preserve upstream's mode-specific
roots: an uplift uses a complete working copy at `modernized/<system>-uplifted/`;
reimagine services use `modernized/<system>-reimagined/<service>/`. Transform
continues to use `modernized/<system>/<module>/`. Record actual roots and mode in
the brief/setup notes; these names let the upstream proof checks identify modes.
Do not create nested Git repositories; use the existing repository's checkpoint
and handoff guidance. Preserve the original source and earlier evidence.

## Transform: rewrite one bounded module

Follow [modernize-transform](../../../upstream/commands/modernize-transform.md)
for the module rewrite, using the actual intent, chosen target and matching brief
phase. This mode changes technology and writes idiomatic target code from the
behavior contract. It does not substitute for a same-stack version uplift.

Select the evidence path from the project and brief before implementation:

- **Captured Playwright BDD:** follow the complete
  [BDD implementation and verification](implementation-and-verification.md)
  reference, including fresh `eligibleForImplementation`, byte-identical candidate
  origin, retained cohort mapping, environment and cleanup checks. An existing
  failed/stale BDD check cannot be bypassed by changing the runner label.
- **Native runner:** establish the shared
  [original baseline](upstream-verification.md#establish-the-native-original-baseline-before-implementation)
  using suitable existing tests and added characterization of material gaps.
  Prove the selected target toolchain and resolve phase entry/behavior decisions.
  Missing executable original evidence limits work to planning unless an actual
  user decision permits the weaker trace-based scope.

For the native path, create `modernized/<system>/<module>/` only after the original
baseline meets the entry criteria. Follow [workspace layout](workspace-layout.md):
copy the prepared original, including the selected tests, fixtures and necessary
setup, and retain its actual pre-edit source/test snapshot. Keep the original and
active application unchanged. Record how the candidate was derived and which
inputs are carried forward; a newly written target is not a retrospective origin.

Use the target stack's idioms and domain boundaries. Reuse the characterized
behavior and concrete expected outputs. Where target-specific test/driver setup
must change, retain the original tests and document the mapping and adaptation;
do not silently weaken assertions or lose a case. Preserve actual rule IDs in
test names/comments so native passing results can be traced. Delegate test work
to `test-engineer` within its test-only scope, without handing it application
implementation or acceptance decisions.

Run focused checks while iterating, then the complete selected suite and relevant
build. Retain actual outputs and executed counts. Capture real legacy/new product
output pairs where available and use the `compare` dispatcher from
[upstream verification](upstream-verification.md). Demonstrate a meaningful
regression canary in an isolated scratch candidate, preserving the failing
assertion evidence and clean implementation. A missing oracle or skipped suite
does not establish a pass.

Use `architecture-critic` to review target idioms, the brief and source behavior
outside the authored scenarios. Address material findings within scope or leave
them explicit. Write `TRANSFORMATION_NOTES.md` in the module root (or the declared
analysis location for captured BDD work): legacy-to-target file/line and rule
mapping, test adaptations, intentional differences and their actual decisions,
unmigrated behavior, counts, canary and review evidence, and remaining work.
Continue to the independent verification required by the brief. Only the full
upstream helper can compute its proof verdict; neither development tests nor
the scoped BDD comparison establishes human acceptance.

## Uplift: preserve structure across a version change

Follow [modernize-uplift](../../../upstream/commands/modernize-uplift.md).
Resolve an exact source/target version pair and requested project scope from
intent and the brief. Split major or combined runtime/framework moves into
testable hops when needed. Prove the target toolchain, inspect whether the old
runtime and existing test framework can run, and inspect where tests connect.
Required test-framework migration belongs early in the brief. Distinguish a
migration tool being present, runnable and actually producing findings.

Inspect the complete project structure and build a dependency graph, reusing
topology. Keep the source unchanged. Default to leaf-first, but prepare shared
test infrastructure first and coordinate cross-cutting dependency changes.
Shared nodes with external consumers need the brief's real transition decision:
dual-target compatibility, expanded scope, or a deliberate scheduled break.

Use `version-delta-analyst` and official version-pair guidance to produce or
refresh `DELTA_CATALOG.md`. Run report-mode tools only in authorized scratch
copies; retain actual outputs and unavailable coverage. Catalog API changes,
silent behavior changes, project/build changes and dependencies. Cite affected
sites, rank blast radius, mark Mechanical versus Judgment, and identify tests
needed before touching silent behavior. Reflection, locale and hosting/config
changes must not disappear into a generic dependency item.

Before application edits, establish the harness on a real type and retain a
measured original baseline in `BASELINE.md`, with each unit's `Code:`, `Command:`
and `Recorded:` result paths. Preserve existing failures as well as passes.
Follow the shared [native original baseline](upstream-verification.md#establish-the-native-original-baseline-before-implementation)
for meaningful coverage, source/test snapshots and the passing selected contract.
Use an authorized scratch copy of unchanged legacy for native builds/tests.
Gap-fill at material delta sites and preserve suitable existing tests. Where a
source runtime cannot execute, continue analysis/planning. Using upstream's
target-only fallback for implementation requires an actual user decision for
that weaker scope; use only retained real outputs, record `target-only: <why>`
and the decision in the brief and notes. It is not a live baseline or a `PROVEN`
result, and does not satisfy the default passing-original requirement.

After that baseline meets the entry criteria, create the whole runnable uplift
copy from the prepared original so relative references, added tests and setup
survive. Record copy exclusions and its actual pre-edit snapshot. Do not seed the
candidate before characterization and then omit the tests added to the original.

Pilot one representative unit before any fanout. Apply the smallest changes that
build and reproduce its baseline. Add surprises to the delta catalog and write
`PLAYBOOK.md`: ordered edits, errors and fixes, discovered environment facts and
the exact successful build/test commands. Present the pilot and any changed
scope or decisions before proceeding. Carry forward authorization already given
for that concrete rollout; do not invent approval of a changed plan.

For a few remaining units, proceed in dependency order. For a larger authorized
rollout, use native `uplift-migrator` tasks in small batches, one unit each, with
the proven playbook and disjoint write scopes. Start only units whose dependencies
have built; coordinate shared-file edits in the parent. Stop the batch rollout
when fewer than two-thirds of attempted builds pass, revise the playbook and
prove the repair on a failed unit before more fanout. Retain failed, blocked and
unattempted units separately. Re-run the complete working-copy build yourself;
returned specialist flags are not independent build evidence.

Run the retained suite on both runtimes when available, and compare every result
delta with the original. A former failure becoming a pass is still a change to
adjudicate. Report executed counts for each leg. Use the native baseline helper
from [upstream verification](upstream-verification.md), and actual output pairs
where available. An unexplained delta blocks completion of that unit.

Write `UPLIFT_NOTES.md` in the working-copy root: delta-to-fix mapping, per-unit
build/baseline outcomes, dual-run or target-only limits, manual residue, deferred
cleanup and the playbook. Ask `architecture-critic` to look for gratuitous
divergence. Continue through independent verification and any authorized hardening.

## Reimagine: rebuild from the retained intent

Follow [modernize-reimagine](../../../upstream/commands/modernize-reimagine.md).
Keep the complete target vision from the request; honor the matching brief phase.
Reuse rules, rule decisions, `DATA_OBJECTS.md`, topology and assessment. Delegate
only missing specification work: rules to `business-rules-extractor`, external
interfaces and domain relationships to `legacy-analyst`.

Write `AI_NATIVE_SPEC.md`: capabilities, domain model/ER diagram, inbound and
outbound interface contracts, inferred nonfunctional constraints and the behavior
contract. Label inferences and gaps. **Capability decisions remain human-owned:**
record which capabilities are P0 and which, if any, should deliberately disappear.
Reuse an existing explicit answer; otherwise resolve that decision before design
depends on it. Never silently drop a behavior because a model prefers a simpler
architecture.

Design the target containers, service boundaries, technology choices and data
migration approach. Use `architecture-critic` against the spec, incorporate
findings and save `REIMAGINED_ARCHITECTURE.md`. **The architecture must be approved
for build-out before scaffolding.** Existing approval must cover this concrete
architecture; a general request to investigate or modernize is not that decision.

Establish meaningful tests of unchanged behavior and known gaps before changing
application behavior, following the shared
[native original baseline](upstream-verification.md#establish-the-native-original-baseline-before-implementation)
or the selected BDD capture path. Then use
native `scaffolder` tasks for approved service directories, at most three at once
or the client's lower limit. Give each its assigned rules and interface contracts.
The output is a project skeleton, domain model, API stubs and executable acceptance
tests. Keep unimplemented rules visibly pending; skipped/expected-failure tests
are not proof that those behaviors work. Inspect returned blockers and run the
actual suites. Report defined, executed, passing and pending cases separately.

Write `AGENTS.md` in the reimagined root instead of Claude's `CLAUDE.md`: architecture,
service responsibilities, spec location, test commands and legacy-to-modern rule
mapping. It records the handoff; its existence does not mean implementation or
verification is complete. Continue to implement pending rules only within the
authorized scope, then independently verify and harden as requested.

## Harden: findings and a reviewable patch

Follow [modernize-harden](../../../upstream/commands/modernize-harden.md), using
its **direct subagent fallback** with native `security-auditor`. This stage reads
the selected legacy tree and writes findings/proposed patches under analysis;
it does not apply fixes or modify the original. A request to assess security is
not permission to operate on a production service.

Before storing credential findings, ensure `analysis/.gitignore` excludes
`SECRETS.local.md` and `*.local.patch`, and verify the actual paths are ignored.
Keep secret values out of tool output, chat, `SECURITY_FINDINGS.md`, shared patches
and the HTML report. Without a verified private location, retain only redacted
locations and defer credential-bearing patches. Do not create personal files
outside the project without authorization. An explicit raw-secret request may
only affect the verified private inventory, never shared artifacts.

Review relevant injection, authentication/session, secrets, access control,
dependency CVEs and input-validation risks. Retain scanner outputs with secrets
redacted. Check current official advisories for dependency claims; an unavailable
scanner/advisory source is a gap. Verify each Critical/High finding against the
actual code; comments alone cannot establish an exploit. Report missing scan
coverage and unverified findings, not an invented clean bill of health or
upstream multi-judge coverage that did not run.

Write `SECURITY_FINDINGS.md` with severity counts, stable `SEC-NNN` IDs, CWE,
file:line, exploit scenario, recommended fix, dependency findings and coverage
gaps. For Critical/High findings, produce minimal unified diffs relative to the
selected source. Put noncredential hunks in `security_remediation.patch`; a
credential-removal diff contains the original secret, so keep those actual hunks
only in verified ignored `security_remediation.local.patch`, with comment-only
pointers in the shared patch. Retain a remediation log and rotation advice.

Have `security-auditor` review the proposed patches against source: RESOLVES,
PARTIAL or INTRODUCES-RISK per hunk, including unintended behavior changes and
secret leakage. Revise and review at most three rounds; remove any hunk whose
last review still fails and record manual work. Do not call a source review a
tested fix. Link findings and patches for the person's decision; applying them
requires its own applicable authorization and subsequent checks. Reassess only
affected findings/coverage when returning, retaining earlier outcomes.
