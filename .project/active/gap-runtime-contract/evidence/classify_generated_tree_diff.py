"""Strict generated-tree classifier for GAP-CLOSE Item 1 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


OLD_DOCSTRING_LINE = (
    "Three-valued (Kleene) semantics; a verdict against the assertion NEVER raises (INV-3)."
)
NEW_DOCSTRING_LINE = (
    "Three-valued (Kleene) semantics. A verdict against the assertion does not itself raise "
    "(INV-3)."
)


def _is_approved_wrapper_change(before_root: Path, after_root: Path, relative_path: str) -> bool:
    if not relative_path.endswith(".py"):
        return False
    before_text = (before_root / relative_path).read_text()
    after_text = (after_root / relative_path).read_text()
    if OLD_DOCSTRING_LINE not in before_text or NEW_DOCSTRING_LINE not in after_text:
        return False
    return before_text.replace(OLD_DOCSTRING_LINE, NEW_DOCSTRING_LINE) == after_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--mode", choices=("exact", "approved-docstring-only"), required=True)
    args = parser.parse_args()
    before = _manifest(args.before)
    after = _manifest(args.after)
    changed = sorted(
        path for path in before.keys() | after.keys() if before.get(path) != after.get(path)
    )
    if args.mode == "exact":
        unapproved = changed
    else:
        allowed_names = {"package_contract.json", "package_manifest.json"}
        unapproved = [
            path
            for path in changed
            if Path(path).name not in allowed_names
            and "contract" not in Path(path).name
            and "manifest" not in Path(path).name
            and not _is_approved_wrapper_change(args.before, args.after, path)
        ]
        predicate_paths = [
            path for path in before if path.endswith("modules/constraints/predicates.py")
        ]
        assert predicate_paths and all(before[path] == after.get(path) for path in predicate_paths)
        for path in changed:
            if _is_approved_wrapper_change(args.before, args.after, path):
                old_imports = [
                    line
                    for line in (args.before / path).read_text().splitlines()
                    if "predicates import" in line
                ]
                new_imports = [
                    line
                    for line in (args.after / path).read_text().splitlines()
                    if "predicates import" in line
                ]
                assert old_imports == new_imports
    result = {"before": before, "after": after, "changed": changed, "unapproved": unapproved}
    print(json.dumps(result, indent=2, sort_keys=True))
    if unapproved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
