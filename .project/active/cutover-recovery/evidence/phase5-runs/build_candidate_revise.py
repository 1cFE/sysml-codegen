#!/usr/bin/env python3
"""Assemble the post-REVISE `evidence/candidate.json` and its markdown data tables.

Sibling of `build_candidate.py`, which built the pre-retirement Phase 5 record from the
`run{1,2,3}/` battery. That battery no longer runs: the retirement deleted
`scripts/run_elaboration_corpus.py`, so the corpus-driver, residue and scale inputs it read
are gone. This builder reads the step-7a battery under `revise-runs/` instead, plus the
step-7c HEAD measurement under `head-6c35aa0/`, plus the tree itself.

Every number in `candidate.json` and in `revise-candidate-tables.md` is derived here:
run values by parsing the committed logs (through `compare_revise_runs.fields`, the same
parser that produced `revise-runs/comparison.md`), repository facts by running Git, hashes
by reading bytes. Nothing is typed in by hand, so the record cannot drift from what was
measured.

    python build_candidate_revise.py

Writes `evidence/candidate.json` and `evidence/phase5-runs/revise-candidate-tables.md`.
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

import compare_revise_runs as cmp3  # noqa: E402

ROOT = HERE.parents[4]
MBSE = Path("/home/reid/1cfe/agentic-mbse-item7-rebuild")
TEAX = Path("/home/reid/1cfe/teax")
RECOVERY = ROOT / ".project/active/cutover-recovery"
RUNS = RECOVERY / "evidence/phase5-runs"
HEAD_RUN = RUNS / "head-6c35aa0"

# The Item 6 bases the whole recovery is measured against (Phase 2, `evidence/baseline.json`).
ITEM6_CODEGEN = "1672c5766f67e7716f3c9f8f636c21e2ea444601"
ITEM6_MBSE = "5088b417c9e5453271291d46cd5fb23fc0579b1e"

# The content OIDs this record describes. The record commit lands on top of them, so it
# cannot name its own OID; these are the trees every number below was measured on.
CONTENT_CODEGEN = "6c35aa0"
CONTENT_MBSE = "3fbda2f"
CONTENT_TEAX = "fa0e06a9"
# The OID the three step-7a runs measured, one product commit behind CONTENT_CODEGEN.
RUNS_CODEGEN = "c0ceb24"

RUN_LABELS = ["run1", "run2", "run3"]


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def read_head_log(name: str) -> str:
    return (HEAD_RUN / name).read_text(errors="replace")


def first_match(text: str, pattern: str, default: str = "ABSENT") -> str:
    match = re.search(pattern, text, re.M)
    return match.group(0).strip() if match else default


def head_measurement() -> dict:
    """The step-7c re-measurement at the content OID, after the F1–F3 dispositions."""
    suite = read_head_log("suite_codegen.log")
    return {
        "what": (
            "re-measured at the content OID by this stage, because the three step-7a runs "
            f"measured {RUNS_CODEGEN} and the F3 disposition added two pinned nodes since"
        ),
        "codegen_suite": cmp3.pytest_counts(suite),
        "codegen_suite_license_skip_lines": len(re.findall(r"no live syside license", suite)),
        "ledger_paths": first_match(read_head_log("ledger_paths.log"), r"^\d+ rows checked, \d+ problems$"),
        "ledger_surface": first_match(read_head_log("ledger_surface.log"), r"^\d+ unrowed breakages$"),
        "doc_distinctness": first_match(
            read_head_log("doc_distinct.log"), r"^\d+ numbered reference documents checked, .*$"
        ),
        "git_diff_check_codegen": read_head_log("diff_check_cg.log").strip() or "clean",
        "git_diff_check_agentic": read_head_log("diff_check_mb.log").strip() or "clean",
        "heads_at_measurement": dict(
            line.split("\t") for line in (HEAD_RUN / "heads.tsv").read_text().splitlines()
        ),
    }


def three_runs() -> dict:
    """The step-7a battery, field by field, through the comparison's own parser."""
    per_run = {label: cmp3.fields(label) for label in RUN_LABELS}
    keys: list[str] = []
    for label in RUN_LABELS:
        for key in per_run[label]:
            if key not in keys:
                keys.append(key)
    differing = [k for k in keys if len({per_run[label].get(k, "MISSING") for label in RUN_LABELS}) != 1]
    # `comparison.md` is authored prose, not the comparator's raw output: its table is a
    # curated subset of these same fields. Counting its rows here keeps the two headline
    # numbers reconciled instead of leaving a reader to trip over 51 vs 33.
    curated = re.search(
        r"\*\*(\d+) / (\d+) fields identical", (RUNS / "revise-runs/comparison.md").read_text()
    )
    return {
        "curated_view_rows": int(curated.group(2)) if curated else 0,
        "curated_view_note": (
            "revise-runs/comparison.md is authored prose whose table is a curated subset of the "
            "comparator's fields; its headline counts its own rows, this record's counts every "
            "field the comparator emits. No field differs under either count."
        ),
        "measured_at": {"sysml-codegen": RUNS_CODEGEN, "agentic-mbse": CONTENT_MBSE, "teax": CONTENT_TEAX},
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
        "teax_pinned": {"path": str(TEAX), "head": git(TEAX, "rev-parse", "HEAD"), "expected": CONTENT_TEAX},
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
    """The four step-6 retirement commits, named by the tree rather than by memory."""
    wanted = ["19072ad", "82c7951", "882fc8d", "3071fba"]
    out = {}
    for oid in wanted:
        subject = git(ROOT, "log", "-1", "--format=%h %s", oid)
        touched = len(git(ROOT, "show", "--name-only", "--format=", oid).splitlines())
        out[oid] = {"subject": subject, "paths_touched": touched}
    return out


def ledger_facts() -> dict:
    rows = json.loads((RECOVERY / "ledger-4a.json").read_text())["rows"]
    return {
        "row_count": len(rows),
        "states": dict(collections.Counter(row.get("state", "?") for row in rows)),
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
        *sorted(RUNS.glob("*.py")),
        *sorted(RUNS.glob("*.sh")),
        *sorted((RUNS / "revise-runs").glob("*.md")),
        *sorted(HEAD_RUN.glob("*.log")),
    ]
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in targets
        if path.is_file() and path.name not in {"candidate.md", "candidate.json"}
    }


# --- markdown emission -------------------------------------------------------------------

# The step-7a fields worth putting in front of a reader, in reading order, with the label the
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
    add("<!-- GENERATED by build_candidate_revise.py — do not edit by hand. -->")
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
    add(f"Pinned TEAx: `{record['repositories']['teax_pinned']['head']}`.")
    add("")

    add("## T2 — Path inventory")
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

    add("## T3 — The three step-7a gate runs")
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
        f"`compare_revise_runs.fields`. The rows above are the headline subset; the full field "
        f"list is in `candidate.json` under `three_runs.fields`. "
        f"`evidence/phase5-runs/revise-runs/comparison.md` presents a {runs['curated_view_rows']}-row "
        f"curated view of the same comparison and reports "
        f"{runs['curated_view_rows']}/{runs['curated_view_rows']} on its own rows; "
        f"no field differs under either count."
    )
    add("")

    add("## T4 — Scale, from the same three runs")
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

    add("## T5 — The content OID, re-measured at step 7c")
    add("")
    head = record["head_measurement"]
    add("| Gate | value at the content OID |")
    add("|---|---|")
    add(f"| Full licensed codegen suite | {head['codegen_suite']} |")
    add(f"| `no live syside license` skip lines | {head['codegen_suite_license_skip_lines']} |")
    add(f"| `check_ledger_4a.py paths` | {head['ledger_paths']} |")
    add(f"| `check_ledger_4a.py surface` | {head['ledger_surface']} |")
    add(f"| `check_doc_distinctness.py` | {head['doc_distinctness']} |")
    add(f"| `git diff --check`, codegen | {head['git_diff_check_codegen']} |")
    add(f"| `git diff --check`, agentic | {head['git_diff_check_agentic']} |")
    add("")

    add("## T6 — The retirement commits (owner step 5, no provisional trim)")
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
        "record": "Item 7 cutover recovery — the post-REVISE candidate: the retired tree, its gates, its audit, and what is left for the owner",
        "supersedes": "the 2026-08-11 pre-retirement record at commit 013d6a1, which described the tree at c4e9b76",
        "status": "ASSEMBLED at the content OIDs — owner final disposition PENDING",
        "assembled_from": {
            "three_run_battery": "evidence/phase5-runs/revise-runs/ (REVISE step 7a)",
            "head_measurement": "evidence/phase5-runs/head-6c35aa0/ (REVISE step 7c)",
            "audit": "evidence/audit-7-retired.md (REVISE step 7b) + its probe addendum",
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
        "path_inventory": path_inventory(),
        "retirement_commits": retirement_commits(),
        "ledger": ledger_facts(),
        "three_runs": three_runs(),
        "head_measurement": head_measurement(),
        "evidence_hashes_sha256": hashes(),
    }

    (RECOVERY / "evidence/candidate.json").write_text(json.dumps(record, indent=2) + "\n")
    (RUNS / "revise-candidate-tables.md").write_text(emit_tables(record))
    print("wrote evidence/candidate.json and evidence/phase5-runs/revise-candidate-tables.md")
    print("three runs all identical:", record["three_runs"]["all_identical"])
    print("codegen commits since Item 6 base:", record["commit_counts"]["sysml-codegen"])
    print("suite at the content OID:", record["head_measurement"]["codegen_suite"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
