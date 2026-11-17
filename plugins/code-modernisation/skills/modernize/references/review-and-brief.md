# Review behavior and prepare the brief

Use this reference for the upstream review/brief stages and conversational
corrections. Retain the user's existing decisions and perform authorized missing
analysis. A missing target, unresolved behavior or unavailable source remains a
specific question/blocker; it is not a reason to invent a completed stage.
Use [project discovery and continuation](project-workflow.md) to identify which
inputs actually need work and keep the next action in `WORKFLOW.md`. Completing a
brief does not require the user to paste another command for an already authorized
journey; continue when its actual entry conditions hold.

## Review rules without rewriting history

Read `INTENT.md`, `rules.json`, its current validation, existing
`BUSINESS_RULES.md`, `RULE_REVIEWS.json` and any brief questions. The port's JSON
findings retain their established IDs such as `R-001`. Do not renumber them to
`RULE-001` to satisfy an upstream parser.

When a readable rules document is needed, derive `BUSINESS_RULES.md` from the
validated findings. Give each card its actual ID, title, source-backed statement,
Given/When/Then, confidence, citations and unresolved questions. Preserve observed
behavior and requested change separately; link the originating JSON and its actual
digest. Add priority with rationale as analysis, not a human verdict: P0 means the
bounded feature's purpose depends on it or being wrong is costly. Mark uncertain
priorities as proposed. Do not manufacture source findings to fill a template.

Default review focuses on important uncertain rules, suspected defects, SME
questions and questions named in the brief. Honor a request to review all or only
P0 rules. If priorities are missing, inspect scope and risk rather than assuming
that no rules need review. Reuse actual decisions already supplied in conversation;
ask a focused question only for a needed decision that is still missing. Present
the statement, concrete example, evidence and uncertainty in ordinary language.
A person may confirm the behavior, reject it, or leave it for discussion. Preserve
free-text answers in their own words; absence of an answer is not confirmation.

Merge actual answers into upstream-shaped `RULE_REVIEWS.json`:

```json
{
  "system": "<system>",
  "version": 1,
  "reviews": {
    "R-001": {
      "verdict": "confirmed",
      "at": "<actual ISO decision time>",
      "title": "<rule title>",
      "note": "<the person's words, optional>"
    }
  }
}
```

Valid verdicts are `confirmed`, `wrong`, and `discuss`. Keep the actual ID as the
key and replace an earlier answer only when a new actual answer supersedes it.
If the decision time is unavailable, record the current transcription time and
explain that distinction in `INTENT.md`. Keep the rule revision/digest, source of
the answer and any limited scope in `INTENT.md`; these local records are not
authenticated organizational approval. Generate `RULE_REVIEWS.md` from the JSON:
a short explanation, then `Rule | Verdict | When | Title | Note` in ID order.
The review stage records decisions; it does not edit an extracted finding to make
an unwanted behavior disappear. Correcting a mistaken source interpretation is a
separate discovery update with preserved prior evidence and revalidation.

A `wrong` verdict needs clarification: does the finding misdescribe the code, or
does the person want to change what it correctly describes? In the latter case,
retain the legacy characterization and document the requested difference. Neither
`wrong` nor `discuss` is settled contract behavior. An unresolved relevant P0 rule
blocks its affected implementation scope, not unrelated authorized analysis.

Recheck decisions when a rule's meaning, cited behavior or scope changes. Preserve
the earlier decision as history and flag its applicability; do not silently apply
it to a new rule meaning. A citation line moving without a semantic change need
not cause the person to answer the same question again.

## Produce real brief inputs

A brief uses `ASSESSMENT.md`, `topology.json`, intent and preflight. For transform
and reimagine, also use `BUSINESS_RULES.md` and actual rule decisions. An uplift
preserves the code and uses the measured original baseline as its behavior
contract; do not require whole-system rule extraction before that version change.
If authorized analysis is missing, produce the needed assessment/map or other
inputs from actual inspected source before completing the brief.
Mark their scope and uninspected areas; an inventory alone is neither artifact.
If essential inputs are unavailable, a draft may record precise gaps but must not
claim to satisfy implementation entry criteria.

For uplift, `DELTA_CATALOG.md` is required before phasing the implementation.
If absent or stale, use `version-delta-analyst` and the catalog steps in
[modernization modes](modernization-modes.md#uplift-preserve-structure-across-a-version-change),
then inspect the returned findings. Establish whether the existing test framework
can run on the target, shared dependency cuts and external-consumer decisions.
Do not launch the application migration just to obtain a planning input.

For reimagine, reuse `DATA_OBJECTS.md`, interface findings and existing
`AI_NATIVE_SPEC.md`/`REIMAGINED_ARCHITECTURE.md` where present. The brief can plan
specification and design work before those outputs exist; make the human P0/drop
decision and approval of the concrete architecture prerequisites of scaffolding.
Do not manufacture them to complete a plan or treat a generic modernization
request as approval of an architecture not yet designed.

`ASSESSMENT.md` should explain the selected system/module and stack, actual build
and test evidence versus unexecuted observations, dependencies and boundaries,
relevant risks, and why the proposed modernization pattern fits the stated intent.
Respect any preflight answers about local setup, prior attempts, off-limits work
and callers outside the selected slice.
For broad initial requests, include the source-backed **Observed functional areas**
table described in [project overview](project-overview.md).
Summarize user-facing capabilities, coverage limits and a recommended first slice
in chat. Do not confuse a list of files with a feature map or infer accepted
requirements from component names. A specifically requested feature needs only
the bounded assessment and dependencies relevant to it.

For a behavior-preserving change, follow the selected replacement boundary through
its actual bindings, configuration and integrations. Identify observable behavior
currently supplied by a framework, library or browser as well as application logic.
Inspect the relevant installed implementation/version or authoritative documentation
when application source delegates that behavior. Investigate only dependencies
that can affect this slice; record inaccessible or uncertain behavior for focused
characterization rather than scanning a whole framework or assuming defaults.

Keep these preservation obligations distinct from domain policy. Record them in
the brief's existing Behavior Contract with their source, concrete observable
example, whether inferred or observed, and scenario coverage or unresolved gap.
The business-rule extractor's domain-only output is an input to this work, not
its completeness boundary. Let the actual code and proposed replacement determine
which interactions and lifecycle transitions need attention.

Keep upstream topology conventions: `system`, a `root` tree of `system`/`domain`
containers and leaf `module`/`datastore`/`job`/`screen` nodes, `edges`,
`entryPoints`, `deadEnds`, `observations` and `flows`. Module nodes have stable IDs,
source locations and measured size when available. Edges use those leaf IDs and
`call`, `dispatch`, `read` or `write`; business flows identify a persona and ordered
steps with node IDs. Inspect routes, wiring and configuration as well as imports.
Do not label a node dead merely because a dynamic caller is unresolved. Retain the
extraction method/script and supporting source evidence so the map can be revisited.
A small feature can have a small map; uninspected external dependencies stay explicit.
Read data/Mermaid files, not a rendered HTML viewer. No custom viewer is required.

For new maps, write edges with `source`, `target` and `kind`; use `name` for a
flow, and `label` plus a `nodes` array for each step. For example, these sections
reference leaf IDs already present in the root tree:

```json
{
  "edges": [
    { "source": "search-form", "target": "search-service", "kind": "call" }
  ],
  "flows": [
    {
      "name": "Find matching records",
      "persona": "Application user",
      "steps": [
        { "label": "Submit a query", "nodes": ["search-form"] },
        { "label": "Return matching records", "nodes": ["search-service"] }
      ]
    }
  ]
}
```

This illustrates field names, not evidence of an actual flow. Keep the complete
`system` and `root` tree in the real artifact. The report can display older
`from`/`to`/`type` edges and `id`/`action`/`nodeId` flow fields with compatibility
warnings; use the canonical fields on new work. Display normalization does not
modify the saved map or establish that its relationships are correct. Unsupported
or unresolved relationships remain explicit gaps, not empty arrows treated as a
complete map.

## Write MODERNIZATION_BRIEF.md

Read the target and constraints from actual intent. Recommend alternatives only
when needed; label an unchosen target as a proposal. Keep the mode from actual
intent: `transform` rewrites a module in another stack, `uplift` moves to an exact
newer version of the same stack, and `reimagine` rebuilds from intent on a new
architecture. Do not route all three through a transform merely because its
captured BDD path is available. Use the selected project's suitable runner.
Record the current input identities and observation times in the header, including
findings, review decisions and the baseline receipt when available. Refresh affected
sections when inputs change; retain the previous brief for evidence continuity.

Preserve these eight upstream sections:

1. **Objective:** from what, to what and why, bounded by actual intent.
2. **Target Architecture:** a small Mermaid container diagram and legacy-to-target
   component mapping. Distinguish proposed structure from existing code.
3. **Phased Sequence:** dependencies, selected module/unit/service IDs, risks and
   checkable entry/exit conditions. A single bounded pilot phase is sufficient
   when appropriate. Order transform slices by dependencies and risk; order uplift
   units leaf-first, with test-harness readiness first and shared dependency cuts
   handled together. Record transition decisions for external consumers. Reimagine
   phases retain specification/architecture decisions before service scaffolding
   and later implementation. Pilot findings may revise the plan; preserve the
   earlier plan and explain the changed inputs.
4. **Business Walkthroughs:** user/persona flows, implementing modules and phases.
   Label inferred flows needing confirmation rather than inventing accepted ones.
5. **Behavior Contract:** relevant P0 rules, retained legacy examples, test/case
   mapping, framework/integration preservation obligations and known defects.
   Link each relevant obligation to a scenario or an explicit coverage gap; cite
   its source without inventing a business rule or a new policy approval.
   Wrong/disputed or low-confidence critical expectations
   remain questions; explicit requested changes are separate from preserved behavior.
   For uplift without a rules file, use `BASELINE.md` and the actual native results
   it references, with required characterization at silent-delta sites.
6. **Validation Strategy:** select the actual runner and required combination of
   characterization, contract tests, output comparison, property tests or human
   UAT. Establish the passing relevant original contract before implementation.
   Captured BDD work retains its full baseline/candidate eligibility checks;
   native-runner work follows the shared original baseline and upstream proof
   guidance. Include test adaptations, independent recheck and a meaningful
   scratch-copy canary. State coverage/fixture limits and whether full proof
   remains incomplete; scaffolded pending tests are not implemented behavior.
7. **Open Questions:** genuine human decisions and missing evidence, with the phase
   each affects. An agent may report a technical fact; it cannot answer a business
   question or accept a difference on the person's behalf.
8. **Approval Block:** retain `Approved by:`, `Date:` and `Approval covers:`. Populate
   only from actual supplied authorization and its exact scope, with a reference
   to the decision record. Otherwise leave pending. Do not invent a signature or
   equate a passing helper with acceptance.

Preserve the upstream phase grammar, using this plugin's command namespace:

```text
#### Phase 1 — <bounded pilot name>
Command: /code-modernisation:modernize-transform
Modules: <module IDs exactly as in topology.json, comma separated>
Scale: S
Risk: <level; principal risks and mitigations>
Entry criteria:
- [ ] <checkable condition>
Exit criteria:
- [ ] <checkable condition>
```

The example uses transform. For each actual phase choose exactly one full command:
`/code-modernisation:modernize-transform`, `/code-modernisation:modernize-uplift`
or `/code-modernisation:modernize-reimagine`, matching the mode and stable scope IDs.

Scale is relative size (`S`, `M`, `L` or `XL`), not a delivery estimate. Criteria are
conditions, not claims already made true by writing a checked box. For phases
that create or implement a candidate, include the current passing original
baseline, settled applicable behavior/target and authorized candidate scope as
entry conditions. Analysis/specification/design phases can precede that baseline;
their criteria describe their actual inputs and decisions. Include executed candidate contract checks,
independent findings and fault sensitivity as appropriate exit conditions. If more
phases are useful, show sequence/dependencies with a Mermaid flowchart, not invented
dates. Reference actual artifact paths; never fabricate measured outcomes.

## Continue, correct and resume

Present the concrete scope and remaining decisions. Existing authorization for a
specified implementation carries forward; do not impose another routine approval
because the upstream command has a popup/plan-mode checkpoint. Broad permission
to develop this plugin does not approve an unspecified application target or behavior
change. If such a decision is essential, leave that work pending and continue
independent authorized preparation.

Treat conversational corrections as changes to the brief. Persist the person's
actual wording and affected scope in `INTENT.md`, update the relevant criterion
and contract, and explain what evidence must be refreshed. The user does not have
to edit the file manually. An agent's proposed relaxation is labelled `Proposed
revision:` and cannot silently replace a binding criterion. Preserve prior versions
and unaffected decisions. A candidate comparison binds the brief's exact bytes;
a changed brief requires review of applicability and a newly bound comparison,
not automatic replay of an earlier pass.

When the original baseline is missing or stale, use
[Playwright baseline preparation](playwright-baseline.md) for the captured BDD
path or the shared [native original baseline](upstream-verification.md#establish-the-native-original-baseline-before-implementation)
for the selected native runner. Then follow the applicable
[modernization mode](modernization-modes.md) when its actual entry criteria hold,
and [upstream verification](upstream-verification.md) for the full proof checks.
The [HTML overview](project-overview.md) presents saved records; it does not replace
test execution, compute new proof or grant acceptance.
