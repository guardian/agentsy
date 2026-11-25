#!/usr/bin/env python3
"""Capture source identities and check bound Playwright BDD baseline evidence.

Read-only: snapshot/record/check print JSON without running application code, tests
or shell commands. Save output outside the source tree or explicitly exclude its
output subtree. Exit 0 means capture/assembly succeeded, or check passed technical
preconditions; 1 means stale/missing/blocked evidence, 2 malformed/unreadable input.
A receipt is not eligibility; check it with current source and environment.
Evidence is not authenticated or a write lock.
"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

sys.dont_write_bytecode = True
_SPEC = importlib.util.spec_from_file_location(
    "baseline_playwright_checker", Path(__file__).with_name("check_playwright_results.py"))
PLAYWRIGHT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(PLAYWRIGHT)
HASH = re.compile(r"[0-9a-f]{64}\Z")
MODE = re.compile(r"[0-7]{4}\Z")
LIMITS = [
    "Evidence, timestamps and runner exit codes are unauthenticated; hashes identify bytes only.",
    "The snapshot covers every regular file except the explicitly declared exclusions; coverage and scope adequacy require review.",
    "Environment equality checks declared observations, not an independent or exhaustive measurement of the running environment.",
    "A passing technical precondition is not business approval, complete behavioral coverage, or an operating-system write lock.",
    "Files and environment may change after this read-only check; check again immediately before implementation.",
]


class Invalid(ValueError):
    pass


class Ineligible(Invalid):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def utc_now():
    return datetime.now(timezone.utc)


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def moment(value):
    require(isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)", value),
        "Expected a UTC timestamp.")
    normalized = value.replace("Z", "+00:00")
    if "." in normalized:
        whole, fraction = normalized.split(".")
        normalized = whole + "." + fraction[:-6].ljust(6, "0") + "+00:00"
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise Invalid("Expected a UTC timestamp.") from error
    require(result.tzinfo is not None and result.utcoffset() == timedelta(0), "Expected a UTC timestamp.")
    return result


def keys(value, expected, optional=()):
    require(isinstance(value, dict) and set(expected) <= set(value)
            and set(value) <= set(expected) | set(optional), "Unexpected or missing object fields.")


def strings(value):
    require(isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value),
            "Expected an array of nonempty strings.")


def relative(value):
    require(isinstance(value, str) and value and "\\" not in value and "\0" not in value,
            "Expected a canonical relative path.")
    path = PurePosixPath(value)
    require(not path.is_absolute() and value == path.as_posix()
            and all(part not in (".", "..", "") for part in path.parts)
            and value != ".", "Expected a canonical relative path.")
    return value


def exclusions(value):
    require(isinstance(value, list), "Expected exclusions array.")
    for item in value:
        relative(item)
    require(value == sorted(set(value)), "Exclusions must be sorted and unique.")
    require(not any(right.startswith(left + "/") for index, left in enumerate(value)
                    for right in value[index + 1:]), "Overlapping exclusions are forbidden.")
    return value


def excluded(path, excludes):
    return any(path == item or path.startswith(item + "/") for item in excludes)


def no_symlinks(path):
    for part in (path,) + tuple(path.parents):
        require(not part.is_symlink(), "Symlink input paths are forbidden.")


def stable_read(path):
    """Reject symlinks/special files and observed changes while reading a file."""
    path = Path(path)
    no_symlinks(path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(str(path), flags)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode), "Only regular files are supported.")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            raw = handle.read()
        after = os.fstat(fd)
        current = os.stat(path, follow_symlinks=False)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_mode, item.st_size,
                                 item.st_mtime_ns, item.st_ctime_ns)
        require(identity(before) == identity(after) == identity(current), "File changed during reading.")
        return raw, "%04o" % stat.S_IMODE(before.st_mode)
    finally:
        os.close(fd)


def parse(raw):
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=PLAYWRIGHT.unique_object,
                            parse_float=PLAYWRIGHT.finite_float, parse_constant=PLAYWRIGHT.reject_constant)
        require(isinstance(result, dict), "Expected a JSON object.")
        return result
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Invalid("Invalid JSON object; duplicate keys and nonfinite numbers are forbidden.") from error


def physical_root(root):
    path = Path(root).absolute()
    no_symlinks(path)
    path = path.resolve(strict=True)
    require(path.is_dir(), "Source root must be a directory.")
    return path


def scan(root, excludes):
    files = []

    def visit(directory):
        before = os.stat(directory, follow_symlinks=False)
        require(stat.S_ISDIR(before.st_mode), "Source directories must not be symlinks.")
        names = sorted(os.listdir(directory))
        for name in names:
            path = directory / name
            rel = path.relative_to(root).as_posix()
            if excluded(rel, excludes):
                continue
            info = os.stat(path, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                visit(path)
            else:
                raw, mode = stable_read(path)
                files.append({"path": rel, "sha256": digest(raw), "mode": mode})
        after = os.stat(directory, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_mode, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_mode, after.st_mtime_ns, after.st_ctime_ns)
                and names == sorted(os.listdir(directory)), "Directory changed during reading.")

    visit(root)
    return sorted(files, key=lambda entry: entry["path"])


def tree_hash(excludes, files):
    return digest(canonical({"excludes": excludes, "files": files}))


def snapshot(root, excludes=()):
    root = physical_root(root)
    excludes = exclusions(list(excludes))
    started = utc_now()
    files = scan(root, excludes)
    require(files, "Source snapshot must contain at least one regular file.")
    require(files == scan(root, excludes), "Source changed between snapshot passes.")
    return {"schemaVersion": 1, "kind": "source-snapshot", "root": str(root),
            "startedAt": iso(started), "completedAt": iso(utc_now()), "excludes": excludes,
            "files": files, "treeSha256": tree_hash(excludes, files)}


def snapshot_schema(value):
    keys(value, ("schemaVersion", "kind", "root", "startedAt", "completedAt", "excludes", "files", "treeSha256"))
    require(type(value["schemaVersion"]) is int and value["schemaVersion"] == 1
            and value["kind"] == "source-snapshot", "Unsupported snapshot version or kind.")
    require(isinstance(value["root"], str) and Path(value["root"]).is_absolute()
            and str(Path(value["root"])) == value["root"], "Expected an absolute snapshot root.")
    require(moment(value["startedAt"]) <= moment(value["completedAt"]), "Snapshot interval is reversed.")
    excludes = exclusions(value["excludes"])
    files = value["files"]
    require(isinstance(files, list) and files, "Snapshot files must be nonempty.")
    paths = []
    for entry in files:
        keys(entry, ("path", "sha256", "mode"))
        paths.append(relative(entry["path"]))
        require(isinstance(entry["sha256"], str) and HASH.fullmatch(entry["sha256"]), "Invalid file digest.")
        require(isinstance(entry["mode"], str) and MODE.fullmatch(entry["mode"]), "Invalid file mode.")
        require(not excluded(entry["path"], excludes), "Snapshot includes an excluded path.")
    require(paths == sorted(set(paths)), "Snapshot paths must be sorted and unique.")
    require(value["treeSha256"] == tree_hash(excludes, files), "Snapshot digest does not match its scope/files.")


def environment_schema(value):
    keys(value, ("schemaVersion", "observedAt", "facts", "limitations"))
    require(type(value["schemaVersion"]) is int and value["schemaVersion"] == 1, "Unsupported environment version.")
    moment(value["observedAt"])
    require(isinstance(value["facts"], dict) and value["facts"], "Environment facts must be a nonempty object.")
    strings(value["limitations"])
    canonical(value["facts"])


def report_sources(data, capture, label, audit):
    """Bind native report locations to files covered by the source snapshot."""
    source_root = PurePosixPath(capture["root"])
    covered = {item["path"] for item in capture["files"]}

    def absolute_path(value, location, file=False):
        require(isinstance(value, str) and value and "\\" not in value and "\0" not in value,
                "Native source locations must be canonical absolute paths.")
        path = PurePosixPath(value)
        require(path.is_absolute() and path.as_posix() == value and ".." not in path.parts,
                "Native source locations must be canonical absolute paths.")
        try:
            relative_path = path.relative_to(source_root).as_posix()
        except ValueError:
            audit.issue("report.source_outside_root", location,
                        "Native report locations must remain inside the captured source root.")
            return None
        if file:
            audit.expect(relative_path in covered, "report.source_not_captured", location,
                         "Every native spec and declared config file must be included in the source snapshot.")
        else:
            audit.expect(not excluded(relative_path, capture["excludes"]), "report.directory_excluded", location,
                         "Native root and project test directories must not be excluded from the snapshot.")
        return path

    config = data.get("config")
    require(isinstance(config, dict) and isinstance(config.get("projects"), list), "Missing native report source configuration.")
    root_dir = absolute_path(config.get("rootDir"), label + ".config.rootDir")
    config_file = config.get("configFile")
    if config_file is not None:
        absolute_path(config_file, label + ".config.configFile", file=True)
    project_dirs = {}
    for index, project in enumerate(config["projects"]):
        require(isinstance(project, dict) and isinstance(project.get("id"), str)
                and isinstance(project.get("name"), str), "Invalid native project identity.")
        project_dirs[(project["id"], project["name"])] = absolute_path(
            project.get("testDir"), "%s.config.projects[%d].testDir" % (label, index))
    require(isinstance(data.get("suites"), list), "Missing native suites for source binding.")
    pending = list(data["suites"])
    spec_paths = set()
    while pending:
        suite = pending.pop()
        require(isinstance(suite, dict) and isinstance(suite.get("specs"), list)
                and isinstance(suite.get("suites", []), list), "Invalid native suite source locations.")
        pending.extend(suite.get("suites", []))
        for spec in suite["specs"]:
            require(isinstance(spec, dict) and isinstance(spec.get("file"), str)
                    and isinstance(spec.get("tests"), list), "Invalid native spec source locations.")
            reported = spec["file"]
            if PurePosixPath(reported).is_absolute():
                spec_path = absolute_path(reported, label + ".spec.file", file=True)
            else:
                relative(reported)
                spec_path = absolute_path((root_dir / reported).as_posix(), label + ".spec.file", file=True) if root_dir else None
            if spec_path is None:
                continue
            spec_paths.add(spec_path.as_posix())
            for test in spec["tests"]:
                require(isinstance(test, dict) and isinstance(test.get("projectId"), str)
                        and isinstance(test.get("projectName"), str), "Invalid native test project identity.")
                test_dir = project_dirs.get((test["projectId"], test["projectName"]))
                if test_dir is not None:
                    audit.expect(test_dir in spec_path.parents,
                                 "report.spec_outside_test_dir", label + ".spec.file",
                                 "Each native spec must belong to its declared project's test directory.")
    return {"rootDir": config.get("rootDir"), "configFile": config_file,
            "projectTestDirs": {key: str(value) if value is not None else None for key, value in project_dirs.items()},
            "specFiles": sorted(spec_paths)}


def bind_report_sources(selection, report, capture, audit):
    before_errors = len(audit.errors)
    selected = report_sources(selection, capture, "selection", audit)
    observed = report_sources(report, capture, "report", audit)
    audit.expect(selected == observed, "report.source_configuration_mismatch", "report.config",
                 "Selection and execution must identify the same source root, config, project test directories and spec files.")
    return len(audit.errors) == before_errors


class Audit:
    def __init__(self, max_environment_age_seconds=300):
        self.max_environment_age_seconds = max_environment_age_seconds
        self.errors = []
        self.invalid = False
        self.hashes = {}
        self.refs = []
        self.counts = {}
        self.checks = {"sourceMatches": False, "reportsPassed": False, "reportSourcesBound": False, "environmentMatches": False,
                       "captureLinked": False, "referencesUnchanged": False}

    def issue(self, code, location, message):
        self.errors.append({"code": code, "location": location, "message": message})

    def expect(self, condition, code, location, message):
        if not condition:
            self.issue(code, location, message)
        return condition

    def read(self, path, label):
        raw, _ = stable_read(path)
        self.hashes[label] = digest(raw)
        return raw

    def ref(self, base, value, label):
        keys(value, ("path", "sha256"))
        relative(value["path"])
        require(isinstance(value["sha256"], str) and HASH.fullmatch(value["sha256"]), "Invalid evidence digest.")
        path = base / value["path"]
        raw = self.read(path, label)
        self.expect(self.hashes[label] == value["sha256"], "reference.changed", label,
                    "Referenced evidence bytes do not match the recorded digest.")
        self.refs.append((path, self.hashes[label]))
        return path, raw

    def result(self):
        passed = not self.errors
        return {"schemaVersion": 1, "checksPassed": passed, "eligibleForImplementation": passed,
                "checks": self.checks, "counts": self.counts, "inputSha256": self.hashes,
                "maxEnvironmentAgeSeconds": self.max_environment_age_seconds,
                "errors": self.errors, "limits": LIMITS}, 2 if self.invalid else (0 if passed else 1)


def check(baseline_path, root, environment_path=None, max_environment_age_seconds=300):
    audit = Audit(max_environment_age_seconds)
    try:
        require(type(max_environment_age_seconds) is int and max_environment_age_seconds > 0,
                "Environment age bound must be a positive integer.")
        baseline_path = Path(baseline_path).absolute()
        no_symlinks(baseline_path)
        baseline_path = baseline_path.parent.resolve(strict=True) / baseline_path.name
        record = parse(audit.read(baseline_path, "baseline"))
        audit.refs.append((baseline_path, audit.hashes["baseline"]))
        keys(record, ("schemaVersion", "kind", "snapshot", "provenance", "execution", "environment", "limitations", "blockers"))
        require(type(record["schemaVersion"]) is int and record["schemaVersion"] == 1
                and record["kind"] == "playwright-bdd-baseline", "Unsupported baseline version or kind.")
        snapshot_schema(record["snapshot"])
        before = record["snapshot"]
        strings(record["limitations"])
        strings(record["blockers"])
        provenance = record["provenance"]
        keys(provenance, ("kind", "references"))
        require(provenance["kind"] in ("captured", "historical-import"), "Unsupported provenance kind.")
        historical = provenance["kind"] == "historical-import"
        require(not historical or record["blockers"], "Historical imports must retain blockers.")
        require(isinstance(provenance["references"], list), "Expected provenance references array.")
        for index, reference in enumerate(provenance["references"]):
            audit.ref(baseline_path.parent, reference, "provenance.references[%d]" % index)
        execution = record["execution"]
        keys(execution, ("selection", "report", "runner", "exitCode", "startedAt", "completedAt"), ("beforeSnapshot", "afterSnapshot"))
        require(type(execution["exitCode"]) is int, "Runner exit code must be an integer.")
        start, end = moment(execution["startedAt"]), moment(execution["completedAt"])
        require(start <= end, "Execution interval is reversed.")
        audit.expect(end <= utc_now() + timedelta(seconds=5), "execution.future", "execution.completedAt",
                     "Execution cannot complete in the future.")
        selection_path, selection_raw = audit.ref(baseline_path.parent, execution["selection"], "execution.selection")
        report_path, report_raw = audit.ref(baseline_path.parent, execution["report"], "execution.report")
        _, runner_raw = audit.ref(baseline_path.parent, execution["runner"], "execution.runner")
        runner = parse(runner_raw)
        keys(runner, ("schemaVersion", "exitCode", "startedAt", "completedAt"))
        require(type(runner["schemaVersion"]) is int and runner["schemaVersion"] == 1
                and type(runner["exitCode"]) is int, "Invalid native process record.")
        moment(runner["startedAt"])
        moment(runner["completedAt"])
        audit.expect(all(runner[field] == execution[field] for field in ("exitCode", "startedAt", "completedAt")),
                     "execution.runner_mismatch", "execution.runner",
                     "Bound native process exit code and interval must match the execution record.")
        observed_report = parse(report_raw)
        selected_report = parse(selection_raw)
        result, status = PLAYWRIGHT.check(selection_path, report_path, execution["exitCode"])
        audit.counts = result["counts"]
        audit.checks["reportsPassed"] = status == 0
        if status:
            audit.invalid |= status == 2
            audit.errors.extend(dict(item, location="playwright." + item["location"]) for item in result["errors"])
        for label in ("selection", "report"):
            audit.expect(result["inputSha256"][label] == audit.hashes["execution." + label],
                         "reference.raced", "execution." + label, "Report changed during the audit.")
        audit.checks["reportSourcesBound"] = bind_report_sources(selected_report, observed_report, before, audit)
        before_bound = False
        if "beforeSnapshot" in execution:
            _, before_raw = audit.ref(baseline_path.parent, execution["beforeSnapshot"], "execution.beforeSnapshot")
            bound_before = parse(before_raw)
            snapshot_schema(bound_before)
            before_bound = audit.expect(canonical(bound_before) == canonical(before), "source.before_snapshot_mismatch", "snapshot",
                                        "Inline source snapshot must exactly match the bound pre-run snapshot.")
            before_bound &= audit.hashes["execution.beforeSnapshot"] == execution["beforeSnapshot"]["sha256"]
        elif not historical:
            raise Invalid("Captured baselines require a beforeSnapshot reference.")
        stats = observed_report.get("stats", {})
        require(isinstance(stats, dict) and PLAYWRIGHT.number(stats.get("duration")), "Invalid native report timing.")
        native_start = moment(stats.get("startTime"))
        try:
            native_end = native_start + timedelta(milliseconds=stats["duration"])
        except OverflowError as error:
            raise Invalid("Native report duration is out of range.") from error
        audit.expect(start <= native_start <= native_end <= end, "execution.time_mismatch", "execution",
                     "Recorded execution must contain the native report's full interval.")
        linked = False
        if "afterSnapshot" in execution:
            _, after_raw = audit.ref(baseline_path.parent, execution["afterSnapshot"], "execution.afterSnapshot")
            after = parse(after_raw)
            snapshot_schema(after)
            same = audit.expect(before["treeSha256"] == after["treeSha256"] and before["root"] == after["root"],
                                "source.changed_during_run", "execution.afterSnapshot",
                                "Before and after snapshots must have identical root, scope, membership, bytes and modes.")
            timing = (moment(before["completedAt"]) <= start and moment(after["startedAt"]) >= end
                      and moment(after["completedAt"]) <= utc_now() + timedelta(seconds=5))
            if not historical:
                audit.expect(timing, "capture.time_mismatch", "snapshot",
                             "Snapshots must bracket the execution; a new snapshot cannot be paired with an old result.")
            linked = (before_bound and same and timing and not historical
                      and audit.hashes["execution.afterSnapshot"] == execution["afterSnapshot"]["sha256"])
        elif not historical:
            raise Invalid("Captured baselines require an afterSnapshot reference.")
        audit.checks["captureLinked"] = linked
        current_root = physical_root(root)
        same_root = audit.expect(str(current_root) == before["root"], "source.root_mismatch", "root",
                                 "Current physical root differs from the recorded root.")
        current = snapshot(current_root, before["excludes"])
        audit.hashes["currentTree"] = current["treeSha256"]
        same_tree = audit.expect(current["treeSha256"] == before["treeSha256"], "source.changed", "source",
                                 "Current file membership, bytes, modes or exclusion scope differ from the baseline.")
        audit.checks["sourceMatches"] = same_root and same_tree
        environment = record["environment"]
        keys(environment, ("record", "facts"))
        require(isinstance(environment["facts"], dict) and environment["facts"], "Expected nonempty environment facts.")
        _, stored_raw = audit.ref(baseline_path.parent, environment["record"], "environment.record")
        stored = parse(stored_raw)
        environment_schema(stored)
        stored_facts_match = audit.expect(canonical(stored["facts"]) == canonical(environment["facts"]),
                                         "environment.record_mismatch", "environment.record",
                                         "Bound environment observation and inline facts must match exactly.")
        if not historical:
            audit.expect(moment(stored["observedAt"]) <= start, "environment.baseline_too_late", "environment.record",
                         "Baseline environment must have been observed before execution started.")
        if environment_path is None:
            audit.issue("environment.missing", "environment", "Supply a current environment observation; historical facts alone are insufficient.")
        else:
            current_environment = Path(environment_path).absolute()
            no_symlinks(current_environment)
            current_environment = current_environment.parent.resolve(strict=True) / current_environment.name
            current_raw = audit.read(current_environment, "currentEnvironment")
            audit.refs.append((current_environment, audit.hashes["currentEnvironment"]))
            observed = parse(current_raw)
            environment_schema(observed)
            current_time = moment(observed["observedAt"])
            now = utc_now()
            time_matches = audit.expect(end <= current_time <= now + timedelta(seconds=5)
                                        and now - current_time <= timedelta(seconds=max_environment_age_seconds),
                                        "environment.stale_or_future", "currentEnvironment.observedAt",
                                        "Current observation must follow execution, satisfy the configured age bound, and cannot be in the future.")
            facts_match = audit.expect(canonical(environment["facts"]) == canonical(observed["facts"]),
                                      "environment.changed", "currentEnvironment.facts",
                                      "Current declared environment facts must match the baseline facts exactly.")
            audit.checks["environmentMatches"] = stored_facts_match and time_matches and facts_match
        for index, _blocker in enumerate(record["blockers"]):
            audit.issue("baseline.blocked", "blockers[%d]" % index, "A recorded baseline blocker remains unresolved.")
        unchanged = True
        for path, original_hash in audit.refs:
            raw, _ = stable_read(path)
            unchanged &= audit.expect(digest(raw) == original_hash, "reference.raced", "references",
                                      "Evidence changed during the audit.")
        audit.checks["referencesUnchanged"] = unchanged and not any(
            item["code"] == "reference.changed" for item in audit.errors)
    except (OSError, Invalid, UnicodeError, RecursionError, OverflowError) as error:
        audit.invalid = True
        # Do not include OS errors or file contents: they can expose environment data.
        audit.issue("input.invalid", "input", str(error) if isinstance(error, Invalid)
                    else "Cannot safely read the complete input or source tree.")
    return audit.result()


def record(directory, before_path, after_path, runner_path, environment_path,
           selection_path, report_path, provenance_paths=()):
    """Assemble a captured receipt, refusing inconsistent inputs; never grant eligibility."""
    directory = physical_root(directory)
    loaded = {}

    def reference(name):
        relative(name)
        raw, _ = stable_read(directory / name)
        loaded[name] = raw
        return {"path": name, "sha256": digest(raw)}

    before_ref = reference(before_path)
    before = parse(loaded[before_path])
    after_ref = reference(after_path)
    after = parse(loaded[after_path])
    for capture in (before, after):
        snapshot_schema(capture)
    runner_ref = reference(runner_path)
    runner = parse(loaded[runner_path])
    keys(runner, ("schemaVersion", "exitCode", "startedAt", "completedAt"))
    require(type(runner["schemaVersion"]) is int and runner["schemaVersion"] == 1
            and type(runner["exitCode"]) is int, "Invalid native process record.")
    start, end = moment(runner["startedAt"]), moment(runner["completedAt"])
    environment_ref = reference(environment_path)
    environment = parse(loaded[environment_path])
    environment_schema(environment)
    selection_ref = reference(selection_path)
    report_ref = reference(report_path)
    report = parse(loaded[report_path])
    audited, status = PLAYWRIGHT.check(directory / selection_path, directory / report_path, runner["exitCode"])
    if status:
        raise (Invalid if status == 2 else Ineligible)("Native Playwright result checks failed; preserve and inspect the raw attempt.")
    require(audited["inputSha256"] == {"selection": selection_ref["sha256"], "report": report_ref["sha256"]},
            "Native report changed during record assembly.")
    binding_audit = Audit()
    if not bind_report_sources(parse(loaded[selection_path]), report, before, binding_audit):
        raise Ineligible("Native report source locations do not match the captured source files.")
    native_start = moment(report["stats"]["startTime"])
    native_end = native_start + timedelta(milliseconds=report["stats"]["duration"])
    if not (moment(before["completedAt"]) <= start <= native_start <= native_end <= end
            <= moment(after["startedAt"]) <= moment(after["completedAt"]) <= utc_now() + timedelta(seconds=5)
            and moment(environment["observedAt"]) <= start):
        raise Ineligible("Captured source/environment/process/report intervals do not agree.")
    if before["treeSha256"] != after["treeSha256"] or before["root"] != after["root"]:
        raise Ineligible("Source root, scope, membership, bytes or modes changed during execution.")
    references = [before_ref]
    for name in sorted(set(provenance_paths) - {before_path}):
        references.append(reference(name))
    for name, original in loaded.items():
        current, _ = stable_read(directory / name)
        require(current == original, "Evidence changed during record assembly.")
    return {"schemaVersion": 1, "kind": "playwright-bdd-baseline", "snapshot": before,
            "provenance": {"kind": "captured", "references": references},
            "execution": {"selection": selection_ref, "report": report_ref, "runner": runner_ref,
                          "exitCode": runner["exitCode"], "startedAt": runner["startedAt"],
                          "completedAt": runner["completedAt"], "beforeSnapshot": before_ref, "afterSnapshot": after_ref},
            "environment": {"record": environment_ref, "facts": environment["facts"]},
            "limitations": environment["limitations"] + [
                "Coverage concerns the selected tests; evidence and timestamps are unauthenticated.",
                "Run check with current source and fresh environment observations before implementation."],
            "blockers": []}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("snapshot", help="Print a complete source snapshot; redirect outside its root.")
    capture.add_argument("--root", required=True)
    capture.add_argument("--exclude", action="append", default=[], help="Explicit canonical relative subtree; repeat as needed.")
    assemble = commands.add_parser("record", help="Assemble a captured receipt from recorded files; never run or write anything.")
    assemble.add_argument("--directory", required=True, help="Physical directory containing all evidence inputs.")
    for flag in ("before", "after", "runner", "environment", "selection", "report"):
        assemble.add_argument("--" + flag, required=True, help="Canonical path relative to --directory.")
    assemble.add_argument("--provenance", action="append", default=[], help="Additional relative evidence path; repeat as needed.")
    verify = commands.add_parser("check", help="Check current source, reports and declared environment against a baseline.")
    verify.add_argument("--baseline", required=True)
    verify.add_argument("--root", required=True)
    verify.add_argument("--environment", help="Fresh observed environment JSON; omission fails closed.")
    verify.add_argument("--max-environment-age-seconds", type=int, default=300, help="Positive freshness window; default 300 seconds.")
    args = parser.parse_args(argv)
    if args.command == "snapshot":
        try:
            result, status = snapshot(args.root, sorted(args.exclude)), 0
        except (OSError, Invalid, UnicodeError, RecursionError) as error:
            result, status = {"checksPassed": False, "errors": [{"code": "input.invalid", "location": "source",
                "message": str(error) if isinstance(error, Invalid) else "Cannot safely read the complete source tree."}]}, 2
    elif args.command == "record":
        try:
            result, status = record(args.directory, args.before, args.after, args.runner,
                                    args.environment, args.selection, args.report, args.provenance), 0
        except (OSError, Invalid, UnicodeError, RecursionError, OverflowError) as error:
            result, status = {"checksPassed": False, "eligibleForImplementation": False,
                "errors": [{"code": "record.invalid", "location": "input", "message": str(error)
                            if isinstance(error, Invalid) else "Cannot safely read the complete evidence."}]}, (1 if isinstance(error, Ineligible) else 2)
    else:
        result, status = check(args.baseline, args.root, args.environment, args.max_environment_age_seconds)
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
