// Runs check-plugins.mjs in temporary Git repositories to test its exit status
// and diagnostics for valid plugins, packaging and ownership errors, and
// missing or out-of-date marketplace entries.

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const script = fileURLToPath(new URL('./check-plugins.mjs', import.meta.url));
const dir = 'plugins/example.tools';
const marketplace = '.github/plugin/marketplace.json';

function fixture(t) {
  const cwd = mkdtempSync(join(tmpdir(), 'plugin-checks-'));
  t.after(() => rmSync(cwd, { recursive: true }));
  const git = (...args) => execFileSync('git', args, { cwd, stdio: 'pipe' });
  const write = (path, content) => {
    const target = join(cwd, path);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, typeof content === 'string' ? content : JSON.stringify(content));
  };
  const manifest = {
    $schema: 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
    name: 'example.tools', description: 'Example tools', version: '1.0.0',
  };
  const entry = { name: manifest.name, description: manifest.description, version: manifest.version, source: `./${dir}` };
  write('CODEOWNERS', `/${dir}/ @guardian/example\n`);
  write(marketplace, { plugins: [entry] });
  write(`${dir}/plugin.json`, manifest);
  write(`${dir}/README.md`, '# Example tools\n');
  write(`${dir}/notes.txt`, 'Notes');
  git('init', '-q');
  git('add', '.');
  git('-c', 'user.name=Plugin checks', '-c', 'user.email=checks@example.invalid',
    '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Fixture');
  const check = (base = 'HEAD') => {
    const { status, stdout, stderr, error } = spawnSync(process.execPath, [script, base], { cwd, encoding: 'utf8' });
    if (error) throw error;
    return { status, output: stdout + stderr };
  };
  return { cwd, write, git, manifest, entry, check };
}

test('accepts a plugin with matching CODEOWNERS and ignores unrelated changes', (t) => {
  const { write, check } = fixture(t);
  write('README.md', '# Repo docs');
  assert.deepEqual(check(), { status: 0, output: 'Checked 1 plugins.\n' });
});

test('requires a marketplace version update for changed, untracked and deleted plugin files', (t) => {
  const { cwd, write, git, manifest, entry, check } = fixture(t);
  write(`${dir}/extra.txt`, 'New file');
  assert.match(check().output, /update the version in both plugins\/example\.tools\/plugin\.json and \.github\/plugin\/marketplace\.json/);
  git('add', `${dir}/extra.txt`);
  assert.match(check().output, /changed without a version update/);
  rmSync(join(cwd, dir, 'extra.txt'));
  rmSync(join(cwd, dir, 'notes.txt'));
  assert.match(check().output, /changed without a version update/);
  write(`${dir}/plugin.json`, { ...manifest, version: '1.0.1' });
  assert.match(check().output, /example\.tools: set version to "1\.0\.1"/);
  write(marketplace, { plugins: [{ ...entry, version: '1.0.1' }] });
  assert.equal(check().status, 0);
  rmSync(join(cwd, dir, 'README.md'));
  assert.match(check().output, /missing README\.md/);
});

test('rejects legacy manifests and misplaced packages', (t) => {
  const { write, manifest, check } = fixture(t);
  write('elsewhere/plugin.json', manifest);
  write(`${dir}/plugin.json`, { ...manifest, $schema: null, agents: 'agents/' });
  const { status, output } = check();
  assert.equal(status, 1);
  assert.match(output, /plugin manifests must be directly under plugins/);
  assert.match(output, /invalid or missing \$schema; set it to "https:\/\/agent-plugins\.org\/schemas\/1\.0\.0\/plugin\.schema\.json"/);
  assert.match(output, /unknown field: agents/);
});

test('rejects incorrect ownership, duplicate names and marketplace entries', (t) => {
  const { write, manifest, entry, check } = fixture(t);
  write('CODEOWNERS', `/${dir}/ @guardian/another\n`);
  write('plugins/example.duplicate/plugin.json', manifest);
  write(marketplace, { plugins: [entry, entry, { ...entry, name: 'stale', source: './skills/stale' }] });
  const { status, output } = check();
  assert.equal(status, 1);
  assert.match(output, /add or update this rule: \/plugins\/example\.tools\/ @guardian\/example/);
  assert.match(output, /marketplace\.json.*duplicate plugin name/);
  assert.match(output, /plugin\.json.*duplicate plugin name/);
  assert.match(output, /stale has no matching plugin/);
});

test('shows the entry to add when the marketplace does not list a plugin', (t) => {
  const { write, entry, check } = fixture(t);
  write(marketplace, { plugins: [] });
  const { status, output } = check();
  assert.equal(status, 1);
  assert.ok(output.includes(`add the missing plugin entry: ${JSON.stringify(entry)}`));
});

test('rejects invalid skill and MCP metadata and escaping paths', (t) => {
  const { cwd, write, check } = fixture(t);
  write(`${dir}/skills/one/SKILL.md`, '---\nname: two\ndescription: A skill\n---\n');
  write(`${dir}/mcp.json`, {
    $schema: 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
    mcpServers: { example: { type: 'stdio', command: '../outside' } },
  });
  const result = check();
  assert.equal(result.status, 1);
  assert.match(result.output, /SKILL\.md: name must be/);
  assert.match(result.output, /mcp\.json \(example\): invalid or missing command/);
  symlinkSync('../../CODEOWNERS', join(cwd, dir, 'outside'));
  assert.match(check().output, /must resolve inside its plugin directory/);
});
