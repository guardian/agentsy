---
description: Extract and verify source-linked business rules and data objects, preserving stable rule IDs and human review questions.
---

<!-- Adapted from Anthropic's code-modernization plugin (Apache-2.0).
Modified for native Copilot commands and this port's workflow.
See [LICENSE](../../LICENSE) and [NOTICE](../../NOTICE). -->

Read the [modernize skill](../../skills/modernize/SKILL.md) from the loaded plugin
and follow its shared rules and package-root resolution.

Use the [rule extraction stage](../../skills/modernize/references/discovery-stages.md#extract-rules).
Use native extraction lenses over the requested scope, verify executable evidence
and merge findings without renumbering existing rules. Save validated `rules.json`,
`BUSINESS_RULES.md` and `DATA_OBJECTS.md`. Keep source interpretation separate from
human decisions; continue to review where needed and then the brief.
