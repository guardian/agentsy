# Progress and continuation

The plugin saves working context under `analysis/<project>/`. You can read the
HTML report, ask for status or return in a new chat using that directory.

## See the features before choosing a change

Select `modernize-start` and ask:

> Assess this project and recommend a small first modernisation.

The assessment records observed features, source evidence, dependencies, existing
coverage and suggested starting slices. Uninspected areas and uncertain behavior
remain visible. If you already know the desired change, request it directly and
keep the investigation focused on that feature.

## Check where things stand

Select `modernize-status`, naming the saved analysis when needed:

```text
/code-modernisation modernize-status Show the saved position in analysis/catalogue/.
```

In CLI, use `/code-modernisation:modernize-status`. The response summarizes saved
progress, gaps, open decisions and the next action. Status is read-only: it does
not rerun tests or continue implementation. Evidence freshness remains unknown
unless it was checked separately.

## Open the HTML report

The agent creates and links `analysis/<project>/REPORT.html` after assessment,
then refreshes it after meaningful saved checkpoints. Open the file in a browser;
it needs no server. The page brings together features, current work, decisions,
evidence and copyable continuation requests.

The six workflow cards group the saved work:

1. **Goal** — outcome and boundaries.
2. **Understand** — observed features, behavior and uncertainties.
3. **Plan** — proposed change and preservation requirements.
4. **Test the original application** — preparation and measured original behavior.
5. **Modernize** — the separate implementation.
6. **Verify the modernized version** — comparison and remaining gaps.

These cards are a summary, not a sequence of prompts you must send. The initial
assessment remains separate from later selected work. Completing one feature
does not imply that the whole application has been modernized.

The evidence view shows selected runs before earlier attempts. Test results,
environment checks and cleanup outcomes stay separate: tests may pass inside an
unsuccessful capture. Deliberate regression canaries remain expected failures.
Missing or unsupported evidence is shown as unknown, rather than assumed passed.

When the upstream proof checks run, their verification record contains the
computed per-module verdict and reasons. A scoped Playwright BDD comparison is a
different result; the report does not promote it into full proof. See
[verification results](supported-scope.md#verification-results).

### Test readiness

**Test readiness** shows the ordered coverage plan and saved stack, fixture and
authentication checks:

- Coverage rows describe user outcomes, dependencies, test state and gaps.
- Setup checks show named assertions, observation time and cleanup results.
- Setup-only continuation prompts let you prepare or repair tests from chat.

A plan records intended work. Authored tests, runnable tests and executed tests
are distinct states; execution can fail. Passing setup checks alone do not
establish preservation coverage or a qualifying original baseline.

### Refresh the view

The report is a snapshot. Reload the browser after the agent regenerates it.
It displays saved records and never runs an agent or revalidates their evidence.
To rebuild only the page, ask:

> Refresh the HTML report for `analysis/catalogue/`.

You can ask to omit HTML. If rendering fails, saved Markdown and evidence remain
available for chat and continuation. Markdown is formatted for readability, with
its original source available in a disclosure; JSON remains literal.

## Continue later

Open the application project, select `modernize-start` in a new chat and send:

> Resume the saved work in `analysis/catalogue/`.

Use the actual analysis directory. The agent reads the intent, setup, decisions,
progress and selected evidence, checks affected inputs and continues the next
unfinished work. Unaffected findings and tests are reused.

To hand work to a teammate, use the application's normal Git workflow to share
selected original and modernized source, tests, configuration, analysis records
and required evidence. Keep dependencies, build output and secrets excluded with
targeted ignore rules. The [project walkthrough](project-walkthrough.md) explains
the folder layout and handoff.

A new checkout or environment needs fresh observations before old results can
support a current pass. Original receipts remain records of their original runs.
The HTML page and chat history alone do not contain everything needed to resume.

Behavior decisions, intentional changes and final acceptance remain yours.
