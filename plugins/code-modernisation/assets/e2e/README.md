# Local E2E recipes

These optional helpers belong to this plugin. Copy only the pieces a project
needs into its tested original tree, normally `e2e-tests/setup/`, and retain their
identity with the test harness. Reuse suitable existing code first. No Agentsy
checkout, skill installation or remote instructions are needed. Node 22+ runs the
helpers; the legacy application may retain a different compatible runtime.

## Shared multi-service stack

Use this recipe when several services need a shared lifecycle. Reuse the project's
existing stack module and script names; add only missing commands. Keep one place
responsible for starting the application, dependencies and fixtures, whether it
uses Testcontainers, Compose or existing project tooling.

| Command     | Stack ownership and behavior                                                                                                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dev:local` | Start the application and local dependencies, wait for readiness, publish connection details and keep them running for development. This process owns cleanup on exit or interruption.                                                            |
| `test`      | Generate the BDD specs and run headlessly against a ready local stack started by `dev:local`. Fail with an actionable message if that stack is missing, stale or configured for remote infrastructure; leave a reused stack running.              |
| `test:ci`   | Generate the specs, start a fresh isolated application and dependencies, run headlessly and stop everything this run started. Do not attach to the shared development stack. This command can run locally; adding a CI workflow is separate work. |
| `test:ui`   | Generate the specs and open Playwright UI against a valid shared local stack, or start an owned local stack if none exists. Leave reused resources running; stop owned resources when the UI exits. Regenerate specs when feature files change.   |

For a new container-based setup, use the same application image and dependency
configuration in local and isolated runs, with separate resources for each owned
stack. Keep a suitable existing setup rather than changing the legacy application
or adding containers solely to adopt these command names.

Adapt the shared lifecycle as follows:

1. Have the stack owner publish connection details only after readiness and fixture
   seeding succeed. Use the existing connection mechanism or a gitignored runtime
   file, for example under `e2e-tests/.runtime/`. Include the application URL,
   mapped mock/service endpoints, local mode and enough run/root/config identity
   to distinguish this stack from another project's or an earlier setup.
2. Let Playwright `globalSetup` (or the existing runner's equivalent) select the
   connection according to the command above. Validate its local routing, identity
   and live readiness before reuse; reject stale or remote records. Keep per-run
   connection state separate from the shared owner's record. Share the active
   connection with test fixtures so every worker uses the same endpoints. Read it
   at fixture runtime; configuration loaded before setup cannot rely on a file
   that setup has yet to create. Keep test keys in restricted ephemeral auth storage.
3. Track handles as resources start. If startup fails, clean up the resources
   already created before propagating the failure. After successful setup, return
   an owned-resource teardown from `globalSetup`, or use the runner's existing
   cleanup mechanism. Bound cleanup on test failure, UI exit and interruption too.
4. Remove only this owner's resources and connection records. A test run borrowing
   `dev:local` must leave that stack and its published record intact. Check for
   leaked owned resources and report cleanup failures rather than hiding them.

Reuse this lifecycle for the validation checks below. It is a project integration
recipe; the bundled [single-server capture](../../skills/modernize/references/local-bdd-capture.md)
does not support global setup or multiple services. Use the project's runner and
the existing evidence requirements for that topology.

## Stack and fixture checks

[validation.mjs](validation.mjs) provides:

- `assertLocalHttp(url, options)` for an expected HTTP status.
- `assertLocalJson(url, verify, options)` for assertions on bounded JSON data.
- `assertNoUnmatchedRequests(baseUrl, options)` for an enabled WireMock journal
  with no unexpected requests. Probe the intended stub paths as well; an empty
  journal without exercised routes is not fixture validation.
- `runSetupChecks({ phase, checks, cleanup, timeoutMs, cleanupTimeoutMs })` for
  sequential named assertions and a separate cleanup result.
- `writeSetupResult(path, result)` to create, never overwrite, a saved receipt.

HTTP probes accept only literal loopback addresses, including mapped container
ports, and reject redirects and embedded credentials. They do not certify an
application's outbound network isolation. Use local-only service configuration,
dummy AWS credentials, explicit SDK endpoints and environment/network controls.
Check the application's actual traffic and seeded resources; do not infer local
routing solely from configuration or an emulator's healthy response. If the
project needs a different network topology, reuse its reviewed probes rather
than disabling these checks or exposing a remote service through a proxy.

The following is a project integration pattern, not a bundled application runner.
The `stack.mjs` functions must use the project's actual lifecycle and readiness
conditions. They must register owned handles immediately, including during failed
startup, stop only those resources and verify that they have gone. Do not replace
them with no-op checks, unconditional returns or a second lifecycle controller.

```js
import assert from "node:assert/strict";
import {
  runSetupChecks,
  assertLocalHttp,
  writeSetupResult,
} from "../setup/validation.mjs";
import {
  startLocalStack,
  stopOwnedResources,
  remainingOwnedResources,
  assertLocalRouting,
  assertExpectedLogs,
} from "../setup/stack.mjs";

const output = process.argv[2];
assert.ok(
  output,
  "Supply a fresh setup-check.json path outside the tested root",
);
const owned = [];
let stack;
const result = await runSetupChecks({
  phase: "stack",
  timeoutMs: 120_000,
  checks: [
    {
      name: "Application ready",
      run: async (signal) => {
        stack = await startLocalStack({
          signal,
          onStarted: (resource) => owned.push(resource),
        });
        await assertLocalHttp(stack.healthUrl, { signal });
      },
    },
    {
      name: "Local dependency routing",
      run: (signal) => assertLocalRouting(stack, signal),
    },
    {
      name: "Expected runtime logs",
      run: (signal) => assertExpectedLogs(stack, signal),
    },
  ],
  cleanup: async (signal) => {
    await stopOwnedResources(owned, signal);
    assert.equal(await remainingOwnedResources(owned, signal), 0);
  },
});
await writeSetupResult(output, result);
process.exitCode = result.passed ? 0 : 1;
```

For `validate:fixtures`, use `phase: 'fixtures'` and assertions against actual
seeded data and mock responses, then check unmatched requests after exercising
those routes. The callbacks below belong inside the project's owned lifecycle:

```js
import {
  assertLocalJson,
  assertNoUnmatchedRequests,
} from "../setup/validation.mjs";

await assertLocalJson(
  stack.recordsUrl,
  (value) => {
    assert.deepEqual(
      value.items.map((item) => item.id),
      ["synthetic-record-1"],
    );
  },
  { signal },
);
await assertLocalJson(
  stack.mockResponseUrl,
  (value) => {
    assert.equal(value.content.id, "synthetic-content-1");
  },
  { signal },
);
await assertNoUnmatchedRequests(stack.mockBaseUrl, { signal });
```

Discover the real endpoints and response shapes; these example fields are not
defaults for another project. Seed after schema creation, reset state per scenario
and distinguish intentional negative responses from unexpected failures. Reuse
existing validation commands or expose these scripts as `validate:stack` and
`validate:fixtures` in the project's package manager. A receipt belongs in a fresh
attempt directory such as `analysis/<system>/attempts/setup-01/stack/setup-check.json`;
create that directory before invoking the script.

Each callback must assert the expected fact, throw on failure, honor its abort
signal and use bounded service-specific timeouts. A false return also fails.
The helper stops dependent checks after failure and still attempts cleanup; raw
exception messages and response bodies are not saved, so keep check names concise
and non-sensitive and retain appropriately redacted project logs separately.
Timeouts request cooperative cancellation, not process termination. A callback
that ignores cancellation can outlive the check. The project must also own its
process deadline, signal handling and resource-leak detection. Such a timed-out
attempt remains failed and cannot qualify as baseline evidence.

## Optional pan-domain authentication

Use [pan-domain-auth.mjs](pan-domain-auth.mjs) only when the application actually
uses Guardian pan-domain authentication. Keep its existing authentication and
authorization logic unchanged. The helper generates fresh RSA keys and unique
synthetic users per run; cookie signing is delegated to Guardian's library.

The tested recipe uses `@guardian/pan-domain-node` **2.0.0**, installed explicitly
and locked in the test workspace with the project's package manager, for example
`npm install --save-dev --save-exact @guardian/pan-domain-node@2.0.0`. This is an
optional library dependency, not a dependency on external skills. The signer is
not exported from that version's main entry point, so the pinned deep import below
is intentional; recheck it before changing the library version. Reuse a project's
already suitable library rather than upgrading the application.

```js
import { createCookie } from "@guardian/pan-domain-node/dist/src/panda.js";
import { createPanDomainFixture } from "./pan-domain-auth.mjs";

const auth = createPanDomainFixture({
  signCookie: createCookie,
  baseUrl: "https://sample.local.dev-gutools.co.uk",
  cookieName: "gutoolsAuth-assym",
  system: "sample",
  roles: { allowed: ["sample_access"], denied: [] },
  emailDomain: "guardian.co.uk",
});
await context.addCookies([auth.cookieFor("allowed")]);
```

Discover the application's cookie name, authenticating system and permission
names first; the example does not grant a universal admin role. Use the default
`example.test` identity domain unless the actual validator requires Guardian
addresses. Even then the helper generates random test-only addresses rather than
accepting real user identities. Cookies are scoped to the supplied local host,
HTTP-only and secure on HTTPS, with a short lifetime.

Before navigating, seed `auth.settings` into the isolated auth settings service,
`auth.publicSettings` into its public-key variant, and map `auth.users` emails and
explicit permissions to the application's real permission-fixture schema. Reuse
the project's parser/serializer when merging settings; do not append duplicate
keys. The private settings contain a test signing key: keep them in memory or
restricted ephemeral storage, never in source control, logs or the HTML report.
Public settings must not contain the private key. Mount static fixtures read-only
where possible and destroy generated keys with the owned stack.

Validate allowed, denied, unauthenticated and relevant expired/refresh behavior
through the actual application. A valid signature alone proves no permission
behavior. Guardian library 2.0.0 accepts stale cookies during a 24-hour refresh
grace period; characterize the application's handling instead of assuming that
nominal cookie expiry immediately means denial. `phase: 'auth'` receipts can retain
these named probe results without cookies, keys or user payloads.

For manual browser use, an existing local auth endpoint/proxy may issue the same
test cookie server-side. Do not require browser flags, real OAuth credentials or a
production login, and do not introduce an application auth bypass.

## What the report displays

The report reads `setup-check.json` receipts under the analysis directory. It
shows each named check, cleanup and observation time, with explicitly selected
evidence first. It never runs the scripts or interprets setup as behavior coverage.
Link chosen receipts under `WORKFLOW.md`'s `## Selected evidence`, keep failures,
update the coverage plan and refresh the report through the existing checkpoint.
The helper's output is an observation, not authenticated proof or current
eligibility; the normal baseline and candidate evidence checks remain separate.
