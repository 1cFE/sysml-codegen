"""Gate 4A ledger checker: exact path-set equality, and real replacement proof.

Two independent checks, both of which the original Item 7 census failed.

**Path-set equality.** The candidate set is derived from a Git *diff*, never from the
worktree. A worktree scan cannot see a deleted file, which is how 118 changed paths went
unrecorded the first time. Every path the forensic candidate deleted, plus every
architecture document and ``CLAUDE.md`` it modified, must have exactly one ledger row, and
every ledger row must either be in that set or be an explicitly carried row that still
exists at ``HEAD``.

**Replacement proof.** ``replacement_is_green`` runs the named pytest node and reports what
actually happened: it collected and passed, it does not exist, it was deselected, or it
failed. A row whose replacement is absent cannot be green, which is the rule the original
run inverted when it accepted absence as proof.

Usage::

    python scripts/check_ledger_4a.py paths
    python scripts/check_ledger_4a.py replacements [--row L-001 ...]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_JSON = REPO_ROOT / ".project/active/cutover-recovery/ledger-4a.json"

#: Row origins that must appear in the Git-derived candidate set.
DIFF_ORIGINS = frozenset({"forensic-diff"})
#: Row origins that must exist at HEAD but must not be in the candidate set.
CARRIED_ORIGINS = frozenset(
    {"phase3-carried", "derived-blast-radius", "phase3-carried-crossrepo"}
)


def git(*args: str, repo: Path = REPO_ROOT) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


def load_ledger(path: Path = LEDGER_JSON) -> dict:
    ledger: dict = json.loads(path.read_text())
    return ledger


def git_candidate_set(base: str, candidate: str) -> set[str]:
    """Every path the candidate retires or rewrites, read from the diff itself.

    Deletions are visible here and invisible to any worktree scan, which is the whole
    reason this function exists.
    """
    paths: set[str] = set()
    for line in git("diff", "--name-status", base, candidate).splitlines():
        status, _, path = line.partition("\t")
        status, path = status.strip(), path.strip()
        if status == "D":
            paths.add(path)
        elif status == "M" and (
            path.startswith("docs/architecture/") or path == "CLAUDE.md"
        ):
            paths.add(path)
    return paths


def path_at_head(path: str, repo: Path = REPO_ROOT) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"HEAD:{path}"],
            capture_output=True,
        ).returncode
        == 0
    )


def check_paths(ledger: dict) -> list[str]:
    """Exact equality in both directions, plus row well-formedness."""
    source = ledger["git_derived_from"]
    derived = git_candidate_set(source["base"], source["candidate"])
    rows = ledger["rows"]

    problems: list[str] = []

    seen: set[str] = set()
    for row in rows:
        if row["path"] in seen:
            problems.append(f"duplicate row for {row['path']}")
        seen.add(row["path"])

    covered = {row["path"] for row in rows if row["origin"] in DIFF_ORIGINS}
    for path in sorted(derived - covered):
        problems.append(f"uncovered path (in the diff, no ledger row): {path}")
    for path in sorted(covered - derived):
        problems.append(f"orphan row (claims the diff, not in it): {path}")

    for row in rows:
        origin = row["origin"]
        if origin in DIFF_ORIGINS:
            continue
        if origin not in CARRIED_ORIGINS:
            problems.append(f"{row['id']}: unknown origin {origin!r}")
            continue
        if row["path"] in derived:
            problems.append(
                f"{row['id']}: carried origin {origin!r} but the path is in the diff — "
                "it must claim the diff instead"
            )
        # A carried row must still be in the tree — unless its own deletion is the thing
        # that already happened, which `check_states` verifies from the other side.
        executed_delete = row.get("state") == "executed" and row["disposition"] == "delete"
        if row["repo"] == "sysml-codegen" and not executed_delete and not path_at_head(row["path"]):
            problems.append(
                f"{row['id']}: carried row {row['path']} does not exist at HEAD"
            )

    problems.extend(check_states(rows))

    ids = {row["id"] for row in rows}
    for row in rows:
        for blocker in row.get("blocked_by", []):
            if blocker not in ids:
                problems.append(f"{row['id']}: blocked_by names unknown row {blocker}")
        if row["disposition"] not in {"delete", "migrate", "retain", "archive"}:
            problems.append(f"{row['id']}: unknown disposition {row['disposition']!r}")
        if not row.get("reason"):
            problems.append(f"{row['id']}: no reason recorded")

    return problems


#: A row is ``proposed`` until its Gate 4B group runs. It becomes ``executed`` with the OID
#: of the commit that spent it, or ``partially-executed`` when its group takes only part of
#: the row and a later group takes the rest — the shape several 4B-G0 rows have, where the
#: two error classes move now and the module they lived in retires in G3. Absent means
#: ``proposed``, so Gate 4A's rows need no edit.
ROW_STATES = frozenset({"proposed", "executed", "partially-executed"})


def check_states(rows: list[dict]) -> list[str]:
    """A spent row must name its commit, and the tree must agree with what it says.

    This is the same discipline the path check applies to the candidate: a state claim is
    checked against Git, not believed. An executed ``delete`` row whose file is still at
    ``HEAD`` did not happen; an executed ``migrate`` or ``retain`` row whose file is gone
    deleted something the ledger never authorised. A ``partially-executed`` row must say
    what is left and which group owes it, and its path must still be there — an unstated
    remainder is how the original run lost track of what it had actually done.
    """
    problems: list[str] = []
    for row in rows:
        state = row.get("state", "proposed")
        if state not in ROW_STATES:
            problems.append(f"{row['id']}: unknown state {state!r}")
            continue
        if state == "proposed":
            if row.get("executed_commit"):
                problems.append(f"{row['id']}: proposed row names an executed_commit")
            continue
        if not row.get("executed_commit"):
            problems.append(f"{row['id']}: {state} row names no commit")
        if state == "partially-executed" and not row.get("remaining"):
            problems.append(f"{row['id']}: partially-executed row does not say what is left")
        if row["repo"] != "sysml-codegen":
            continue
        present = path_at_head(row["path"])
        if state == "partially-executed":
            if not present:
                problems.append(
                    f"{row['id']}: partially-executed but {row['path']} is gone from HEAD"
                )
            continue
        if row["disposition"] == "delete" and present:
            problems.append(
                f"{row['id']}: executed delete but {row['path']} is still at HEAD"
            )
        if row["disposition"] in {"migrate", "retain"} and not present:
            problems.append(
                f"{row['id']}: executed {row['disposition']} but {row['path']} is gone from HEAD"
            )
    return problems


class Verdict(Enum):
    GREEN = "green"
    MISSING = "missing"
    DESELECTED = "deselected"
    FAILED = "failed"
    PENDING = "pending"
    NOT_REQUIRED = "not-required"


@dataclass(frozen=True)
class Proof:
    verdict: Verdict
    detail: str

    @property
    def is_green(self) -> bool:
        return self.verdict is Verdict.GREEN


def _pytest(node: str, python: str, extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    return subprocess.run(
        [python, "-m", "pytest", *extra, node],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


#: Suites a row may name, and the marker expression each one runs under.
SUITES = {None: (), "default": (), "execution": ("-m", "execution")}


def replacement_is_green(
    node: str | list[str] | None,
    python: str = sys.executable,
    required_suite: str | None = None,
) -> Proof:
    """Resolve a row's named replacement node and report what it actually did.

    ``None`` means the row deletes nothing, so no replacement is owed.
    ``PENDING-4C:`` means the replacement has not been authored yet — a real answer, and
    never a green one. A list means the responsibility is carried by several nodes, as
    C1's ruling carries signature preservation: every one of them must be green, and the
    first that is not is the verdict.
    """
    if isinstance(node, list):
        if not node:
            return Proof(Verdict.MISSING, "empty replacement node list")
        proofs = [replacement_is_green(one, python, required_suite) for one in node]
        failed = next((proof for proof in proofs if not proof.is_green), None)
        if failed is not None:
            return failed
        return Proof(Verdict.GREEN, "; ".join(proof.detail for proof in proofs))
    if node is None:
        return Proof(Verdict.NOT_REQUIRED, "row deletes nothing")
    if node.startswith("PENDING-4C"):
        return Proof(Verdict.PENDING, node)
    if required_suite not in SUITES:
        return Proof(Verdict.MISSING, f"unknown required suite {required_suite!r}")
    suite = SUITES[required_suite]

    collected = _pytest(node, python, (*suite, "--collect-only", "-q"))
    collected_tail = _tail(collected.stdout)
    if collected.returncode not in (0, 5):
        return Proof(Verdict.MISSING, f"collection failed: {collected_tail}")
    if "no tests collected" in collected_tail or collected.returncode == 5:
        if "deselected" in collected_tail:
            return Proof(Verdict.DESELECTED, collected_tail)
        return Proof(Verdict.MISSING, collected_tail or "node resolves to nothing")

    ran = _pytest(node, python, (*suite, "-q"))
    tail = _tail(ran.stdout)
    if ran.returncode == 5:
        return Proof(Verdict.DESELECTED, tail or "no tests ran")
    if ran.returncode != 0:
        return Proof(Verdict.FAILED, tail)
    if " passed" not in tail:
        return Proof(Verdict.FAILED, f"exit 0 without a passing summary: {tail}")
    return Proof(Verdict.GREEN, tail)


def _tail(stdout: str) -> str:
    lines = [line for line in stdout.strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""


def check_replacements(ledger: dict, python: str, only: set[str] | None) -> list[tuple[str, Proof]]:
    results = []
    for row in ledger["rows"]:
        if only and row["id"] not in only:
            continue
        if row["repo"] != "sysml-codegen":
            continue
        results.append(
            (
                row["id"],
                replacement_is_green(
                    row["replacement_proof_node"], python, row.get("required_suite")
                ),
            )
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["paths", "replacements"])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--row", action="append", default=[])
    args = parser.parse_args(argv)

    ledger = load_ledger()

    if args.mode == "paths":
        problems = check_paths(ledger)
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"{len(ledger['rows'])} rows checked, {len(problems)} problems")
        return 1 if problems else 0

    only = set(args.row) or None
    failures = 0
    for row_id, proof in check_replacements(ledger, args.python, only):
        if proof.verdict in {Verdict.MISSING, Verdict.DESELECTED, Verdict.FAILED}:
            failures += 1
            print(f"FAIL {row_id} {proof.verdict.value}: {proof.detail}")
        else:
            print(f"{proof.verdict.value:12s} {row_id} {proof.detail}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
