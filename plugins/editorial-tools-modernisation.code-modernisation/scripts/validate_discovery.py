#!/usr/bin/env python3
"""Validate discovery artifacts against current source without executing it.

Exit 0 means the implemented checks found no errors; warnings can still identify
unverified evidence. Exit 1 means validation errors; exit 2 means unreadable or
invalid inputs. This is not behavioral verification, test execution, or approval.
Only bundled inventory code is imported. JSON output never includes source text
or values copied from the supplied artifacts.
"""

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys


sys.dont_write_bytecode = True
CORE_FIELDS = (
    "source", "files", "shards", "skipped", "selectedFiles", "totalFiles", "scopeDigest",
)
HASH = re.compile(r"[0-9a-f]{64}\Z")
RULE_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
STALE_DIGEST = re.compile(
    r"\s*(?:(?:inventory\s+)?digest\s+(?:is\s+)?"
    r"(?:unavailable|missing|unknown|not available|null)\b|"
    r"scopeDigest\s*(?:is|:|=)\s*null\b)", re.IGNORECASE,
)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def integer(value):
    return type(value) is int and value >= 0


def safe_relative(value):
    """Require canonical POSIX paths, including on hosts that accept backslashes."""
    return (
        nonempty(value)
        and not any(ord(char) < 32 for char in value)
        and "\\" not in value
        and not re.match(r"[A-Za-z]:", value)
        and not PurePosixPath(value).is_absolute()
        and all(part not in ("", ".", "..") for part in value.split("/"))
        and PurePosixPath(value).as_posix() == value
    )


def json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON keys")
        result[key] = value
    return result


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("nonfinite JSON number")
    return result


def invalid_constant(_value):
    raise ValueError("nonfinite JSON constant")


class Validation:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.input_failed = False
        self.counts = {"candidateRules": 0, "requestedRules": 0,
                       "exactCitations": 0, "redactedCitationsUnverified": 0}

    def error(self, code, location, message):
        self.errors.append({"code": code, "location": location, "message": message})

    def warning(self, code, location, message):
        self.warnings.append({"code": code, "location": location, "message": message})

    def load(self, path, label):
        try:
            data = json.loads(
                Path(path).read_text(encoding="utf-8"), object_pairs_hook=json_object,
                parse_float=finite_float, parse_constant=invalid_constant,
            )
        except (OSError, ValueError, RecursionError):
            self.input_failed = True
            self.error("input.invalid_json", label,
                       "Cannot read a valid UTF-8 JSON object; duplicate keys and nonfinite numbers are forbidden.")
            return None
        if not isinstance(data, dict):
            self.input_failed = True
            self.error("input.not_object", label, "The artifact must be a JSON object.")
            return None
        return data

    def require(self, condition, location, message, code="schema.invalid"):
        if not condition:
            self.error(code, location, message)
        return condition

    def string_list(self, value, location):
        return self.require(isinstance(value, list) and all(nonempty(item) for item in value),
                            location, "Expected an array of nonempty strings.")

    def result(self):
        return {
            "checksPassed": not self.errors,
            "counts": self.counts,
            "errors": self.errors,
            "warnings": self.warnings,
            "limits": [
                "Checks cover artifact structure, current inventory, citation bytes, and optional rule-ID retention only.",
                "Requested-rule citations are legacy context, not evidence that requested behavior exists.",
                "Redacted citations remain unverified even when checksPassed is true; warnings require review.",
                "No behavioral correctness, complete coverage, runtime results, approval, semantic ID continuity, or secret scanning is certified.",
                "Source is read without execution or writes; these checks do not create an atomic source snapshot.",
            ],
        }


def inventory_schema(data, report):
    report.require(nonempty(data.get("source")), "inventory.source", "Expected a source path.")
    report.require(isinstance(data.get("scopeDigest"), str) and bool(HASH.fullmatch(data["scopeDigest"])),
                   "inventory.scopeDigest", "Expected a lowercase SHA-256 digest.")
    for field in ("selectedFiles", "totalFiles"):
        report.require(integer(data.get(field)), "inventory." + field, "Expected a nonnegative integer.")
    files = data.get("files")
    paths = []
    if report.require(isinstance(files, list), "inventory.files", "Expected an array of file records."):
        for index, record in enumerate(files):
            location = "inventory.files[%d]" % index
            if not report.require(isinstance(record, dict), location, "Expected a file object."):
                continue
            path = record.get("path")
            if report.require(safe_relative(path), location + ".path", "Expected a canonical source-relative path."):
                paths.append(path)
            report.require(isinstance(record.get("sha256"), str) and bool(HASH.fullmatch(record["sha256"])),
                           location + ".sha256", "Expected a lowercase SHA-256 digest.")
            report.require(integer(record.get("loc")), location + ".loc", "Expected a nonnegative line count.")
        report.require(len(paths) == len(set(paths)), "inventory.files", "File paths must be unique.")
        if integer(data.get("selectedFiles")):
            report.require(data["selectedFiles"] == len(files), "inventory.selectedFiles",
                           "Selected file count must equal the file record count.")
    if integer(data.get("selectedFiles")) and integer(data.get("totalFiles")):
        report.require(data["selectedFiles"] <= data["totalFiles"], "inventory.totalFiles",
                       "Total files must not be less than selected files.")
    skipped = data.get("skipped")
    report.require(isinstance(skipped, dict) and all(integer(value) for value in skipped.values()),
                   "inventory.skipped", "Expected an object of nonnegative exclusion counts.")
    shards = data.get("shards")
    shard_paths = []
    if report.require(isinstance(shards, list), "inventory.shards", "Expected an array of shards."):
        for index, shard in enumerate(shards):
            location = "inventory.shards[%d]" % index
            if not report.require(isinstance(shard, dict), location, "Expected a shard object."):
                continue
            report.require(nonempty(shard.get("name")), location + ".name", "Expected a nonempty string.")
            report.require(integer(shard.get("loc")), location + ".loc", "Expected a nonnegative line count.")
            shard_files = shard.get("files")
            valid_files = report.require(isinstance(shard_files, list) and all(safe_relative(path) for path in shard_files),
                                         location + ".files", "Expected an array of canonical source-relative paths.")
            if valid_files:
                shard_paths.extend(shard_files)
            # The bundled tree sharder uses dirname(relative_path), which is empty
            # for root files. Preserve that native representation only for such shards.
            root_files = valid_files and bool(shard_files) and all("/" not in path for path in shard_files)
            report.require(nonempty(shard.get("domain")) or (shard.get("domain") == "" and root_files),
                           location + ".domain", "Expected a nonempty domain, or an empty domain for root-file shards.")
        report.require(sorted(shard_paths) == sorted(paths), "inventory.shards",
                       "Shard file membership must match the inventory exactly.")


def load_inventory(source, module, include_tests):
    script = Path(__file__).resolve().with_name("inventory.py")
    spec = importlib.util.spec_from_file_location("modernisation_inventory_validator", script)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper.inventory(source, module, include_tests)


def rule_ids(data, label, report):
    rules = data.get("rules")
    if not report.require(isinstance(rules, list), label + ".rules", "Expected an array of rules."):
        return None
    ids = set()
    for index, rule in enumerate(rules):
        location = "%s.rules[%d]" % (label, index)
        if not report.require(isinstance(rule, dict), location, "Expected a rule object."):
            continue
        value = rule.get("id")
        if report.require(isinstance(value, str) and bool(RULE_ID.fullmatch(value)), location + ".id",
                          "Expected a 1–64 character identifier beginning with a letter, using letters, digits, '-' or '_'."):
            report.require(value not in ids, location + ".id", "Rule IDs must be unique.", "rules.duplicate_id")
            ids.add(value)
    return ids


def read_citation_source(source, relative, file_record):
    path = source
    for part in PurePosixPath(relative).parts:
        path /= part
        if path.is_symlink():
            raise ValueError("symbolic link")
    resolved = path.resolve(strict=True)
    if source not in resolved.parents or not resolved.is_file():
        raise ValueError("outside source")
    before = resolved.stat()
    data = resolved.read_bytes()
    after = resolved.stat()
    identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    if identity(before) != identity(after) or hashlib.sha256(data).hexdigest() != file_record["sha256"]:
        raise ValueError("source changed")
    # Match the inventory's physical LF line count. splitlines() also treats
    # form feeds and Unicode separators inside source strings as line breaks.
    text = data.decode("utf-8")
    pieces = text.split("\n")
    return [part + "\n" for part in pieces[:-1]] + ([pieces[-1]] if pieces[-1] else [])


def check_citation(evidence, location, actual, cache, report):
    if not report.require(isinstance(evidence, dict), location, "Expected an evidence object."):
        return
    relative = evidence.get("path")
    if not report.require(safe_relative(relative), location + ".path",
                          "Expected a canonical source-relative path.", "citation.unsafe_path"):
        return
    if actual is None:
        return  # The source/inventory error already explains why byte checks cannot run.
    records = {record["path"]: record for record in actual["files"]}
    if not report.require(relative in records, location + ".path", "Citation must refer to an inventoried file.",
                          "citation.out_of_scope"):
        return
    start, end = evidence.get("startLine"), evidence.get("endLine")
    if not report.require(type(start) is int and type(end) is int and 1 <= start <= end,
                          location, "Expected an inclusive positive integer line range.", "citation.invalid_range"):
        return
    excerpt = evidence.get("excerpt")
    if not report.require(nonempty(excerpt), location + ".excerpt", "Expected a nonempty literal source excerpt."):
        return
    if relative not in cache:
        try:
            cache[relative] = read_citation_source(Path(actual["source"]), relative, records[relative])
        except (OSError, ValueError):
            cache[relative] = None
    lines = cache[relative]
    if lines is None:
        report.error("citation.source_unreadable_or_changed", location,
                     "Cannot read unchanged UTF-8 source through a regular in-scope path.")
        return
    if not report.require(end <= len(lines), location, "Citation range exceeds the current file length.",
                          "citation.invalid_range"):
        return
    if "<redacted>" in excerpt:
        report.counts["redactedCitationsUnverified"] += 1
        report.warning("citation.redacted_unverified", location,
                       "The citation contains <redacted>; its excerpt was not certified as an exact source match.")
    elif report.require(excerpt in "".join(lines[start - 1:end]), location + ".excerpt",
                        "Excerpt does not occur exactly within the cited lines; source content is not printed.",
                        "citation.excerpt_mismatch"):
        report.counts["exactCitations"] += 1


def rules_schema(data, actual, report):
    digest = data.get("scopeDigest")
    report.require(isinstance(digest, str) and bool(HASH.fullmatch(digest)), "rules.scopeDigest",
                   "Expected the current lowercase SHA-256 inventory digest.")
    if actual is not None:
        report.require(digest == actual["scopeDigest"], "rules.scopeDigest",
                       "Rule scope digest differs from the current inventory.", "rules.stale_digest")
    file_fields = ("inspectedFiles", "uninspectedFiles", "outOfSelectionDependencies")
    for field in (*file_fields, "limitations", "questions", "sourceWarnings"):
        if not report.string_list(data.get(field), "rules." + field):
            continue
        if field in file_fields:
            for index, value in enumerate(data[field]):
                report.require(safe_relative(value), "rules.%s[%d]" % (field, index),
                               "Expected a canonical source-relative path.")
    limits = data.get("limitations")
    if isinstance(digest, str) and HASH.fullmatch(digest) and isinstance(limits, list):
        for index, value in enumerate(limits):
            if isinstance(value, str) and STALE_DIGEST.match(value):
                report.warning("metadata.possibly_stale_digest_limitation", "rules.limitations[%d]" % index,
                               "Heuristic: a limitation starts with an unavailable/null digest claim while a digest is present; review its wording.")
    cache = {}
    if not isinstance(data.get("rules"), list):
        return
    for index, rule in enumerate(data["rules"]):
        location = "rules.rules[%d]" % index
        if not isinstance(rule, dict):
            continue  # rule_ids reports the invalid rule object.
        for field in ("title", "category", "observedBehavior", "given", "when", "then"):
            report.require(nonempty(rule.get(field)), location + "." + field, "Expected a nonempty string.")
        report.require(isinstance(rule.get("parameters"), dict), location + ".parameters", "Expected an object.")
        report.string_list(rule.get("questions"), location + ".questions")
        report.require(rule.get("confidence") in ("high", "medium", "low"), location + ".confidence",
                       "Expected high, medium, or low confidence.")
        status = rule.get("status")
        if report.require(status in ("candidate", "requested"), location + ".status",
                          "Expected candidate or requested; verification and acceptance are not rule statuses here."):
            report.counts["candidateRules" if status == "candidate" else "requestedRules"] += 1
        change = rule.get("requestedChange")
        report.require("requestedChange" in rule and (change is None or nonempty(change)), location + ".requestedChange",
                       "Expected null or a nonempty requested-change statement separate from legacy behavior.")
        if status == "requested":
            report.require(nonempty(change), location + ".requestedChange",
                           "A requested rule must carry a separate requestedChange statement.", "rules.missing_requested_change")
        evidence = rule.get("evidence")
        if report.require(isinstance(evidence, list), location + ".evidence", "Expected an array of evidence records."):
            if status == "candidate":
                report.require(bool(evidence), location + ".evidence", "A legacy candidate requires source evidence.")
            elif status == "requested" and not evidence:
                report.warning("rules.requested_without_legacy_context", location + ".evidence",
                               "Requested behavior has no legacy source context; it is not an observed behavior.")
            for number, citation in enumerate(evidence):
                check_citation(citation, location + ".evidence[%d]" % number, actual, cache, report)


def validate(source, inventory_path, rules_path, *, module="", include_tests=False, previous_rules_path=None):
    report = Validation()
    saved = report.load(inventory_path, "inventory")
    rules = report.load(rules_path, "rules")
    previous = report.load(previous_rules_path, "previousRules") if previous_rules_path is not None else None
    try:
        actual = load_inventory(source, module, include_tests)
    except (OSError, ValueError, RuntimeError, ImportError):
        actual = None
        report.input_failed = True
        report.error("source.inventory_unavailable", "source",
                     "Cannot generate the selected source inventory; check source, module selection, and permissions.")
    if saved is not None:
        inventory_schema(saved, report)
        if actual is not None:
            for field in CORE_FIELDS:
                if field not in saved or saved[field] != actual[field]:
                    report.error("inventory.current_mismatch", "inventory." + field,
                                 "Saved inventory differs from the current selection; regenerate and review affected findings.")
    if rules is not None:
        current_ids = rule_ids(rules, "rules", report)
        rules_schema(rules, actual, report)
        if previous is not None:
            previous_ids = rule_ids(previous, "previousRules", report)
            if current_ids is not None and previous_ids is not None:
                report.require(previous_ids <= current_ids, "rules.rules",
                               "Previously recorded rule IDs are missing; preserve or explicitly reconcile prior findings.",
                               "rules.previous_ids_missing")
    return report.result(), 2 if report.input_failed else (1 if report.errors else 0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Read-only project source directory.")
    parser.add_argument("--inventory", required=True, help="Saved inventory JSON.")
    parser.add_argument("--rules", required=True, help="Saved rule candidates JSON.")
    parser.add_argument("--module", default="", help="Use the same module selector as the saved inventory.")
    parser.add_argument("--include-tests", action="store_true", help="Use when the saved inventory included test directories.")
    parser.add_argument("--previous-rules", help="Optional prior rules JSON for rule-ID retention checks.")
    args = parser.parse_args(argv)
    result, status = validate(args.source, args.inventory, args.rules, module=args.module,
                              include_tests=args.include_tests, previous_rules_path=args.previous_rules)
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
