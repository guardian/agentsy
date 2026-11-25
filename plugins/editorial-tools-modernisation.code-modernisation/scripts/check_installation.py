#!/usr/bin/env python3
"""Check the loaded package and directly execute its runtime helpers with --help.

Run with Python. The default is read-only. --repair-execute-bits explicitly
restores missing executable bits only on byte-identical, owner-controlled helpers.
It never repairs content, installs a package, bypasses a denied execution, or runs
Copilot, models, application code or browser tests. Package hashes detect drift;
they are not a publisher signature or protection against a compromised package.
"""

import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
INTEGRITY = "scripts/installation-integrity.json"
HELPERS = (
    "inventory.py",
    "validate_discovery.py",
    "check_playwright_results.py",
    "baseline_evidence.py",
    "compare_candidate.py",
    "capture_playwright.py",
    "observe_node_environment.mjs",
    "build_report.py",
    "upstream_checks.py",
)
# Include the checker and the runtime helpers' bundled import closure. New imports
# require updating this fixed list and the reviewed package integrity manifest.
SUPPORT_FILES = ("LICENSE", "NOTICE", "upstream/scripts/make_shards.py", "assets/report/report.html",
                 "assets/report/markdown.js", "assets/report/vendor/markdown-it-15.0.3.umd.min.js",
                 "assets/report/diagrams.js", "assets/report/vendor/mermaid-11.17.2.min.js",
                 "assets/report/vendor/LICENSE-mermaid.txt",
                 "assets/report/vendor/LICENSES.txt", "assets/e2e/validation.mjs",
                 "assets/e2e/pan-domain-auth.mjs",
                 "upstream/scripts/compare.py", "upstream/scripts/baseline_diff.py",
                 "upstream/scripts/trace_rules.py", "upstream/scripts/proof_pack.py",
                 "upstream/scripts/uplift_checks.py")
PACKAGE_FILES = ("plugin.json", "scripts/check_installation.py", *SUPPORT_FILES,
                 *("scripts/" + name for name in HELPERS))
EXPECTED_MODE = 0o755


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def regular_file(root, relative, stack):
    """Open a fixed package path without following a symlink below its root."""
    path = root
    for part in Path(relative).parts[:-1]:
        path /= part
        if not stat.S_ISDIR(path.lstat().st_mode):
            raise ValueError("package directory is not a physical directory: " + str(path))
    path /= Path(relative).name
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("package path is not a regular file: " + str(path))
    # A nonblocking open also handles replacement by a FIFO between lstat/open.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    stream = stack.enter_context(os.fdopen(descriptor, "rb"))
    metadata = os.fstat(stream.fileno())
    if not stat.S_ISREG(metadata.st_mode) or identity(before) != identity(metadata):
        raise ValueError("package path changed or is not a regular file: " + str(path))
    return stream


def identity(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns, metadata.st_mode)


def digest_stream(stream):
    before = os.fstat(stream.fileno())
    stream.seek(0)
    digest = hashlib.sha256(stream.read()).hexdigest()
    if identity(before) != identity(os.fstat(stream.fileno())):
        raise ValueError("package file changed while reading")
    return digest


def reference_manifest(stack):
    stream = regular_file(PACKAGE_ROOT, INTEGRITY, stack)
    raw = stream.read()
    manifest = json.loads(raw, object_pairs_hook=unique_object)
    if (not isinstance(manifest, dict)
            or set(manifest) != {"formatVersion", "name", "version", "files"}
            or type(manifest["formatVersion"]) is not int or manifest["formatVersion"] != 1
            or manifest["name"] != "editorial-tools-modernisation.code-modernisation"
            or not isinstance(manifest["version"], str) or not manifest["version"]
            or not isinstance(manifest["files"], dict)
            or set(manifest["files"]) != set(PACKAGE_FILES)
            or any(not isinstance(value, str) or len(value) != 64
                   or any(char not in "0123456789abcdef" for char in value)
                   for value in manifest["files"].values())):
        raise ValueError("invalid package integrity manifest")
    # The metadata used as a reference must describe this exact checker, not a
    # target package's self-asserted replacement list or executable paths.
    checker = regular_file(PACKAGE_ROOT, "scripts/check_installation.py", stack)
    if digest_stream(checker) != manifest["files"]["scripts/check_installation.py"]:
        raise ValueError("reference integrity manifest does not match this checker")
    return manifest, raw


def check_installation(root, repair_execute_bits=False):
    report = {"scope": "package identity, helper modes and direct --help only",
              "pluginRoot": str(root), "referenceRoot": str(PACKAGE_ROOT),
              "passed": False, "identityVerified": False, "repairEligible": False,
              "repair": {"requested": repair_execute_bits, "changed": [],
                         "rolledBack": [], "rollbackErrors": []}, "helpers": []}
    with ExitStack() as stack:
        try:
            if os.name != "posix" or not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_NONBLOCK", "fchmod", "geteuid")):
                raise ValueError("installed helper mode checking currently requires a POSIX host")
            root = Path(root).expanduser().resolve()
            report["pluginRoot"] = str(root)
            manifest, reference_raw = reference_manifest(stack)
            installed_manifest = regular_file(root, INTEGRITY, stack)
            if installed_manifest.read() != reference_raw:
                raise ValueError("installed integrity manifest differs from the checker package; refresh the matching package")
            streams = {}
            # Read and verify every code dependency before modes, repair or help.
            for relative, expected in manifest["files"].items():
                stream = regular_file(root, relative, stack)
                streams[relative] = stream
                if digest_stream(stream) != expected:
                    raise ValueError("package content differs from its integrity manifest: " + relative)
            streams["plugin.json"].seek(0)
            package = json.load(streams["plugin.json"], object_pairs_hook=unique_object)
            if (not isinstance(package, dict) or package.get("name") != manifest["name"]
                    or package.get("version") != manifest["version"]):
                raise ValueError("plugin identity does not match its integrity manifest")
            report.update(name=package["name"], version=package["version"], identityVerified=True)
            pending = []
            for name in HELPERS:
                path = root / "scripts" / name
                stream = streams["scripts/" + name]
                metadata = os.fstat(stream.fileno())
                mode = stat.S_IMODE(metadata.st_mode)
                helper = {"path": str(path), "mode": format(mode, "04o"),
                          "executableAccess": os.access(path, os.X_OK),
                          "invoked": False, "ready": False}
                report["helpers"].append(helper)
                if (mode & ~0o111) != (EXPECTED_MODE & ~0o111):
                    helper["error"] = "unexpected read/write or special mode bits; no automatic repair"
                elif mode != EXPECTED_MODE:
                    # Do not turn a known execution denial into a permissions fix.
                    # With an owner execute bit already present, a failed access
                    # check is not the observed missing-execute-bit installation bug.
                    if metadata.st_nlink != 1:
                        helper["error"] = "missing execute bits on a multiply linked helper; no automatic repair"
                    elif metadata.st_uid != os.geteuid():
                        helper["error"] = "missing execute bits on a helper not owned by this user"
                    elif mode & stat.S_IXUSR and not helper["executableAccess"]:
                        helper["error"] = "execution denied despite owner execute bit; no automatic repair"
                    else:
                        helper["error"] = "missing execute bits"
                        pending.append((stream, mode, helper))
                elif not helper["executableAccess"]:
                    helper["error"] = "execution denied despite executable mode; no automatic repair"
                else:
                    helper["ready"] = True
            repairable = bool(pending) and all(helper["ready"] or helper.get("error") == "missing execute bits"
                                              for helper in report["helpers"])
            report["repairEligible"] = repairable
            if pending and repair_execute_bits and repairable:
                changed = []
                try:
                    # Recheck the complete package before the first mutation.
                    verify_open_files(root, streams, manifest)
                    for stream, mode, _helper in pending:
                        metadata = os.fstat(stream.fileno())
                        if stat.S_IMODE(metadata.st_mode) != mode or metadata.st_nlink != 1 or metadata.st_uid != os.geteuid():
                            raise ValueError("helper permissions or ownership changed before repair")
                    for stream, mode, helper in pending:
                        os.fchmod(stream.fileno(), mode | 0o111)
                        changed.append((stream, mode, helper))
                        report["repair"]["changed"].append(helper["path"])
                    for stream, _mode, helper in pending:
                        new_mode = stat.S_IMODE(os.fstat(stream.fileno()).st_mode)
                        if new_mode != EXPECTED_MODE or not os.access(helper["path"], os.X_OK):
                            raise ValueError("execution still denied after restoring missing bits")
                        helper.update(mode=format(new_mode, "04o"), executableAccess=True, ready=True)
                        helper.pop("error", None)
                except (OSError, ValueError):
                    for stream, mode, helper in reversed(changed):
                        try:
                            os.fchmod(stream.fileno(), mode)
                            report["repair"]["rolledBack"].append(helper["path"])
                            helper.update(mode=format(mode, "04o"), ready=False,
                                          executableAccess=os.access(helper["path"], os.X_OK),
                                          error="repair rolled back")
                        except OSError as error:
                            report["repair"]["rollbackErrors"].append({"path": helper["path"], "error": str(error)})
                    raise
            if not all(helper["ready"] for helper in report["helpers"]):
                report["error"] = "helper precheck failed; no helpers were invoked"
                return report
            verify_open_files(root, streams, manifest)
            for helper in report["helpers"]:
                helper.update(invoked=True, passed=False)
                try:
                    result = subprocess.run([helper["path"], "--help"], cwd=root,
                                            text=True, capture_output=True, timeout=10,
                                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                    helper.update(exitCode=result.returncode, stdout=result.stdout,
                                  stderr=result.stderr, passed=result.returncode == 0)
                except (OSError, subprocess.SubprocessError) as error:
                    helper["error"] = str(error)
            report["passed"] = all(helper["passed"] for helper in report["helpers"])
            if not report["passed"]:
                report["error"] = "one or more direct helper --help commands failed; do not bypass a denial with an interpreter"
        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as error:
            report["error"] = str(error)
    return report


def verify_open_files(root, streams, manifest):
    """Recheck path identity and content; a hash check is not a filesystem lock."""
    for relative, stream in streams.items():
        path = root / relative
        if path.resolve(strict=True) != path or identity(path.stat()) != identity(os.fstat(stream.fileno())):
            raise ValueError("package path changed during readiness check: " + relative)
        if digest_stream(stream) != manifest["files"][relative]:
            raise ValueError("package content changed during readiness check: " + relative)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", type=Path, default=PACKAGE_ROOT,
                        help="Actual loaded plugin directory; default: this script's package.")
    parser.add_argument("--repair-execute-bits", action="store_true",
                        help="Explicitly restore only missing helper executable bits after full package verification.")
    args = parser.parse_args()
    report = check_installation(args.plugin_root, args.repair_execute_bits)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
