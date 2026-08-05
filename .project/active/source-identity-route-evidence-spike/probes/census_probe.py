"""Whole-corpus semantic-source census over committed extraction snapshots.

SOURCE-IDENTITY Item 2 probe (license-free). Usage:
    uv run python .project/active/source-identity-route-evidence-spike/probes/census_probe.py \
        .project/active/source-identity-route-evidence-spike/probes/raw/census.json


For every fixture with a snapshot:
  - build the full graph (license-free)
  - attribute each entry point to its minting binding where possible
  - classify: authored literal / reference-derived literal (Path A) /
    lenient-miss reference (Path B) / converged design-attr / library default / other
  - group per-usage EPs by (owner_path, referent leaf) -> fan-out groups
  - evidence-sufficiency: can (owner_path or owner_def_qn) + written leaf
    reconstruct a unique design attribute?
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO))

import logging
logging.disable(logging.WARNING)

from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot

FIXDIR = REPO / "tests" / "fixtures"
fixtures = sorted(p.parent.name for p in FIXDIR.glob("*/extraction_snapshot.json"))

report = {}
for name in fixtures:
    row = {"status": "ok", "eps": 0, "authored_literal": [], "path_a": [], "path_b": [],
           "converged_attr": [], "library_default": [], "unattributed": [],
           "fanout_groups": [], "recon": {}}
    try:
        ctx = build_pipeline_context_from_snapshot(snapshot_fixture(name))
    except Exception as e:
        row["status"] = f"BUILD-FAIL {type(e).__name__}: {e}"
        report[name] = row
        continue
    graph = ctx.computation_graph
    eps = {ep.qualified_name: ep for gr in graph.entry_point_groups for ep in gr.parameters}
    row["eps"] = len(eps)

    # design-attr index (post-pipeline ctx attrs; includes synthesized ones if any)
    attr_qns = set()
    attr_default = {}
    for attrs in ctx.design_attributes.values():
        for a in attrs:
            if a.qualified_name:
                attr_qns.add(a.qualified_name)
                attr_default[a.qualified_name] = a.default_value

    claimed = set()
    per_usage_records = []  # (ep_qn, owner, leaf, kind, usage)
    for cu in ctx.calc_usages:
        owner = cu.qualified_name.rsplit("__", 1)[0] if "__" in cu.qualified_name else ""
        for b in cu.bindings:
            ep_qn = f"{cu.qualified_name}__{b.param_name}"
            if ep_qn not in eps:
                continue
            claimed.add(ep_qn)
            attr_name = getattr(b, "source_attribute_name", None)
            btype = str(b.binding_type).rsplit(".", 1)[-1].lower()
            if btype == "literal" and attr_name:
                kind = "path_a"; leaf = attr_name
            elif btype == "literal":
                kind = "authored_literal"; leaf = None
            elif btype == "reference":
                kind = "path_b"; leaf = attr_name or (b.source_path or "").replace("::", "__").rsplit("__", 1)[-1]
            else:
                kind = "other"; leaf = attr_name
            row[kind if kind in row else "unattributed"].append(ep_qn)
            if kind in ("path_a", "path_b") and leaf:
                per_usage_records.append((ep_qn, owner, leaf, kind, cu))

    for qn, ep in eps.items():
        if qn in claimed:
            continue
        et = str(ep.entry_type).rsplit(".", 1)[-1]
        if qn in attr_qns or et == "DESIGN_ATTRIBUTE":
            row["converged_attr"].append(qn)
        elif et == "LIBRARY_DEFAULT":
            row["library_default"].append(qn)
        else:
            row["unattributed"].append(qn)

    # fan-out groups: same (owner, leaf) minting >1 per-usage EP, or coexisting with a
    # converged design-attr EP of the same key
    groups = defaultdict(list)
    for ep_qn, owner, leaf, kind, cu in per_usage_records:
        groups[(owner, leaf)].append((ep_qn, kind))
    for (owner, leaf), members in sorted(groups.items()):
        converged_sibling = f"{owner}__{leaf}" in eps
        if len(members) > 1 or converged_sibling:
            row["fanout_groups"].append({
                "owner": owner, "leaf": leaf,
                "members": [m[0] for m in members],
                "kinds": sorted({m[1] for m in members}),
                "converged_sibling": converged_sibling,
            })

    # evidence-sufficiency reconstruction attempt per per-usage EP
    recon = {"exact_occurrence": 0, "def_default": 0, "unresolved": [], "ambiguous": []}
    for ep_qn, owner, leaf, kind, cu in per_usage_records:
        cand_occ = f"{owner}__{leaf}"
        def_qn = getattr(cu, "owning_part_def_qn", None)
        cand_def = f"{def_qn}__{leaf}" if def_qn else None
        hits = [c for c in (cand_occ, cand_def) if c and c in attr_qns]
        if len(set(hits)) == 1:
            recon["exact_occurrence" if hits[0] == cand_occ else "def_default"] += 1
        elif len(set(hits)) > 1:
            recon["ambiguous"].append((ep_qn, hits))
        else:
            recon["unresolved"].append((ep_qn, cand_occ, cand_def))
    row["recon"] = recon
    report[name] = row

# ---- print summary ----
tot_fan = 0
for name, row in report.items():
    if row["status"] != "ok":
        print(f"{name:35s} {row['status']}")
        continue
    fg = row["fanout_groups"]
    tot_fan += len(fg)
    print(f"{name:35s} eps={row['eps']:3d} pathA={len(row['path_a']):2d} pathB={len(row['path_b']):2d} "
          f"authoredLit={len(row['authored_literal']):2d} conv={len(row['converged_attr']):2d} "
          f"libdef={len(row['library_default']):2d} unattr={len(row['unattributed']):2d} FANOUT={len(fg)}")
    for g in fg:
        print(f"    FANOUT owner={g['owner']} leaf={g['leaf']} kinds={g['kinds']} conv_sib={g['converged_sibling']}")
        for m in g["members"]:
            print(f"        {m}")
    r = row["recon"]
    if r and (r["unresolved"] or r["ambiguous"] or r["exact_occurrence"] or r["def_default"]):
        print(f"    recon: exact_occ={r['exact_occurrence']} def_default={r['def_default']} "
              f"unresolved={len(r['unresolved'])} ambiguous={len(r['ambiguous'])}")
        for u in r["unresolved"][:6]:
            print(f"        UNRES {u[0]}  occ_cand={u[1]}  def_cand={u[2]}")
        for a in r["ambiguous"]:
            print(f"        AMBIG {a[0]}  hits={a[1]}")
print(f"\nTOTAL fan-out groups across corpus: {tot_fan}")

out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if out:
    out.write_text(json.dumps(report, indent=1, default=str))
    print("wrote", out)
