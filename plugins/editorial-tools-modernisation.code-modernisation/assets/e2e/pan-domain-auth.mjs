import assert from 'node:assert/strict';
import { generateKeyPairSync, randomUUID } from 'node:crypto';

export function createPanDomainFixture({ signCookie, baseUrl, cookieName, system, roles, emailDomain = 'example.test' }) {
  assert.equal(typeof signCookie, 'function', 'Supply the installed Guardian createCookie function');
  const url = new URL(baseUrl);
  const local = ['127.0.0.1', '[::1]', 'localhost'].includes(url.hostname)
    || url.hostname.endsWith('.localhost') || url.hostname.endsWith('.test')
    || url.hostname === 'local.dev-gutools.co.uk' || url.hostname.endsWith('.local.dev-gutools.co.uk');
  assert.ok(local && ['http:', 'https:'].includes(url.protocol) && !url.username && !url.password,
    'Auth fixtures are restricted to local test hosts');
  assert.match(cookieName, /^[a-zA-Z0-9_-]{1,80}$/, 'Discover the application cookie name');
  assert.match(system, /^[a-zA-Z0-9_-]{1,80}$/, 'Discover the authenticating system');
  assert.ok(['example.test', 'example.com', 'guardian.co.uk'].includes(emailDomain), 'Use a synthetic test identity domain');
  assert.ok(roles && typeof roles === 'object' && !Array.isArray(roles), 'Supply explicit allowed and denied roles');
  const entries = Object.entries(roles);
  assert.ok(entries.length > 0 && entries.length <= 20, 'Supply 1 to 20 roles');
  for (const [name, permissions] of entries) {
    assert.match(name, /^[a-zA-Z0-9_-]{1,40}$/);
    assert.ok(Array.isArray(permissions) && permissions.every(value => typeof value === 'string' && value.trim()),
      'Each role must list its permissions; use an empty list for a denied role');
  }
  const identifier = randomUUID();
  const users = Object.freeze(Object.fromEntries(entries.map(([name, permissions]) => [name, Object.freeze({
    email: `e2e-${identifier}-${name}@${emailDomain}`, permissions: Object.freeze([...permissions]),
  })])));
  const keys = generateKeyPairSync('rsa', { modulusLength: 4096 });
  const privateKeyPem = keys.privateKey.export({ type: 'pkcs8', format: 'pem' });
  const publicKeyPem = keys.publicKey.export({ type: 'spki', format: 'pem' });
  const publicSettings = Object.freeze({ publicKey: keys.publicKey.export({ type: 'spki', format: 'der' }).toString('base64') });
  const settings = Object.freeze({ ...publicSettings,
    privateKey: keys.privateKey.export({ type: 'pkcs8', format: 'der' }).toString('base64') });

  function cookieFor(role, { expiresInMs = 300_000 } = {}) {
    assert.ok(Object.hasOwn(users, role), 'Unknown synthetic role');
    assert.ok(Number.isInteger(expiresInMs) && expiresInMs > 0 && expiresInMs <= 900_000, 'Use a lifetime of at most 15 minutes');
    const expires = Date.now() + expiresInMs;
    const value = signCookie({ firstName: 'E2E', lastName: 'Test', email: users[role].email,
      authenticatingSystem: system, authenticatedIn: [system], expires, multifactor: true }, privateKeyPem);
    assert.ok(typeof value === 'string' && value.length > 0, 'The signing library must return a cookie');
    return { name: cookieName, value, domain: url.hostname.replace(/^\[|\]$/g, ''), path: '/',
      httpOnly: true, secure: url.protocol === 'https:', sameSite: 'Lax', expires: Math.floor(expires / 1000) };
  }

  return { users, settings, publicSettings, publicKeyPem, cookieFor };
}