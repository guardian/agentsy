#!/usr/bin/env python3
"""Compare a retained Playwright BDD cohort across legacy and candidate evidence.

Read-only: inspect captured receipts, current trees/environment observations, an
untouched candidate-origin snapshot and an explicit scenario mapping. No source,
test, browser, shell or model code is executed. Exit 0 means the supplied technical
checks pass, 1 means an evidence/coverage check fails, 2 malformed/unreadable input.
This does not prove semantic preservation, human acceptance or upstream PROVEN.
"""

import argparse
from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_SPEC = importlib.util.spec_from_file_location(
    "candidate_baseline_evidence", Path(__file__).with_name("baseline_evidence.py"))
BASELINE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(BASELINE)

LIMITS = [
    "Hashes bind supplied bytes; evidence, timestamps, observations and declared scenario mappings are unauthenticated.",
    "A complete case mapping does not prove that expectations, assertions, selectors or fixtures retain their meaning; review them independently.",
    "This compares only the selected preserved-behavior cohort; additional or deliberately changed behavior requires separate evidence and decisions.",
    "Each run is checked against its own source and declared environment; cross-run environment equivalence is not established.",
    "Origin matching and chronology check supplied snapshots, not an authenticated record of copying or a write lock.",
    "A technical pass is not full behavioral equivalence, business approval, final acceptance, or upstream PROVEN.",
    "Files and environment may change after this read-only check; recheck affected evidence on continuation.",
]


class Audit:
    def __init__(self):
        self.errors = []
        self.invalid = False
        self.hashes = {}
        self.refs = []
        self.runs = {}
        self.mapped = []
        self.trees = {}
        self.declared_limits = {}

    def issue(self, code, location, message):
        self.errors.append({"code": code, "location": location, "message": message})

    def expect(self, condition, code, location, message):
        if not condition:
            self.issue(code, location, message)
        return condition

    def read(self, path, label):
        path = Path(path).absolute()
        BASELINE.no_symlinks(path)
        path = path.parent.resolve(strict=True) / path.name
        raw, _ = BASELINE.stable_read(path)
        value = BASELINE.digest(raw)
        self.hashes[label] = value
        self.refs.append((path, value))
        return raw

    def reference(self, directory, reference, label):
        BASELINE.keys(reference, ("path", "sha256"))
        BASELINE.relative(reference["path"])
        valid_hash(reference["sha256"])
        raw = self.read(directory / reference["path"], label)
        self.expect(self.hashes[label] == reference["sha256"], "reference.changed", label,
                    "Referenced evidence no longer matches its recorded digest.")
        return raw

    def result(self, max_environment_age_seconds):
        result = {
            "schemaVersion": 1, "checksPassed": not self.errors,
            "runs": self.runs, "mappedCases": self.mapped,
            "treeIdentities": self.trees, "inputSha256": self.hashes,
            "declaredLimitations": self.declared_limits,
            "maxEnvironmentAgeSeconds": max_environment_age_seconds,
            "errors": self.errors, "limits": LIMITS,
        }
        return result, 2 if self.invalid else (1 if self.errors else 0)


def valid_hash(value):
    BASELINE.require(isinstance(value, str) and BASELINE.HASH.fullmatch(value), "Expected a lowercase SHA-256 digest.")


def native_identity(value):
    BASELINE.keys(value, ("specId", "projectId", "projectName"))
    BASELINE.require(isinstance(value["specId"], str) and value["specId"].strip()
                     and isinstance(value["projectId"], str) and isinstance(value["projectName"], str),
                     "Expected a nonempty spec identifier and string project identifier/name.")
    return value["specId"], value["projectId"], value["projectName"]


def contract_schema(value):
    BASELINE.keys(value, ("schemaVersion", "kind", "bindings", "cases", "limitations"))
    BASELINE.require(type(value["schemaVersion"]) is int and value["schemaVersion"] == 1
                     and value["kind"] == "preserved-behavior-contract", "Unsupported contract version or kind.")
    BASELINE.keys(value["bindings"], ("legacyReceiptSha256", "candidateOriginSha256", "briefSha256"))
    for digest in value["bindings"].values():
        valid_hash(digest)
    BASELINE.strings(value["limitations"])
    BASELINE.require(isinstance(value["cases"], list) and value["cases"], "Contract cases must be a nonempty array.")
    for case in value["cases"]:
        BASELINE.keys(case, ("id", "expectation", "legacy", "candidate", "adaptation"))
        for field in ("id", "expectation", "adaptation"):
            BASELINE.require(isinstance(case[field], str) and case[field].strip(), "Contract text fields must be nonempty strings.")
        native_identity(case["legacy"])
        native_identity(case["candidate"])


def capture_run(audit, label, path, root, environment, max_age):
    """Reuse the complete per-run audit and retain its exact input identities."""
    path = Path(path).absolute()
    raw = audit.read(path, label)
    receipt = BASELINE.parse(raw)
    result, status = BASELINE.check(path, root, environment, max_age)
    audit.runs[label] = {key: result[key] for key in ("checksPassed", "checks", "counts", "inputSha256")}
    audit.invalid |= status == 2
    for error in result["errors"]:
        audit.issue(label + "." + error["code"], label + "." + error["location"], error["message"])
    audit.expect(result["inputSha256"].get("baseline") == BASELINE.digest(raw), "reference.raced", label,
                 "The run checker must use the same receipt bytes as this comparison.")
    if status != 0:
        return None
    audit.expect(receipt["provenance"]["kind"] == "captured", "run.not_captured", label,
                 "Both runs require a complete captured evidence chain.")
    for field in ("selection", "report", "runner", "beforeSnapshot", "afterSnapshot"):
        reference = receipt["execution"][field]
        reference_raw = audit.reference(path.parent, reference, label + "." + field)
        audit.expect(result["inputSha256"].get("execution." + field) == BASELINE.digest(reference_raw),
                     "reference.raced", label + "." + field, "The run checker and comparison must use identical evidence bytes.")
        if field == "selection":
            selection = BASELINE.parse(reference_raw)
    stored_raw = audit.reference(path.parent, receipt["environment"]["record"], label + ".storedEnvironment")
    for index, reference in enumerate(receipt["provenance"]["references"]):
        audit.reference(path.parent, reference, "%s.provenance[%d]" % (label, index))
    current_raw = audit.read(environment, label + ".currentEnvironment")
    audit.expect(result["inputSha256"].get("currentEnvironment") == BASELINE.digest(current_raw), "reference.raced",
                 label + ".currentEnvironment", "The run checker and comparison must use the same current environment observation.")
    cases_audit = BASELINE.PLAYWRIGHT.Audit()
    cases = cases_audit.read_report(selection, "selection")
    BASELINE.require(not cases_audit.errors, "The checked native selection must remain valid.")
    audit.trees[label] = receipt["snapshot"]["treeSha256"]
    current_environment = BASELINE.parse(current_raw)
    audit.declared_limits[label] = {"receipt": receipt["limitations"],
                                    "recordedEnvironment": BASELINE.parse(stored_raw)["limitations"],
                                    "currentEnvironment": current_environment["limitations"]}
    return {"receipt": receipt, "cases": cases, "root": BASELINE.physical_root(root),
            "environment": current_environment}


def compare(contract, brief, legacy, legacy_root, legacy_environment,
            candidate, candidate_root, candidate_environment, origin, max_environment_age_seconds=300):
    audit = Audit()
    try:
        BASELINE.require(type(max_environment_age_seconds) is int and max_environment_age_seconds > 0,
                         "Environment age bound must be a positive integer.")
        contract_data = BASELINE.parse(audit.read(contract, "contract"))
        contract_schema(contract_data)
        audit.declared_limits["contract"] = contract_data["limitations"]
        brief_raw = audit.read(brief, "brief")
        BASELINE.require(bool(brief_raw.decode("utf-8").strip()), "The modernization brief must contain UTF-8 text.")
        origin_data = BASELINE.parse(audit.read(origin, "origin"))
        BASELINE.snapshot_schema(origin_data)
        audit.trees["candidateOrigin"] = origin_data["treeSha256"]
        runs = {}
        for label, path, root, environment in (("legacy", legacy, legacy_root, legacy_environment),
                                                ("candidate", candidate, candidate_root, candidate_environment)):
            runs[label] = capture_run(audit, label, path, root, environment, max_environment_age_seconds)
        for binding, label in (("legacyReceiptSha256", "legacy"), ("candidateOriginSha256", "origin"), ("briefSha256", "brief")):
            audit.expect(contract_data["bindings"][binding] == audit.hashes[label], "contract.binding_changed", "bindings." + binding,
                         "A contract-bound input differs from the retained digest; inspect the affected contract and evidence.")
        if all(runs.values()):
            old, new = runs["legacy"], runs["candidate"]
            old_snapshot, new_snapshot = old["receipt"]["snapshot"], new["receipt"]["snapshot"]
            audit.expect(old["root"] != new["root"] and old["root"] not in new["root"].parents
                         and new["root"] not in old["root"].parents, "origin.overlapping_roots", "origin.root",
                         "Legacy and candidate must have distinct, nonoverlapping physical source roots.")
            audit.expect(origin_data["root"] == str(new["root"]), "origin.root_mismatch", "origin.root",
                         "The untouched origin must name this candidate's physical source root.")
            audit.expect(origin_data["treeSha256"] == old_snapshot["treeSha256"], "origin.tree_mismatch", "origin.treeSha256",
                         "The untouched candidate must match the legacy snapshot's membership, bytes, modes and exclusion scope.")
            audit.expect(new_snapshot["excludes"] == origin_data["excludes"], "candidate.scope_changed", "candidate.snapshot.excludes",
                         "Retain the origin's explicit exclusion scope for this preservation comparison.")
            after_raw = audit.reference(Path(legacy).absolute().parent, old["receipt"]["execution"]["afterSnapshot"], "legacy.originChronology")
            old_after = BASELINE.parse(after_raw)
            audit.expect(BASELINE.moment(old_after["completedAt"]) <= BASELINE.moment(origin_data["startedAt"])
                         <= BASELINE.moment(origin_data["completedAt"]) <= BASELINE.moment(new_snapshot["startedAt"]),
                         "origin.chronology", "origin", "Origin capture must follow legacy completion and precede the candidate's before-run capture.")
            seen_ids, mapped = set(), {"legacy": set(), "candidate": set()}
            for index, case in enumerate(contract_data["cases"]):
                where = "cases[%d]" % index
                audit.expect(case["id"] not in seen_ids, "contract.duplicate_id", where + ".id", "Stable contract case identifiers must be unique.")
                seen_ids.add(case["id"])
                for label in ("legacy", "candidate"):
                    identity = native_identity(case[label])
                    audit.expect(identity not in mapped[label], "contract.duplicate_case", where + "." + label,
                                 "Every selected native case must be mapped exactly once on each side.")
                    mapped[label].add(identity)
                    audit.expect(identity in runs[label]["cases"], "contract.foreign_case", where + "." + label,
                                 "Mapped native identity is absent from that side's captured selection.")
                audit.mapped.append({key: case[key] for key in ("id", "legacy", "candidate")})
            for label in ("legacy", "candidate"):
                audit.expect(mapped[label] == set(runs[label]["cases"]), "contract.incomplete_coverage", label,
                             "The mapping must cover exactly every selected case on this side, including Examples rows and projects.")
            # The other run's check may take time. Reject source/environment drift
            # observed since each per-run audit rather than treating it as intended edits.
            for label, run in runs.items():
                current = BASELINE.snapshot(run["root"], run["receipt"]["snapshot"]["excludes"])
                audit.expect(current["treeSha256"] == audit.trees[label], "source.raced", label,
                             "Current source changed during the comparison; capture and verify the affected run again.")
                observed_at = BASELINE.moment(run["environment"]["observedAt"])
                now = BASELINE.utc_now()
                audit.expect(now - observed_at <= timedelta(seconds=max_environment_age_seconds)
                             and observed_at <= now + timedelta(seconds=5), "environment.expired", label,
                             "The current environment observation must remain fresh when comparison finishes.")
        for path, original_hash in audit.refs:
            raw, _ = BASELINE.stable_read(path)
            audit.expect(BASELINE.digest(raw) == original_hash, "reference.raced", "references", "Input evidence changed during comparison.")
    except (OSError, BASELINE.Invalid, UnicodeError, RecursionError, OverflowError) as error:
        audit.invalid = True
        audit.issue("input.invalid", "input", str(error) if isinstance(error, BASELINE.Invalid)
                    else "Cannot safely read the complete comparison evidence or source trees.")
    return audit.result(max_environment_age_seconds)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("contract", "brief", "legacy", "legacy-root", "legacy-environment", "candidate",
                 "candidate-root", "candidate-environment", "origin"):
        parser.add_argument("--" + flag, required=True)
    parser.add_argument("--max-environment-age-seconds", type=int, default=300,
                        help="Positive freshness window for both per-run observations; default 300 seconds.")
    args = parser.parse_args(argv)
    result, status = compare(**vars(args))
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
