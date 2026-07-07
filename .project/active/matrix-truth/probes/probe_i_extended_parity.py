"""Probe (i) — F4 extended parity: backtracker DFS vs resolve_input(AGG_STRATEGIES).

Mirrors tests/conformance/test_dual_resolution.py's comparison logic
(TestBacktrackerVsResolveInputChain + TestBacktrackerVsResolveInputReference +
TestEntryPointFallbackConsistent) but over Item 1's landed fixtures, which the
committed suite does not cover:

    plant_values, plant_value_shapes, spec_chain_twolevel

Pass bar (spec HARD-F4 probe i): 100% parity. Any MODULE_OUTPUT ref where the two
paths resolve to different channels, or where the backtracker says MODULE_OUTPUT and
resolve_input falls back to entry_point on a CHAIN-dot ref, is a KILL.

Known-asymmetry carve-out (same as the committed suite): REFERENCE (::) refs the
backtracker resolves via its Step-2 leaf+parent scoped lookup that Strategy B does not
replicate are counted as bt_only, not mismatches — a documented capability gap, not a
correctness divergence.

Run: uv run python .project/active/matrix-truth/probes/probe_i_extended_parity.py
"""

from __future__ import annotations

from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.resolution.input_resolver import (
    AGG_STRATEGIES,
    ResolutionContext,
    resolve_input,
)
from tests.conformance.test_dual_resolution import (
    _build_backtracker_from_snapshot,
    _flatten_design_attrs,
)

FIXTURES = ["plant_values", "plant_value_shapes", "spec_chain_twolevel"]


def _ctx(registry, redefs, design_attrs, usage_qn):
    parts = usage_qn.split("__")
    consumer_scope = ".".join(parts[1:-1]) if len(parts) >= 3 else ""
    instance_path = "__".join(parts[:-1]) if len(parts) >= 2 else usage_qn
    return ResolutionContext(
        output_registry=registry,
        redefinitions=redefs,
        design_attrs=design_attrs,
        module_eqn=usage_qn,
        consumer_scope=consumer_scope,
        instance_path=instance_path,
    )


def run() -> int:
    total_kills = 0
    for fx in FIXTURES:
        result, registry, snap = _build_backtracker_from_snapshot(fx)
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        mo_verified = ep_verified = bt_only = 0
        kills: list[str] = []

        for key, res in result.binding_resolutions.items():
            sp = res.source_path
            if not sp:
                continue
            usage_qn = key.split("|")[0]
            ctx = _ctx(registry, redefs, design_attrs, usage_qn)
            ir = resolve_input(sp, ctx, AGG_STRATEGIES)

            is_ref = "::" in sp
            if res.resolution_type == BindingResolutionType.MODULE_OUTPUT:
                if ir.source_type == "module_output":
                    if ir.producer_channel != res.qualified_name:
                        kills.append(
                            f"CHANNEL MISMATCH key={key!r} ref={sp!r}: "
                            f"BT={res.qualified_name!r} IR={ir.producer_channel!r}"
                        )
                    else:
                        mo_verified += 1
                elif is_ref:
                    bt_only += 1  # Strategy-B capability gap (documented)
                else:
                    kills.append(
                        f"CHAIN-DOT FALLBACK key={key!r} ref={sp!r}: "
                        f"BT=MODULE_OUTPUT({res.qualified_name!r}) IR=entry_point"
                    )
            else:  # ENTRY_POINT
                # Backtracker fell back. resolve_input must also fall back OR find
                # a valid module_output (strictly more capable, not a divergence).
                if "." not in sp:
                    continue
                if ir.source_type not in ("entry_point", "module_output"):
                    kills.append(
                        f"UNEXPECTED TYPE key={key!r} ref={sp!r}: IR={ir.source_type}"
                    )
                else:
                    ep_verified += 1

        total_kills += len(kills)
        verdict = "KILL" if kills else "PARITY"
        print(f"[{verdict}] {fx}: mo_verified={mo_verified} ep_verified={ep_verified} "
              f"bt_only(Strategy-B gap)={bt_only} kills={len(kills)}")
        for k in kills:
            print(f"    {k}")

    print()
    print(f"OVERALL: {'KILL' if total_kills else '100% PARITY — no kill'} "
          f"(total kills={total_kills})")
    return total_kills


if __name__ == "__main__":
    raise SystemExit(1 if run() else 0)
