<!-- Adapted from Anthropic's code-modernization plugin (Apache-2.0).
Modified for native Copilot discovery and local artifacts.
See [LICENSE](../../../LICENSE) and [NOTICE](../../../NOTICE). -->

# Preflight, assessment, mapping and rule extraction

Use the selected stage below, together with the main skill's shared rules for
scope, source protection, native delegation, continuation and report refresh.
Read its linked pinned command for the complete checks and artifact format.
These adaptations replace Claude tools and presentation; they retain the
underlying analysis. Do not invoke Claude `Workflow`, telemetry, panes or viewers.
Use native Copilot specialists and save their returned findings in the existing
analysis records. A saved result permits continuation; it is not a resumed process.

## Preflight

Follow the pinned [preflight](../../../upstream/commands/modernize-preflight.md).
Establish the runnable original under `legacy/<system>/` using the existing
[workspace layout](workspace-layout.md), preserving the active application.
Record its real location and completeness. Reuse an existing root; never replace
it or create a symlink into the enclosing consumer checkout.

Keep all five upstream **Answers** topics: scope and external consumers, local
build/test feasibility, bespoke build infrastructure, prior attempts and off-limits
work. Reuse actual answers already supplied; quote them faithfully. Inspect what
the repository can establish and label it as observation, not a person's answer.
Ask only for essential unresolved information; leave other unanswered topics as
open items. No fixed popup sequence or repeated permission is required.

Complete every applicable check, even if an earlier one fails:

- Detect the stack and source split; identify analysis tools and missing capability.
- Inspect CI, manifests, parent build files, generators and private feed setup.
  Report actual versions and dependency sources without exposing credentials.
- In an authorized disposable copy, syntax-check a representative source and
  restore/build one small real project using the discovered build path. Prove the
  target stack with a tiny project that builds and executes one real test. Keep
  commands, output and failures. Source inspection alone is not this smoke test.
- Identify missing includes, schemas, deployment descriptors and binary-only code.
- Note available runtime evidence and source history; do not add telemetry collection.
- Trace outbound dependencies and inbound consumers across the selected boundary.
  Record shared nodes needing a transition decision in the brief.
- Inspect the source protections actually available in this environment. Do not
  read or write Claude settings, invent a Copilot permission equivalent, or claim
  a prompt instruction is an operating-system write lock.

Builds and analyzers that write use scratch copies; never build inside the
preserved original. Respect established service/environment access. Missing
tooling is a measured gap, not permission to move execution elsewhere.

Write `PREFLIGHT.md` with **Answers**, the scope-boundary finding, all check
outcomes and fixes, and readiness per requested stage. A missing old runtime may
permit source analysis and planning with recorded traces; it does not establish
an executed original baseline or full equivalence. Target build/test readiness
is required before implementation. Follow the chosen execution path's baseline
requirements. Finish with the most important remaining prerequisite and assessment.

## Assess

Follow the pinned [assessment](../../../upstream/commands/modernize-assess.md).
Bound the work to the requested feature or whole system; do not silently shrink
an estate request into one convenient module.

Measure inventory, complexity and technology from real tooling or clearly named
fallbacks. Keep the COCOMO calculation `2.94 × KSLOC^1.10` as a relative index;
never turn it into an agent delivery estimate, price or schedule. Inspect build,
data, integration and test infrastructure. Use native `legacy-analyst` tasks for
the structural map and technical debt, and `security-auditor` for source-backed
security findings, concurrently when useful. A missing specialist result remains
a gap. Check citations and synthesize the returned findings yourself.

Write the upstream `ASSESSMENT.md` sections: Executive Summary, System Inventory,
Architecture at a Glance, Production Runtime Profile (or unavailable), Technical
Debt, Security Findings, Documentation Gaps, Relative Scale and Recommended
Modernization Pattern. Save the domain diagram as `ARCHITECTURE.mmd`. For broad
requests add the existing observed-features table; show actual coverage limits.
Recommend uplift, transform or reimagine from the user's goal and source; rehost
and replace may require analysis without a code implementation phase.

Keep credentials out of shared artifacts. Follow the hardening reference's
quarantine rules if an inventory is needed. Assessing security does not authorize
applying a patch. Use available runtime observations only when access is already
authorized; absence of telemetry is explicit, not a blocker to static assessment.

For an authorized portfolio request, assess the immediate system directories
with the same metric definitions and report which were actually examined. Save
the comparison and sequencing rationale as `analysis/PORTFOLIO.md`; use each
system's normal HTML report instead of introducing another viewer.

## Map

Follow the pinned [map](../../../upstream/commands/modernize-map.md) for extraction
and the exact `topology.json` schema. Reuse an existing compiler/ecosystem graph
or supplied export first, spot-check its edges against source, and add entry
points, configuration-mediated calls, data stores and business flows it omits.
If a script is needed, retain it as `extract_topology.py` or `.sh` with its method.

Resolve direct calls, configuration/dispatch edges and source-to-storage joins.
Use unique source locations for module leaves, stable node IDs, `source`/`target`/
`kind` edges and source-backed persona flows. Incomplete dynamic-call resolution
prevents a confident dead-code claim. Sanitize datastore URLs and observations.
Preserve upstream's `entryPoints`, `deadEnds`, `observations` and `flows` fields.

For large estates, save per-domain chunks under `map/`, with their inspected
source scope and missing coverage. Reuse unchanged chunks after checking their
inputs; an existing filename alone does not establish freshness. Merge by stable
IDs and retain unresolved relationships. A native `legacy-analyst` may describe
selected nodes from their source and connections; omit invented details and keep
description work proportionate to the task, honoring `--no-describe`.

Save `call-graph.mmd`, `data-lineage.mmd` and `critical-path.mmd`, collapsing dense
graphs to readable domain views. The existing HTML report presents the saved
map and diagrams; do not generate Claude's `TOPOLOGY.html` or add a second UI.

## Extract rules

Follow **Method B — Direct subagents** in the pinned
[extraction command](../../../upstream/commands/modernize-extract-rules.md).
Use the existing inventory and `business-rules-extractor` role. Delegate the
calculation, validation/eligibility and state/lifecycle lenses over the selected
source, then merge and verify their findings. Scope larger work by module; the
bundled sharder can prepare `extract-rules.modules.json` from the existing map.
Include configuration tables, SQL and shared definitions when they hold logic;
an omitted file type is a coverage gap, not evidence that it has no rules.

Keep a finite batch size within native client limits and the operating agreement.
Collect results before continuing, retain completed module coverage, and retry
only missing or affected work. Do not import upstream workflow journals, large
fanout estimates or a durable execution engine. Broadening the agreed resource
scope requires an actual decision, not an assumed unlimited extraction budget.

Reinspect every cited executable range and governing guard. De-duplicate rules
without discarding distinct conditions. Keep the port's validated `rules.json`,
stable IDs such as `R-001`, previous decisions and current inventory binding.
Run its existing discovery validation. Generate `BUSINESS_RULES.md` with a summary
table and cards containing category, priority, source, plain-English meaning,
concrete Given/When/Then, parameters, edge cases, suspected defects and confidence.
Use `### R-001: <title>` for retained IDs; do not renumber history to `RULE-001`.
Keep the machine-readable upstream labels, for example:

```markdown
### R-001: <source-backed title>
**Category:** Validation
**Priority:** P0
**Source:** `relative/source.ext:10-20`
**Plain English:** <actual behavior>
**Specification:**
  Given <concrete condition>
  When <action>
  Then <observed or source-supported outcome>
**Confidence:** High | Medium | Low — <evidence or question>
```

This is a format example, not a rule to copy as evidence. Mark priorities as
analysis, and end with the questions needing human review.

Also write `DATA_OBJECTS.md`: core record/entity names, typed fields, relationships,
source locations and the rule IDs using them. Mark inferred types or relationships.
Report source coverage, rejected/comment-only findings and unresolved questions.
No findings are accepted merely because an agent agreed with another agent.
Continue to rule review where decisions are needed, then the brief, using the
existing continuation and report checkpoints.
