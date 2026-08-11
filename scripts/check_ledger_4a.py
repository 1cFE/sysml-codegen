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

**Surface coverage.** Gate 4C part 3. The path check above proves every path the candidate
*touched* has a row. It says nothing about a file the candidate never touched that a future
deletion group will break. Two such files were found by hand at Gate 4B-G2 —
``test_generation_boundary.py`` and ``test_pipeline_e2e.py``, both importing a delete-row
symbol at module level with no ledger row at all. ``check_surface_coverage`` closes that
class: it derives the removal surface from the ledger's own delete and migrate rows, walks
``tests/`` and ``scripts/`` by AST, and fails for any file that imports the surface at
module level (so it stops collecting) without a row saying what becomes of it.

**What this checker cannot see.** Four ceilings, measured by the Phase 4 composite audit (F7)
by attacking the machinery rather than reading it. They are limits, not defects: read a green
run as "these four classes are unchecked", never as "the ledger is true".

1. **Transitive import breakage is invisible.** ``surface_hits`` walks each file's own AST, so
   a file that breaks because a *helper it imports* breaks is not seen. Measured: the checker
   reports 2 surviving files broken at module level by ``4B-G4``; deleting
   ``tests/helpers/legacy_route.py`` actually stops 16 modules collecting. The detector for
   this class is executing the step in a scratch worktree and running the suite, which is what
   the runbook's per-step simulations do.
2. **``group_readiness`` clears on the disposition *label*, not on measurement.**
   ``check_surface_coverage`` skips any path that has a row at all, so a ``repoint`` row clears
   its group whether or not the repoint was performed. "All six groups READY" means 187
   hand-authored labels say the files are handled. One of them (L-298) was false.
3. **Vacuity is undetectable, and 89 proof entries name a whole file.** ``replacement_is_green``
   runs the node and looks for ``passed``; a node that exists and asserts nothing is green. For
   the 89 entries (32 distinct files) that name a file rather than a ``::node``, "green" means
   "that file passes", usually true regardless of whether it covers the retired responsibility.
   The per-node accounting that carries that weight lives in prose on the rows.
4. **A textual data scan misses computed filenames.** ``data_hits`` matches literal basenames,
   so a path built by f-string or reached by ``glob("*.json")`` is missed. The over-reporting
   posture on the non-module axis is the deliberate trade.

Usage::

    python scripts/check_ledger_4a.py paths
    python scripts/check_ledger_4a.py replacements [--row L-001 ...]
    python scripts/check_ledger_4a.py surface
    python scripts/check_ledger_4a.py groups
"""

from __future__ import annotations

import argparse
import ast
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


#: Directories whose files must have a row before a deletion group may break them.
SCANNED_TREES = ("tests", "scripts")
#: Files the retirement preserves as records rather than as live code (plan rule 7). They keep
#: their ledger row under their original path and carry ``archived_to``; scanning them for the
#: removal surface would report the very legacy names they exist to remember.
ARCHIVE_DIR = "scripts/archive"


@dataclass(frozen=True)
class Owner:
    """The row that removes one piece of surface, and the group that spends it."""

    row_id: str
    group: str


@dataclass(frozen=True)
class Surface:
    """What the remaining deletion groups take away, keyed for import matching.

    ``modules`` are dotted module names that stop existing. ``symbols`` maps a surviving
    module to the names it stops exporting. ``owners`` maps every key in either to the row
    that removes it, so a hit can always name its authority.
    """

    modules: frozenset[str]
    symbols: dict[str, frozenset[str]]
    owners: dict[str, Owner]


def _dotted(path: str) -> str:
    stem = path[: -len(".py")]
    if stem.startswith("src/"):
        stem = stem[len("src/") :]
    if stem.endswith("/__init__"):
        stem = stem[: -len("/__init__")]
    return stem.replace("/", ".")


def removal_surface(
    ledger: dict, only_groups: frozenset[str] | None = None
) -> Surface:
    """Derive what the unspent deletion groups remove, from the rows themselves.

    A ``delete`` row removes its whole module. A ``migrate`` row removes only the names its
    ``removes`` blocks list, each block naming the group that spends it — machine-readable
    rather than prose, because the checker must not have to parse a reason paragraph to know
    what goes away, and because one row can now split across groups: Gate 4C part 3 measured
    that ``snapshot/__init__`` drops its three read-path re-exports in G2 while its three
    write-path ones stay until the v5 family retires. Rows already spent are excluded — they
    removed what they removed, and the tree agrees.

    ``only_groups`` narrows the surface to the groups named, which is how a caller asks the
    question "what breaks if *this* group runs" rather than "what breaks eventually".
    """
    modules: set[str] = set()
    symbols: dict[str, set[str]] = {}
    owners: dict[str, Owner] = {}

    def record_module(module: str, owner: Owner) -> None:
        modules.add(module)
        owners[module] = owner

    for row in ledger["rows"]:
        if row.get("state") == "executed":
            continue
        if not row["path"].endswith(".py"):
            continue
        module = _dotted(row["path"])
        group = row.get("group") or ""
        if row["disposition"] == "delete" and group:
            if only_groups is None or group in only_groups:
                record_module(module, Owner(row["id"], group))
        for block in row.get("removes", []):
            block_group = block["group"]
            if only_groups is not None and block_group not in only_groups:
                continue
            owner = Owner(row["id"], block_group)
            if block["symbols"] == ["*"]:
                record_module(module, owner)
                continue
            symbols.setdefault(module, set()).update(block["symbols"])
            for name in block["symbols"]:
                owners[f"{module}:{name}"] = owner

    return Surface(
        frozenset(modules),
        {module: frozenset(names) for module, names in symbols.items()},
        owners,
    )


def data_surface(
    ledger: dict, only_groups: frozenset[str] | None = None
) -> dict[str, Owner]:
    """What a deletion group removes that is *not* an importable module.

    Gate 4C part 3 measured one axis — imports of ``src/`` modules — and Part B step 1 walked
    into the two it missed. A test can depend on a delete row by reading its bytes
    (``tests/fixtures/<name>/extraction_snapshot.json``) or by importing a *script* that is
    itself a row (``from scripts.capture_extraction_snapshots import MODELS``). Neither is an
    import of a package module, so neither was visible.

    Keys are the token a dependent would have to name: a removed data file's basename, or
    ``scripts.<stem>`` for a removed script.
    """
    owners: dict[str, Owner] = {}
    for row in ledger["rows"]:
        if row.get("state") == "executed" or row["disposition"] != "delete":
            continue
        group = row.get("group") or ""
        if only_groups is not None and group not in only_groups:
            continue
        path = row["path"]
        if path.endswith(".py"):
            if path.startswith("scripts/"):
                stem = path[len("scripts/") : -len(".py")].replace("/", ".")
                owners[f"scripts.{stem}"] = Owner(row["id"], group)
            continue
        owners[Path(path).name] = Owner(row["id"], group)
    return owners


def data_hits(repo: Path, surface: dict[str, Owner]) -> dict[str, dict[str, str]]:
    """Map each file to the non-module surface tokens its source names.

    Deliberately textual and therefore conservative: a glob, an f-string, a subprocess
    argument and a docstring all count. Under-reporting here is what produced the Part B
    stop, and a gate that must not under-report is allowed to over-report.
    """
    hits: dict[str, dict[str, str]] = {}
    for tree in SCANNED_TREES:
        for file in sorted((repo / tree).rglob("*.py")):
            if str(file.relative_to(repo)).startswith(ARCHIVE_DIR):
                continue
            try:
                source = file.read_text()
            except UnicodeDecodeError:
                continue
            relative = str(file.relative_to(repo))
            found = {}
            for token, owner in surface.items():
                if token.startswith("scripts."):
                    stem = token[len("scripts.") :]
                    named = f"import {token}" in source or f"from {token} " in source
                    named = named or f"scripts/{stem.replace('.', '/')}.py" in source
                    if named and relative != f"scripts/{stem.replace('.', '/')}.py":
                        found[token] = "script-import"
                elif token in source and relative != f"{tree}/{token}":
                    found[token] = "data-read"
            if found:
                hits[relative] = found
    return hits


def check_data_surface_coverage(ledger: dict, repo: Path = REPO_ROOT) -> list[str]:
    """Fail for any file that reads a delete row's bytes or imports it, with no row."""
    surface = data_surface(ledger)
    rows = {row["path"] for row in ledger["rows"]}
    problems = []
    for path, found in sorted(data_hits(repo, surface).items()):
        if path in rows:
            continue
        authorities = ", ".join(
            f"{token} ({surface[token].row_id}, {surface[token].group})"
            for token in sorted(found)
        )
        problems.append(
            f"unrowed data breakage: {path} depends on removed non-module surface "
            f"— {authorities}"
        )
    return problems


def _import_keys(node: ast.stmt, surface: Surface) -> set[str]:
    """Which surface keys one import statement depends on."""
    keys: set[str] = set()
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if module in surface.modules:
            keys.add(module)
        for alias in node.names:
            if f"{module}.{alias.name}" in surface.modules:
                keys.add(f"{module}.{alias.name}")
            if alias.name in surface.symbols.get(module, ()):
                keys.add(f"{module}:{alias.name}")
    elif isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name in surface.modules:
                keys.add(alias.name)
    return keys


def surface_hits(repo: Path, surface: Surface) -> dict[str, dict[str, str]]:
    """Map each affected file to its surface keys and the depth of the dependency.

    ``module`` means the import sits at module level, so the whole file stops collecting.
    ``func`` means it is inside a function, so only the nodes that run it fail.
    """
    hits: dict[str, dict[str, str]] = {}
    for tree in SCANNED_TREES:
        for file in sorted((repo / tree).rglob("*.py")):
            if str(file.relative_to(repo)).startswith(ARCHIVE_DIR):
                continue
            try:
                parsed = ast.parse(file.read_text())
            except (SyntaxError, UnicodeDecodeError):
                continue
            found: dict[str, str] = {}
            for node in ast.walk(parsed):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                for key in _import_keys(node, surface):
                    found.setdefault(key, "func")
            for node in parsed.body:
                for key in _import_keys(node, surface):
                    found[key] = "module"
            if found:
                hits[str(file.relative_to(repo))] = found
    return hits


def check_surface_coverage(ledger: dict, repo: Path = REPO_ROOT) -> list[str]:
    """Fail for any file a pending deletion group breaks at import time with no row.

    Module-level only. A function-local import breaks nodes, not collection, and the
    reviewer sees it as a test failure; a module-level one silently removes the whole
    file's coverage from the run, which is the failure mode this check exists for.
    """
    surface = removal_surface(ledger)
    rows = {row["path"] for row in ledger["rows"]}
    problems: list[str] = []
    for path, found in sorted(surface_hits(repo, surface).items()):
        broken = sorted(key for key, depth in found.items() if depth == "module")
        if not broken or path in rows:
            continue
        authorities = ", ".join(
            f"{key} ({surface.owners[key].row_id}, {surface.owners[key].group})"
            for key in broken
        )
        problems.append(
            f"unrowed breakage: {path} imports removed surface at module level "
            f"— {authorities}"
        )
    return problems


#: Gate 4C part 3 dispositions. ``retire-with-owner``, ``repoint`` and
#: ``archive-with-findings`` clear a group; ``defer-to-v5-family`` blocks it, because the
#: file still holds live coverage.
#:
#: ``archive-with-findings`` is Gate 4C part 7's addition, for plan rule 7: a probe or spike
#: carries no test node, so it loses no coverage when its owner goes, but erasing it to
#: satisfy a residue scan is exactly what the rule forbids. The file is preserved and its
#: finding is named on the row, so the disposition is neither a retirement nor a repoint and
#: recording it as either would misstate what happens. It clears a group because a script
#: that no longer runs blocks no deletion.
CLEARING_4C = frozenset({"retire-with-owner", "repoint", "archive-with-findings"})


@dataclass(frozen=True)
class GroupReadiness:
    """Whether one deletion group may run, and exactly what is holding it if not."""

    group: str
    affected: int
    blockers: tuple[str, ...]

    @property
    def is_ready(self) -> bool:
        return not self.blockers


def group_readiness(ledger: dict, group: str, repo: Path = REPO_ROOT) -> GroupReadiness:
    """A group may run only when every file its surface breaks is disposed of.

    This is plan rule 6 made mechanical: a file whose Gate 4C part 3 disposition is
    ``defer-to-v5-family`` still holds coverage nothing replaces, so deleting the owner it
    depends on would delete that coverage. The group is blocked until the disposition
    changes, and the blocker list says by what.
    """
    only = frozenset({group})
    rows = {row["path"]: row for row in ledger["rows"]}
    # Both axes, because a group is just as blocked by a file that reads a removed
    # fixture's bytes as by one that imports a removed module. Readiness measured on
    # imports alone is what let Part B step 1 walk into the second axis; the ``paths``
    # check has measured both since Gate 4C part 5 and this now agrees with it.
    hits = set(surface_hits(repo, removal_surface(ledger, only)))
    hits |= set(data_hits(repo, data_surface(ledger, only)))
    blockers = tuple(
        f"{rows[path]['id'] if path in rows else 'NO ROW'} {path}"
        for path in sorted(hits)
        if rows.get(path, {}).get("disposition_4c") not in CLEARING_4C
    )
    return GroupReadiness(group, len(hits), blockers)


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
        # that already happened, which `check_states` verifies from the other side. The
        # probe is the worktree rather than HEAD so that a row added in the same commit as
        # the file it names is not a false failure; an unauthorised deletion still fails,
        # because the file is gone from the worktree too.
        executed_delete = row.get("state") == "executed" and _authorises_absence(row)
        present = (REPO_ROOT / row["path"]).exists()
        if row["repo"] == "sysml-codegen" and not executed_delete and not present:
            problems.append(
                f"{row['id']}: carried row {row['path']} does not exist at HEAD"
            )

    problems.extend(check_states(rows))
    problems.extend(check_surface_coverage(ledger))
    problems.extend(check_data_surface_coverage(ledger))

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

#: Gate 4C dispositions that take a file out of the tree, alongside a plain ``delete``. A
#: ``retire-with-owner`` row carries ``disposition: retain`` from Gate 4A — the Gate 4C
#: disposition is what authorises its absence, and the state check has to read both or the
#: whole test-side retirement reads as an unauthorised deletion.
ABSENCE_DISPOSITIONS_4C = frozenset({"retire-with-owner", "archive-with-findings"})


def _authorises_absence(row: dict) -> bool:
    return (
        row["disposition"] == "delete" or row.get("disposition_4c") in ABSENCE_DISPOSITIONS_4C
    )


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
        # Gate 4C part 7: an archive disposition is only honest if the finding has a
        # durable home outside the file being archived. Requiring the path here is what
        # stops "archive-with-findings" degrading into a polite word for deletion.
        if row.get("disposition_4c") == "archive-with-findings" and not row.get(
            "findings_home"
        ):
            problems.append(
                f"{row['id']}: archive-with-findings names no findings_home"
            )
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
        if _authorises_absence(row) and present:
            problems.append(
                f"{row['id']}: executed delete but {row['path']} is still at HEAD"
            )
        survives = not _authorises_absence(row) and row["disposition"] in {"migrate", "retain"}
        if survives and not present:
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
    parser.add_argument("mode", choices=["paths", "replacements", "surface", "groups"])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--row", action="append", default=[])
    args = parser.parse_args(argv)

    ledger = load_ledger()

    if args.mode == "groups":
        groups = sorted(
            {row["group"] for row in ledger["rows"] if (row.get("group") or "").startswith("4B-")}
        )
        for group in groups:
            readiness = group_readiness(ledger, group)
            state = "READY" if readiness.is_ready else f"BLOCKED by {len(readiness.blockers)}"
            print(f"{group:16s} affected={readiness.affected:3d}  {state}")
            for blocker in readiness.blockers:
                print(f"                 blocked by {blocker}")
        return 0

    if args.mode == "surface":
        problems = check_surface_coverage(ledger) + check_data_surface_coverage(ledger)
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"{len(problems)} unrowed breakages")
        return 1 if problems else 0

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
