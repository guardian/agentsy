#!/usr/bin/env python3
"""Run the pinned Claude verification tools with this port's existing rule IDs.

The original tools own their formats and verdicts. This adapter preserves R-001
cards and mentions without renumbering saved records. It does not run applications.
"""

import argparse
import importlib
import importlib.util
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = {"compare": "compare", "baseline": "baseline_diff", "trace": "trace_rules",
         "proof": "proof_pack", "uplift": "uplift_checks"}
R_CARD = re.compile(r"(#{2,5}[ \t]+[*`\[]*)(R[-_](\d{1,6}))(?![A-Za-z0-9])", re.I)
R_MENTION = re.compile(r"(?<![A-Za-z0-9])R[-_](\d{1,6})(?!\d)", re.I)


def preserve_rule_ids(trace):
    """Keep the port's R IDs distinct from upstream RULE IDs in all evidence."""
    original_parse = trace.parse_rules
    original_find = trace.find_ids
    original_run = trace.run_evidence

    def parse_rules(text):
        port_ids, upstream_ids, fence = {}, set(), ""
        lines = []
        for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            marker = trace.FENCE.match(line)
            if fence:
                if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                    fence = ""
            elif marker:
                fence = marker[1]
            else:
                port = R_CARD.match(line)
                upstream = trace.CARD.match(line)
                if port:
                    number = int(port[3])
                    port_ids.setdefault(number, port[2])
                    line = line[:port.start(2)] + "RULE" + line[port.start(2) + 1:]
                elif upstream:
                    upstream_ids.add(int(upstream[1]))
                elif line.lstrip().startswith("|"):
                    line = re.sub(r"(\|[ \t*`]*)R(?=[-_]\d{1,6}[ \t*`]*\|)", r"\1RULE", line, flags=re.I)
            lines.append(line)
        # Upstream indexes cards by number. Refuse a collision rather than let
        # one namespace silently borrow another namespace's passing result.
        if set(port_ids) & upstream_ids:
            raise ValueError("R and RULE cards share a number; select one existing catalogue without renumbering it")
        rules, notes = original_parse("\n".join(lines))
        for rule in rules:
            if rule["n"] in port_ids:
                rule.update(id=port_ids[rule["n"]], n=-rule["n"] - 1)
        return rules, notes

    def find_ids(text):
        found = original_find(text)
        for match in R_MENTION.finditer(text):
            found.append((-int(match[1]) - 1, match.start()))
            more = trace.MORE.match(text, match.end())
            while more:
                found.append((-int(more[1]) - 1, match.start()))
                more = trace.MORE.match(text, more.end())
        return found

    def run_evidence(results):
        evidence = original_run(results)
        for result in results:
            for identity, status in (result or {}).get("tests", {}).items():
                if status == "PASS":
                    evidence["ids"].update(number for number, _ in find_ids(identity) if number < 0)
        return evidence

    trace.parse_rules = parse_rules
    trace.find_ids = find_ids
    trace.run_evidence = run_evidence

    def restore():
        trace.parse_rules = original_parse
        trace.find_ids = original_find
        trace.run_evidence = original_run
    return restore


def use_source_snapshot(proof, snapshot_path):
    """Compare the prepared original with an existing source-snapshot record."""
    spec = importlib.util.spec_from_file_location(
        "modernisation_source_snapshot", ROOT / "scripts/baseline_evidence.py")
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    path = Path(snapshot_path).expanduser().absolute()
    raw, _ = baseline.stable_read(path)
    path = path.resolve(strict=True)
    before = baseline.parse(raw)
    baseline.snapshot_schema(before)
    baseline.require(baseline.moment(before["completedAt"]) <= baseline.utc_now(),
                     "Source snapshot cannot complete in the future.")
    original = proof.source_check
    original_rules = proof.RULES_TEXT

    def source_check(workspace, system, adir):
        root = baseline.physical_root(Path(workspace) / "legacy" / system)
        baseline.require(before["root"] == str(root),
                         "Source snapshot root must match this system's physical legacy root.")
        baseline.require(root not in path.parents,
                         "Source snapshot must be saved outside the measured legacy root.")
        current = baseline.snapshot(root, before["excludes"])
        baseline.require(baseline.stable_read(path)[0] == raw,
                         "Source snapshot changed during verification.")
        expected = {entry["path"]: entry for entry in before["files"]}
        observed = {entry["path"]: entry for entry in current["files"]}
        changed = sorted(name for name in expected.keys() | observed.keys()
                         if expected.get(name) != observed.get(name))
        excludes = before["excludes"]
        scope = "no exclusions" if not excludes else "declared exclusions: " + proof.clean(", ".join(excludes), 250)
        return {
            "state": "changed" if changed else "clean", "path": "legacy/" + system, "target": "",
            "method": "by SHA-256, file modes and membership against the prepared-original snapshot (" + scope + ")",
            "detail": (str(len(changed)) + " included file(s) differ from the prepared original") if changed else (
                str(len(expected)) + " included files match the prepared original"),
            "files": changed[:proof.EXAMPLES],
            "snapshot": {"path": str(path), "sha256": baseline.digest(raw),
                         "startedAt": before["startedAt"], "completedAt": before["completedAt"],
                         "treeSha256": before["treeSha256"], "excludes": excludes},
            "limitations": [
                "Identity is checked only within the declared snapshot scope; exclusions require review.",
                "The snapshot and timestamps are unauthenticated and do not prove capture preceded implementation.",
                "Current equality does not establish earlier execution, behavior coverage or an environment match.",
            ],
        }

    proof.source_check = source_check
    proof.RULES_TEXT = tuple((
        "6. Source identity: the prepared original's current file hashes, modes and membership match "
        "the supplied source snapshot within its declared exclusions. The snapshot and timestamps "
        "are unauthenticated; capture before implementation and the adequacy of exclusions require review."
    ) if rule.startswith("6. Source untouched:") else rule for rule in original_rules)

    def restore():
        proof.source_check = original
        proof.RULES_TEXT = original_rules
    return restore


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "proof additionally accepts --source-snapshot PATH to check the prepared original's "
        "file identity using a saved baseline_evidence.py snapshot."))
    parser.add_argument("tool", choices=TOOLS, help="follow with the original tool's arguments; TOOL --help lists them")
    if not arguments or arguments[0] in ("-h", "--help"):
        parser.print_help()
        return 0 if arguments else 2
    selected = parser.parse_args(arguments[:1]).tool
    previous_path = sys.path[:]
    previous_bytecode = sys.dont_write_bytecode
    restorers = []
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "upstream/scripts"))
    try:
        if selected in ("trace", "proof"):
            restorers.append(preserve_rule_ids(importlib.import_module("trace_rules")))
        tool = importlib.import_module(TOOLS[selected])
        remaining = arguments[1:]
        if selected == "proof":
            options = argparse.ArgumentParser(add_help=False)
            options.add_argument("--source-snapshot", type=Path)
            extra, remaining = options.parse_known_args(remaining)
            if extra.source_snapshot is not None:
                restorers.append(use_source_snapshot(tool, extra.source_snapshot))
            if any(arg in ("-h", "--help") for arg in remaining):
                print("Adapter option: --source-snapshot PATH checks a saved prepared-original file snapshot.\n")
        return tool.main(remaining)
    except (OSError, ValueError, ImportError) as error:
        print("upstream_checks: " + str(error), file=sys.stderr)
        return 2
    finally:
        for restore in reversed(restorers):
            restore()
        sys.path[:] = previous_path
        sys.dont_write_bytecode = previous_bytecode


if __name__ == "__main__":
    raise SystemExit(main())
