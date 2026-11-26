# Examples

## Try a small review

The bundled [checkout example](../../examples/checkout/README.md) contains a small
Python module for delivery pricing and refund eligibility. Copy it into a new
folder from the plugin root:

```sh
plugin_dir="$(pwd -P)"
example_dir="$(mktemp -d "${TMPDIR:-/tmp}/modernisation-example.XXXXXX")"
cp -R "$plugin_dir/examples/checkout/." "$example_dir/"
printf '%s\n' "$example_dir"
```

Open that folder in VS Code with the plugin installed, select `modernize-start`
and send:

```text
/editorial-tools-modernisation.code-modernisation modernize-start Review legacy/shop/checkout.py and propose tests that protect its current behaviour. Stop before implementation.
```

For CLI, start a session from the example folder:

```sh
cd "$example_dir"
copilot --no-auto-update --plugin-dir "$plugin_dir"
```

Then use `/editorial-tools-modernisation.code-modernisation:modernize-start` with the same request.

Expect a source-backed review, saved findings and a test proposal. The request
stops before test authoring or application changes. This example checks discovery
and conversation; it has no browser application and cannot establish a browser
baseline or a completed migration.

## Assess your own application

Open the application and select `modernize-start`:

> Assess this project and recommend a small first modernisation.

The assessment should identify observed features, existing coverage, suggested
slices and inspection limits. Continue with your chosen scope:

> Migrate only the search form from Angular to React, preserving its current behaviour.

The agent reuses suitable infrastructure and tests, establishes missing
characterization coverage on the original, then verifies a separate candidate.
Keep existing tests. See the [project walkthrough](project-walkthrough.md) for
working folders and the [supported scope](supported-scope.md) for execution limits.

## Choose a different modernization mode

For a same-stack version change, select `modernize-uplift` and specify both versions:

> Upgrade this application from Java 8 to Java 17, preserving its behavior and structure.

For a replacement architecture, select `modernize-reimagine`:

> Propose a simpler architecture for this application. Keep the existing user-facing capabilities and stop before scaffolding.

The agent saves the specification and architecture for your concrete decisions.
Scaffolding starts only after applicable approval and original-behavior tests.
For security findings and proposed fixes, select `modernize-harden`:

> Review this application's security risks and prepare patches for review. Do not apply them.

## Prepare tests without migrating

Select `modernize-setup-tests`:

> Prepare the E2E setup for the search form. Reuse existing infrastructure and validate a small starter suite. Stop before migration.

The result includes actual setup checks, coverage gaps and the next action.
Repeating the request should reuse the saved setup and revisit affected checks.

## Check progress or return later

Select `modernize-status` for a read-only check:

> Where are we with the saved work in `analysis/catalogue/`?

Select `modernize-start` to continue:

> Resume the saved work in `analysis/catalogue/`.

Use your actual analysis directory. The HTML report links supporting records and
provides continuation text. Share the application's source, tests and analysis
through your normal Git workflow so a teammate can use the same request. See
[progress and continuation](progress.md).
