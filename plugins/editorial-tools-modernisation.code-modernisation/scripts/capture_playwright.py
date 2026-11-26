#!/usr/bin/env python3
"""Capture one bounded local Playwright BDD attempt using a reviewed webServer config.

This opt-in convenience supports a single owned loopback webServer and an explicit
Chromium executable. Other service/fixture lifecycles need a project adapter. It
never chooses scenarios, changes application code, installs packages, or migrates.
"""
import argparse
from datetime import datetime, timezone
import errno
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("capture_baseline", HERE / "baseline_evidence.py")
BASELINE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(BASELINE)
HELPERS = ("capture_playwright.py", "observe_node_environment.mjs", "baseline_evidence.py", "check_playwright_results.py")
OUTCOME_CHECKS = ("executionClean", "cleanup", "serviceClosed", "afterSnapshot", "environmentAfter",
                  "environmentStable", "resultsClean", "baselineChecked", "helpersUnchanged")


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def read(path):
    return BASELINE.parse(BASELINE.stable_read(path)[0])


def physical(path):
    value = Path(path).absolute()
    BASELINE.no_symlinks(value)
    BASELINE.require(value.resolve(strict=True) == value, "Use a physical absolute path.")
    return value


def port_number(url):
    address = urlsplit(url)
    BASELINE.require(address.scheme == "http" and address.hostname == "127.0.0.1" and address.port
                     and not address.username and not address.password and not address.query and not address.fragment,
                     "Unsupported lifecycle: use an explicit local http://127.0.0.1:PORT URL.")
    return address.port


def port_closed(port):
    with socket.socket() as probe:
        probe.settimeout(1)
        result = probe.connect_ex(("127.0.0.1", port))
    if result == 0:
        return False
    if result != errno.ECONNREFUSED:
        raise OSError("Port observation did not establish closure.")
    return True


def process_table():
    result = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,pgid=,stat=,lstart="],
                            check=True, capture_output=True, text=True, timeout=2)
    table = {}
    for line in result.stdout.splitlines():
        pid, parent, group, state, birth = line.split(None, 4)
        table[int(pid)] = (int(parent), int(group), state, birth)
    return table


def same_live(table, known):
    return [pid for pid, birth in known.items() if pid in table and table[pid][3] == birth
            and not table[pid][2].startswith("Z")]


def remember(table, known):
    parents = set(same_live(table, known))
    while True:
        children = {pid for pid, row in table.items() if row[0] in parents
                    and (pid not in known or known[pid] == row[3])} - parents
        if not children:
            return
        for pid in children:
            known[pid] = table[pid][3]
        parents |= children


def remember_group(table, known, group, active):
    # Before Popen's child is reaped its PID/PGID is reserved. Keep following that
    # group while observed members remain; never reacquire an observed-empty group.
    if active:
        members = {pid: row for pid, row in table.items() if row[1] == group}
        for pid, row in members.items():
            if pid not in known or known[pid] == row[3]:
                known[pid] = row[3]
        active = any(pid in same_live(table, known) for pid in members)
    remember(table, known)
    return active


def supervise(argv, root, directory, label, env, deadline, cancelled, output=None):
    """Own a process group and sampled descendants; failed observation fails closed."""
    write(directory / (label + '-command.json'), {"argv": argv, "cwd": str(root),
          "deadlineSecondsRemaining": max(0, deadline - time.monotonic())})
    started, process, known, cause, errors, signals = now(), None, {}, None, [], []
    remaining, group_active = [], False
    try:
        if cancelled or time.monotonic() >= deadline:
            cause = "cancelled" if cancelled else "timeout"
        else:
            with (directory / (output or label + '.stdout')).open('x') as out, (directory / (label + '.stderr')).open('x') as err:
                process = subprocess.Popen(argv, cwd=root, env=env, stdout=out, stderr=err, start_new_session=True)
                group_active = remember_group(process_table(), known, process.pid, True)
                while True:
                    table = process_table()
                    group_active = remember_group(table, known, process.pid, group_active)
                    if cancelled or time.monotonic() >= deadline:
                        cause = "cancelled" if cancelled else "timeout"
                        break
                    if process.poll() is not None:
                        break
                    time.sleep(0.05)
    except Exception as error:
        cause = "observation-or-spawn-failure"
        errors.append(type(error).__name__)
    finally:
        if process is not None:
            try:
                group_active = remember_group(process_table(), known, process.pid, group_active)
            except Exception as error:
                errors.append(type(error).__name__)
            # The unreaped Popen child is ours; never signal an unrelated port owner.
            if process.poll() is None:
                for signum, grace in ((signal.SIGTERM, 3), (signal.SIGKILL, 3)):
                    try:
                        os.killpg(process.pid, signum)
                        signals.append({"group": process.pid, "signal": int(signum)})
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=grace)
                        break
                    except subprocess.TimeoutExpired:
                        continue
            cleanup_deadline = time.monotonic() + 8
            try:
                for signum in (signal.SIGTERM, signal.SIGKILL):
                    table = process_table()
                    group_active = remember_group(table, known, process.pid, group_active)
                    remaining = same_live(table, known)
                    for pid in remaining:
                        if time.monotonic() >= cleanup_deadline:
                            break
                        if pid in same_live(process_table(), known):
                            try:
                                os.kill(pid, signum)
                                signals.append({"pid": pid, "signal": int(signum)})
                            except ProcessLookupError:
                                pass
                    if remaining:
                        time.sleep(0.15)
                table = process_table()
                group_active = remember_group(table, known, process.pid, group_active)
                remaining = same_live(table, known)
            except Exception as error:
                errors.append(type(error).__name__)
            if process.poll() is None:
                errors.append("UnreapedChild")
        if cancelled:
            cause = "cancelled"
        cleanup = {"stopped": not errors and not remaining and not group_active, "owned": known, "remaining": remaining,
                   "processGroup": process.pid if process else None, "groupStillObserved": group_active,
                   "signals": signals, "observationErrors": errors,
                   "limitations": ["Descendants are sampled; deliberately escaped/reparented processes between samples are not proven absent."]}
        write(directory / (label + '-cleanup.json'), cleanup)
        write(directory / (label + '-process.json'), {"schemaVersion": 1,
              "exitCode": process.returncode if process else None, "startedAt": started, "completedAt": now()})
        if cancelled:
            cause = "cancelled"
        write(directory / (label + '-termination.json'), {"cause": cause, "receivedSignals": list(cancelled)})
    return process is not None and process.returncode == 0 and not cause and not cancelled and cleanup["stopped"]


def local_lifecycle(selection, root, url):
    config = selection.get('config', {})
    server = config.get('webServer')
    BASELINE.require(isinstance(server, dict) and isinstance(server.get('command'), str) and server['command'].strip()
                     and server.get('url', '').rstrip('/') == url.rstrip('/') and server.get('reuseExistingServer') is False,
                     "Unsupported lifecycle: require one reviewed webServer with the supplied local URL and reuseExistingServer:false.")
    BASELINE.require(config.get('globalSetup') is None and config.get('globalTeardown') is None,
                     "Unsupported lifecycle: global setup/teardown requires a project adapter.")
    config_path = physical(config.get('configFile', ''))
    BASELINE.require(root == config_path.parent or root in config_path.parents, "Native config leaves the source root.")
    cwd = physical(server.get('cwd', str(config_path.parent)))
    BASELINE.require(root == cwd or root in cwd.parents, "Unsupported lifecycle: webServer cwd leaves the source root.")
    shutdown = server.get('gracefulShutdown')
    BASELINE.require(isinstance(shutdown, dict) and shutdown.get('signal') == 'SIGTERM'
                     and type(shutdown.get('timeout')) is int and 0 < shutdown['timeout'] <= 10000,
                     "Unsupported lifecycle: require explicit bounded SIGTERM webServer shutdown.")
    return {"webServer": server, "configFile": str(config_path),
            "limitations": ["Configuration/source review must establish local commands, the supplied browser launch, and fixture boundaries.",
                            "A ready URL or closed port is not a behavioral test result."]}


def compare_environment(directory, name, left, right):
    before, after = read(directory / left), read(directory / right)
    BASELINE.environment_schema(before); BASELINE.environment_schema(after)
    different = sorted(key for key in set(before['facts']) | set(after['facts'])
                       if BASELINE.canonical(before['facts'].get(key)) != BASELINE.canonical(after['facts'].get(key)))
    write(directory / name, {"checksPassed": not different, "mismatchingKeys": different})
    BASELINE.require(not different, "Measured environment changed; preserve this attempt and resolve it before retrying.")


def publish_outcome(directory, outcome, cancelled):
    """Commit only after the provisional write and final pending-signal check."""
    provisional = directory / 'outcome.provisional.json'
    write(provisional, outcome)
    watched = {signal.SIGINT, signal.SIGTERM}
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, watched)
    try:
        pending = sorted(set(cancelled) | (signal.sigpending() & watched))
        if pending:
            outcome.update(checksPassed=False, cancelledSignals=pending)
        # Atomic publication is provisional until the pending-signal check below.
        provisional.rename(directory / 'outcome.json')
        pending = sorted(set(cancelled) | (signal.sigpending() & watched))
        if pending:
            outcome.update(checksPassed=False, cancelledSignals=pending)
            (directory / 'outcome.json').rename(directory / 'unqualified-outcome.json')
            write(directory / 'outcome.json', outcome)
        if not outcome['checksPassed']:
            for name in ('baseline.json', 'baseline-check.json'):
                if (directory / name).exists():
                    (directory / name).rename(directory / ('unqualified-' + name))
        # Successful qualification commits here. A later signal does not undo a
        # completed attempt; earlier signals cannot leave a qualifying receipt.
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    return outcome


def capture(args, cancelled):
    BASELINE.require(os.name == 'posix', "Unsupported lifecycle: this bounded supervisor requires POSIX processes.")
    root, browser = physical(args.root), physical(args.browser_executable)
    BASELINE.require(root.is_dir() and browser.is_file(), "Expected a source directory and installed browser executable.")
    BASELINE.relative(args.config)
    config = physical(root / args.config)
    excludes = sorted(args.exclude)
    BASELINE.exclusions(excludes)
    port = port_number(args.url)
    node = Path(shutil.which(args.node) or args.node).resolve(strict=True)
    physical(node)
    directory = Path(args.attempt).absolute()
    BASELINE.no_symlinks(directory)
    BASELINE.require(root != directory and root not in directory.parents, "Keep immutable attempt output outside the covered source root.")
    BASELINE.require(directory.parent.resolve(strict=True) == directory.parent, "Attempt parent must already be a physical directory.")
    directory.mkdir(exist_ok=False)
    deadline = time.monotonic() + args.timeout_seconds
    outcome = {"schemaVersion": 1, "kind": "playwright-capture-outcome", "checksPassed": False,
               "attempt": str(directory), "checks": {key: None for key in OUTCOME_CHECKS}}
    env = {key: os.environ[key] for key in ('HOME', 'TMPDIR', 'LANG', 'LC_ALL', 'TZ') if key in os.environ}
    env.update(PATH=str(node.parent) + ':/usr/bin:/bin', PYTHONDONTWRITEBYTECODE='1',
               MODERNIZE_BASE_URL=args.url, MODERNIZE_BROWSER_EXECUTABLE=str(browser))

    def unchanged_helpers():
        originals = {name: BASELINE.digest(BASELINE.stable_read(HERE / name)[0]) for name in HELPERS}
        copies = {name: BASELINE.digest(BASELINE.stable_read(directory / name)[0]) for name in HELPERS}
        BASELINE.require(originals == copies == helper_hashes, 'Capture helper bytes changed during the attempt.')

    def run(label, argv, output=None, extra=None):
        if extra and extra.get('PLAYWRIGHT_JSON_OUTPUT_FILE'):
            BASELINE.require(not Path(extra['PLAYWRIGHT_JSON_OUTPUT_FILE']).exists(), 'Native report destination must be fresh.')
        unchanged_helpers()
        clean = supervise([str(item) for item in argv], root, directory, label, dict(env, **(extra or {})), deadline, cancelled, output)
        check = {"after": "afterSnapshot", "environment-after": "environmentAfter",
                 "results-check": "resultsClean", "baseline-check": "baselineChecked"}.get(label)
        if check:
            outcome["checks"][check] = clean
        if not clean:
            raise BASELINE.Invalid('Capture command did not complete cleanly: ' + label)

    def observe(label):
        run(label, [node, HERE / 'observe_node_environment.mjs', '--root', root,
                    '--browser-executable', browser, '--url', args.url], label + '.json')
        recorded = {name: BASELINE.digest(BASELINE.stable_read(directory / name)[0]) for name in HELPERS}
        BASELINE.require(recorded == helper_hashes == read(directory / (label + '.json'))['facts']['helpers'],
                         'Capture helper bytes changed or differ from the preserved copies.')

    def snapshot(label):
        argv = [sys.executable, HERE / 'baseline_evidence.py', 'snapshot', '--root', root]
        for exclusion in excludes:
            argv.extend(['--exclude', exclusion])
        run(label, argv, label + '.json')

    post_complete = False
    try:
        helper_hashes = {}
        for name in HELPERS:
            raw = BASELINE.stable_read(HERE / name)[0]
            helper_hashes[name] = BASELINE.digest(raw)
            with (directory / name).open('xb') as output:
                output.write(raw)
        write(directory / 'helpers.json', helper_hashes)
        write(directory / 'request.json', {"root": str(root), "config": args.config, "url": args.url,
              "browserExecutable": str(browser), "nodeExecutable": str(node), "excludes": excludes, "grep": args.grep,
              "project": args.project, "timeoutSeconds": args.timeout_seconds})
        BASELINE.require(port_closed(port), "Local port is occupied; its owner is not ours and will not be stopped.")
        write(directory / 'service-before.json', {"port": port, "closed": True})
        observe('environment-preparation')
        bdd = read(root / 'node_modules/playwright-bdd/package.json').get('bin', {}).get('bddgen')
        BASELINE.relative(bdd)
        generator = physical(root / 'node_modules/playwright-bdd' / bdd)
        cli = physical(root / 'node_modules/playwright/cli.js')
        run('generation', [node, generator, '--config', config])
        command = [node, cli, 'test', '--config=' + str(config)]
        if args.grep:
            command += ['--grep=' + args.grep]
        if args.project:
            command += ['--project=' + args.project]
        run('listing', command + ['--list', '--reporter=json'], extra={"PLAYWRIGHT_JSON_OUTPUT_FILE": str(directory / 'selection.json')})
        selection = read(directory / 'selection.json')
        write(directory / 'lifecycle.json', local_lifecycle(selection, root, args.url))
        observe('environment-before')
        compare_environment(directory, 'environment-precheck.json', 'environment-preparation.json', 'environment-before.json')
        snapshot('before')
        BASELINE.require(port_closed(port), "Local port became occupied before test execution; nothing unrelated will be stopped.")
        remaining_ms = max(1, int((deadline - time.monotonic()) * 1000) - 5000)
        configured_ms = selection['config'].get('globalTimeout', 0)
        native_ms = min(remaining_ms, configured_ms) if type(configured_ms) is int and configured_ms > 0 else remaining_ms
        BASELINE.require(not (directory / 'results.json').exists() and not (directory / 'artifacts').exists(),
                         'Native execution destinations must be fresh.')
        unchanged_helpers()
        execution_ok = supervise([str(item) for item in command + ['--workers=1', '--retries=0', '--forbid-only',
            '--global-timeout=' + str(native_ms), '--reporter=line,json',
            '--output=' + str(directory / 'artifacts')]], root, directory, 'execution',
            dict(env, PLAYWRIGHT_JSON_OUTPUT_FILE=str(directory / 'results.json')), deadline, cancelled)
        outcome['checks']['executionClean'] = execution_ok
        cleanup = read(directory / 'execution-cleanup.json').get('stopped')
        outcome['checks']['cleanup'] = cleanup if type(cleanup) is bool else None
        with (directory / 'process.json').open('xb') as output:
            output.write((directory / 'execution-process.json').read_bytes())
        closed = port_closed(port)
        outcome['checks']['serviceClosed'] = closed
        write(directory / 'service-after.json', {"port": port, "closed": closed})
        # Retain failed execution observations too; never generate a receipt for failure.
        snapshot('after')
        observe('environment-after')
        post_complete = True
        try:
            compare_environment(directory, 'environment-postcheck.json', 'environment-before.json', 'environment-after.json')
        finally:
            if (directory / 'environment-postcheck.json').is_file():
                outcome['checks']['environmentStable'] = read(directory / 'environment-postcheck.json')['checksPassed']
        BASELINE.require(execution_ok and closed and not cancelled, "Execution, cancellation or owned cleanup did not qualify.")
        run('results-check', [sys.executable, HERE / 'check_playwright_results.py', '--selection', directory / 'selection.json',
            '--report', directory / 'results.json', '--runner-exit-code', str(read(directory / 'process.json')['exitCode'])], 'results-check.json')
        provenance = sorted(path.name for path in directory.iterdir() if path.is_file() and path.name not in
                            ('before.json', 'after.json', 'process.json', 'environment-before.json', 'selection.json', 'results.json'))
        argv = [sys.executable, HERE / 'baseline_evidence.py', 'record', '--directory', directory,
                '--before', 'before.json', '--after', 'after.json', '--runner', 'process.json',
                '--environment', 'environment-before.json', '--selection', 'selection.json', '--report', 'results.json']
        for name in provenance:
            argv.extend(['--provenance', name])
        run('record', argv, 'baseline.json')
        run('baseline-check', [sys.executable, HERE / 'baseline_evidence.py', 'check', '--baseline', directory / 'baseline.json',
            '--root', root, '--environment', directory / 'environment-after.json'], 'baseline-check.json')
        BASELINE.require(not cancelled, "Capture was cancelled.")
        unchanged_helpers()
        outcome['checks']['helpersUnchanged'] = True
        outcome.update(checksPassed=True, counts=read(directory / 'baseline-check.json')['counts'])
    except Exception as error:
        outcome.update(error={"type": type(error).__name__, "message": str(error)})
    finally:
        if cancelled:
            outcome.update(checksPassed=False, cancelledSignals=list(cancelled))
        outcome['postExecutionEvidenceComplete'] = post_complete
        outcome = publish_outcome(directory, outcome, cancelled)
    return outcome, 0 if outcome['checksPassed'] else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--attempt', required=True, help='Fresh directory outside source; its physical parent must exist.')
    parser.add_argument('--config', required=True, help='Reviewed config path relative to source root.')
    parser.add_argument('--url', required=True, help='Owned native webServer URL: http://127.0.0.1:PORT[/ready].')
    parser.add_argument('--browser-executable', required=True, help='Installed Chromium executable used by the reviewed config.')
    parser.add_argument('--node', default='node', help='Installed Node executable; no package downloads.')
    parser.add_argument('--grep')
    parser.add_argument('--project')
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--timeout-seconds', type=int, default=180, help='Whole-attempt command deadline; default 180 seconds plus bounded cleanup.')
    args = parser.parse_args(argv)
    if not 10 <= args.timeout_seconds <= 3600:
        parser.error('--timeout-seconds must be between 10 and 3600')
    cancelled, previous = [], {}
    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.signal(signum, lambda received, _frame: cancelled.append(received))
    try:
        result, status = capture(args, cancelled)
    except Exception as error:
        result, status = {"checksPassed": False, "error": {"type": type(error).__name__, "message": str(error)}}, 2
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)
    print(json.dumps(result, indent=2, allow_nan=False))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
