#!/usr/bin/env node
/** Observe a local Node/Chromium installation; never start the application. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const identity = info => ['dev', 'ino', 'mode', 'size', 'mtimeNs', 'ctimeNs'].map(key => String(info[key])).join(':');
const inside = (root, file) => file === root || file.startsWith(root + path.sep);

export function physical(file) {
  if (!path.isAbsolute(file) || path.normalize(file) !== file || fs.realpathSync(file) !== file)
    throw new Error('Use an existing physical absolute path without symlinks.');
  return file;
}

export function fileIdentity(file) {
  if (fs.lstatSync(file).isSymbolicLink()) throw new Error('Unexpected file symlink.');
  const descriptor = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
  try {
    const before = fs.fstatSync(descriptor, { bigint: true });
    if (!before.isFile()) throw new Error('Only regular files are supported.');
    const hash = crypto.createHash('sha256');
    const buffer = Buffer.alloc(1024 * 1024);
    let count;
    while ((count = fs.readSync(descriptor, buffer, 0, buffer.length, null))) hash.update(buffer.subarray(0, count));
    if (identity(before) !== identity(fs.fstatSync(descriptor, { bigint: true })) ||
        identity(before) !== identity(fs.lstatSync(file, { bigint: true }))) throw new Error('File changed during observation.');
    return { sha256: hash.digest('hex'), mode: (Number(before.mode) & 0o7777).toString(8).padStart(4, '0') };
  } finally { fs.closeSync(descriptor); }
}

export function dependencyIdentity(directory) {
  physical(directory);
  function scan() {
    const records = [];
    function visit(current) {
      const before = fs.lstatSync(current, { bigint: true });
      const names = fs.readdirSync(current).sort();
      for (const name of names) {
        const file = path.join(current, name);
        const relative = path.relative(directory, file).split(path.sep).join('/');
        const info = fs.lstatSync(file);
        if (info.isSymbolicLink()) {
          const target = fs.readlinkSync(file);
          if (!inside(directory, fs.realpathSync(file))) throw new Error('Dependency symlink leaves the installed tree.');
          records.push([relative, 'symlink', target]);
        } else if (info.isDirectory()) visit(file);
        else if (info.isFile()) {
          const found = fileIdentity(file);
          records.push([relative, 'file', found.mode, found.sha256]);
        } else throw new Error('Unsupported dependency file type.');
      }
      if (identity(before) !== identity(fs.lstatSync(current, { bigint: true })) ||
          JSON.stringify(names) !== JSON.stringify(fs.readdirSync(current).sort())) throw new Error('Dependency tree changed during observation.');
    }
    visit(directory);
    if (!records.length) throw new Error('Installed dependencies are empty.');
    return { sha256: sha(JSON.stringify(records)), entries: records.length };
  }
  const before = scan();
  if (JSON.stringify(before) !== JSON.stringify(scan())) throw new Error('Dependency tree changed between observations.');
  return before;
}

export function observe(root, browser, url) {
  physical(root); physical(browser);
  const address = new URL(url);
  if (address.protocol !== 'http:' || address.hostname !== '127.0.0.1' || !address.port ||
      address.username || address.password || address.search || address.hash)
    throw new Error('Only an explicit local http://127.0.0.1:PORT URL is supported.');
  const packages = {};
  for (const name of ['@playwright/test', 'playwright', 'playwright-core', 'playwright-bdd']) {
    const file = path.join(root, 'node_modules', name, 'package.json');
    physical(file);
    const measured = fileIdentity(file);
    const bytes = fs.readFileSync(file);
    if (sha(bytes) !== measured.sha256) throw new Error('Package identity changed during observation.');
    const data = JSON.parse(bytes.toString('utf8'));
    if (data.name !== name || typeof data.version !== 'string') throw new Error('Installed package identity is invalid.');
    packages[name] = { version: data.version, ...measured };
  }
  const browserIdentity = fileIdentity(browser);
  const version = spawnSync(browser, ['--version'], { encoding: 'utf8', timeout: 10_000, maxBuffer: 16_384,
    env: { PATH: '/usr/bin:/bin', HOME: os.homedir(), LANG: 'en_US.UTF-8' } });
  if (version.error || version.status !== 0 || !version.stdout.trim()) throw new Error('Browser version observation failed.');
  if (JSON.stringify(browserIdentity) !== JSON.stringify(fileIdentity(browser))) throw new Error('Browser changed during observation.');
  const helpers = {};
  for (const name of ['observe_node_environment.mjs', 'capture_playwright.py', 'baseline_evidence.py', 'check_playwright_results.py'])
    helpers[name] = fileIdentity(path.join(here, name)).sha256;
  const facts = {
      node: { executable: physical(fs.realpathSync(process.execPath)), version: process.version, ...fileIdentity(process.execPath) },
      host: { platform: process.platform, architecture: process.arch, release: os.release(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone },
      processEnvironment: { LANG: process.env.LANG ?? null, LC_ALL: process.env.LC_ALL ?? null, TZ: process.env.TZ ?? null },
      installedPackages: packages, installedDependencies: dependencyIdentity(path.join(root, 'node_modules')),
      suppliedChromium: { executable: browser, version: version.stdout.trim(), ...browserIdentity },
      localURL: address.href, helpers,
  };
  for (const [name, measured] of Object.entries(packages))
    if (fileIdentity(path.join(root, 'node_modules', name, 'package.json')).sha256 !== measured.sha256)
      throw new Error('Package identity changed during observation.');
  return {
    schemaVersion: 1, observedAt: new Date().toISOString(), facts,
    limitations: [
      'The supplied browser executable is measured; source review must establish that the native config launches this executable.',
      'Browser support libraries, fonts and host services are not exhaustively inventoried.',
      'No application, fixtures or external services are observed by this command; unsupported lifecycle needs require a project adapter.',
      'Installed dependency symlinks are allowed only within the measured installation; no external dependency links are silently followed.',
    ],
  };
}

if (process.argv[1] && fs.realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length === 3 && process.argv[2] === '--help') {
      console.log('Usage: observe_node_environment.mjs --root <physical-project> --browser-executable <physical-Chromium> --url http://127.0.0.1:PORT');
      process.exit(0);
    }
    const flags = {};
    for (let index = 2; index < process.argv.length; index += 2) {
      const key = process.argv[index];
      if (!['--root', '--browser-executable', '--url'].includes(key) || !process.argv[index + 1] || flags[key])
        throw new Error('Expected --root, --browser-executable and --url exactly once.');
      flags[key] = process.argv[index + 1];
    }
    if (Object.keys(flags).length !== 3) throw new Error('Expected --root, --browser-executable and --url.');
    console.log(JSON.stringify(observe(flags['--root'], flags['--browser-executable'], flags['--url']), null, 2));
  } catch (error) {
    console.error(JSON.stringify({ checksPassed: false, error: error.message }));
    process.exitCode = 2;
  }
}
