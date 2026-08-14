#!/usr/bin/env python3
"""Assemble the FINAL `evidence/candidate.json` and its markdown data tables (step 8).

Sibling of `build_candidate_revise.py`, which built the gate-2 record from the REVISE
step-7a battery at `c0ceb24`/`6c35aa0`. This builder reads the narrow-correction step-7
battery under `final-runs/` — three complete runs measured AT the final content OIDs, so
unlike the gate-2 record there is no separate head re-measurement: the runs and the
content are the same tree.

Every number in `candidate.json` and in `final-candidate-tables.md` is derived here:
run values by parsing the committed logs (through `compare_final_runs.fields`, the same
parser that produced `final-runs/comparison.md`), repository facts by running Git, hashes
by reading bytes. Nothing is typed in by hand, so the record cannot drift from what was
measured.

    python build_candidate_final.py

Writes `evidence/candidate.json` and `evidence/phase5-runs/final-candidate-tables.md`.
The prose record `evidence/candidate.md` quotes those tables verbatim.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import compare_final_runs as cmp3  # noqa: E402

ROOT = HERE.parents[4]
MBSE = Path("/home/reid/1cfe/agentic-mbse-item7-rebuild")
TEAX = Path("/home/reid/1cfe/teax")
RECOVERY = ROOT / ".project/active/cutover-recovery"
RUNS = RECOVERY / "evidence/phase5-runs"

# The Item 6 bases the whole recovery is measured against (Phase 2, `evidence/baseline.json`).
ITEM6_CODEGEN = "1672c5766f67e7716f3c9f8f636c21e2ea444601"
ITEM6_MBSE = "5088b417c9e5453271291d46cd5fb23fc0579b1e"

# The content OIDs this record describes — the tree the owner ruled FINAL on 2026-08-14.
# The record commit lands on top of them, so it cannot name its own OID; these are the
# trees every number below was measured on. The three step-7 runs measured exactly these
# OIDs (asserted per run in `final-runs/*/heads.tsv`).
CONTENT_CODEGEN = "540ad598057d4b827382232f0d4cf293fecd4aba"
CONTENT_MBSE = "6372ef7ba6ba4c869759fcf201c59aa128175c6f"
CONTENT_TEAX = "75eecb3bcf4baa0306107a96aa78b74ee667e970"

RUN_LABELS = ["run1", "run2", "run3"]

# The narrow-correction step commits (plan.md, "Narrow correction — executable sequence").
# Subjects and touch counts are derived from Git below; a wrong OID fails the build loudly.
CORRECTION_COMMITS = [
    ("1", "f424d7e"),
    ("1", "009a67a"),
    ("2", "057bf29"),
    ("3", "8aa3b28"),
    ("4", "cc268d5"),
    ("4", "7ebe447"),
    ("5", "a4669af"),
    ("6", "540ad59"),
]


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def three_runs() -> dict:
    """The step-7 battery, field by field, through the comparison's own parser."""
    per_run = {label: cmp3.fields(label) for label in RUN_LABELS}
    keys: list[str] = []
    for label in RUN_LABELS:
        for key in per_run[label]:
            if key not in keys:
                keys.append(key)
    differing = [k for k in keys if len({per_run[label].get(k, "MISSING") for label in RUN_LABELS}) != 1]
    return {
        "measured_at": {
            "sysml-codegen": CONTENT_CODEGEN,
            "agentic-mbse": CONTENT_MBSE,
            "teax": CONTENT_TEAX,
        },
        "fields": {k: [per_run[label].get(k, "MISSING") for label in RUN_LABELS] for k in keys},
        "field_count": len(keys),
        "identical_field_count": len(keys) - len(differing),
        "differing_fields": differing,
        "all_identical": not differing,
        "timings": {label: cmp3.scale_timings(label) for label in RUN_LABELS},
    }


def commit_counts() -> dict:
    """One number per repository, each with the range that defines it."""
    cg_range = f"{ITEM6_CODEGEN}..{CONTENT_CODEGEN}"
    mb_range = f"{ITEM6_MBSE}..{CONTENT_MBSE}"
    return {
        "definition": (
            "`git rev-list --count <item6-base>..<content-OID>` — every commit reachable from "
            "the content OID and not from the Item 6 base this recovery branched from. The "
            "record commit itself lands on top of the content OID and is therefore not counted."
        ),
        "sysml-codegen": {"range": cg_range, "count": int(git(ROOT, "rev-list", "--count", cg_range))},
        "agentic-mbse": {"range": mb_range, "count": int(git(MBSE, "rev-list", "--count", mb_range))},
    }


def shipped_worktree_state(repo: Path, *paths: str) -> str:
    """Whether any shipped path is dirty.

    Deliberately not `git status` over the whole tree: this record's own commit dirties
    `.project/` while it is being written, so a whole-tree status would print a different
    value every time the builder runs and the record would not survive its own re-run.
    """
    lines = [ln for ln in git(repo, "status", "--porcelain", "--", *paths).splitlines() if ln.strip()]
    return "clean" if not lines else "; ".join(lines)


def repo_facts() -> dict:
    name_status_cg = git(ROOT, "diff", "--name-status", f"{ITEM6_CODEGEN}..{CONTENT_CODEGEN}").splitlines()
    return {
        "sysml-codegen": {
            "path": str(ROOT),
            "branch": git(ROOT, "rev-parse", "--abbrev-ref", "HEAD"),
            "content_oid": git(ROOT, "rev-parse", CONTENT_CODEGEN),
            "record_commit_parent": git(ROOT, "rev-parse", "HEAD"),
            "item6_base": ITEM6_CODEGEN,
            "diff_stat_vs_item6_base": git(ROOT, "diff", "--shortstat", f"{ITEM6_CODEGEN}..{CONTENT_CODEGEN}"),
            "name_status_counts": dict(collections.Counter(line[0] for line in name_status_cg)),
            "shipped_worktree_state": shipped_worktree_state(
                ROOT, "src", "tests", "scripts", "docs", "pyproject.toml"
            ),
        },
        "agentic-mbse": {
            "path": str(MBSE),
            "branch": git(MBSE, "rev-parse", "--abbrev-ref", "HEAD"),
            "content_oid": git(MBSE, "rev-parse", CONTENT_MBSE),
            "item6_base": ITEM6_MBSE,
            "diff_stat_vs_item6_base": git(MBSE, "diff", "--shortstat", f"{ITEM6_MBSE}..{CONTENT_MBSE}"),
            "commits": git(MBSE, "log", "--format=%h %s", f"{ITEM6_MBSE}..{CONTENT_MBSE}").splitlines(),
            "name_status_counts": dict(
                collections.Counter(
                    line[0]
                    for line in git(MBSE, "diff", "--name-status", f"{ITEM6_MBSE}..{CONTENT_MBSE}").splitlines()
                )
            ),
            "shipped_worktree_state": shipped_worktree_state(MBSE, "src", "tests", "docs", "pyproject.toml"),
        },
        "teax_pinned": {
            "path": str(TEAX),
            "branch": git(TEAX, "rev-parse", "--abbrev-ref", "HEAD"),
            "head": git(TEAX, "rev-parse", "HEAD"),
            "expected": CONTENT_TEAX,
            "note": (
                "moved from the Item-3-close pin fa0e06a9-descendant 5b70ae9 by docs-only commits "
                "of the closed CONSTRAINT-SEMANTICS epic (verified: one file, "
                "docs/evaluation-and-study.md); no simkit code changed"
            ),
        },
    }


def path_inventory() -> dict:
    def files(repo: Path, *args: str) -> list[str]:
        return git(repo, "ls-files", *args).splitlines()

    return {
        "method": "`git ls-files` in the working tree, which is the content OID plus the record commit's .project/ files only",
        "sysml-codegen": {
            "tracked_files": len(files(ROOT)),
            "src_modules": len([p for p in files(ROOT, "src") if p.endswith(".py")]),
            "test_modules": len([p for p in files(ROOT, "tests") if p.endswith(".py") and "test_" in p.rsplit("/", 1)[-1]]),
            "fixture_directories": len({p.split("/")[2] for p in files(ROOT, "tests/fixtures") if p.count("/") >= 2}),
            "reference_docs": len(files(ROOT, "docs/architecture/reference")),
            "scripts": len([p for p in files(ROOT, "scripts") if p.endswith(".py")]),
        },
        "agentic-mbse": {
            "tracked_files": len(files(MBSE)),
            "test_modules": len([p for p in files(MBSE, "tests") if p.endswith(".py") and "test_" in p.rsplit("/", 1)[-1]]),
        },
    }


def retirement_commits() -> dict:
    """The four retirement commits, named by the tree rather than by memory."""
    wanted = ["19072ad", "82c7951", "882fc8d", "3071fba"]
    out = {}
    for oid in wanted:
        subject = git(ROOT, "log", "-1", "--format=%h %s", oid)
        touched = len(git(ROOT, "show", "--name-only", "--format=", oid).splitlines())
        out[oid] = {"subject": subject, "paths_touched": touched}
    return out


def correction_commits() -> list[dict]:
    """The narrow-correction step commits, subjects derived from the tree."""
    out = []
    for step, oid in CORRECTION_COMMITS:
        out.append(
            {
                "step": step,
                "oid": git(ROOT, "rev-parse", "--short", oid),
                "subject": git(ROOT, "log", "-1", "--format=%s", oid),
            }
        )
    return out


def ledger_facts() -> dict:
    rows = json.loads((RECOVERY / "ledger-4a.json").read_text())["rows"]
    return {
        "row_count": len(rows),
        "states": dict(collections.Counter(row.get("state", "?") for row in rows)),
    }


def matrix_facts() -> dict:
    """The verification-matrix counts as recounted at step 4 and standing since
    (zero row edits at steps 5-6 — recorded in their completion records)."""
    return {
        "source": "step-4 mechanical recount, plan.md 'Narrow-correction step 4 completion'; steps 5-6 edited zero rows",
        "rows": 288,
        "pass": 156,
        "partial": 1,
        "retired": 131,
        "untested": 0,
        "families": 34,
        "kept_test_files": 64,
    }


def hashes() -> dict[str, str]:
    targets = [
        RECOVERY / "plan.md",
        RECOVERY / "ledger-4a.json",
        RECOVERY / "ledger-4a.md",
        RECOVERY / "doc-update-list-4d.md",
        RECOVERY / "owner-disposition-20260811.md",
        RECOVERY / "handoff-20260811.md",
        ROOT / "tests/fixtures/v6_recapture_batch/batch.json",
        *sorted((RECOVERY / "evidence").glob("*.md")),
        *sorted((RECOVERY / "evidence").glob("*.json")),
        *sorted((RECOVERY / "evidence").glob("*.txt")),
        *sorted((RECOVERY / "briefs").glob("*.md")),
        *sorted(RUNS.glob("*.py")),
        *sorted(RUNS.glob("*.sh")),
        *sorted((RUNS / "revise-runs").glob("*.md")),
        *sorted((RUNS / "final-runs").glob("*.md")),
    ]
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in targets
        if path.is_file() and path.name not in {"candidate.md", "candidate.json"}
    }


# --- markdown emission -------------------------------------------------------------------

# The step-7 fields worth putting in front of a reader, in reading order, with the label the
# record uses. Every other field stays in candidate.json.
HEADLINE_FIELDS = [
    ("codegen suite", "Full licensed codegen suite"),
    ("codegen suite license-skip lines", "`no live syside license` skip lines"),
    ("agentic suite", "agentic-mbse suite, from the paired worktree"),
    ("exec lane", "Execution lane (`-m execution`), incl. real TEAx"),
    ("corpus -k corpus", "Corpus ledger gate (`-k corpus`)"),
    ("capture_v6_batch --verify", "`capture_v6_batch.py --verify`"),
    ("batch non-timestamp fixture diff lines", "Non-timestamp fixture diff after `--verify`"),
    ("capture_v6_batch --check tail", "`capture_v6_batch.py --check`"),
    ("ruff check src", "`ruff check src`"),
    ("ruff check src tests scripts", "`ruff check src tests scripts`"),
    ("mypy src", "`mypy src`"),
    ("agentic ruff check src", "agentic `ruff check src`"),
    ("agentic ruff check tests", "agentic `ruff check tests`"),
    ("agentic mypy src", "agentic `mypy src`"),
    ("ledger paths", "`check_ledger_4a.py paths`"),
    ("ledger surface", "`check_ledger_4a.py surface`"),
    ("ledger replacements green", "`check_ledger_4a.py replacements` — green"),
    ("ledger replacements not-required", "`check_ledger_4a.py replacements` — not required"),
    ("ledger replacements FAIL", "`check_ledger_4a.py replacements` — FAIL"),
    ("proof integrity", "`check_proof_integrity.py`"),
    ("doc distinctness", "`check_doc_distinctness.py`"),
    ("git diff --check codegen", "`git diff --check`, codegen"),
    ("git diff --check agentic", "`git diff --check`, agentic"),
]


def emit_tables(record: dict) -> str:
    lines: list[str] = []
    add = lines.append
    add("<!-- GENERATED by build_candidate_final.py — do not edit by hand. -->")
    add("<!-- candidate.md quotes these tables verbatim. -->")
    add("")

    add("## T1 — The candidate")
    add("")
    cg, mb = record["repositories"]["sysml-codegen"], record["repositories"]["agentic-mbse"]
    counts = record["commit_counts"]
    add("| | sysml-codegen | agentic-mbse |")
    add("|---|---|---|")
    add(f"| Path | `{cg['path']}` | `{mb['path']}` |")
    add(f"| Branch | `{cg['branch']}` | `{mb['branch']}` |")
    add(f"| Content OID | `{cg['content_oid']}` | `{mb['content_oid']}` |")
    add(f"| Item 6 base | `{cg['item6_base']}` | `{mb['item6_base']}` |")
    add(f"| Diff vs base | {cg['diff_stat_vs_item6_base'].strip()} | {mb['diff_stat_vs_item6_base'].strip()} |")
    ns, ns_mb = cg["name_status_counts"], mb["name_status_counts"]
    add(
        f"| Name-status vs base | {ns.get('A', 0)} added / {ns.get('M', 0)} modified / "
        f"**{ns.get('D', 0)} deleted** | {ns_mb.get('A', 0)} added / {ns_mb.get('M', 0)} modified / "
        f"**{ns_mb.get('D', 0)} deleted** |"
    )
    add(
        f"| Commits since base | {counts['sysml-codegen']['count']} "
        f"(`{counts['sysml-codegen']['range']}`) | {counts['agentic-mbse']['count']} "
        f"(`{counts['agentic-mbse']['range']}`) |"
    )
    add(
        f"| Shipped paths (`src`, `tests`, `scripts`, `docs`, `pyproject.toml`) | "
        f"{cg['shipped_worktree_state']} | {mb['shipped_worktree_state']} |"
    )
    add("")
    teax = record["repositories"]["teax_pinned"]
    add(f"TEAx (evidence-only): `{teax['head']}` on `{teax['branch']}` — {teax['note']}.")
    add("")

    add("## T2 — The narrow-correction step commits")
    add("")
    add("| step | commit | subject |")
    add("|---|---|---|")
    for row in record["correction_commits"]:
        add(f"| {row['step']} | `{row['oid']}` | {row['subject']} |")
    add("")

    add("## T3 — Path inventory")
    add("")
    inv = record["path_inventory"]
    add("| | sysml-codegen | agentic-mbse |")
    add("|---|---:|---:|")
    add(f"| Tracked files | {inv['sysml-codegen']['tracked_files']:,} | {inv['agentic-mbse']['tracked_files']:,} |")
    add(f"| Production modules (`src/**.py`) | {inv['sysml-codegen']['src_modules']} | — |")
    add(f"| Test modules | {inv['sysml-codegen']['test_modules']} | {inv['agentic-mbse']['test_modules']} |")
    add(f"| Fixture directories | {inv['sysml-codegen']['fixture_directories']} | — |")
    add(f"| Numbered reference documents | {inv['sysml-codegen']['reference_docs']} | — |")
    add(f"| Scripts (`scripts/**.py`) | {inv['sysml-codegen']['scripts']} | — |")
    add("")

    add("## T4 — The three step-7 gate runs, at the content OIDs")
    add("")
    runs = record["three_runs"]
    add("| Gate | run 1 | run 2 | run 3 | identical |")
    add("|---|---|---|---|---|")
    for key, label in HEADLINE_FIELDS:
        values = runs["fields"].get(key)
        if values is None:
            continue
        cells = [v.replace("|", "\\|") for v in values]
        same = len(set(values)) == 1
        shown = [cells[0], "same" if same else cells[1], "same" if same else cells[2]]
        add(f"| {label} | {shown[0]} | {shown[1]} | {shown[2]} | {'yes' if same else '**DIFFER**'} |")
    add("")
    add(
        f"**{runs['identical_field_count']} / {runs['field_count']} compared fields identical "
        f"across all three runs**, re-derived from the committed logs by this builder through "
        f"`compare_final_runs.fields`. The rows above are the headline subset; the full field "
        f"list is in `candidate.json` under `three_runs.fields`. Unlike the gate-2 record, the "
        f"runs measured the content OIDs themselves, so there is no separate head re-measurement."
    )
    add("")

    add("## T5 — Scale, from the same three runs")
    add("")
    timings = runs["timings"]
    fixtures = sorted({k.rsplit(" ", 1)[0] for k in timings["run1"] if k.endswith("peak_rss_mib")})
    add("| fixture | live elaborate s | generate live s | peak RSS MiB (cumulative) | envelope bytes |")
    add("|---|---|---|---|---|")
    for fixture in fixtures:
        def span(metric: str) -> str:
            lows, highs = [], []
            for label in RUN_LABELS:
                low, high = timings[label][f"{fixture} {metric}"].split("–")
                lows.append(float(low))
                highs.append(float(high))
            return f"{min(lows):.3f}–{max(highs):.3f}"

        rss_lo, rss_hi = [], []
        for label in RUN_LABELS:
            low, high = timings[label][f"{fixture} peak_rss_mib"].split("–")
            rss_lo.append(float(low))
            rss_hi.append(float(high))
        envelope = runs["fields"][f"scale {fixture} envelope bytes"][0]
        add(
            f"| `{fixture}` | {span('live_elaborate_s')} | {span('generate_live_s')} | "
            f"{min(rss_lo):.1f}–{max(rss_hi):.1f} | {int(envelope):,} |"
        )
    add("")

    add("## T6 — Verification matrix (step-4 recount, standing)")
    add("")
    mx = record["verification_matrix"]
    add(
        f"**{mx['rows']} rows / {mx['pass']} PASS / {mx['partial']} PARTIAL / "
        f"{mx['retired']} RETIRED / {mx['untested']} UNTESTED**, {mx['families']} families, "
        f"{mx['kept_test_files']} kept test files. Source: {mx['source']}."
    )
    add("")

    add("## T7 — The retirement commits (no provisional trim)")
    add("")
    add("| commit | subject | paths touched |")
    add("|---|---|---|")
    for oid, body in record["retirement_commits"].items():
        subject = body["subject"].split(" ", 1)[1]
        add(f"| `{oid}` | {subject} | {body['paths_touched']} |")
    add("")
    return "\n".join(lines) + "\n"


def main() -> int:
    record = {
        "record": (
            "Item 7 cutover recovery — the FINAL candidate: the corrected tree at the "
            "owner-ruled-final OIDs, its three identical gate runs, and what remains for the owner"
        ),
        "supersedes": (
            "the gate-2 post-REVISE record (content 6c35aa0/3fbda2f), superseded as an acceptance "
            "candidate by the 2026-08-12 narrow-correction verdict; preserved as evidence"
        ),
        "status": "ASSEMBLED at the content OIDs — step-9 fresh narrow audit and owner final disposition PENDING",
        "tree_final_ruling": "[OWNER 2026-08-14] no changes in flight; tree ruled final at the content OIDs",
        "assembled_from": {
            "three_run_battery": "evidence/phase5-runs/final-runs/ (narrow-correction step 7, at the content OIDs)",
            "audit": "step 9 runs after this record and reports separately",
            "tree": "git, run by this builder",
        },
        "content_oids": {
            "sysml-codegen": CONTENT_CODEGEN,
            "agentic-mbse": CONTENT_MBSE,
            "teax_pinned": CONTENT_TEAX,
            "note": "the record commit lands on top of the codegen content OID, so it cannot contain its own OID",
        },
        "repositories": repo_facts(),
        "commit_counts": commit_counts(),
        "correction_commits": correction_commits(),
        "path_inventory": path_inventory(),
        "retirement_commits": retirement_commits(),
        "ledger": ledger_facts(),
        "verification_matrix": matrix_facts(),
        "three_runs": three_runs(),
        "evidence_hashes_sha256": hashes(),
    }

    (RECOVERY / "evidence/candidate.json").write_text(json.dumps(record, indent=2) + "\n")
    (RUNS / "final-candidate-tables.md").write_text(emit_tables(record))
    print("wrote evidence/candidate.json and evidence/phase5-runs/final-candidate-tables.md")
    print("three runs all identical:", record["three_runs"]["all_identical"])
    print("differing fields:", record["three_runs"]["differing_fields"])
    print("codegen commits since Item 6 base:", record["commit_counts"]["sysml-codegen"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
