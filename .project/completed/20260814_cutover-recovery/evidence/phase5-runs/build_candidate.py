#!/usr/bin/env python3
"""Assemble `evidence/candidate.json` from the three battery runs and the tree itself.

Everything here is derived: run numbers come from the run logs, repository facts from
Git, inventories from `git ls-files`, hashes from the files on disk. Nothing is typed
in by hand, so the record cannot drift from what was measured.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
MBSE = Path("/home/reid/1cfe/agentic-mbse-item7-rebuild")
TEAX = Path("/home/reid/1cfe/teax")
RECOVERY = ROOT / ".project/active/cutover-recovery"
RUNS = RECOVERY / "evidence/phase5-runs"
BASELINE = json.loads((RECOVERY / "evidence/baseline.json").read_text())

ITEM6_CODEGEN = "1672c5766f67e7716f3c9f8f636c21e2ea444601"
ITEM6_MBSE = "5088b417c9e5453271291d46cd5fb23fc0579b1e"
RUN_LABELS = ["run1", "run2", "run3"]


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def pytest_summary(text: str) -> dict[str, int] | None:
    line = next(
        (ln for ln in reversed(text.splitlines()) if " passed" in ln and "==" in ln), None
    )
    if line is None:
        return None
    return {
        key: int(value)
        for value, key in re.findall(r"(\d+) (passed|failed|error|errors|skipped|deselected)", line)
    }


def last_match(text: str, pattern: str, groups: int = 1):
    hits = re.findall(pattern, text)
    return hits[-1] if hits else None


def read_run(label: str) -> dict:
    directory = RUNS / label
    log = lambda name: (directory / f"{name}.log").read_text()  # noqa: E731
    status = {
        parts[0]: {"rc": int(parts[1]), "seconds": int(parts[2])}
        for parts in (
            line.split("\t") for line in (directory / "status.tsv").read_text().splitlines()
        )
    }
    corpus = json.loads(log("corpus_driver"))
    arms: dict[str, dict[str, int]] = {}
    for arm in ("legacy", "exact"):
        counter: collections.Counter[str] = collections.Counter()
        for row in corpus["rows"]:
            outcome = row.get(arm)
            if outcome is None:
                counter["absent"] += 1
            elif outcome["status"] == "graph":
                counter["graph"] += 1
            else:
                counter[outcome["error_type"]] += 1
        arms[arm] = dict(counter)
    exact_codes: collections.Counter[str] = collections.Counter()
    per_fixture = {}
    for row in corpus["rows"]:
        outcome = row["exact"]
        state = (
            "graph"
            if outcome["status"] == "graph"
            else f"{outcome['error_type']}:{','.join(sorted(outcome['codes']))}"
        )
        per_fixture[row["fixture"]] = state
        if outcome["status"] != "graph":
            exact_codes.update(outcome["codes"])

    batch = log("batch_verify")
    ruff_src = last_match(log("ruff_src"), r"Found (\d+) errors")
    ruff_all = last_match(log("ruff_all"), r"Found (\d+) errors")
    mypy = re.findall(r"Found (\d+) errors in (\d+) files \(checked (\d+) source files\)", log("mypy_src"))

    return {
        "status": status,
        "suite_codegen": pytest_summary(log("suite_codegen")),
        "suite_agentic": pytest_summary(log("suite_agentic")),
        "execution_lane": pytest_summary(log("execution_lane")),
        "corpus_ledger_tests": pytest_summary(log("corpus_tests")),
        "corpus_driver": {
            "fixture_count": corpus["fixture_count"],
            "arms": arms,
            "exact_code_multiset": dict(sorted(exact_codes.items())),
            "per_fixture_exact_outcome": per_fixture,
            "canonical_sha256": hashlib.sha256(
                json.dumps(corpus, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        },
        "v6_batch_verify": last_match(batch, r"(\d+) captured, (\d+) refused, (\d+) deviations"),
        "v6_batch_check": last_match(
            log("batch_check"), r"(\d+) captured, (\d+) refused, (\d+) deviations"
        ),
        "batch_verify_left_worktree": (directory / "batch_verify_worktree.txt").read_text().strip().splitlines(),
        "batch_verify_nontimestamp_diff_lines": len(
            (directory / "batch_verify_nontimestamp_diff.txt").read_text().splitlines()
        ),
        "ruff": {"src": int(ruff_src) if ruff_src else 0, "src_tests_scripts": int(ruff_all) if ruff_all else 0},
        "mypy_src": {
            "errors": int(mypy[-1][0]),
            "files_with_errors": int(mypy[-1][1]),
            "source_files_checked": int(mypy[-1][2]),
        }
        if mypy
        else None,
        "checker": {
            "paths": last_match(log("ledger_paths"), r"(\d+) rows checked, (\d+) problems"),
            "surface": log("ledger_surface").strip().splitlines()[-1],
            "groups": [ln.strip() for ln in log("ledger_groups").strip().splitlines() if "READY" in ln or "BLOCKED" in ln],
            "proof_integrity": log("proof_integrity").strip().splitlines()[0],
        },
        "doc_distinctness": log("doc_distinct").strip().splitlines()[-1],
        "git_diff_check": {
            "sysml-codegen": log("diff_check_cg").strip(),
            "agentic-mbse": log("diff_check_mb").strip(),
        },
        "git_status": {
            "sysml-codegen": log("status_cg").strip().splitlines(),
            "agentic-mbse": log("status_mb").strip().splitlines(),
            "teax": log("status_teax").strip().splitlines(),
        },
        "environment": json.loads((directory / "env.json").read_text()),
    }


def test_files(repo: Path) -> set[str]:
    return {
        path
        for path in git(repo, "ls-files", "tests").split()
        if path.endswith(".py") and "test_" in path.rsplit("/", 1)[-1]
    }


def hashes() -> dict[str, str]:
    targets = [
        RECOVERY / "plan.md",
        RECOVERY / "ledger-4a.json",
        RECOVERY / "ledger-4a.md",
        RECOVERY / "doc-update-list-4d.md",
        ROOT / "tests/fixtures/v6_recapture_batch/batch.json",
        *sorted((RECOVERY / "evidence").glob("*.md")),
        *sorted((RECOVERY / "evidence").glob("*.json")),
        *sorted((RECOVERY / "evidence").glob("*.txt")),
        *sorted((RECOVERY / "runbook-patches").rglob("*.patch")),
        *sorted((RECOVERY / "runbook-patches").glob("*.txt")),
        *sorted(RUNS.glob("*.py")),
        *sorted(RUNS.glob("*.sh")),
    ]
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in targets
        if path.is_file() and path.name not in {"candidate.md", "candidate.json"}
    }


def main() -> int:
    runs = {label: read_run(label) for label in RUN_LABELS}

    baseline_cg = set(BASELINE["test_inventory"]["sysml-codegen_files"])
    baseline_mb = set(BASELINE["test_inventory"]["agentic-mbse_files"])
    current_cg, current_mb = test_files(ROOT), test_files(MBSE)
    added = sorted(current_cg - baseline_cg)
    introduced = {
        path: git(ROOT, "log", "--diff-filter=A", "--format=%h %s", "-1", f"{ITEM6_CODEGEN}..HEAD", "--", path)
        for path in added
    }

    record = {
        "record": "Phase 5 candidate — a certification of the current tree pair, and the owner's priced decision surface",
        "assembled": git(ROOT, "log", "-1", "--format=%cI"),
        "authority": ".project/active/cutover-recovery/plan.md — Phase 5",
        "status": "ASSEMBLED — owner disposition PENDING; the independent audit is a separate stage",
        "repositories": {
            "sysml-codegen": {
                "path": str(ROOT),
                "branch": git(ROOT, "rev-parse", "--abbrev-ref", "HEAD"),
                "head": git(ROOT, "rev-parse", "HEAD"),
                "item6_base": ITEM6_CODEGEN,
                "diff_stat_vs_item6_base": git(ROOT, "diff", "--shortstat", f"{ITEM6_CODEGEN}..HEAD"),
                "name_status_counts": dict(
                    collections.Counter(
                        line[0]
                        for line in git(ROOT, "diff", "--name-status", f"{ITEM6_CODEGEN}..HEAD").splitlines()
                    )
                ),
                "deleted_paths": [
                    line.split("\t", 1)[1]
                    for line in git(ROOT, "diff", "--name-status", f"{ITEM6_CODEGEN}..HEAD").splitlines()
                    if line.startswith("D")
                ],
                "commits_since_item6_base": len(
                    git(ROOT, "log", "--format=%h", f"{ITEM6_CODEGEN}..HEAD").splitlines()
                ),
            },
            "agentic-mbse": {
                "path": str(MBSE),
                "branch": git(MBSE, "rev-parse", "--abbrev-ref", "HEAD"),
                "head": git(MBSE, "rev-parse", "HEAD"),
                "item6_base": ITEM6_MBSE,
                "diff_stat_vs_item6_base": git(MBSE, "diff", "--shortstat", f"{ITEM6_MBSE}..HEAD"),
                "changed_paths": git(MBSE, "diff", "--name-status", f"{ITEM6_MBSE}..HEAD").splitlines(),
                "commits_since_item6_base": git(MBSE, "log", "--format=%h %s", f"{ITEM6_MBSE}..HEAD").splitlines(),
            },
            "teax_pinned": {
                "path": str(TEAX),
                "head": git(TEAX, "rev-parse", "HEAD"),
                "expected_head": "fa0e06a99b070346e68a3b3c29cfec546f3ac728",
            },
            "forensic_do_not_merge": BASELINE["heads"]["forensic_do_not_merge"],
        },
        "path_inventory": {
            "sysml-codegen": {
                "tracked_files": len(git(ROOT, "ls-files").splitlines()),
                "src_modules": len([p for p in git(ROOT, "ls-files", "src").splitlines() if p.endswith(".py")]),
                "test_modules": len(current_cg),
                "fixtures": len({p.split("/")[2] for p in git(ROOT, "ls-files", "tests/fixtures").splitlines() if p.count("/") >= 2}),
                "reference_docs": len(git(ROOT, "ls-files", "docs/architecture/reference").splitlines()),
                "scripts": len([p for p in git(ROOT, "ls-files", "scripts").splitlines() if p.endswith(".py")]),
            },
            "agentic-mbse": {
                "tracked_files": len(git(MBSE, "ls-files").splitlines()),
                "test_modules": len(current_mb),
            },
        },
        "test_inventory_reconciliation": {
            "method": "collected test-module paths from `git ls-files tests`, against the Phase 2 baseline inventory in evidence/baseline.json",
            "sysml-codegen": {
                "baseline_modules": len(baseline_cg),
                "current_modules": len(current_cg),
                "removed": sorted(baseline_cg - current_cg),
                "removed_authority": {
                    "tests/unit/test_signature_extractor.py": "ledger-4a L-241 (with production row L-006), group 4B-G1, executed at 6ba346e; responsibility carried by generation/preservation.py and re-proved green by the checker"
                },
                "added": introduced,
                "node_counts": {
                    "baseline_collected": BASELINE["test_inventory"]["node_counts"]["sysml-codegen"],
                    "current_passed_skipped_deselected": runs["run1"]["suite_codegen"],
                },
            },
            "agentic-mbse": {
                "baseline_modules": len(baseline_mb),
                "current_modules": len(current_mb),
                "removed": sorted(baseline_mb - current_mb),
                "added": sorted(current_mb - baseline_mb),
                "node_counts": {
                    "baseline_collected": BASELINE["test_inventory"]["node_counts"]["agentic-mbse"],
                    "current_passed_skipped_deselected": runs["run1"]["suite_agentic"],
                },
            },
        },
        "runs": runs,
        "evidence_hashes_sha256": hashes(),
    }

    identical = {}
    for field in ("suite_codegen", "suite_agentic", "execution_lane", "corpus_ledger_tests",
                  "v6_batch_verify", "v6_batch_check", "ruff", "mypy_src", "checker",
                  "doc_distinctness"):
        values = [json.dumps(runs[label][field], sort_keys=True) for label in RUN_LABELS]
        identical[field] = len(set(values)) == 1
    identical["corpus_driver_per_fixture"] = (
        len({json.dumps(runs[label]["corpus_driver"]["per_fixture_exact_outcome"], sort_keys=True) for label in RUN_LABELS}) == 1
    )
    identical["corpus_driver_canonical_sha256"] = (
        len({runs[label]["corpus_driver"]["canonical_sha256"] for label in RUN_LABELS}) == 1
    )
    record["three_runs_identical"] = identical
    record["three_runs_identical_overall"] = all(identical.values())

    # Scale, measured once on a quiet machine after the three runs (timings are the subject,
    # so they are not taken while a suite is competing for the CPU).
    scale = json.loads((RUNS / "scale.json").read_text())
    record["scale"] = {
        "budget_authority": ".project/active/elaborator-cutover/spec.md — R10 [INFERRED], thresholds declared for tests/fixtures/fusion_tea",
        "budget_fusion_tea": {
            "live_load_and_elaboration_s": 10.0,
            "projection_s": 2.0,
            "capture_and_envelope_serialization_s": 5.0,
            "generation_and_seal_s": 30.0,
            "real_teax_execution_s": 30.0,
            "peak_rss_mib": 512,
            "envelope_mib": 25,
        },
        "method": "one warm-up plus three measured runs per fixture, public entry points only",
        "measurements": scale,
    }

    replacements = (RUNS / "replacements.log").read_text().splitlines()
    ledger_rows = {row["id"] for row in json.loads((RECOVERY / "ledger-4a.json").read_text())["rows"]}
    emitted = {m.group(1) for m in (re.search(r"\b(L-\d+)\b", line) for line in replacements) if m}
    record["replacements_gate"] = {
        "note": "one out-of-band run; a pytest invocation per proof-node row, ~40 minutes",
        "green": sum(1 for line in replacements if line.startswith("green")),
        "not_required": sum(1 for line in replacements if line.startswith("not-required")),
        "fail": sum(1 for line in replacements if line.lower().startswith("fail")),
        "ledger_rows": len(ledger_rows),
        "rows_emitting_no_line": sorted(ledger_rows - emitted),
    }

    record["residue_and_boundary"] = json.loads((RUNS / "residue.json").read_text())

    out = RECOVERY / "evidence/candidate.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=False) + "\n")
    print(f"wrote {out}")
    print("identical across the three runs:", record["three_runs_identical_overall"])
    for key, value in identical.items():
        if not value:
            print("  DIVERGENT:", key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
