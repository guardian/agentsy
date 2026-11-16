# Use the loaded plugin and native specialists

Use this reference when first using helpers in a session, after a plugin refresh,
or when delegating work. These are client setup checks within the existing
workflow, not another modernization stage or a user questionnaire.

## Check the actual installed copy

Find the loaded plugin root from the command/skill path supplied by the client.
Walk its ancestors to the nearest `plugin.json` naming `code-modernisation` with
the bundled `scripts/check_installation.py`. Do not assume a fixed parent count:
clients can expose `skills/modernize` or materialize skills below
`com.github.copilot/skills`. Do not use the application's working directory or a
different source checkout as evidence that the loaded cache is ready. Read the
canonical `<plugin-directory>/skills/modernize/` skill and references before
following their cross-package links; do not resolve those links from a relocated
client-generated copy.

Before the first helper execution, run the bootstrap checker through Python:

```text
python3 "<plugin-directory>/scripts/check_installation.py" --plugin-root "<plugin-directory>"
```

Retain its actual output and loaded root/version in the existing workflow/setup
record. The checker verifies packaged runtime bytes and directly invokes the
runtime helpers with `--help`; it does not execute the application or call a model.
Reuse a successful check within the same session while that installation remains
unchanged. Recheck after a refresh, a different loaded root or a helper error.
Delegates using the same unchanged copy can reuse the parent's recorded check.

If the report says `repairEligible: true`, the only detected fault is repairable
missing execute bits. Within existing authorization to maintain this plugin,
restore those bits once using the checker's explicit repair option:

```text
python3 "<plugin-directory>/scripts/check_installation.py" --plugin-root "<plugin-directory>" --repair-execute-bits
```

Inspect the actual repair and direct-help results before continuing. This repair
is limited to the allowlisted, byte-matching installed helpers; it does not alter
code or project files. Do not use blanket `chmod`, repair a mismatched package,
copy files from another version, or repeatedly retry. Missing/corrupted files
need a fresh trusted installation. A non-owner/read-only cache, executable-access
failure, or client permission denial is not a missing-bit repair: retain the
diagnosis and continue permitted inspection. Do not reroute a denied command
through Python, another shell or a different installation. Python here is the
documented bootstrap interface, not an alternative runtime-helper execution path.

## Preserve helper output

Save helper output exactly as emitted, including explanatory notes. Prefer direct
shell redirection when command execution and artifact writes are authorized. Use
fresh regular-file paths in the existing analysis area, never source/input files,
symlinks or special files. For source snapshots, keep outputs outside the measured
root or in an explicitly excluded output subtree, following that helper's rules.
For example:

```sh
(
  set -C
  "<plugin-directory>/scripts/inventory.py" --source "<source-directory>" \
    > "<analysis-directory>/inventory.json" \
    2> "<analysis-directory>/inventory.stderr.log"
)
```

The subshell's `set -C` refuses to overwrite existing regular files. The helper is
its final command, so the native tool retains the actual exit code. Use the same
capture pattern for other helpers with their documented arguments; the readiness
checker still uses its Python bootstrap invocation above. Record the command,
output paths and observed exit in the existing setup/workflow note. Do not merge
stderr into JSON, use a pipeline that masks the exit, or retype, reword or
parse/re-serialize the raw output. Keep interpretation in separate notes.

For a legitimate correction/recheck, preserve prior output and use fresh paths
for both streams; update downstream inputs and workflow links to the actual paths.
A redirection failure may occur before the helper runs and leave an empty new
file. Record it as a capture failure, not helper evidence. A nonzero helper exit
can still produce a useful JSON error report: retain it without claiming a pass.
Inventory errors go to stderr and may leave stdout empty.

If the client has already retained the output as a resource, an authorized exact
copy is also suitable; do not rerun solely to obtain prettier output. Keep wrapped
terminal resources as `.log`/`.txt`, not purported JSON. If raw JSON or the exit
cannot be recovered, record that limit rather than reconstructing evidence. A
permission denial remains a stop, not a reason to switch capture/invocation tools.

## Select the actual specialist and model

Use the bundled roles as work requires: `business-rules-extractor` for bounded
source rules, `test-engineer` for scoped tests/execution, and `architecture-critic`
for independent read-only review. Prefer the registered specialist, using the
exact identifier exposed by this client's agent inventory/tool schema; names may
be namespaced. Loading a skill or reading a role file alone does not start one.

Carry forward the user's model choice or the current session's selected model.
Use the live client/tool contract and available session information to distinguish
these routes; the editor name or model brand alone does not identify the harness.
The bundled agents deliberately omit a fixed model to remain reusable.

- **VS Code Local `runSubagent`:** when the parent uses BYOK and the selected
  registered profile has no fixed model, omit the optional `model` argument to
  inherit the parent's selection. A missing override identifier is not a reason
  to skip that supported delegation. This satisfies a request to keep the current
  parent model; it does not satisfy a request for a different child model.
  A profile's configured model can override inheritance. Local's optional
  `chat.subagents.defaultToAuto` can also affect non-BYOK parents; use an established
  inheritance contract or a known explicit override in those sessions. For a
  generic fallback, account for its current/inherited profile before assuming the
  same route. Do not generalize this Local behavior to SDK tasks hosted in VS Code.
- **Copilot CLI/SDK `task`:** when the tool exposes a model argument, pass the
  selected model explicitly, including independent reruns and follow-up tasks.
  Built-in task profiles can select their own model when it is omitted. Saying
  “inherit the model” in the prompt does not override that selection.

For an explicit override, resolve its identifier from the live client information:
Copilot `task` uses runtime/provider-qualified IDs; Local `runSubagent` uses
qualified display names such as `Model Name (Vendor)`. Use only exposed fields;
do not guess identifiers, copy aliases between clients, or deliberately submit an
invalid model to obtain a list. A supported inheritance route does not need an
override identifier or an extra model-discovery call.

Where no per-call model control exists, use supported session/profile selection.
Do not edit user/global configuration, inspect credentials, or hardcode a pilot
model into the package. If the required selection has no supported route, report
that limitation and continue permitted parent work; keep the dependent independent
check incomplete. Distinguish a supported selection route from observed routing:
if child metadata is unavailable, record the observed model as unknown without
discarding an otherwise completed review. Do not infer identity from a child's
prose or launch extra model calls just to collect it.

Give each specialist a concrete task with the relevant source/artifact paths,
intent, actual decisions, allowed tools/writes/execution, cleanup/retry limits and
expected return. Include applicable project instructions; do not assume all
parent conversation or repository instructions are inherited. Preserve the role's
boundaries: extractor/critic are read-only; a test engineer may write tests and
run the authorized harness but may not implement the application change.

Use a listed native specialist when available. Distinguish a role absent from an
exposed inventory from registration that is unknown because no inventory exists.
If the tool supports custom profiles and the exact client identifier is known,
try that role once and retain the result/error. Otherwise record the narrower
capability uncertainty. Do not infer “unavailable” merely because a generic task
was used, and do not probe invented aliases or retry a permission denial.

When a native role cannot be selected through the available interface but ordinary
delegation is allowed,
read the corresponding bundled file in `com.github.copilot/agents/` and supply its
instructions to a suitable generic delegate, together with the same bounded
task and selected model. Apply native tool restrictions where supported. Label
this as a **generic delegate using bundled role instructions**; prompt restrictions
are not proof of the named profile's enforced tool configuration. A separate
reviewer can still provide independent findings, but do not claim the named agent
ran. Without delegation, perform permitted work directly and retain the lack of
independent review/execution.

Collect the completed result with the client's native task/result mechanism.
Record the actual agent/profile identifier, requested model (or selected parent
when its identifier is hidden), selection route (explicit override, supported
inheritance or client default), observed model (or unknown), result location and
any fallback/error in the existing workflow or verification record. A background
handle is not a completed review. Neither an override nor supported inheritance
proves the model actually used. Report a discovered
model mismatch; do not relabel or erase the run, or silently repeat costly work.
