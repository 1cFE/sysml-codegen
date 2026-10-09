"""Recount matrix summaries and check active test citations without importing tests."""

from __future__ import annotations

import argparse
import ast
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/architecture/verification-matrix.md"
STATUSES = ("PASS", "PARTIAL", "RETIRED", "UNTESTED", "DEFERRED", "DESCOPED")
CITATION = re.compile(r"(?:tests/[\w/-]+/)?test_[\w]+\.py(?:::[\w]+)*|(?<!\w)::[\w]+")


def rows(text: str) -> list[tuple[str, str, str]]:
    result = []
    for line in text.splitlines():
        if line.startswith("| REQ-"):
            prefix, evidence, ending = line.rsplit(" | ", 2)
            identifier = prefix[2:].split(" | ", 1)[0]
            status = ending.split()[0]
            if status not in STATUSES:
                raise ValueError(f"{identifier}: unknown status {status}")
            result.append((identifier, evidence, status))
    if len({row[0] for row in result}) != len(result):
        raise ValueError("duplicate requirement ID")
    return result


def nodes(path: Path) -> set[str]:
    result = set()
    for item in ast.parse(path.read_text()).body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            result.add(item.name)
        if isinstance(item, ast.ClassDef):
            result.update(f"{item.name}::{child.name}" for child in item.body
                          if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)))
    return result


def check(text: str, root: Path = ROOT) -> tuple[list[str], dict[str, Counter], set[Path]]:
    errors = []
    families: dict[str, Counter] = {}
    cited = set()
    files = list((root / "tests").rglob("test_*.py"))
    for identifier, evidence, status in rows(text):
        families.setdefault(identifier.split("-")[1], Counter())[status] += 1
        if status not in {"PASS", "PARTIAL"}:
            continue
        previous = []
        for match in CITATION.finditer(evidence):
            citation = match.group()
            if citation.startswith("::"):
                targets, node = previous, citation[2:]
            else:
                filename, _, node = citation.partition("::")
                targets = [root / filename] if filename.startswith("tests/") else [
                    path for path in files if path.name == filename
                ]
                targets = [path for path in targets if path.is_file()]
                previous = targets
            if not targets:
                errors.append(f"{identifier}: missing citation {citation}")
            elif node and not any(node in nodes(path) for path in targets):
                errors.append(f"{identifier}: missing test node {citation}")
            cited.update(targets)
    catalog = root / ".project/concepts/constraint-execution-lifecycle-requirements.md"
    expected_grades = dict(re.findall(r"LC-SI-(\d+[A-Z]?) \[([A-Z]+)\]", catalog.read_text()))
    actual_grades = dict(re.findall(r"^\| REQ-SI-(\d+[A-Z]?) \| \[([A-Z]+)\]", text, re.M))
    if actual_grades != expected_grades:
        errors.append("REQ-SI inventory/authority grades differ from the LC-SI catalog")
    return errors, families, cited


def recount(text: str, families: dict[str, Counter], cited: set[Path]) -> str:
    totals = sum(families.values(), Counter())
    output = []
    for line in text.splitlines():
        if line.startswith("| Total requirements |"):
            line = f"| Total requirements | {sum(totals.values())} |"
        elif line.startswith("| REQ families |"):
            line = f"| REQ families | {len(families)} |"
        elif line.startswith("| Distinct kept test files cited |"):
            line = f"| Distinct kept test files cited | {len(cited)} |"
        else:
            for status in STATUSES:
                if line.startswith(f"| {status} "):
                    line = line.rsplit(" | ", 2)[0] + f" | {totals[status]} |"
            index = re.match(r"(- \[([A-Z]+) — .*\]\(#[a-z]+\))", line)
            if index:
                counts = ", ".join(f"{families.get(index.group(2), Counter())[status]} "
                                   f"{status.lower()}" for status in STATUSES
                                   if families.get(index.group(2), Counter())[status])
                line = index.group(1) + " (" + counts + ")"
        if line.startswith("<!-- matrix-counts:"):
            counts = ", ".join(f"{status}={totals[status]}" for status in STATUSES)
            line = (f"<!-- matrix-counts: total={sum(totals.values())}, "
                    f"families={len(families)}, tests={len(cited)}, {counts} -->")
        output.append(line)
    return "\n".join(output) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh computed counts")
    args = parser.parse_args()
    text = MATRIX.read_text()
    errors, families, cited = check(text)
    indexed = set(re.findall(r"^- \[([A-Z]+) — .*\]\(#[a-z]+\)", text, re.MULTILINE))
    if indexed != set(families):
        errors.append(f"family index mismatch: missing={sorted(set(families) - indexed)}, "
                      f"extra={sorted(indexed - set(families))}")
    if "<!-- matrix-counts:" not in text:
        errors.append("missing footer counts")
    expected = recount(text, families, cited)
    if args.write:
        MATRIX.write_text(expected)
    elif text != expected:
        errors.append("summary/index/footer counts drifted; run with --write")
    for error in errors:
        print(error)
    print(f"{len(rows(text))} requirements, {len(families)} families, "
          f"{len(cited)} existing active test files")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
