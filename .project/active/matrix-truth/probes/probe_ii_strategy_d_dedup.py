"""Probe (ii) — F4 Strategy D dedup key-set diff vs catf_mfe / solar_battery.

Strategy D (DesignAttributeLookup, input_resolver.py:200) is a documented no-op today.
Its promised behavior: when an aggregation term's leaf name matches a design attribute,
collapse the per-consumer entry-point key (module_eqn__leaf) to the shared design-attr QN,
deduplicating params-JSON keys.

This probe computes the aggregation-EP key-set diff that *implementing* Strategy D would
produce against the two params baselines (entry points inside computation_graph.json).

Method: for every aggregation term in each model, run resolve_input(AGG_STRATEGIES) as it
is today (Strategy D no-op) to get the current entry-point key. Then simulate the promised
Strategy D: on a design-attr leaf match at fallthrough, emit the design-attr QN instead.
Diff the two key sets.

KILL (spec): the diff collapses keys a consumer depends on being distinct, or the review
judges the change otherwise unwanted.

Run: PYTHONPATH=. uv run python .project/active/matrix-truth/probes/probe_ii_strategy_d_dedup.py
"""

from __future__ import annotations

from sysml_codegen.resolution.input_resolver import (
    AGG_STRATEGIES,
    ResolutionContext,
    resolve_input,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture
from tests.conformance.test_dual_resolution import _flatten_design_attrs

MODELS = ["catf_mfe_model", "solar_battery_model"]


def run() -> None:
    for model in MODELS:
        snap = load_extraction_snapshot(snapshot_fixture(model))
        agg = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        das = snap.get("design_attributes", {})
        design_attrs = _flatten_design_attrs(das)
        # leaf-name -> design-attr QN (for the dedup simulation)
        leaf_to_qn: dict[str, str] = {}
        for _p, lst in das.items():
            for da in lst:
                if da.qualified_name:
                    leaf_to_qn.setdefault(da.name, da.qualified_name)

        current_ep_keys: list[str] = []
        deduped_ep_keys: list[str] = []
        d_fires: list[str] = []

        for a in agg:
            parts = a.module_eqn.split("__")
            ctx = ResolutionContext(
                output_registry=None,  # not needed; we build a real one below
                redefinitions=redefs,
                design_attrs=design_attrs,
                module_eqn=a.module_eqn,
                consumer_scope=".".join(parts[1:-1]) if len(parts) >= 3 else "",
                instance_path=a.instance_path,
            )
            # Rebuild ctx with a real registry (resolve_input needs it for A/B/C)
            from sysml_codegen.orchestration.output_registry_builder import (
                build_output_registry,
            )
            registry = build_output_registry(
                calc_usages=snap["calc_usages"],
                calc_defs=snap["calc_defs"],
                aggregation_data=snap["aggregation_expressions"],
                computed_attributes=snap["computed_attributes"],
                channel_aliases=snap.get("channel_aliases", []),
                design_attributes=das,
            )
            ctx = ResolutionContext(
                output_registry=registry,
                redefinitions=redefs,
                design_attrs=design_attrs,
                module_eqn=a.module_eqn,
                consumer_scope=".".join(parts[1:-1]) if len(parts) >= 3 else "",
                instance_path=a.instance_path,
            )

            refs = [f"{t.part_usage_name}.{t.attribute_name}" for t in a.expression.sum_terms]
            refs += [s.source_path for s in a.expression.singleton_terms if "." in s.source_path]
            for ref in refs:
                ir = resolve_input(ref, ctx, AGG_STRATEGIES)
                if ir.source_type != "entry_point":
                    continue  # resolved to a channel; Strategy D never reached
                current_key = ir.qualified_name
                current_ep_keys.append(current_key)
                # Simulate Strategy D: leaf match -> collapse to design-attr QN
                leaf = ref.rsplit(".", 1)[-1]
                if leaf in leaf_to_qn:
                    deduped_ep_keys.append(leaf_to_qn[leaf])
                    d_fires.append(f"{ref} : {current_key}  ->  {leaf_to_qn[leaf]}")
                else:
                    deduped_ep_keys.append(current_key)

        cur, ded = set(current_ep_keys), set(deduped_ep_keys)
        print(f"=== {model} ===")
        print(f"  agg exprs: {len(agg)}   agg-EP keys (current): {len(cur)}   after Strategy D: {len(ded)}")
        print(f"  Strategy D fires on {len(d_fires)} term(s):")
        for f in d_fires:
            print(f"    {f}")
        removed = cur - ded
        added = ded - cur
        # A key is a harmful collapse only if two DISTINCT current keys map to one QN
        from collections import Counter
        collide = {q: c for q, c in Counter(deduped_ep_keys).items() if c > 1 and q in added}
        print(f"  keys removed from set: {len(removed)}   keys added: {len(added)}")
        print(f"  MERGE collisions (>1 distinct consumer collapsed to one key): {len(collide)}")
        for q, c in collide.items():
            print(f"    COLLISION {q} <- {c} consumers")
        print()


if __name__ == "__main__":
    run()
