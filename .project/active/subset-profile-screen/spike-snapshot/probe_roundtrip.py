"""Throwaway: does screen(facts) == screen(decode(encode(facts))) on every subject?

Usage (licensed; from the sysml-codegen repo root):

    uv run --extra dev python .project/active/subset-profile-screen/spike-snapshot/probe_roundtrip.py \
        OUT_DIR [--stage]

Subjects: every 2a corpus case (`tests.helpers.subset_profile.cases.all_answers()`, model root
via `cases.model_root`) and the source tree of each of the 23 committed snapshots
(`sources.json`, written by `resolve_sources.py`).

`--stage` copies each subject root into a fresh temporary folder before loading, as
`sysml-codegen snapshot` does (`snapshot/capture.py` loads private staged copies), so the
facts' file paths differ from a direct load.

Per subject it writes `OUT_DIR/<group>__<name>.json` with: load status, timings, the encoded
facts size, every equality check, and the screen result encoded with the subject root's
absolute path replaced by `<ROOT>` (so two runs can be diffed). `OUT_DIR/summary.json`
collects the rows.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

import factcodec  # noqa: E402
from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: E402
from agentic_mbse.sysml.subset_profile import evaluate_subset_profile  # noqa: E402
from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402

from tests.helpers.subset_profile import cases  # noqa: E402


def subjects() -> list[tuple[str, str, Path]]:
    out = []
    for answer in cases.all_answers():
        out.append(("case", answer.case_id, cases.model_root(answer)))
    for snap, root in json.loads((HERE / "sources.json").read_text()).items():
        out.append(("snapshot", Path(snap).parent.name, REPO / root))
    return out


def walk_refs(x, acc):
    """Collect every SafeLocation.file and every anonymous ElementRef in a fact tree."""
    from dataclasses import fields, is_dataclass

    from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation

    if isinstance(x, SafeLocation):
        acc["files"].add(x.file)
    if isinstance(x, ElementRef) and x.qualified_name is None:
        acc["anon"].add(str(x.element_id))
    if is_dataclass(x) and not isinstance(x, type):
        for f in fields(x):
            walk_refs(getattr(x, f.name), acc)
    elif isinstance(x, (tuple, list, frozenset, set)):
        if isinstance(x, tuple) and len(x) == 2 and isinstance(x[0], str) and isinstance(x[1], int):
            acc["files"].add(x[0])  # InvocationUse.location is (file, line)
        for i in x:
            walk_refs(i, acc)
    elif isinstance(x, dict):
        for k, v in x.items():
            walk_refs(k, acc)
            walk_refs(v, acc)


def run_one(group: str, name: str, root: Path, stage: bool) -> dict:
    row: dict = {"group": group, "name": name, "root": str(root)}
    tmp = None
    load_root = root
    if stage:
        tmp = Path(tempfile.mkdtemp(prefix="spike-stage-"))
        load_root = tmp / root.name
        if root.is_dir():
            shutil.copytree(root, load_root)
        else:
            shutil.copy2(root, load_root)
    try:
        t0 = time.perf_counter()
        model, diagnostics = SysideAdapter.load_model([load_root])
        row["load_s"] = time.perf_counter() - t0
        if diagnostics.contains_errors():
            row["status"] = "load_error"
            return row
        t0 = time.perf_counter()
        facts = extract_subset_facts(model)
        row["extract_s"] = time.perf_counter() - t0
        t0 = time.perf_counter()
        r1 = evaluate_subset_profile(facts)
        row["screen_s"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        encoded = factcodec.encode(facts)
        row["encode_s"] = time.perf_counter() - t0
        t0 = time.perf_counter()
        facts2 = factcodec.decode(encoded)
        row["decode_s"] = time.perf_counter() - t0
        r2 = evaluate_subset_profile(facts2)

        row["prefix"] = str(load_root.resolve())
        row["_facts"] = encoded
        row["facts_bytes"] = len(encoded.encode())
        row["facts_gzip_bytes"] = len(gzip.compress(encoded.encode(), mtime=0))
        row["facts_equal"] = facts == facts2
        row["facts_reencode_equal"] = factcodec.encode(facts2) == encoded
        row["result_equal"] = r1 == r2
        row["result_repr_equal"] = repr(r1) == repr(r2)
        e1, e2 = factcodec.encode(r1), factcodec.encode(r2)
        row["result_json_equal"] = e1 == e2
        row["findings_json_equal"] = factcodec.encode(r1.findings) == factcodec.encode(r2.findings)
        row["unverified_json_equal"] = factcodec.encode(r1.unverified) == factcodec.encode(
            r2.unverified
        )
        row["verdict"] = r1.verdict.value
        row["findings"] = len(r1.findings)
        row["unverified"] = len(r1.unverified)

        acc: dict = {"files": set(), "anon": set()}
        walk_refs(facts, acc)
        prefix = str(load_root.resolve())
        row["fact_files"] = sorted(
            "<none>" if f is None else f.replace(prefix, "<ROOT>") for f in acc["files"]
        )
        row["fact_files_raw_sample"] = sorted(str(f) for f in acc["files"])[:2]
        row["anonymous_refs"] = len(acc["anon"])
        # The screen result with the root path replaced, for cross-run diffs.
        normalized = e1.replace(prefix, "<ROOT>")
        row["result_normalized_sha"] = hashlib.sha256(normalized.encode()).hexdigest()
        # Same, but with anonymous (session) UUIDs replaced by their first-seen ordinal.
        anon_free = normalized
        for i, u in enumerate(sorted(acc["anon"], key=normalized.find)):
            anon_free = anon_free.replace(u, f"<ANON{i}>")
        row["result_anonfree_sha"] = hashlib.sha256(anon_free.encode()).hexdigest()
        row["_result_normalized"] = normalized
        if not row["result_json_equal"]:
            row["status"] = "MISMATCH"
        else:
            row["status"] = "ok"
        return row
    except Exception as error:  # noqa: BLE001
        row["status"] = "error"
        row["error"] = f"{type(error).__name__}: {error}"
        row["traceback"] = traceback.format_exc()[-3000:]
        return row
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    out = Path(sys.argv[1])
    stage = "--stage" in sys.argv
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for group, name, root in subjects():
        row = run_one(group, name, root, stage)
        normalized = row.pop("_result_normalized", None)
        encoded = row.pop("_facts", None)
        if encoded is not None and "--dump-facts" in sys.argv:
            (out / f"{group}__{name}.facts.json").write_text(encoded)
        if normalized is not None:
            (out / f"{group}__{name}.result.json").write_text(normalized)
        summary.append(row)
        print(row["status"], group, name, row.get("findings"), row.get("unverified"), flush=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
