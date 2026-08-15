#!/usr/bin/env python3
"""Compare the three narrow-correction step-7 battery runs field by field.

Reads `final-runs/run{1,2,3}/` and prints one row per measured field with three
columns. Any field whose three values are not identical is marked DIFFER, which
under the step-7 sequence is a rule-10 stop.

Scale timings are excluded from the identity comparison on purpose — wall-clock
is not a semantic result. The deterministic half of the scale measurement (node
counts, module/entry-point counts, envelope bytes) IS compared, and the timings
are printed separately as a measured range.

    python compare_revise_runs.py > final-runs/comparison.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = ["run1", "run2", "run3"]


def read(run: str, name: str) -> str:
    path = HERE / "final-runs" / run / name
    return path.read_text(errors="replace") if path.exists() else ""


def status(run: str) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for line in read(run, "status.tsv").splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            out[parts[0]] = (int(parts[1]), int(parts[2]))
    return out


def pytest_counts(text: str) -> str:
    """The last pytest summary line, reduced to its count clauses."""
    hits = re.findall(r"^=+ (.*?) in [\d.]+s.*$", text, re.M)
    if not hits:
        return "NO SUMMARY"
    clauses = [c.strip() for c in hits[-1].split(",")]
    keep = [c for c in clauses if not c.endswith("warning") and not c.endswith("warnings")]
    return ", ".join(keep)


def first_match(text: str, pattern: str, default: str = "ABSENT") -> str:
    m = re.search(pattern, text, re.M)
    return m.group(0).strip() if m else default


def field_env(run: str) -> dict[str, str]:
    try:
        data = json.loads(read(run, "env.json"))
    except json.JSONDecodeError:
        return {"env gate": "UNPARSEABLE"}
    return {
        "env import-path gate": data["import_path_gate"],
        "env license key present": str(data["license_key_present"]),
        "env python": data["python"],
        "env ruff / mypy / pytest": "{ruff} / {mypy} / {pytest}".format(**data["versions"]),
        "env sysml_codegen": data["resolved_import_paths"]["sysml_codegen"],
        "env agentic_mbse": data["resolved_import_paths"]["agentic_mbse"],
        "env simkit": data["resolved_import_paths"]["simkit"],
    }


def field_heads(run: str) -> dict[str, str]:
    out = {}
    for line in read(run, "heads.tsv").splitlines():
        repo, oid = line.split("\t")
        out[f"HEAD {repo}"] = oid
    return out


def field_scale(run: str) -> dict[str, str]:
    raw = read(run, "scale.log")
    start = raw.find("{")
    if start < 0:
        return {"scale": "ABSENT"}
    try:
        data = json.loads(raw[start:])
    except json.JSONDecodeError:
        return {"scale": "UNPARSEABLE"}
    out: dict[str, str] = {}
    for fixture, body in data.items():
        runs = body["runs"]
        counts = {json.dumps(r["counts"], sort_keys=True) for r in runs}
        envs = {r["envelope_bytes"] for r in runs}
        out[f"scale {fixture} counts"] = counts.pop() if len(counts) == 1 else "UNSTABLE"
        out[f"scale {fixture} envelope bytes"] = str(envs.pop()) if len(envs) == 1 else "UNSTABLE"
    return out


def scale_timings(run: str) -> dict[str, str]:
    raw = read(run, "scale.log")
    start = raw.find("{")
    if start < 0:
        return {}
    data = json.loads(raw[start:])
    out: dict[str, str] = {}
    for fixture, body in data.items():
        runs = body["runs"]
        for key in runs[0]["timings"]:
            vals = [r["timings"][key] for r in runs]
            out[f"{fixture} {key}"] = f"{min(vals):.3f}–{max(vals):.3f}"
        rss = [r["peak_rss_mib_process_cumulative"] for r in runs]
        out[f"{fixture} peak_rss_mib"] = f"{min(rss):.1f}–{max(rss):.1f}"
    return out


def fields(run: str) -> dict[str, str]:
    st = status(run)
    f: dict[str, str] = {}
    f.update(field_env(run))
    f.update(field_heads(run))

    cg = read(run, "suite_codegen.log")
    f["codegen suite"] = pytest_counts(cg)
    f["codegen suite license-skip lines"] = str(len(re.findall(r"no live syside license", cg)))
    f["codegen suite rc"] = str(st.get("suite_codegen", ("?",))[0])

    f["exec lane"] = pytest_counts(read(run, "execution_lane.log"))
    f["corpus -k corpus"] = pytest_counts(read(run, "corpus_tests.log"))

    bv = read(run, "batch_verify.log")
    f["capture_v6_batch --verify"] = first_match(bv, r"^\d+ captured, \d+ refused, \d+ deviations$")
    nz = [ln for ln in read(run, "batch_verify_nontimestamp_diff.txt").splitlines() if ln.strip()]
    f["batch non-timestamp fixture diff lines"] = str(len(nz))
    f["capture_v6_batch --check rc"] = str(st.get("batch_check", ("?",))[0])
    f["capture_v6_batch --check tail"] = (read(run, "batch_check.log").strip().splitlines() or ["EMPTY"])[-1]

    f["ruff check src"] = first_match(read(run, "ruff_src.log"), r"^Found \d+ error")
    f["ruff check src tests scripts"] = first_match(read(run, "ruff_all.log"), r"^Found \d+ error")
    f["mypy src"] = first_match(read(run, "mypy_src.log"), r"^Found \d+ errors? in \d+ files?")

    ag = read(run, "suite_agentic.log")
    f["agentic suite"] = pytest_counts(ag)
    f["agentic ruff check src"] = first_match(read(run, "mb_ruff_src.log"), r"^Found \d+ error")
    f["agentic ruff check tests"] = first_match(read(run, "mb_ruff_tests.log"), r"^Found \d+ error")
    f["agentic mypy src"] = first_match(read(run, "mb_mypy_src.log"), r"^Found \d+ errors? in \d+ files?")

    f["ledger paths"] = first_match(read(run, "ledger_paths.log"), r"^\d+ rows checked, \d+ problems$")
    f["ledger surface"] = first_match(read(run, "ledger_surface.log"), r"^\d+ unrowed breakages$")
    for line in read(run, "ledger_groups.log").splitlines():
        m = re.match(r"^(\S+)\s+affected=\s*(\d+)\s+(.*)$", line)
        if m:
            f[f"ledger group {m.group(1)}"] = f"affected={m.group(2)} {m.group(3).strip()}"
    rep = read(run, "ledger_replace.log")
    f["ledger replacements green"] = str(len(re.findall(r"^green\b", rep, re.M)))
    # The checker writes `not-required`, hyphenated. An earlier `^not required` pattern here
    # matched nothing and reported 0; corrected at step 7c. `comparison.md`'s 81 was read from
    # the log directly and was right all along.
    f["ledger replacements not-required"] = str(len(re.findall(r"^not[- ]required\b", rep, re.M)))
    f["ledger replacements FAIL"] = str(len(re.findall(r"^FAIL\b", rep, re.M)))
    f["ledger replacements rc"] = str(st.get("ledger_replace", ("?",))[0])

    f["proof integrity"] = first_match(read(run, "proof_integrity.log"), r"^proof integrity: .*$")
    f["doc distinctness"] = first_match(read(run, "doc_distinct.log"), r"^\d+ numbered reference documents checked, .*$")

    for key, label in (
        ("diff_check_cg", "git diff --check codegen"),
        ("diff_check_mb", "git diff --check agentic"),
    ):
        body = read(run, f"{key}.log").strip()
        f[label] = f"rc={st.get(key, ('?',))[0]} {'clean' if not body else body}"
    for key, label in (
        ("status_cg", "git status codegen"),
        ("status_mb", "git status agentic"),
        ("status_teax", "git status teax"),
    ):
        f[label] = " | ".join(read(run, f"{key}.log").strip().splitlines()) or "EMPTY"

    f.update(field_scale(run))
    return f


def main() -> int:
    per_run = {run: fields(run) for run in RUNS}
    keys: list[str] = []
    for run in RUNS:
        for key in per_run[run]:
            if key not in keys:
                keys.append(key)

    differing = []
    print("| field | run1 | run2 | run3 | identical |")
    print("|---|---|---|---|---|")
    for key in keys:
        vals = [per_run[run].get(key, "MISSING") for run in RUNS]
        same = len(set(vals)) == 1
        if not same:
            differing.append(key)
        cells = [v.replace("|", "\\|") for v in vals]
        print(f"| {key} | {cells[0]} | {cells[1]} | {cells[2]} | {'yes' if same else '**DIFFER**'} |")

    print()
    print(f"**{len(keys) - len(differing)} / {len(keys)} fields identical across all three runs.**")
    if differing:
        print()
        print("**DIFFERING FIELDS — rule-10 stop:**")
        for key in differing:
            print(f"- {key}")

    print()
    print("### Step wall-clock (measurement, not an identity field)")
    print()
    print("| step | run1 s | run2 s | run3 s |")
    print("|---|---|---|---|")
    step_keys: list[str] = []
    sts = {run: status(run) for run in RUNS}
    for run in RUNS:
        for key in sts[run]:
            if key not in step_keys:
                step_keys.append(key)
    for key in step_keys:
        cols = [str(sts[run].get(key, ("?", "?"))[1]) for run in RUNS]
        print(f"| {key} | {cols[0]} | {cols[1]} | {cols[2]} |")

    print()
    print("### Scale timings and peak RSS (measurement, not an identity field)")
    print()
    print("| measurement | run1 | run2 | run3 |")
    print("|---|---|---|---|")
    timings = {run: scale_timings(run) for run in RUNS}
    tkeys: list[str] = []
    for run in RUNS:
        for key in timings[run]:
            if key not in tkeys:
                tkeys.append(key)
    for key in tkeys:
        cols = [timings[run].get(key, "MISSING") for run in RUNS]
        print(f"| {key} | {cols[0]} | {cols[1]} | {cols[2]} |")

    return 1 if differing else 0


if __name__ == "__main__":
    raise SystemExit(main())
