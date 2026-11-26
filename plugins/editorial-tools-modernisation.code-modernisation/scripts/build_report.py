#!/usr/bin/env python3
"""Summarize saved modernization artifacts; optionally refresh REPORT.html.

Run directly: "/path/to/plugin/scripts/build_report.py" --analysis "/path/to/analysis/system"
Default: read-only JSON to stdout. --write-report additionally creates or refreshes
only that directory's generated REPORT.html. Never runs models, application code,
tests or validators. Saved outcomes are historical observations, not current
eligibility or acceptance. Exit 0 means the overview was collected, not tests passed;
exit 2 means the request or report write failed.
"""

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
from html import escape
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit


sys.dont_write_bytecode = True
TEMPLATE = Path(__file__).resolve().parents[1] / "assets/report/report.html"
RENDER_ASSETS = {
    "__PLUGIN_LICENSE__": TEMPLATE.parents[2] / "LICENSE",
    "__PLUGIN_NOTICE__": TEMPLATE.parents[2] / "NOTICE",
    "__MARKDOWN_PARSER__": TEMPLATE.parent / "vendor/markdown-it-15.0.3.umd.min.js",
    "__MARKDOWN_RENDERER__": TEMPLATE.parent / "markdown.js",
    "__DIAGRAM_RENDERER__": TEMPLATE.parent / "vendor/mermaid-11.17.2.min.js",
    "__DIAGRAM_UI__": TEMPLATE.parent / "diagrams.js",
    "__REPORT_LICENSES__": TEMPLATE.parent / "vendor/LICENSES.txt",
    "__DIAGRAM_LICENSE__": TEMPLATE.parent / "vendor/LICENSE-mermaid.txt",
}
MARKER = "<!-- code-modernisation-report:v1 -->"
TOKEN = "__REPORT_DATA__"
MAX_BYTES = 512 * 1024
MAX_TEXT = 64 * 1024
MAX_ASSESSMENT_TEXT = 6000
MAX_DIAGRAMS = 20
MAX_EVIDENCE = 200
SCOPE = "Saved analysis artifacts only; no current source/environment validation, application execution or model calls."
DOCUMENTS = (
    ("INTENT.md", "Goal and scope", "intent"),
    ("PROJECT_SETUP.md", "Project setup", "setup"),
    ("PREFLIGHT.md", "Preflight", "setup"),
    ("ASSESSMENT.md", "Assessment", "discovery"),
    ("BUSINESS_RULES.md", "Behavior findings", "discovery"),
    ("DATA_OBJECTS.md", "Data objects", "discovery"),
    ("RULE_REVIEWS.md", "Recorded rule decisions", "review"),
    ("MODERNIZATION_BRIEF.md", "Modernization plan", "plan"),
    ("TEST_PROPOSAL.md", "Proposed tests", "tests"),
    ("TEST_PLAN.md", "Test plan", "tests"),
    ("TEST_PREPARATION.md", "Test preparation", "tests"),
    ("TRANSFORMATION_NOTES.md", "Modernized version notes", "implementation"),
    ("BASELINE.md", "Original native test baseline", "tests"),
    ("DELTA_CATALOG.md", "Version changes", "plan"),
    ("PLAYBOOK.md", "Upgrade procedure", "implementation"),
    ("AI_NATIVE_SPEC.md", "Rebuild specification", "plan"),
    ("REIMAGINED_ARCHITECTURE.md", "Rebuild architecture", "plan"),
    ("SECURITY_FINDINGS.md", "Security findings", "verification"),
    ("VERIFICATION.md", "Verification notes", "verification"),
    ("WORKFLOW.md", "Work and next action", "continuation"),
)
JSON_DOCUMENTS = (
    ("inventory.json", "Source inventory", "discovery"),
    ("rules.json", "Source-backed rules", "discovery"),
    ("topology.json", "Structure and user flows", "discovery"),
    ("RULE_REVIEWS.json", "Rule decisions", "review"),
    ("VERIFICATION.json", "Recorded upstream proof", "verification"),
    ("EQUIVALENCE.json", "Recorded output comparison", "verification"),
)
EVIDENCE_NAMES = {
    "setup-check.json": "E2E setup check",
    "validation.json": "Source citation check",
    "baseline-check.json": "Source/test baseline check (role unclassified)",
    "result-check.json": "Playwright result check",
    "results-check.json": "Playwright result check",
    "comparison.json": "Modernized version comparison",
    "candidate-comparison.json": "Modernized version comparison",
    "comparison-check.json": "Modernized version comparison",
}
SKIP_DIRS = {"candidate", "source", "modernized", "modernised", "node_modules", "__pycache__"}
TEST_DOCUMENTS = {name: (title, category) for name, title, category in DOCUMENTS if category == "tests"}
ATTEMPT_CHECKS = ("cleanup", "afterSnapshot", "environment-after", "environment-current", "runtimeCurrent",
                  "runtimeStable", "nativeClean", "resultsClean", "recordAssembled")
CAPTURE_CHECKS = ("executionClean", "cleanup", "serviceClosed", "afterSnapshot", "environmentAfter",
                  "environmentStable", "resultsClean", "baselineChecked", "helpersUnchanged",
                  "postExecutionEvidenceComplete")
RESULT_CHECK_NAMES = {"result-check.json", "results-check.json"}


def timestamp(seconds=None):
    value = datetime.now(timezone.utc) if seconds is None else datetime.fromtimestamp(seconds, timezone.utc)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def safe_read(root, relative):
    """Read a bounded regular artifact, never following links under its root."""
    path = root
    parts = Path(relative).parts
    if not parts or any(part in ("..", "") for part in parts) or Path(relative).is_absolute():
        raise ValueError("artifact path is not relative")
    for part in parts[:-1]:
        path /= part
        if not stat.S_ISDIR(path.lstat().st_mode):
            raise ValueError("artifact parent is not a physical directory")
    path /= parts[-1]
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
        raise ValueError("artifact is not a regular file or exceeds the 512 KiB display limit")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError("artifact changed while opening")
        raw = stream.read(MAX_BYTES + 1)
        after = os.fstat(stream.fileno())
    if len(raw) > MAX_BYTES or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (
            after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError("artifact changed while reading or exceeds the display limit")
    return raw, after


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite JSON value")


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite JSON value")
    return result


def parse_json(raw):
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=reject_constant, parse_float=finite_float)
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def mask_fenced_examples(text):
    """Keep offsets while excluding fenced examples from structural extraction."""
    result, fence = [], None
    for line in text.splitlines(keepends=True):
        delimiter = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        masked = fence is not None or delimiter is not None
        if delimiter:
            marker, suffix = delimiter.groups()
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not suffix.strip():
                fence = None
        result.append(re.sub(r"[^\r\n]", " ", line) if masked else line)
    return "".join(result)


def section(text, name, empty=None):
    headings = list(re.finditer(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$",
                                mask_fenced_examples(text), re.MULTILINE))
    for index, match in enumerate(headings):
        if match.group(2).casefold() != name.casefold():
            continue
        end = next((candidate.start() for candidate in headings[index + 1:]
                    if len(candidate.group(1)) <= len(match.group(1))), len(text))
        return text[match.end():end].strip() or empty
    return None


def table_cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, current, index = [], [], 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line) and line[index + 1] == "|":
            current.append("|")
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def section_table(text, heading):
    block = section(text, heading) or ""
    lines = mask_fenced_examples(block).splitlines()
    for index in range(len(lines) - 1):
        columns, separator = table_cells(lines[index]), table_cells(lines[index + 1])
        if len(columns) < 2 or len(separator) != len(columns) or not all(
                re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            continue
        rows = []
        for line in lines[index + 2:]:
            if not line.strip() or "|" not in line:
                break
            row = table_cells(line)
            if len(row) != len(columns):
                break
            rows.append(row)
        return {"columns": columns, "rows": rows[:100], "truncated": len(rows) > 100}
    return {"columns": [], "rows": [], "truncated": False}


def feature_table(text):
    table = section_table(text, "Observed functional areas")
    if not table["columns"]:
        table = section_table(text, "Observed features and suggested slices")
    if table["columns"]:
        return {"columns": table["columns"], "rows": table["rows"],
                "note": "Historical assessment from ASSESSMENT.md; it does not override the current work recorded in WORKFLOW.md. "
                        "These observed functional areas are agent-recorded findings, not an exhaustive or validated inventory."
                        + (" Showing the first 100 rows." if table["truncated"] else "")}
    return {"columns": [], "rows": [], "note": "No observed functional areas table recorded yet."}


def assessment_data(text):
    """Present named saved sections without generating conclusions or decisions."""
    recommendations, recommendation_heading = None, None
    for heading in ("Candidate Comparison", "Recommended Modernization Pattern"):
        recommendations = section(text, heading)
        if recommendations:
            recommendation_heading = heading
            break

    def excerpt(content):
        if content and len(content) > MAX_ASSESSMENT_TEXT:
            prefix = content[:MAX_ASSESSMENT_TEXT]
            boundaries = list(re.finditer(r"\r?\n[ \t]*\r?\n", prefix))
            if boundaries and boundaries[-1].start() >= MAX_ASSESSMENT_TEXT // 2:
                prefix = prefix[:boundaries[-1].start()]
            return prefix + "\n\n[Excerpt; read ASSESSMENT.md for the full saved section.]"
        return content

    return {"summary": excerpt(section(text, "Executive Summary")),
            "recommendations": excerpt(recommendations),
            "recommendationHeading": recommendation_heading, "path": "ASSESSMENT.md"}


def diagram_records(root, warnings):
    """Read only bounded, top-level Mermaid sources; never traverse their content."""
    if not root.exists():
        return []
    names = []
    try:
        with os.scandir(root) as stream:
            for index, entry in enumerate(stream):
                if index >= 5000:
                    warnings.append("Diagram scan limited to 5000 entries in the analysis directory.")
                    break
                if entry.name.endswith(".mmd"):
                    names.append(entry.name)
    except OSError as error:
        warnings.append("Analysis diagrams could not be listed: " + type(error).__name__)
    if len(names) > MAX_DIAGRAMS:
        warnings.append("Diagram display limited to 20 top-level .mmd files; inspect the analysis directory for others.")
    records = []
    for name in sorted(names)[:MAX_DIAGRAMS]:
        record = {"path": name, "href": None, "status": "unreadable", "text": None,
                  "sha256": None, "truncated": False}
        try:
            raw, _ = safe_read(root, name)
            content = raw.decode("utf-8")
            record.update(status="recorded", href=quote(name), text=content[:MAX_TEXT],
                          sha256=hashlib.sha256(raw).hexdigest(), truncated=len(content) > MAX_TEXT)
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            warnings.append(name + ": unavailable or unsupported diagram (" + type(error).__name__ + ").")
        records.append(record)
    return records


def topology_data(value, warnings):
    empty = {"nodes": [], "edges": [], "flows": []}
    if value is None:
        return empty
    if not isinstance(value.get("root"), dict):
        warnings.append("topology.json: no supported root tree; inspect the original artifact.")
        return empty
    nodes, pending, identifiers = [], deque([value["root"]]), set()
    inspected = 0
    while pending and inspected < 200:
        node = pending.popleft()
        inspected += 1
        if not isinstance(node, dict):
            warnings.append("topology.json: invalid node omitted.")
            continue
        if all(isinstance(node.get(key), str) and node[key].strip() for key in ("id", "name", "kind")) and node["id"] not in identifiers:
            nodes.append({key: node.get(key, "") if isinstance(node.get(key, ""), str) else ""
                          for key in ("id", "name", "kind", "file")})
            identifiers.add(node["id"])
        else:
            warnings.append("topology.json: node with missing/invalid fields or duplicate id omitted.")
        children = node.get("children", [])
        if isinstance(children, list):
            remaining = max(0, 200 - inspected - len(pending))
            pending.extend(children[:remaining])
            if len(children) > remaining:
                warnings.append("Topology display limited to 200 nodes; inspect topology.json for the complete recorded map.")
        else:
            warnings.append("topology.json: invalid node children omitted.")
    if pending:
        warnings.append("Topology display limited to 200 nodes; inspect topology.json for the complete recorded map.")
    edges = value.get("edges", [])
    flows = value.get("flows", [])
    if not isinstance(edges, list) or not isinstance(flows, list):
        warnings.append("topology.json: unsupported edges/flows; inspect the original artifact.")
    valid_edges, used_aliases = [], False
    for edge in (edges[:400] if isinstance(edges, list) else []):
        if not isinstance(edge, dict):
            warnings.append("topology.json: invalid edge omitted.")
            continue
        normalized = {key: edge.get(key, edge.get(alias)) for key, alias in (
            ("source", "from"), ("target", "to"), ("kind", "type"))}
        if not all(isinstance(normalized[key], str) and normalized[key].strip() for key in ("source", "target")):
            warnings.append("topology.json: edge with missing/invalid endpoints omitted.")
            continue
        if normalized["source"] not in identifiers or normalized["target"] not in identifiers:
            warnings.append("topology.json: edge with unknown endpoint omitted; inspect the original artifact.")
            continue
        if not isinstance(normalized["kind"], str):
            warnings.append("topology.json: edge with missing/invalid kind omitted.")
            continue
        valid_edges.append(normalized)
        used_aliases = used_aliases or any(key not in edge and alias in edge for key, alias in (
            ("source", "from"), ("target", "to"), ("kind", "type")))
    if isinstance(edges, list) and len(edges) > 400:
        warnings.append("Topology display limited to 400 edges.")
    valid_flows = []
    for flow in (flows[:50] if isinstance(flows, list) else []):
        if not isinstance(flow, dict):
            warnings.append("topology.json: invalid flow omitted.")
            continue
        name = flow.get("name", flow.get("label", flow.get("id")))
        if not isinstance(name, str) or not name.strip():
            warnings.append("topology.json: flow with missing/invalid name omitted.")
            continue
        used_aliases = used_aliases or "name" not in flow
        steps = flow.get("steps", [])
        valid_steps = []
        if not isinstance(steps, list):
            warnings.append("topology.json: invalid flow steps omitted.")
        for step in (steps[:100] if isinstance(steps, list) else []):
            if not isinstance(step, dict):
                warnings.append("topology.json: invalid flow step omitted.")
                continue
            label = step.get("label", step.get("action"))
            endpoints = step.get("nodes", [step["nodeId"]] if "nodeId" in step else [])
            if not isinstance(label, str) or not label.strip() or not isinstance(endpoints, list):
                warnings.append("topology.json: flow step with missing/invalid action or endpoints omitted.")
                continue
            valid_endpoints = [node for node in endpoints if isinstance(node, str) and node in identifiers]
            if not endpoints or len(valid_endpoints) != len(endpoints):
                warnings.append("topology.json: flow step has missing/unknown endpoints; inspect the original artifact.")
            valid_steps.append({"label": label, "nodes": valid_endpoints})
            used_aliases = used_aliases or "label" not in step or ("nodes" not in step and "nodeId" in step)
        if isinstance(steps, list) and len(steps) > 100:
            warnings.append("Topology display limited to 100 steps per flow.")
        valid_flows.append({"name": name,
                            "persona": flow.get("persona") if isinstance(flow.get("persona"), str) else "",
                            "description": flow.get("description") if isinstance(flow.get("description"), str) else "",
                            "steps": valid_steps})
    if isinstance(flows, list) and len(flows) > 50:
        warnings.append("Topology display limited to 50 flows.")
    if used_aliases:
        warnings.append("topology.json: legacy edge/flow aliases normalized for display; the saved artifact is unchanged.")
    warnings[:] = list(dict.fromkeys(warnings))
    return {"nodes": nodes, "edges": valid_edges, "flows": valid_flows}


def artifact_paths(root, warnings):
    """Breadth-first, bounded discovery of known evidence and test documents only."""
    paths, documents, visited = [], [], 0
    if not root.exists():
        return paths, documents
    pending = deque([Path()])
    scan_warnings = set()
    while pending and visited < 500:
        relative = pending.popleft()
        directory = root / relative
        visited += 1
        try:
            if not stat.S_ISDIR(directory.lstat().st_mode):
                continue
            entries = []
            with os.scandir(directory) as stream:
                for entry in stream:
                    if len(entries) >= 5000:
                        scan_warnings.add("Artifact scan limited to 5000 entries per directory.")
                        break
                    entries.append(entry)
            for entry in sorted(entries, key=lambda item: item.name):
                name = entry.name
                if entry.is_dir(follow_symlinks=False):
                    if name.startswith(".") or name.casefold() in SKIP_DIRS:
                        continue
                    if len(relative.parts) >= 6:
                        scan_warnings.add("Artifact scan depth limit reached; deeper saved records are not shown.")
                    elif visited + len(pending) >= 500:
                        scan_warnings.add("Artifact scan limited to 500 directories.")
                    else:
                        pending.append(relative / name)
                    continue
                if name in EVIDENCE_NAMES:
                    if len(paths) < MAX_EVIDENCE:
                        paths.append((relative / name).as_posix())
                    else:
                        scan_warnings.add("Evidence scan limited to 200 results; inspect the analysis directory for other attempts.")
                if relative.parts and name in TEST_DOCUMENTS:
                    if len(documents) < 100:
                        documents.append((relative / name).as_posix())
                    else:
                        scan_warnings.add("Test preparation display limited to 100 nested documents.")
        except OSError as error:
            scan_warnings.add("Some analysis folders could not be read: " + type(error).__name__)
    warnings.extend(sorted(scan_warnings))
    return paths, documents


def saved_outcome(value):
    outcome = value.get("checksPassed")
    if type(outcome) is not bool:
        return "unknown"
    failed = not outcome or bool(value.get("errors")) or value.get("eligibleForImplementation") is False
    return "recorded-fail" if failed else "recorded-pass"


def setup_check(value):
    if (value.get("kind") != "e2e-setup-check" or type(value.get("formatVersion")) is not int
            or value["formatVersion"] != 1 or value.get("phase") not in ("stack", "fixtures", "auth")
            or type(value.get("passed")) is not bool):
        raise ValueError("unsupported setup check")
    checks = value.get("checks")
    cleanup = value.get("cleanup")
    outcomes = ("passed", "failed", "timed-out", "not-run")
    if (not isinstance(checks, list) or not 1 <= len(checks) <= 100 or not isinstance(cleanup, dict)
            or cleanup.get("outcome") not in outcomes):
        raise ValueError("incomplete setup checks")
    normalized, names = [], set()
    for check in checks:
        if (not isinstance(check, dict) or not isinstance(check.get("name"), str)
                or not check["name"].strip() or len(check["name"]) > 160 or check["name"] in names
                or check.get("outcome") not in outcomes):
            raise ValueError("invalid setup check detail")
        names.add(check["name"])
        normalized.append({"name": check["name"], "outcome": check["outcome"]})
    times = []
    for key in ("startedAt", "completedAt"):
        text = value.get(key)
        if not isinstance(text, str) or len(text) > 64:
            raise ValueError("missing setup observation time")
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("setup observation time needs a timezone")
        times.append(parsed)
    if times[1] < times[0]:
        raise ValueError("reversed setup observation times")
    passed = value["passed"] and all(check["outcome"] == "passed" for check in normalized) and cleanup["outcome"] == "passed"
    return {"outcome": "recorded-pass" if passed else "recorded-fail", "setup": {
        "phase": value["phase"], "checks": normalized, "cleanup": cleanup["outcome"],
        "startedAt": value["startedAt"], "completedAt": value["completedAt"],
    }}


def attempt_record(root, result_path, warnings):
    relative = (Path(result_path).parent / "outcome.json").as_posix()
    record = {"path": relative, "href": None, "outcome": "unknown", "checks": {},
              "sha256": None, "modifiedAt": None, "producerOutcome": "unknown",
              "unrecordedChecks": list(ATTEMPT_CHECKS),
              "note": "No sibling attempt outcome is available; lifecycle details are not established."}
    try:
        raw, metadata = safe_read(root, relative)
        record.update(href=quote(relative), sha256=hashlib.sha256(raw).hexdigest(),
                      modifiedAt=timestamp(metadata.st_mtime))
        value = parse_json(raw)
        expected, flags, schema = ATTEMPT_CHECKS, value, "legacy-lifecycle"
        if value.get("kind") == "playwright-capture-outcome":
            if type(value.get("schemaVersion")) is int and value["schemaVersion"] == 1:
                schema = "bundled-capture-v1"
                flags = dict(value["checks"]) if isinstance(value.get("checks"), dict) else {}
                flags["postExecutionEvidenceComplete"] = value.get("postExecutionEvidenceComplete")
            else:
                schema, flags = "unsupported-capture", {}
            expected = CAPTURE_CHECKS
        elif "postExecutionEvidenceComplete" in value and not any(key in value for key in ATTEMPT_CHECKS):
            # Historical bundled summaries did not save the detailed lifecycle
            # flags. Retain their producer claim without inventing those checks.
            schema, expected = "unversioned-capture", CAPTURE_CHECKS
        record["schema"] = schema
        record["checks"] = {key: flags[key] for key in expected if type(flags.get(key)) is bool}
        record["producerOutcome"] = saved_outcome(value)
        record["outcome"] = record["producerOutcome"]
        record["unrecordedChecks"] = [key for key in expected if key not in record["checks"]]
        invalid = [key for key in expected if key in flags and flags[key] is not None and type(flags[key]) is not bool]
        failure_metadata = schema == "bundled-capture-v1" and any(key in value for key in ("error", "cancelledSignals"))
        if False in record["checks"].values() or value.get("error") or value.get("cancelledSignals"):
            record["outcome"] = "recorded-fail"
        elif (record["unrecordedChecks"] or failure_metadata) and record["outcome"] == "recorded-pass":
            record["outcome"] = "unknown"
        record["note"] = (
            "The bundled capture has empty or invalid failure/cancellation metadata; an overall pass is not established."
            if failure_metadata and record["outcome"] == "unknown" else
            "The producer reports an outcome, but some recognized lifecycle details are unrecorded or invalid. "
            "Missing checks have not been inferred from the producer's summary or filenames."
            if record["unrecordedChecks"] else
            "Producer outcome and recognized lifecycle flags are saved observations; current validity has not been rechecked."
        )
        if invalid:
            warnings.append(relative + ": non-boolean lifecycle flags omitted; no overall pass inferred from them.")
    except FileNotFoundError:
        pass
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        record["outcome"] = "unreadable"
        record["producerOutcome"] = "unreadable"
        record["note"] = "The sibling attempt outcome is unreadable; no overall outcome or lifecycle details are established."
        warnings.append(relative + ": attempt outcome unavailable or unsupported (" + type(error).__name__ + ").")
    return record


def measured_table_rows(block):
    """Only table bodies are evidence references; surrounding prose is not selection."""
    lines = mask_fenced_examples(block).splitlines()
    rows = []
    for index in range(len(lines) - 1):
        columns, separator = table_cells(lines[index]), table_cells(lines[index + 1])
        if len(columns) < 2 or len(separator) != len(columns) or not all(
                re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            continue
        for line in lines[index + 2:]:
            if not line.strip() or "|" not in line or len(table_cells(line)) != len(columns):
                break
            rows.append(line)
    return "\n".join(rows)


def evidence_selection(contents, warnings):
    block = section(contents.get("WORKFLOW.md", ""), "Selected evidence", empty="")
    explicit = block is not None
    source = "WORKFLOW.md#Selected evidence" if explicit else None
    if not explicit:
        measured = section(contents.get("VERIFICATION.md", ""), "Measured results", empty="")
        if measured is not None:
            source = "VERIFICATION.md#Measured results"
            block = measured_table_rows(measured)
    labels = {}
    # Inline Markdown links only, never opening their targets. Angle brackets allow spaces.
    link_pattern = r'\[([^\]\n]{0,500})\]\(\s*(?:<([^<>\r\n]+)>|([^\s)]+))(?:\s+(?:"[^"\n]*"|\x27[^\x27\n]*\x27))?\s*\)'
    for match in re.finditer(link_pattern, mask_fenced_examples(block or "")):
        label, angled, plain = match.groups()
        destination = angled if angled is not None else plain
        try:
            target = urlsplit(destination)
            path = unquote(target.path, errors="strict")
            parts = Path(path).parts
            if (target.scheme or target.netloc or target.query or not path or path.startswith("/")
                    or "\\" in path or any(part == ".." for part in parts)
                    or any(ord(char) < 32 or ord(char) == 127 for char in destination + path)):
                raise ValueError("not a local analysis path")
            relative = Path(path).as_posix()
            if relative == ".":
                raise ValueError("not an artifact")
        except (ValueError, UnicodeError):
            warnings.append((source or "Evidence links") + ": ignored a nonlocal or unsupported evidence link.")
            continue
        if relative not in labels and len(labels) >= MAX_EVIDENCE:
            warnings.append("Evidence references limited to 200 paths.")
            break
        labels.setdefault(relative, [])
        if label and label not in labels[relative]:
            labels[relative].append(label)
    note = (
        "Explicit links recorded under WORKFLOW.md Selected evidence. Selection is not validation or acceptance."
        if explicit else
        "References from the current VERIFICATION.md Measured results table; no explicit final evidence selection is recorded."
        if source else
        "No explicit evidence selection or measured-results table references recorded. No latest attempt is inferred."
    )
    return {"source": source, "explicit": explicit, "paths": list(labels), "note": note}, labels


def selection_references(root, selection, warnings):
    """Check exact reference readability, without interpreting it as passing evidence."""
    references = []
    for path in selection["paths"]:
        reference = {"path": path, "status": "available", "href": quote(path)}
        try:
            safe_read(root, path)
        except FileNotFoundError:
            reference.update(status="missing", href=None)
            warnings.append(path + ": referenced evidence is missing; no sibling association inferred from this link.")
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            reference.update(status="unreadable", href=None)
            warnings.append(path + ": referenced evidence unavailable or unsupported (" + type(error).__name__
                            + "); no sibling association inferred from this link.")
        references.append(reference)
    selection["references"] = references
    return {reference["path"] for reference in references if reference["status"] == "available"}


def generator_version(warnings):
    try:
        raw, _ = safe_read(TEMPLATE.parents[2], "plugin.json")
        version = parse_json(raw).get("version")
        if not isinstance(version, str) or not version.strip() or len(version) > 100:
            raise ValueError("invalid plugin version")
        return version
    except (OSError, ValueError, UnicodeError, RecursionError):
        warnings.append("Generator version unavailable in plugin.json.")
        return None


def collect(analysis):
    root = Path(analysis).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ValueError("analysis must be a directory")
    warnings, artifacts, contents, modified, decoded = [], [], {}, {}, {}
    if not root.exists():
        warnings.append("Analysis directory does not exist yet; no work has been recorded here.")
    evidence_paths, nested_documents = artifact_paths(root, warnings)
    diagrams = diagram_records(root, warnings)
    document_entries = [*DOCUMENTS, *JSON_DOCUMENTS,
                        *((name, *TEST_DOCUMENTS[Path(name).name]) for name in nested_documents)]
    for name, title, category in document_entries:
        record = {"path": name, "title": title, "category": category, "status": "missing",
                  "modifiedAt": None, "sha256": None}
        try:
            raw, metadata = safe_read(root, name)
            content = raw.decode("utf-8")
            if name.endswith(".json"):
                decoded[name] = parse_json(raw)
            record.update(status="recorded", modifiedAt=timestamp(metadata.st_mtime),
                          sha256=hashlib.sha256(raw).hexdigest(), href=quote(name),
                          text=content[:MAX_TEXT], truncated=len(content) > MAX_TEXT)
            contents[name] = content
            modified[name] = metadata.st_mtime_ns
        except FileNotFoundError:
            pass
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            record["status"] = "unreadable"
            warnings.append(name + ": unavailable or unsupported artifact (" + type(error).__name__ + ").")
        artifacts.append(record)
    selection, selection_labels = evidence_selection(contents, warnings)
    available_references = selection_references(root, selection, warnings)
    evidence, associated_paths = [], set()
    for relative in evidence_paths:
        record = {"path": relative, "kind": EVIDENCE_NAMES[Path(relative).name], "outcome": "unreadable",
                  "counts": {}, "modifiedAt": None, "sha256": None,
                  "limits": ["Saved outcome only; current source, environment and referenced inputs have not been rechecked."]}
        try:
            raw, metadata = safe_read(root, relative)
            value = parse_json(raw)
            saved_limits = value.get("limits", [])
            if isinstance(saved_limits, list):
                record["limits"].extend(item[:2000] for item in saved_limits[:20] if isinstance(item, str))
            if Path(relative).name == "setup-check.json":
                record.update(setup_check(value))
                record["limits"].append("Setup checks are not behavior-test execution, preservation coverage or baseline eligibility.")
            else:
                record["outcome"] = saved_outcome(value)
            counts = value.get("counts", {}) if record["kind"] != "E2E setup check" else {}
            if isinstance(counts, dict):
                record["counts"] = {str(key): number for key, number in list(counts.items())[:30]
                                    if type(number) is int and number >= 0}
            if record["kind"] != "E2E setup check" and type(value.get("mappedCases")) is int and value["mappedCases"] >= 0:
                record["counts"]["mappedCases"] = value["mappedCases"]
            elif record["kind"] != "E2E setup check" and isinstance(value.get("mappedCases"), list):
                record["counts"]["mappedCases"] = len(value["mappedCases"])
            record.update(modifiedAt=timestamp(metadata.st_mtime), sha256=hashlib.sha256(raw).hexdigest(), href=quote(relative))
            modified[relative] = metadata.st_mtime_ns
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            warnings.append(relative + ": saved result unavailable or unsupported (" + type(error).__name__ + ").")
        linked_paths = [relative]
        if Path(relative).name in RESULT_CHECK_NAMES:
            record["attempt"] = attempt_record(root, relative, warnings)
            linked_paths.extend((Path(relative).parent / name).as_posix()
                                for name in ("outcome.json", "baseline.json", "results.json"))
        associated_paths.update(linked_paths)
        record["selectionLabels"] = list(dict.fromkeys(
            label for path in linked_paths if path in available_references for label in selection_labels.get(path, [])))
        referenced = any(path in available_references for path in linked_paths)
        record["selection"] = ("selected" if selection["explicit"] else "verification-reference") if referenced else "other"
        evidence.append(record)
    if any(path not in associated_paths and path not in contents for path in selection["paths"]):
        warnings.append("Some evidence links are retained as references but have no supported result in this bounded display; "
                        "inspect their linked artifacts. Their outcomes have not been inferred.")
    dependencies = {
        "MODERNIZATION_BRIEF.md": ("INTENT.md", "ASSESSMENT.md", "topology.json", "rules.json", "BUSINESS_RULES.md", "RULE_REVIEWS.json"),
        "VERIFICATION.md": ("MODERNIZATION_BRIEF.md", "TEST_PLAN.md", "rules.json"),
        "validation.json": ("inventory.json", "rules.json"),
    }
    stale = [{"path": name, "reason": "Older than " + dependency + "; may need review. Modification time is only a hint."}
             for name, inputs in dependencies.items() for dependency in inputs
             if name in modified and dependency in modified and modified[name] < modified[dependency]]
    workflow = contents.get("WORKFLOW.md", "")
    summary = {"currentWork": section(workflow, "Current work"), "nextAction": section(workflow, "Next action"),
               "openDecisions": section(workflow, "Open decisions")}
    if workflow and not any(summary.values()):
        warnings.append("WORKFLOW.md uses older/freeform notes; read it before choosing the next action.")
    preparation_paths = [name for name in contents if Path(name).name in TEST_DOCUMENTS]
    coverage_plans = []
    for name in preparation_paths:
        table = section_table(contents[name], "Coverage plan")
        if table["columns"]:
            coverage_plans.append({"path": name, "href": quote(name), **table})
    setup_records = [record for record in evidence if record["kind"] == "E2E setup check"]
    setup_records.sort(key=lambda record: record["selection"] != "selected")
    location = (json.dumps("analysis/" + root.name, ensure_ascii=False) + " relative to the project root"
                if root.parent.name == "analysis" else
                '"." relative to the folder containing this REPORT.html (open that analysis folder first)')
    resume = "Resume the saved work in " + location + ". Recheck what is current and continue within the recorded scope."
    status = "Show where the work in " + location + " stands, what needs rechecking, and the next action."
    intent = contents.get("INTENT.md", "")
    project_scope = section(intent, "Scope") or section(intent, "Goal") or section(intent, "Objective")
    if not project_scope:
        project_scope = re.sub(r"\A\s*# [^\n]*(?:\n|$)", "", intent).strip() or None
    if project_scope and len(project_scope) > 2000:
        project_scope = project_scope[:2000] + "\n[Excerpt; read INTENT.md for the full recorded intent.]"
    return {"schemaVersion": 1, "generatorVersion": generator_version(warnings),
            "system": root.name, "generatedAt": timestamp(), "analysisPath": str(root), "scope": SCOPE,
            "projectScope": project_scope,
            "summary": summary, "features": feature_table(contents.get("ASSESSMENT.md", "")),
            "assessment": assessment_data(contents.get("ASSESSMENT.md", "")), "diagrams": diagrams,
            "testing": {"coveragePlans": coverage_plans, "setupChecks": setup_records},
            "artifacts": artifacts, "evidence": evidence, "evidenceSelection": selection,
            "staleHints": stale, "warnings": warnings,
            "prompts": {"vscode": "/editorial-tools-modernisation.code-modernisation modernize-start " + resume,
                        "cli": "/editorial-tools-modernisation.code-modernisation:modernize-start " + resume,
                        "statusVscode": "/editorial-tools-modernisation.code-modernisation modernize-status " + status,
                        "statusCli": "/editorial-tools-modernisation.code-modernisation:modernize-status " + status,
                        "setupVscode": "/editorial-tools-modernisation.code-modernisation modernize-setup-tests Prepare or repair only the test setup for the saved work in " + location + ". Stop before modernization.",
                        "setupCli": "/editorial-tools-modernisation.code-modernisation:modernize-setup-tests Prepare or repair only the test setup for the saved work in " + location + ". Stop before modernization."},
            "topology": topology_data(decoded.get("topology.json"), warnings)}


def render(model):
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(TOKEN) != 1 or MARKER not in template:
        raise ValueError("report template is missing its single data slot or generated-file marker")
    for token, path in RENDER_ASSETS.items():
        if template.count(token) != 1:
            raise ValueError("report template is missing a single renderer asset slot")
        content = ("" if token == "__DIAGRAM_RENDERER__" and not model.get("diagrams")
                   else path.read_text(encoding="utf-8"))
        if token in {"__PLUGIN_LICENSE__", "__PLUGIN_NOTICE__", "__REPORT_LICENSES__", "__DIAGRAM_LICENSE__"}:
            content = escape(content)
        elif re.search(r"</script", content, re.IGNORECASE):
            raise ValueError("bundled renderer contains an unsafe closing script tag")
        template = template.replace(token, content)
    payload = json.dumps(model, ensure_ascii=True, allow_nan=False)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return template.replace(TOKEN, payload)


def write_report(root, html):
    if not root.is_dir():
        raise ValueError("analysis directory must exist before writing a report")
    output = root / "REPORT.html"
    before = None
    if output.exists() or output.is_symlink():
        before = output.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError("REPORT.html must be an unlinked regular generated file")
        descriptor = os.open(output, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (opened.st_dev, opened.st_ino, opened.st_mtime_ns, opened.st_ctime_ns) != (
                    before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns):
                raise ValueError("REPORT.html changed while opening")
            if MARKER.encode() not in stream.read(4096):
                raise ValueError("REPORT.html already exists and is not this tool's generated report")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=root, prefix=".modernisation-report-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(html.encode("utf-8"))
        if before:
            current = output.lstat()
            if (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns) != (
                    current.st_dev, current.st_ino, current.st_mtime_ns, current.st_ctime_ns):
                raise ValueError("REPORT.html changed before refresh")
            os.chmod(temporary, stat.S_IMODE(before.st_mode))
            os.replace(temporary, output)
        else:
            # Atomic no-clobber creation: a concurrent file must not be replaced.
            os.link(temporary, output)
        return str(output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", required=True, help="Existing project's analysis directory; never executes its content.")
    parser.add_argument("--write-report", action="store_true", help="Refresh only the optional generated REPORT.html in that directory.")
    args = parser.parse_args(argv)
    try:
        model = collect(args.analysis)
        if args.write_report:
            rendered = render(model)
            path = write_report(Path(model["analysisPath"]), rendered)
            model["report"] = {"path": path, "written": True,
                               "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest()}
        print(json.dumps(model, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        print(json.dumps({"error": str(error), "scope": SCOPE}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
