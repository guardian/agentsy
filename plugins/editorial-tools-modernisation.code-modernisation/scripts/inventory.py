#!/usr/bin/env python3
"""Read-only source inventory using the pinned upstream directory sharder.

Run from any working directory:
  "/path/to/plugin/scripts/inventory.py" --source "/path/to/source"

No analyzed source is imported or executed. JSON goes to stdout; this helper
does not create artifacts. Its hashes describe the files read, not an isolated
snapshot or a guarantee that the source cannot change after the command ends.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


# Loading the bundled Python helper must not write into an installed plugin.
sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = PLUGIN_ROOT / "upstream" / "scripts" / "make_shards.py"
ADDITIONAL_SOURCE_EXT = {".html", ".htm"}


def sharder():
    spec = importlib.util.spec_from_file_location("modernisation_upstream_shards", UPSTREAM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Static pages can contain application logic. Extend only this fresh module;
    # the pinned upstream bytes and its selection/exclusion rules stay unchanged.
    module.SOURCE_EXT = module.SOURCE_EXT | ADDITIONAL_SOURCE_EXT
    return module


def file_record(source, relative):
    path = source / relative
    resolved = path.resolve(strict=True)
    if path.is_symlink() or source not in resolved.parents or not resolved.is_file():
        raise ValueError("source file escaped the selected directory or changed type")
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
    if identity(before) != identity(after):
        raise ValueError("source changed during inventory; repeat against stable source")
    return {
        "path": relative,
        "sha256": hashlib.sha256(data).hexdigest(),
        "loc": data.count(b"\n") + int(bool(data) and not data.endswith(b"\n")),
    }


def inventory(source, pattern="", include_tests=False):
    root = Path(source).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("source must be a directory")
    upstream = sharder()
    if upstream.too_broad(str(root)):
        raise ValueError("select a project directory, not the filesystem or home root")
    shards, selected, skipped, total = upstream.from_tree(str(root), pattern, include_tests)
    paths = sorted({path for shard in shards for path in shard["files"]})
    if not paths:
        raise ValueError("no supported source files matched; adjust source or module selection")
    files = [file_record(root, path) for path in paths]
    scope = {"source": str(root), "files": files}
    scope_digest = hashlib.sha256(json.dumps(scope, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "source": str(root),
        "files": files,
        "shards": shards,
        "skipped": skipped,
        "selectedFiles": selected,
        "totalFiles": total,
        "scopeDigest": scope_digest,
        "notes": [
            "Inventory only: source was not executed and business rules are not verified.",
            "Uses upstream source extensions plus .html/.htm and upstream exclusion rules; this is not whole-system coverage.",
            "A file hash is evidence identity, not runtime isolation or human approval.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Project source directory; it is only read.")
    parser.add_argument("--module", default="", help="Upstream module name or glob filter.")
    parser.add_argument("--include-tests", action="store_true", help="Include source in test directories.")
    options = parser.parse_args(argv)
    try:
        result = inventory(options.source, options.module, options.include_tests)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
