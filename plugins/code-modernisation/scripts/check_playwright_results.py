#!/usr/bin/env python3
"""Audit native Playwright JSON selection/execution reports without running tests.

Use JSON from `playwright test --list --reporter=json` as --selection and the
execution's JSON as --report. Supply the actual process exit code explicitly.
Exit 0 means these structural/result checks pass, 1 means they fail, and 2 means
an input cannot be read or parsed. Reports and exit codes are not authenticated.
"""

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys


sys.dont_write_bytecode = True
OUTCOMES = ("expected", "unexpected", "flaky", "skipped")
RESULT_STATUSES = ("passed", "failed", "timedOut", "skipped", "interrupted")


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def number(value):
    return (type(value) is int and value >= 0) or (type(value) is float and math.isfinite(value) and value >= 0)


def timestamp(value):
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("nonfinite JSON number")
    return result


def reject_constant(_value):
    raise ValueError("nonfinite JSON constant")


class Audit:
    def __init__(self):
        self.errors = []
        self.input_failed = False
        self.hashes = {"selection": None, "report": None}
        self.counts = {"selected": 0, "observed": 0, "executed": 0, "passed": 0, "skipped": 0}

    def require(self, condition, code, location, message):
        if not condition:
            self.errors.append({"code": code, "location": location, "message": message})
        return condition

    def load(self, path, label):
        try:
            raw = Path(path).read_bytes()
            self.hashes[label] = hashlib.sha256(raw).hexdigest()
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                              parse_float=finite_float, parse_constant=reject_constant)
            if not isinstance(data, dict):
                raise ValueError("not an object")
            return data
        except (OSError, ValueError, RecursionError):
            self.input_failed = True
            self.require(False, "input.invalid_json", label,
                         "Cannot read a UTF-8 JSON object; duplicate keys and nonfinite numbers are forbidden.")
            return None

    def annotations(self, annotations, location):
        if not self.require(isinstance(annotations, list), "schema.annotations", location,
                            "Expected an annotations array."):
            return
        for index, annotation in enumerate(annotations):
            target = "%s[%d]" % (location, index)
            if self.require(isinstance(annotation, dict) and isinstance(annotation.get("type"), str),
                            "schema.annotation", target, "Expected an annotation with a string type."):
                self.require(annotation["type"] not in ("skip", "fixme", "fail"),
                             "test.excluded_or_expected_failure", target,
                             "Skip, fixme, and expected-failure annotations cannot satisfy this audit.")

    def steps(self, steps, location):
        if not self.require(isinstance(steps, list), "schema.steps", location, "Expected a steps array."):
            return
        pending = [(step, "%s[%d]" % (location, index)) for index, step in enumerate(steps)]
        while pending:
            step, target = pending.pop()
            if not self.require(isinstance(step, dict), "schema.step", target, "Expected a step object."):
                continue
            self.require(isinstance(step.get("title"), str) and number(step.get("duration")),
                         "schema.step", target, "Expected a string title and nonnegative duration.")
            self.require(step.get("error") is None, "result.step_error", target,
                         "A reported step error prevents a clean result; error payload is not printed.")
            if "steps" in step:
                children = step["steps"]
                if self.require(isinstance(children, list), "schema.steps", target + ".steps", "Expected a steps array."):
                    pending.extend((child, "%s.steps[%d]" % (target, index)) for index, child in enumerate(children))

    def execution_result(self, result, location):
        if not self.require(isinstance(result, dict), "schema.result", location, "Expected a result object."):
            return
        self.require(result.get("status") == "passed", "result.not_passed", location + ".status",
                     "Every execution result must have passed.")
        self.require(type(result.get("retry")) is int and result["retry"] == 0,
                     "result.retried", location + ".retry", "Only the initial attempt (retry 0) is accepted.")
        self.require(result.get("errors") == [], "result.errors", location + ".errors",
                     "Expected an empty errors array; error payloads are not printed.")
        self.require(result.get("error") is None, "result.error", location + ".error",
                     "A reported error prevents a clean result; its payload is not printed.")
        for field in ("workerIndex", "parallelIndex"):
            self.require(integer(result.get(field)), "schema.result", location + "." + field,
                         "Expected a nonnegative integer execution index.")
        self.require(number(result.get("duration")) and timestamp(result.get("startTime")),
                     "schema.result", location, "Expected a nonnegative duration and a timestamp with timezone.")
        for field in ("stdout", "stderr", "attachments"):
            self.require(isinstance(result.get(field), list), "schema.result", location + "." + field,
                         "Expected an array; its contents are not copied to audit output.")
        self.annotations(result.get("annotations"), location + ".annotations")
        if "steps" in result:
            self.steps(result["steps"], location + ".steps")

    def projects(self, config, label):
        projects = {}
        if not self.require(isinstance(config, dict) and isinstance(config.get("projects"), list),
                            "schema.projects", label + ".config.projects", "Expected a native projects array."):
            return projects
        for index, project in enumerate(config["projects"]):
            location = "%s.config.projects[%d]" % (label, index)
            if not self.require(isinstance(project, dict) and isinstance(project.get("id"), str)
                                and isinstance(project.get("name"), str), "schema.project", location,
                                "Expected string project id and name; the default project's empty strings are valid."):
                continue
            self.require(project["id"] not in projects, "identity.duplicate_project", location,
                         "Project identifiers must be unique.")
            projects[project["id"]] = project["name"]
            self.require(integer(project.get("repeatEach"), 1) and integer(project.get("retries")),
                         "schema.project", location, "Expected positive repeatEach and nonnegative retries integers.")
        return projects

    def read_report(self, data, label):
        selection = label == "selection"
        cases, outcomes = {}, Counter()
        projects = self.projects(data.get("config"), label)
        self.require(data.get("errors") == [], "report.global_errors", label + ".errors",
                     "Expected an empty global errors array; error payloads are not printed.")
        suites = data.get("suites")
        if not self.require(isinstance(suites, list), "schema.suites", label + ".suites", "Expected a native suites array."):
            return cases
        pending = [(suite, "%s.suites[%d]" % (label, index)) for index, suite in enumerate(suites)]
        case_count = 0
        while pending:
            suite, location = pending.pop()
            if not self.require(isinstance(suite, dict), "schema.suite", location, "Expected a suite object."):
                continue
            for field in ("title", "file"):
                self.require(isinstance(suite.get(field), str), "schema.suite", location + "." + field,
                             "Expected a string suite location/title.")
            for field in ("line", "column"):
                self.require(integer(suite.get(field)), "schema.suite", location + "." + field,
                             "Expected a nonnegative integer source coordinate.")
            children = suite.get("suites", [])
            if self.require(isinstance(children, list), "schema.suites", location + ".suites", "Expected a suites array."):
                pending.extend((child, "%s.suites[%d]" % (location, index)) for index, child in enumerate(children))
            specs = suite.get("specs")
            if not self.require(isinstance(specs, list), "schema.specs", location + ".specs", "Expected a native specs array."):
                continue
            for index, spec in enumerate(specs):
                target = "%s.specs[%d]" % (location, index)
                if not self.require(isinstance(spec, dict), "schema.spec", target, "Expected a spec object."):
                    continue
                valid_id = self.require(isinstance(spec.get("id"), str) and bool(spec["id"]),
                                        "schema.spec_id", target + ".id", "Expected a nonempty native spec identifier.")
                for field in ("file", "title"):
                    self.require(isinstance(spec.get(field), str), "schema.spec", target + "." + field,
                                 "Expected string spec location/title context.")
                for field in ("line", "column"):
                    self.require(integer(spec.get(field)), "schema.spec", target + "." + field,
                                 "Expected a nonnegative integer source coordinate.")
                self.require(spec.get("ok") is True, "spec.not_ok", target + ".ok", "The native spec must report ok=true.")
                tests = spec.get("tests")
                if not self.require(isinstance(tests, list) and bool(tests), "schema.tests", target + ".tests",
                                    "Expected a nonempty array of native test cases."):
                    continue
                for test_index, test in enumerate(tests):
                    case_count += 1
                    where = "%s.tests[%d]" % (target, test_index)
                    before = len(self.errors)
                    if not self.require(isinstance(test, dict), "schema.test", where, "Expected a native test case object."):
                        continue
                    valid_project = self.require(isinstance(test.get("projectId"), str)
                                                 and isinstance(test.get("projectName"), str),
                                                 "schema.test_project", where, "Expected string projectId and projectName.")
                    if valid_project:
                        self.require(test["projectId"] in projects and projects[test["projectId"]] == test["projectName"],
                                     "identity.unknown_project", where, "Test project identity must match the report configuration.")
                    if valid_id and valid_project:
                        key = (spec["id"], test["projectId"], test["projectName"])
                        self.require(key not in cases, "identity.duplicate_case", where,
                                     "Selected and observed test identities must each be unique.")
                        cases[key] = tuple(spec.get(field) for field in ("file", "title", "line", "column"))
                    status = test.get("status")
                    if self.require(status in OUTCOMES, "schema.outcome", where + ".status", "Expected a native test outcome."):
                        outcomes[status] += 1
                    self.require(test.get("expectedStatus") == "passed", "test.not_expected_pass", where + ".expectedStatus",
                                 "Every selected and observed test must expect a pass, not a skip or expected failure.")
                    self.require(number(test.get("timeout")), "schema.timeout", where + ".timeout", "Expected a nonnegative timeout.")
                    self.annotations(test.get("annotations"), where + ".annotations")
                    results = test.get("results")
                    if not self.require(isinstance(results, list), "schema.results", where + ".results", "Expected a native results array."):
                        continue
                    if selection:
                        self.require(status == "skipped" and not results, "selection.not_list_report", where,
                                     "A --list selection has skipped outcome placeholders and no execution results.")
                    else:
                        statuses = [result.get("status") for result in results if isinstance(result, dict)]
                        if any(value in RESULT_STATUSES and value != "skipped" for value in statuses):
                            self.counts["executed"] += 1
                        if status == "skipped" or "skipped" in statuses:
                            self.counts["skipped"] += 1
                        self.require(status == "expected", "test.not_clean", where + ".status",
                                     "Observed tests must have expected outcome; skips, failures, and flaky outcomes fail this audit.")
                        self.require(len(results) == 1, "test.attempt_count", where + ".results",
                                     "Every observed test must contain exactly one execution attempt.")
                        for result_index, result in enumerate(results):
                            self.execution_result(result, "%s.results[%d]" % (where, result_index))
                        if len(self.errors) == before and spec.get("ok") is True:
                            self.counts["passed"] += 1
        self.counts["selected" if selection else "observed"] = case_count
        self.require(case_count > 0, "report.zero_cases", label + ".suites", "At least one test case is required.")
        stats = data.get("stats")
        if self.require(isinstance(stats, dict), "schema.stats", label + ".stats", "Expected native report statistics."):
            self.require(number(stats.get("duration")) and timestamp(stats.get("startTime")),
                         "schema.stats", label + ".stats", "Expected a nonnegative duration and a timestamp with timezone.")
            for outcome in OUTCOMES:
                self.require(integer(stats.get(outcome)) and stats[outcome] == outcomes[outcome],
                             "report.counter_mismatch", label + ".stats." + outcome,
                             "Each nonnegative integer counter must match the observed native test outcomes.")
            self.require(sum(outcomes.values()) == case_count, "report.counter_mismatch", label + ".stats",
                         "Every test case must contribute exactly one known native outcome.")
        return cases

    def result(self):
        return {
            "checksPassed": not self.errors,
            "counts": self.counts,
            "inputSha256": self.hashes,
            "errors": self.errors,
            "limits": [
                "Reports and the supplied runner exit code are unauthenticated; hashes identify input bytes only.",
                "Counts and identities concern the supplied selection, not complete application or behavioral coverage.",
                "This read-only audit verifies report consistency and one clean passing attempt per selected case.",
                "It does not establish source, environment, or Playwright BDD provenance; human acceptance; or a modernization gate.",
            ],
        }


def check(selection_path, report_path, runner_exit_code):
    audit = Audit()
    selection = audit.load(selection_path, "selection")
    report = audit.load(report_path, "report")
    audit.require(type(runner_exit_code) is int and runner_exit_code == 0,
                  "runner.nonzero_exit", "runnerExitCode", "The actual test runner must have exited successfully.")
    selected = audit.read_report(selection, "selection") if selection is not None else None
    observed = audit.read_report(report, "report") if report is not None else None
    if selected is not None and observed is not None:
        audit.require(selected.keys() == observed.keys(), "identity.selection_mismatch", "report.suites",
                      "Observed identities must match the selection exactly; missing and additional cases are rejected.")
        for key in selected.keys() & observed.keys():
            audit.require(selected[key] == observed[key], "identity.context_mismatch", "report.suites",
                          "The selected case's file, title, and source coordinates must match its execution context.")
    return audit.result(), 2 if audit.input_failed else (1 if audit.errors else 0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True, help="Native Playwright --list --reporter=json output.")
    parser.add_argument("--report", required=True, help="Native Playwright execution JSON report.")
    parser.add_argument("--runner-exit-code", type=int, required=True, help="Actual execution process exit code.")
    args = parser.parse_args(argv)
    result, status = check(args.selection, args.report, args.runner_exit_code)
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
