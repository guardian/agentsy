// Run locally or in CI to catch plugin packaging and publication errors before merge.
// This does not install or run plugins.
//
// For each plugin, we check that:
// 1. It lives directly under plugins/<name>/ and its files resolve inside that directory.
// 2. It has a README.md at the root of the plugin.
// 3. Its root plugin.json and any skills or MCP configuration meet key Agent Plugins v1.0.0 rules.
// 4. Its name is unique, matches its directory and starts with a lowercase team slug and a dot.
// 5. CODEOWNERS has an exact rule assigning the plugin to that team.
// 6. Its marketplace entry matches the manifest's name, description and version, and points to the plugin.
// 7. If an existing plugin's files change, its version in both manifests differs from the base version.

import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync, realpathSync, lstatSync, statSync } from 'node:fs';
import { basename, dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import { parse as parseYaml } from 'yaml';

const marketplacePath = '.github/plugin/marketplace.json';
const schema = (name) => `https://agent-plugins.org/schemas/1.0.0/${name}.schema.json`;
const slug = '[a-z0-9]+(?:-[a-z0-9]+)*';
const pluginName = /^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const prefix = new RegExp(`^(${slug})\\.`);
const skillName = new RegExp(`^${slug}$`);
const namespace = /^[a-z0-9-]+(?:\.[a-z0-9-]+)+$/i;
const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isString = (value) => typeof value === 'string';
const nonEmpty = (value) => isString(value) && value.trim().length > 0;
const strings = (value) => Array.isArray(value) && value.every(isString);
const mapOf = (predicate) => (value) => isObject(value) && Object.values(value).every(predicate);
const file = (path) => statSync(path, { throwIfNoEntry: false })?.isFile();
const directory = (path) => statSync(path, { throwIfNoEntry: false })?.isDirectory();
const git = (...args) => execFileSync('git', args, { encoding: 'utf8' });
const paths = (output) => output.split('\0').filter(Boolean);
const issues = [];
const report = (path, message) => issues.push(`${path}: ${message}`);

function json(path, text = readFileSync(path, 'utf8')) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${path}: ${error.message}`);
  }
}

// Report all field errors before the caller decides whether it can use the file.
function fields(path, object, required, optional = {}) {
  if (!isObject(object)) {
    report(path, 'must be an object');
    return false;
  }
  const start = issues.length;
  for (const [key, rule] of Object.entries(required)) {
    const valid = Object.hasOwn(object, key) && (typeof rule === 'function' ? rule(object[key]) : object[key] === rule);
    if (!valid) {
      const action = typeof rule === 'string' ? `; set it to ${JSON.stringify(rule)}` : '';
      report(path, `invalid or missing ${key}${action}`);
    }
  }
  for (const [key, value] of Object.entries(object)) {
    if (Object.hasOwn(required, key)) continue;
    if (!Object.hasOwn(optional, key)) report(path, `unknown field: ${key}`);
    else if (!optional[key](value)) report(path, `invalid ${key}`);
  }
  return issues.length === start;
}

// Check the v1.0.0 manifest fields and require a description and version for the marketplace.
function readManifest(path) {
  const manifest = json(path);
  const valid = fields(path, manifest, {
    $schema: schema('plugin'),
    name: (value) => isString(value) && value.length <= 64 && pluginName.test(value) && value === value.trim(),
    description: nonEmpty,
    version: nonEmpty,
  }, {
    author: (value) => isObject(value) && Object.entries(value).every(
      ([key, item]) => ['name', 'email', 'url'].includes(key) && isString(item),
    ),
    homepage: isString,
    repository: isString,
    license: isString,
    keywords: strings,
    extensions: (value) => isObject(value) && Object.entries(value).every(
      ([key, item]) => namespace.test(key) && isObject(item),
    ),
  });
  return valid ? manifest : null;
}

// Check YAML frontmatter and require the skill name to match its directory.
function checkSkill(path) {
  const match = readFileSync(path, 'utf8').match(/^---[ \t]*\r?\n([\s\S]*?)^---[ \t]*\r?$/m);
  if (!match || match.index !== 0) return report(path, 'missing YAML frontmatter');
  let metadata;
  try {
    metadata = parseYaml(match[1], { maxAliasCount: 0 });
  } catch (error) {
    return report(path, `invalid YAML frontmatter: ${error.message}`);
  }
  if (!isObject(metadata)) return report(path, 'frontmatter must be an object');
  if (metadata.name !== basename(dirname(path)) || metadata.name.length > 64 || !skillName.test(metadata.name)) {
    report(path, 'name must be a lowercase hyphenated slug matching the skill directory (at most 64 characters)');
  }
  if (!nonEmpty(metadata.description) || metadata.description.length > 1024) {
    report(path, 'description must be non-empty and at most 1024 characters');
  }
  for (const key of ['license', 'allowed-tools']) {
    if (Object.hasOwn(metadata, key) && !isString(metadata[key])) report(path, `invalid ${key}`);
  }
  if (Object.hasOwn(metadata, 'compatibility') && (!nonEmpty(metadata.compatibility) || metadata.compatibility.length > 500)) {
    report(path, 'compatibility must be non-empty and at most 500 characters');
  }
  if (Object.hasOwn(metadata, 'metadata') && !mapOf(isString)(metadata.metadata)) report(path, 'invalid metadata');
}

function within(root, path) {
  const rel = relative(root, path);
  return rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel);
}

// Keep paths inside the plugin, resolving links before stepping through '..'.
function packagePath(root, suffix) {
  if (isAbsolute(suffix)) return false;
  let current = root;
  for (const part of suffix.split(sep === '\\' ? /[\\/]/ : '/')) {
    current = resolve(current, part);
    if (!within(root, current)) return false;
    if (lstatSync(current, { throwIfNoEntry: false })?.isSymbolicLink()) {
      current = realpathSync.native(current);
      if (!within(root, current)) return false;
    }
  }
  return true;
}

// Check MCP settings by transport: local command paths for stdio, URLs and headers for HTTP.
function checkMcp(root, path) {
  const config = json(path);
  if (!fields(path, config, { $schema: schema('mcp'), mcpServers: isObject })) return;
  const rootPath = '${PLUGIN_ROOT}';
  const dataPath = '${PLUGIN_DATA}';
  const rooted = (value, placeholder) => value === placeholder || value.startsWith(`${placeholder}/`);
  const cwd = (value) => isString(value) && (
    (value.startsWith('./') && packagePath(root, value)) ||
    (rooted(value, rootPath) && packagePath(root, `.${value.slice(rootPath.length)}`)) ||
    (rooted(value, dataPath) && within(root, resolve(root, `.${value.slice(dataPath.length)}`)))
  );
  for (const [name, server] of Object.entries(config.mcpServers)) {
    const label = `${path} (${name})`;
    if (server?.type === 'stdio') {
      fields(label, server, {
        type: () => true,
        command: (value) => nonEmpty(value) && (value.startsWith('./')
          ? packagePath(root, value)
          : !/[/\\\s]/.test(value) && value !== '.' && value !== '..'),
      }, {
        args: strings,
        env: (value) => mapOf(isString)(value) && !Object.keys(value).some(
          (key) => ['PLUGIN_ROOT', 'PLUGIN_DATA'].includes(key),
        ),
        cwd,
      });
    } else {
      fields(label, server, {
        type: (value) => value === 'streamable-http' || value === 'sse',
        url: (value) => {
          if (!isString(value) || !/^https?:\/\//i.test(value) || value.includes('#')) return false;
          const url = URL.parse(value);
          return url && !url.username && !url.password && (
            url.protocol === 'https:' || /^(localhost|127\.\d+\.\d+\.\d+|\[::1\])$/.test(url.hostname)
          );
        },
      }, {
        headers: (value) => mapOf(isString)(value) &&
          new Set(Object.keys(value).map((key) => key.toLowerCase())).size === Object.keys(value).length &&
          Object.entries(value).every(([key, item]) => /^[!#$%&'*+.^_`|~0-9a-z-]+$/i.test(key) &&
            !/[\x00-\x08\x0a-\x1f\x7f-\uffff]/.test(item)),
      });
    }
  }
}

// Require each skill to use skills/<name>/SKILL.md and flag skill files elsewhere.
function checkSkills(dir, files) {
  if (lstatSync(`${dir}/skills`, { throwIfNoEntry: false })) {
    if (!directory(`${dir}/skills`)) report(dir, 'skills must be a directory');
    else for (const item of readdirSync(`${dir}/skills`)) {
      const path = `${dir}/skills/${item}/SKILL.md`;
      if (directory(dirname(path))) {
        if (file(path)) checkSkill(path);
        else report(path, 'missing SKILL.md');
      }
    }
  }
  for (const path of files) {
    if (basename(path) === 'SKILL.md' && !/^skills\/[^/]+\/SKILL\.md$/.test(relative(dir, path))) {
      report(path, 'skills belong in skills/<name>/SKILL.md');
    }
  }
}

// Check file containment before reading components, and require a README at the plugin root.
function checkLayout(dir, files) {
  const start = issues.length;
  const root = resolve(dir);
  for (const path of files) {
    if (!packagePath(root, relative(dir, path))) report(path, 'must resolve inside its plugin directory');
  }
  if (issues.length !== start) return;

  if (!file(`${dir}/README.md`)) report(dir, 'missing README.md; add one at the root of the plugin directory');
  checkSkills(dir, files);
  const mcp = `${dir}/mcp.json`;
  if (lstatSync(mcp, { throwIfNoEntry: false })) {
    if (file(mcp)) checkMcp(root, mcp);
    else report(mcp, 'must be a regular file');
  }
}

// Require each listing's metadata and flag duplicate names or sources.
function readMarketplaceEntries() {
  const marketplace = json(marketplacePath);
  if (!isObject(marketplace) || !Array.isArray(marketplace.plugins)) {
    throw new Error(`${marketplacePath}: expected a plugins array`);
  }
  const byName = new Map();
  const sources = new Set();
  for (const [index, entry] of marketplace.plugins.entries()) {
    const label = `${marketplacePath} (plugins[${index}])`;
    if (!isObject(entry) || !['name', 'description', 'version', 'source'].every((key) => nonEmpty(entry[key]))) {
      report(label, 'requires non-empty name, description, version and source strings');
      continue;
    }
    if (byName.has(entry.name)) report(label, `duplicate plugin name: ${entry.name}`);
    if (sources.has(entry.source)) report(label, `duplicate plugin source: ${entry.source}`);
    byName.set(entry.name, entry);
    sources.add(entry.source);
  }
  return byName;
}

// Read the base commit's published versions, not the values in the working tree.
function previousVersions(base) {
  if (/^0{40}$/.test(base)) return new Map(); // First push to the branch.
  const commit = git('rev-parse', '--verify', '--end-of-options', `${base}^{commit}`).trim();
  if (!git('ls-tree', commit, '--', marketplacePath)) return new Map();
  const { plugins } = json(`${commit}:${marketplacePath}`, git('show', `${commit}:${marketplacePath}`));
  if (!Array.isArray(plugins)) throw new Error(`${commit}:${marketplacePath}: expected a plugins array`);
  return new Map(plugins.map(({ name, version }) => [name, version]));
}

// Read ownership rules from the repository root and strip comments before matching.
function readCodeowners() {
  const path = 'CODEOWNERS';
  const rules = readFileSync(path, 'utf8').split(/\r?\n/)
    .map((line) => line.split('#', 1)[0].trim().split(/\s+/));
  return { path, rules };
}

// Include untracked files and compare tracked files against the base when prior versions exist.
function changedPluginFiles(base, oldVersions, untracked) {
  const changed = new Set(untracked);
  if (oldVersions.size > 0) {
    for (const path of paths(git('diff', '--name-only', '--no-renames', '-z', base, '--', 'plugins'))) changed.add(path);
  }
  return changed;
}

// Group tracked and non-ignored untracked files by their immediate directory under plugins/.
function findPluginPackages(untracked) {
  const files = new Set([...paths(git('ls-files', '-z', '--cached')), ...untracked]);
  const packages = new Map();
  for (const path of files) {
    if (!lstatSync(path, { throwIfNoEntry: false })) continue;
    if (basename(path) === 'plugin.json' && !/^plugins\/[^/]+\/plugin\.json$/.test(path)) {
      report(path, 'plugin manifests must be directly under plugins/<name>/');
    }
    if (!path.startsWith('plugins/')) continue;
    const dir = path.split('/').slice(0, 2).join('/');
    if (path === dir) report(path, 'plugins/ may only contain plugin directories');
    else {
      if (!packages.has(dir)) packages.set(dir, []);
      packages.get(dir).push(path);
    }
  }
  if (lstatSync('plugins', { throwIfNoEntry: false }) && realpathSync('plugins') !== resolve('plugins')) {
    throw new Error('plugins/ must not be a symlink');
  }
  return packages;
}

// Require a root manifest that belongs to the package before reading it.
function checkManifest(dir, files) {
  const path = `${dir}/plugin.json`;
  if (!files.includes(path) || !file(path) || !packagePath(resolve(dir), 'plugin.json')) {
    report(path, 'add a plugin.json file at the root of the plugin directory that resolves inside it');
    return null;
  }
  return readManifest(path);
}

// Require a unique manifest name that also matches the package directory.
function checkPluginName(dir, name, names) {
  const path = `${dir}/plugin.json`;
  if (names.has(name)) report(path, `duplicate plugin name: ${name}`);
  names.add(name);
  if (dir !== `plugins/${name}`) report(path, `directory must be plugins/${name}`);
}

// Match the team prefix to an exact CODEOWNERS rule without looking up the team on GitHub.
function checkOwnership(dir, name, codeowners) {
  const team = name.match(prefix)?.[1];
  if (!team) {
    report(`${dir}/plugin.json`, 'name must start with a lowercase team slug followed by a dot');
    return;
  }
  const rule = codeowners.rules.findLast(([pattern]) => pattern === `/plugins/${name}/`);
  if (!rule?.slice(1).includes(`@guardian/${team}`)) {
    report(codeowners.path, `missing owner for ${name}; add or update this rule: /plugins/${name}/ @guardian/${team}`);
  }
}

// Keep the listing in sync with the manifest and point it at the matching directory.
function checkMarketplaceEntry({ name, description, version }, entry) {
  const expected = { name, description, version, source: `./plugins/${name}` };
  if (!entry) {
    report(marketplacePath, `add the missing plugin entry: ${JSON.stringify(expected)}`);
    return;
  }
  for (const [field, value] of Object.entries(expected)) {
    if (entry[field] !== value) {
      report(marketplacePath, `${name}: set ${field} to ${JSON.stringify(value)}`);
    }
  }
}

// Require a different version when an existing plugin's files change.
function checkVersionUpdate(dir, entry, oldVersions, changed) {
  if (entry && oldVersions.get(entry.name) === entry.version && [...changed].some((path) => path.startsWith(`${dir}/`))) {
    report(marketplacePath, `${entry.name} changed without a version update (still ${entry.version}); update the version in both ${dir}/plugin.json and ${marketplacePath}`);
  }
}

// Catch stale listings and listings for plugins without a valid manifest.
function checkForUnmatchedMarketplaceEntries(entries, names) {
  for (const name of entries.keys()) {
    if (!names.has(name)) report(marketplacePath, `${name} has no matching plugin under plugins/; remove the entry or fix the plugin manifest`);
  }
}

// Check all discovered plugins, using the base commit only to decide which need a version update.
function main(base) {
  process.chdir(git('rev-parse', '--show-toplevel').trimEnd());
  const entries = readMarketplaceEntries();
  const codeowners = readCodeowners();

  base ??= git('merge-base', 'HEAD', 'origin/main').trim();
  const oldVersions = previousVersions(base);
  const untracked = paths(git('ls-files', '-z', '--others', '--exclude-standard'));
  const changed = changedPluginFiles(base, oldVersions, untracked);
  const packages = findPluginPackages(untracked);

  const names = new Set();
  for (const [dir, files] of packages) {
    if (realpathSync(dir) !== resolve(dir)) {
      report(dir, 'plugin directories must not be symlinks');
      continue;
    }
    checkLayout(dir, files);
    const manifest = checkManifest(dir, files);
    if (!manifest) continue;

    checkPluginName(dir, manifest.name, names);
    checkOwnership(dir, manifest.name, codeowners);
    const entry = entries.get(manifest.name);
    checkMarketplaceEntry(manifest, entry);
    checkVersionUpdate(dir, entry, oldVersions, changed);
  }
  checkForUnmatchedMarketplaceEntries(entries, names);

  if (issues.length > 0) {
    console.error(issues.join('\n'));
    process.exitCode = 1;
  } else {
    console.log(`Checked ${names.size} plugins.`);
  }
}

try {
  if (process.argv.length > 3) throw new Error('Usage: npm --prefix checks run check-plugins -- [base-commit]');
  main(process.argv[2]);
} catch (error) {
  console.error([...issues, error.message].join('\n'));
  process.exitCode = 1;
}
