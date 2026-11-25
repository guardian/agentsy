---
description: Independently recheck modernization with actual tests, output comparisons and the applicable scoped evidence or upstream proof checks.
---

<!-- Adapted from Anthropic's code-modernization plugin (Apache-2.0).
Modified for native Copilot commands and this port's workflow.
See [LICENSE](../../LICENSE) and [NOTICE](../../NOTICE). -->

Read the [modernize skill](../../skills/modernize/SKILL.md) from the loaded plugin
and follow its shared rules and package-root resolution.

Read [upstream verification](../../skills/modernize/references/upstream-verification.md)
for native results, rule tracing, independent canaries, fresh output comparisons
and the computed proof verdict. Existing Playwright BDD work also retains its
[candidate contract checks](../../skills/modernize/references/implementation-and-verification.md).
Follow the brief's verification scope and report each path's actual results
separately; a scoped pass is not automatically upstream `PROVEN`.

Preserve failures, earlier evidence and human decisions. Distinguish missing or
stale execution from a documentation correction; never present old results as a
fresh check or a computed verdict as human acceptance.
