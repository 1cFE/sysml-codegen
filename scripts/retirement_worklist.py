#!/usr/bin/env python3
"""Derive the post-acceptance retirement work-list from the Gate 4A ledger.

The runbook in the plan names four steps. Every ledger row that the retirement has to
touch must be named by exactly one of them (or by the owner-gated fifth entry), and the
naming must be *derived* rather than hand-copied — a hand-copied list is exactly what
audit 4 found incomplete (F1).

Two ledger columns carry the derivation:

- `group` places the production, fixture and script rows that a deletion group removes.
  `4B-G2` is step 1, `4B-v5-family` step 2, `4B-G3` step 3, `4B-G4` step 4. That order is
  measured, not stated: the v5 read path imports the v5 family (`snapshot/graph_rebuild.py:15`
  imports `analysis.constraint_lowering`), so deleting the family first leaves
  `import sysml_codegen.snapshot` raising ModuleNotFoundError until the reader goes too.
- `breaks_on` places every dispositioned test/probe/script row: it names the group whose
  deletion breaks the file, so the row belongs to the earliest step that names such a
  group.

Seventeen dispositioned rows carry no `breaks_on` because they were found on the *data*
axis (they read a v5 fixture or shell out to the v5 capture script) rather than the import
axis. Those are placed by the explicit table below, one reason per row.

Usage:
    retirement_worklist.py check            # every actionable row named exactly once
    retirement_worklist.py step 1           # the full work-list for one step
    retirement_worklist.py paths 1 delete   # newline-separated paths, for a driver script
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / ".project/active/cutover-recovery/ledger-4a.json"

#: Deletion group -> step number in the runbook's sequence. The reader before the read.
GROUP_STEP = {
    "4B-G2": 1,
    "4B-v5-family": 2,
    "4B-G3": 3,
    "4B-G4": 4,
}

#: Rows the retirement may not execute at all until the owner rules on the dual qualifier
#: drop (`agentic-mbse` validation levels 4 and 6 call the legacy members).
OWNER_GATED = {"L-036", "L-037"}

#: Dispositioned rows with no `breaks_on`, placed by hand with the reason recorded. Every one
#: of them is a data-axis find from Gate 4C part 5 or part 7, and every one lands on the v5
#: family step because that is the step that deletes the fixtures and scripts they read.
DATA_AXIS_STEP = {
    "L-043": (2, "reads shared_producer's v5 extraction_snapshot.json by path"),
    "L-127": (2, "its live dual-run half drives pipeline_builder (L-029)"),
    "L-284": (2, "16 of its 52 nodes are bound to the L-033 legacy shape"),
    "L-285": (2, "calls pipeline_builder (L-029) inside a function"),
    "L-286": (2, "calls pipeline_builder (L-029) inside a function"),
    "L-287": (2, "took its corpus enumeration from the v5 capture script (L-275)"),
    "L-288": (2, "took its corpus enumeration from the v5 capture script (L-275)"),
    "L-289": (2, "hosts snapshot_fixture(), which reads the retiring v5 fixtures"),
    "L-290": (2, "both nodes scan the committed v5 snapshot corpus the v5-family step deletes"),
    "L-291": (2, "reaches its fixture directory through snapshot_fixture() (L-289)"),
    "L-292": (2, "subprocess-runs scripts/capture_extraction_snapshots.py (L-275)"),
    "L-293": (2, "quotes the retiring surface tokens in its own documentation"),
    "L-294": (2, "quotes the retiring surface tokens in its own documentation"),
    "L-295": (2, "its docstring names the retiring v5 capture script"),
    "L-296": (2, "names the surface tokens in synthetic fixtures, not in the real tree"),
    "L-297": (2, "names the v5 snapshot filename to exclude it from a variant"),
    "L-298": (2, "asserts the v5 snapshot file exists (test_d5_variants.py:116)"),
    "L-299": (2, "quotes the retiring surface tokens in its own placement table"),
    "L-300": (2, "quotes the retiring surface tokens in its own cases"),
}

#: The three tests/execution rows below are pinned here rather than left to
#: `tighten_by_test_imports`, because that walk reads the tree: once step 1 has deleted the
#: module they import, the edge is gone and the placement would drift back a step.
#:
#: Rows the per-step scratch-worktree simulation measured red EARLIER than the ledger's own
#: columns place them. Every one is a function-local import or a fixture use, which is the
#: class `check_ledger_4a.py`'s module-level AST scan cannot see (its ceiling 1). The reason
#: is what the simulation measured, not what the row says.
PULLED_FORWARD = {
    "L-098": (1, "reaches the graph through build_full_graph_from_snapshot in a test body"),
    "L-104": (1, "reaches the graph through build_full_graph_from_snapshot in a test body"),
    "L-187": (1, "its fixture data comes from the conformance extraction_snapshots fixture"),
    "L-140": (1, "loads a v5 snapshot inside the node that seals it"),
    "L-169": (1, "loads a v5 snapshot inside the node that seals it"),
    "L-207": (1, "drives the runner from a graph built by the v5 read path"),
    "L-251": (1, "its legacy arm reconciles warnings off the v5 read path"),
    "L-279": (1, "its 3E residual pin names snapshot.loader, which step 1 removes"),
    "L-281": (1, "its SysIDE-dependent nodes read the conformance v5 fixtures"),
    "L-135": (1, "its wired-path nodes read the conformance v5 fixtures"),
    "L-292": (1, "subprocess-runs scripts/capture_pipeline_baselines.py, an L-040 deletion"),
    "L-191": (1, "imports the helper in tests/execution/test_constraint_execution.py"),
    "L-193": (1, "imports the helper in tests/execution/test_constraint_execution.py"),
    "L-194": (1, "imports the helper in tests/execution/test_constraint_execution.py"),
    # final-audit F1: the patch-replay test necessarily fails once step 1's patches are
    # applied to HEAD (it asserts unapplied patches replay cleanly). Deleting it in step 1
    # instead of step 4 keeps every boundary at 0 failed. Measured: 1 failed at boundaries
    # 1-3 with the module present, 0 failed at step 4 where L-304 originally deleted it.
    "L-304": (
        1,
        "self-referential: asserts spent step-1 patches still apply; fails from step 1 on",
    ),
}

#: How each disposition executes.
ACTION = {
    "delete": "delete",  # production/fixture/script rows carrying `disposition: delete`
    "migrate": "edit",  # rows that lose named symbols and survive
    "retire-with-owner": "delete",
    "archive-with-findings": "archive",  # move to scripts/archive/, plan rule 7
    "repoint": "edit",
    "defer-to-v5-family": "delete",
}


@dataclass(frozen=True)
class Item:
    """One ledger row placed in the retirement sequence."""

    row: str
    path: str
    step: int | None  # None == the owner-gated fifth entry
    action: str
    disposition: str
    placed_by: str
    node_count: int | None


def _groups_named(breaks_on: str) -> set[str]:
    return set(re.findall(r"4B-[A-Za-z0-9-]+", breaks_on or ""))


def place(row: dict) -> Item | None:
    """Place one ledger row in the sequence, or return None if it needs no action.

    A row needs no action when it is already executed, when its disposition is `retain`,
    or when it is a 4D documentation row (the documentation pass is named in the runbook
    separately, because it is not driven off a disposition column).
    """
    rid = row["id"]
    if row.get("state") == "executed":
        return None
    if rid in OWNER_GATED:
        return Item(
            rid,
            row["path"],
            None,
            "owner-gated",
            row["disposition"],
            "owner-gated: agentic-mbse production call sites, no ledger row",
            row.get("node_count"),
        )

    if rid in PULLED_FORWARD:
        step, why = PULLED_FORWARD[rid]
        return Item(
            rid,
            row["path"],
            step,
            ACTION[row.get("disposition_4c") or row["disposition"]],
            row.get("disposition_4c") or row["disposition"],
            f"simulation: {why}",
            row.get("node_count"),
        )

    group = row.get("group")
    if group in GROUP_STEP:
        return Item(
            rid,
            row["path"],
            GROUP_STEP[group],
            ACTION[row["disposition"]],
            row["disposition"],
            f"group {group}",
            row.get("node_count"),
        )

    disposition_4c = row.get("disposition_4c")
    if not disposition_4c:
        return None

    steps = sorted(
        (GROUP_STEP[g], g) for g in _groups_named(row.get("breaks_on", "")) if g in GROUP_STEP
    )
    if steps:
        step, deciding_group = steps[0]
        placed_by = f"breaks_on {deciding_group}"
    elif rid in DATA_AXIS_STEP:
        step, why = DATA_AXIS_STEP[rid]
        placed_by = f"data axis: {why}"
    else:
        raise SystemExit(
            f"{rid} carries disposition_4c={disposition_4c!r} but names no deletion "
            f"group and has no DATA_AXIS_STEP entry. Place it before running the step."
        )
    return Item(
        rid,
        row["path"],
        step,
        ACTION[disposition_4c],
        disposition_4c,
        placed_by,
        row.get("node_count"),
    )


def _test_module_imports(path: Path) -> set[str]:
    """Every `tests.*` module a test file imports at module level, as a repo-relative path.

    The Gate 4A checker records import edges into *production*; it has no view of one test
    module importing another. That blind spot is what made deleting
    `tests/helpers/legacy_route.py` turn 16 modules into collection errors (audit 4, F1).
    """
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError):
        return set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
    return {
        m.replace(".", "/") + ".py" for m in modules if m == "tests" or m.startswith("tests.")
    }


def tighten_by_test_imports(items: list[Item], repo: Path = REPO_ROOT) -> list[Item]:
    """Pull each test module forward to the step that deletes a test module it imports.

    A module that imports a deleted sibling stops collecting when the sibling goes, so it
    cannot be scheduled later than the sibling. Applied to a fixpoint, because the edges
    chain.
    """
    by_path = {item.path: item for item in items}
    changed = True
    while changed:
        changed = False
        for path, item in list(by_path.items()):
            if item.step is None or item.action != "delete" or not path.startswith("tests/"):
                continue
            for imported in _test_module_imports(repo / path):
                target = by_path.get(imported)
                if target is None or target.step is None or target.action != "delete":
                    continue
                if target.step < item.step:
                    by_path[path] = replace(
                        item,
                        step=target.step,
                        placed_by=f"{item.placed_by}; pulled forward: imports {imported}",
                    )
                    item = by_path[path]
                    changed = True
    return [by_path.get(item.path, item) for item in items]


def load_items(ledger: Path = LEDGER) -> list[Item]:
    rows = json.loads(ledger.read_text())["rows"]
    placed = [item for item in (place(row) for row in rows) if item is not None]
    return tighten_by_test_imports(placed)


def check(items: list[Item], ledger: Path = LEDGER) -> int:
    """Assert the placement is total and unambiguous. Returns a process exit code."""
    rows = json.loads(ledger.read_text())["rows"]
    problems: list[str] = []

    placed = {item.row for item in items}
    if len(placed) != len(items):
        dupes = [r for r, n in Counter(i.row for i in items).items() if n > 1]
        problems.append(f"rows placed more than once: {sorted(dupes)}")

    for row in rows:
        if row.get("state") == "executed" or row["id"] in placed:
            continue
        if row.get("disposition_4c"):
            problems.append(f"{row['id']} has a disposition_4c and no step")
        if row.get("group") in GROUP_STEP:
            problems.append(f"{row['id']} is in a deletion group and has no step")

    by_step = Counter(item.step for item in items)
    print(f"{len(rows)} ledger rows; {len(items)} placed")
    for step in (1, 2, 3, 4, None):
        label = "owner-gated" if step is None else f"step {step}"
        actions = Counter(i.action for i in items if i.step == step)
        print(f"  {label:>12}: {by_step[step]:>3} rows  {dict(sorted(actions.items()))}")
    for problem in problems:
        print(f"PROBLEM {problem}")
    print(f"{len(problems)} problems")
    return 1 if problems else 0


def show_step(items: list[Item], step: int) -> None:
    for item in sorted(
        (i for i in items if i.step == step), key=lambda i: (i.action, i.path)
    ):
        nodes = "" if item.node_count is None else f"  nodes={item.node_count}"
        print(f"{item.row}  {item.action:<7} {item.path}{nodes}   [{item.placed_by}]")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    step_parser = sub.add_parser("step")
    step_parser.add_argument("step", type=int, choices=(1, 2, 3, 4))
    paths_parser = sub.add_parser("paths")
    paths_parser.add_argument("step", type=int, choices=(1, 2, 3, 4))
    paths_parser.add_argument("action", choices=("delete", "archive", "edit"))
    args = parser.parse_args(argv)

    items = load_items()
    if args.cmd == "check":
        return check(items)
    if args.cmd == "step":
        show_step(items, args.step)
        return 0
    for item in sorted(items, key=lambda i: i.path):
        if item.step == args.step and item.action == args.action:
            print(item.path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
