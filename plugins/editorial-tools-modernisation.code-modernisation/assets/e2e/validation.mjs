import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';

function duration(value) {
  assert.ok(Number.isInteger(value) && value > 0 && value <= 300_000, 'Use a timeout between 1 and 300000 milliseconds');
  return value;
}

function localUrl(value) {
  const url = new URL(value);
  assert.ok(['http:', 'https:'].includes(url.protocol), 'Use HTTP or HTTPS');
  assert.ok(['127.0.0.1', '[::1]'].includes(url.hostname), 'Use an explicit loopback address and a locally mapped port');
  assert.ok(!url.username && !url.password && !url.hash, 'Do not put credentials or fragments in probe URLs');
  return url;
}

async function localResponse(url, { status = 200, timeoutMs = 5000, signal, headers } = {}) {
  const deadline = AbortSignal.timeout(duration(timeoutMs));
  const response = await fetch(localUrl(url), {
    redirect: 'error', headers,
    signal: signal ? AbortSignal.any([signal, deadline]) : deadline,
  });
  if (response.status !== status) {
    await response.body?.cancel();
    throw new Error('Unexpected HTTP status');
  }
  return response;
}

export async function assertLocalHttp(url, options) {
  const response = await localResponse(url, options);
  await response.body?.cancel();
}

export async function assertLocalJson(url, verify, options) {
  assert.equal(typeof verify, 'function', 'Supply a fixture assertion');
  const response = await localResponse(url, options);
  const chunks = [];
  let bytes = 0;
  for await (const chunk of response.body) {
    bytes += chunk.length;
    assert.ok(bytes <= 64 * 1024, 'Probe response exceeds 64 KiB');
    chunks.push(chunk);
  }
  const value = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  assert.notEqual(await verify(value), false, 'Fixture assertion returned false');
}

export async function assertNoUnmatchedRequests(baseUrl, options) {
  const url = new URL('/__admin/requests/unmatched', localUrl(baseUrl));
  await assertLocalJson(url, value => {
    assert.equal(value.requestJournalDisabled, false, 'The mock request journal must be enabled');
    assert.ok(Array.isArray(value.requests), 'Expected the mock request journal');
    assert.equal(value.requests.length, 0, 'Unexpected requests reached the mock');
  }, options);
}

async function operation(run, timeoutMs) {
  const controller = new AbortController();
  let timer;
  try {
    const timeout = new Promise((resolve, reject) => {
      timer = setTimeout(() => {
        controller.abort();
        reject(new Error('Operation timed out'));
      }, timeoutMs);
    });
    assert.notEqual(await Promise.race([Promise.resolve().then(() => run(controller.signal)), timeout]), false);
    return 'passed';
  } catch {
    return controller.signal.aborted ? 'timed-out' : 'failed';
  } finally {
    clearTimeout(timer);
  }
}

export async function runSetupChecks({ phase, checks, cleanup, timeoutMs = 10_000, cleanupTimeoutMs = 10_000 }) {
  assert.ok(['stack', 'fixtures', 'auth'].includes(phase), 'Unknown setup phase');
  assert.ok(Array.isArray(checks) && checks.length > 0 && checks.length <= 100, 'Supply 1 to 100 checks');
  assert.equal(typeof cleanup, 'function', 'Supply cleanup and owned-resource verification');
  duration(timeoutMs);
  duration(cleanupTimeoutMs);
  const names = new Set();
  for (const check of checks) {
    assert.ok(typeof check.name === 'string' && check.name.trim() && check.name.length <= 160, 'Use short, non-sensitive check names');
    assert.ok(!names.has(check.name), 'Check names must be unique');
    assert.equal(typeof check.run, 'function');
    names.add(check.name);
  }
  const startedAt = new Date().toISOString();
  const results = [];
  let stopped = false;
  for (const check of checks) {
    const outcome = stopped ? 'not-run' : await operation(check.run, timeoutMs);
    results.push({ name: check.name, outcome });
    stopped ||= outcome !== 'passed';
  }
  const cleanupOutcome = await operation(cleanup, cleanupTimeoutMs);
  return {
    kind: 'e2e-setup-check', formatVersion: 1, phase, startedAt,
    completedAt: new Date().toISOString(), checks: results,
    cleanup: { outcome: cleanupOutcome },
    passed: !stopped && cleanupOutcome === 'passed',
  };
}

export async function writeSetupResult(path, result) {
  assert.equal(result.kind, 'e2e-setup-check');
  const record = {
    kind: result.kind, formatVersion: result.formatVersion, phase: result.phase,
    startedAt: result.startedAt, completedAt: result.completedAt, passed: result.passed,
    checks: result.checks.map(check => ({ name: check.name, outcome: check.outcome })),
    cleanup: { outcome: result.cleanup.outcome },
  };
  await writeFile(path, JSON.stringify(record, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
}