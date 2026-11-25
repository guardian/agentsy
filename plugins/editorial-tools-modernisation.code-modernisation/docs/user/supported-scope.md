# Supported scope

This plugin ports the Claude modernization workflow to native Copilot chat. It
retains conversation, reviewed behavior rules, planning, separate implementation
and verification. The HTML report provides a saved overview in place of the
Claude-specific UI.

## Included

- Source discovery, feature mapping, source-backed rule extraction and review.
- A scoped modernization brief and conversational corrections/continuation.
- Test setup discovery, suitable existing-test reuse and missing coverage.
- Tests on unchanged behavior before a separate implementation, using suitable
  native suites or the bundled Playwright BDD path.
- Same-stack uplift, cross-stack transformation and architectural reimagine.
- Candidate comparison, rule tracing, independent verification and proof checks.
- Security review with proposed remediation patches.
- Named analysis, extraction, testing, migration, architecture and security roles.
- A local HTML report with features, progress, readiness, evidence and next steps.

Guardian Agentsy practices inform E2E setup, feature ordering, source-linked BDD
scenarios, reusable steps, fixture checks and optional pan-domain auth. They are
adapted for preservation of unchanged behavior. Full Guardian policy compliance
is not implied.

## Current boundaries

| Area | Current support |
| --- | --- |
| Clients | Copilot CLI and VS Code Agent chat. Specialist and model-selection capabilities depend on the client. Standalone Codex is outside this package's supported path. |
| Runtime | Python 3.9+, Node.js and POSIX helper execution. Optional E2E probe/auth helpers require Node 22+. Windows-native helper execution is unsupported. |
| Modernization modes | Uplift preserves structure across versions; transform rewrites a selected module; reimagine designs and scaffolds approved services. Hardening proposes reviewed patches without applying them. |
| Test runner | Reuse suitable native suites. Upstream checks parse JUnit/TRX reports and supported runner logs. Per-test reports support rule tracing; logs can establish counts. Unsupported formats remain gaps. The Playwright BDD path retains its stricter source/test/environment capture checks. |
| Capture | The bundled helper handles one local Node web server with Chromium. Other lifecycles need suitable project-local capture integration and environment/cleanup checks. |
| E2E setup | Bundled recipes and probe/auth helpers support bounded starter validation. Container access and application-specific integration must be available. No generic Testcontainers capture adapter or automatic CI setup is included. |
| Report | A snapshot refreshed at saved checkpoints. It displays evidence, without validating it or resuming processes. |
| Acceptance | Scoped passing tests do not establish whole-application equivalence or your acceptance of a change. |

The added uplift, reimagine, hardening and native-report paths have not yet had
live consumer trials. Test and package checks alone do not establish ordinary
model-backed use in every client or application.

A setup-only request stops after its bounded checks. A migration request can
continue through supported stages within the existing scope. Normal client
permissions and essential behavior decisions can still require your input.

Meaningful unchanged-original tests are required before implementation. If the
original runtime is unavailable, analysis and planning can continue. Any decision
to implement using recorded traces needs explicit scope and retains its limits;
the ability to produce a partial proof verdict does not waive that decision.

Reimagine preserves two human decisions: which capabilities are essential or
deliberately dropped, and approval of the concrete architecture before scaffolding.
Its generated acceptance tests can expose pending implementation; scaffolding is
not a completed rebuild.

## Verification results

The Playwright BDD comparison checks a retained scenario cohort. The upstream
proof pack computes `PROVEN`, `PARTLY PROVEN` or `NOT PROVEN` from actual native
results, traced rules, output comparisons, fresh inputs, an independent canary
and source checks, plus additional uplift checks. A scoped BDD pass is not a
proof-pack verdict. Target-only execution cannot establish full `PROVEN` evidence.

The verdict applies to the supplied evidence and selected scope. It does not
establish correctness outside that scope or replace human acceptance.

The plugin records whether named specialists actually ran and whether their
model routing is known. It can continue permitted work in the main session when
delegation is unavailable, while identifying checks that were not independent.
No particular model or provider is required.

## Evidence and sharing

Original and modernized applications are tested in separate roots under the
consumer project. Saved receipts describe the source, tests and environment at
execution time. Changes to those inputs can require fresh measurements; restoring
a receipt does not make it a current pass.

The plugin saves and refreshes analysis records and the report. Committing,
pushing, opening pull requests and integrating a candidate into the active
application follow your explicit request and normal review process.
