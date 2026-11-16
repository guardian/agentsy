# Keep modernization inside the project

Use this reference before creating source copies, choosing new evidence paths or
preparing a handoff. Preserve the Claude plugin's `legacy/`, `analysis/` and
`modernized/` arrangement inside the consumer project/workspace. The plugin package
remains separate. A normal request is enough; the agent chooses and records paths
without requiring a folder specification, a config file or a new Git workflow.

## Default layout for new work

```text
<consumer-project>/
├── <existing application files>          # Remain unchanged by the migration
├── analysis/<system>/                   # Plans, progress, REPORT.html and evidence
│   ├── PROJECT_SETUP.md
│   ├── WORKFLOW.md
│   ├── attempts/                        # Preserved baseline/candidate attempts
│   └── .local/                          # Optional private scratch and bulky output
├── legacy/<system>/                     # Runnable original plus prepared tests
└── modernized/<system>/<module>/         # Transform candidate
```

Uplift and reimagine retain Claude's mode-specific roots:
`modernized/<system>-uplifted/` for a complete version-upgrade copy, and
`modernized/<system>-reimagined/<service>/` for rebuilt services. The upstream
proof tools discover these modes by their paths. Keeping those conventions avoids
a separate track configuration and leaves existing transformation runs unchanged.
Record the selected mode and actual roots in the brief and setup notes.

Reuse the existing analysis name; otherwise choose a short name from the project
identity or the user's preference. Keep the active application's paths and files
in place. Create the original test copy when the authorized work needs testing,
and the modernized copy only after the passing original meets the implementation
entry criteria. Discovery-only work does not require either copy.

The baseline root is `legacy/<system>/`, **not the enclosing project root**.
The candidate root is the selected transform, uplift or reimagine tree. These physical test roots
must be nonoverlapping: neither can contain the other or the analysis outputs.
A source symlink back to the enclosing project defeats this separation and is
not a substitute for the original copy. Keep the existing physical-root checks.
This materialized test copy is a deliberate addition to upstream's copy-or-link
source convention, needed for independent captured executions and portable tests.

Inspect existing paths before creating anything. Named directories are not
necessarily plugin output and are never disposable merely because of their names.
For a collision or monorepo, choose suitable unoccupied paths within the same
repository and record the reason; preserve existing applications and analyses.
Include the dependencies needed to run the selected feature, even if that needs
a whole-project copy. The implementation remains bounded to the selected change.
No external sibling folders, worktrees or new branches are required by default.
An explicit user layout or an existing recorded run can retain another location.

Keep read-only discovery scoped to the actual application. Before output copies
exist, use its normal source scope. Once a prepared original exists, use that
selected `legacy/<system>/` tree for further legacy discovery. For a workspace
already containing mixed output trees, choose an actual source subtree or a
precise supported module selection, and inspect other relevant files directly.
Do not count copies or runner code in `analysis/` as additional product features.
Record the discovery root and selection separately from test roots; inventory
does not inherit snapshot exclusions. A change of discovery root needs a fresh
inventory and validation with reviewed citations, preserving prior records and
stable rule IDs; do not rewrite a saved inventory's source path.

## Prepare copies without copying the workspace into itself

Record the selected source revision, relevant local changes and copy method in
`PROJECT_SETUP.md`. Use workspace-relative paths for the active source, original,
candidate, analysis and any scratch directories so a teammate can locate them.
For a non-Git source, record its provenance and the absence of a commit identity.

Build the original copy from the actual selected source. Do not copy the enclosing
`.git` file/directory, modernization output trees or private scratch into it, and
do not initialize nested repositories. Determine the exact source exclusions
before copying so a recursive copy cannot ingest its own destination. Apply
exclusions to the actual paths; an application may have legitimate source named
`legacy`, `analysis` or `modernized`. Record any materialized symlinks and their
provenance rather than silently following links into unrelated content.

Keep source, relevant configuration, locks, fixtures and suitable existing tests.
Prepare the missing tests and harness in the original copy before its baseline
capture. Do not blanket-exclude generated files: generated BDD specs are required
captured inputs. Source-copy exclusions and snapshot exclusions have different
purposes; record both. Snapshot scope must cover all execution inputs required by
the [baseline contract](playwright-baseline.md).

Establish Git trackability during this preparation, before baseline capture.
Check required generated specs and copied ignore rules using the handoff checks
below. Prefer narrow rules in the enclosing repository where sufficient. Any
necessary change to a copied `.gitignore` or other captured configuration belongs
before the baseline; changing it later requires the affected recapture/new-origin
flow rather than an edit to frozen evidence.

After the original baseline permits implementation, create transform and uplift
copies from that **prepared original**, not from a fresh Git export that
could omit new tests or local setup. Preserve the complete included file membership,
bytes and modes. Capture its origin before changes, using the same evidence
exclusions as the original. Keep dependencies and build output separate from
required inputs as the existing capture guidance describes.
Reimagine creates the approved target skeleton separately and carries forward the
original behavior contract and fixtures; it does not pretend the skeleton is a
byte-identical copy. Keep its authored but unimplemented tests visibly pending.

## Make a checkpoint shareable

Keep the original and modernized source trees, required tests/configuration,
generated specs and shareable analysis records trackable by the enclosing
repository. Preserve the exact receipt, linked snapshots, native listing/results,
process/environment records and runner/config provenance needed to inspect saved
claims. Keep their attempt-relative relationships intact. `REPORT.html` is a
convenient committed view; it cannot replace those records.

Recheck the ignore rules established during preparation. Where needed, make
narrow ignore entries for the
actual dependency installations, build output, local secrets and private scratch
or bulky traces, rather than ignoring whole `analysis/`, `legacy/` or `modernized/`
trees. Confirm necessary files with scoped `git status --short --untracked-files=all`
and `git check-ignore -v --no-index -- <required-paths>`; inspect ignored required
specs as well as source and JSON evidence. If a required input is ignored, repair
the narrow rule within scope or record the gap, rather than claiming the handoff
is complete. Do not force-add an entire output tree. In a non-Git workspace, report
that files are prepared locally and Git sharing is not yet established.

Keep credentials and private traces out of the shared files. Evidence already
containing sensitive data must remain intact in private storage: do not sanitize
or edit a bound receipt to make it shareable. Record its private dependency and
handoff limitation, and create a new safe attempt when needed. Missing referenced
files mean a partial handoff, not a portable verified result. Keep disposable
scratch under `analysis/<system>/.local/` when appropriate; retain shareable canary
results and the fault diff outside it, so cleanup does not erase the evidence.

Record the next action and any required setup in `WORKFLOW.md`, with relative
links to the exact files. Use the repository's existing branch/commit workflow.
Report what is ready to commit and any omitted evidence; commit or push only when
the current user authorization includes that action. The modernization request
alone does not publish to GitHub. Do not introduce automatic commits, a mandatory
branch pair, worktrees or nested Git histories to provide this layout.

## Resume after a clone or move

Read the committed intent, setup, workflow, brief and attempt records, then resolve
their relative locations against the new checkout. Preserve old receipts exactly,
including their original physical roots and environment observations. Portable
paths in notes help find the work; they do not make those executions current in a
new directory or on another machine.

Check the active application against the revision and local changes from which
the original was copied. If it has changed, report the divergence and use the
recorded scope to decide whether to continue the saved snapshot or refresh the
selected source; resolve a genuine scope ambiguity with the user. Do not silently
copy active changes into the frozen original or imply that an old baseline covers
them. Compare the current original/candidate source, tests and configuration and
collect the required environment observations. A different physical test root or
relevant environment requires a new capture for the affected execution. Never
rewrite absolute paths, times or hashes in old receipts to make a validator pass.
Where a fresh baseline requires
a new candidate origin, preserve the existing implementation diff, create a new
candidate round from that baseline, capture its untouched origin, and reapply the
bounded change before verifying it. Do not reconstruct an origin from already
modernized files. Follow [continuation and corrections](project-workflow.md) for
the affected dependencies; unchanged discovery and human decisions remain useful.

Previously recorded external folders remain valid historical locations. Do not
move them or rewrite their evidence merely to adopt this default. Apply the
in-project layout to new work or a documented new round; preserve the old results
and link the transition. Sharing Git history supplies continuity, not an automatic
passing baseline or human acceptance.
