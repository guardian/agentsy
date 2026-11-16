---
description: Review security risks and prepare independently reviewed remediation patches without changing the original application.
---

Read the [modernize skill](../../skills/modernize/SKILL.md) from the loaded plugin
and follow its shared rules and package-root resolution.

Use the [hardening mode](../../skills/modernize/references/modernization-modes.md#harden-findings-and-a-reviewable-patch).
Use native security review, verify important findings and retain scan gaps.
Save redacted findings and minimal proposed patches, isolating credential-bearing
hunks in verified private locations. Review each patch and keep failed hunks out
of the deliverable. Applying a patch or changing behavior needs its own applicable
authorization; a hardening report does not establish that a fix was executed.
