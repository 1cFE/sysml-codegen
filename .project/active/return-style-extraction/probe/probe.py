"""Throwaway Phase-0 probe for SC-2 (return-style / bare-parameter extraction).

Records the live node shapes the design's V8 rule and fixture depend on:

  Probe 1  (B4, GATES V8): anonymous `return : Real = expr;` — direction,
           sanitize_name, result-parameter membership/heritage.
  Probe 1b (I3): does anonymous return + a named `out attribute` even parse?
  Probe 2  (B1/I5): named `return y : Real = expr;` carries feature_value_expression.
  Probe 3  (Risk 1): style-D `return attribute y; y = expr;` runs through
           build_pipeline_context and generates a stencil without a codegen crash.

Run: uv run --env-file ~/1cfe/agentic-mbse/.env python \
        .project/active/return-style-extraction/probe/probe.py
Not committed to production; lives beside the design like the type-indexing probe.
"""
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.extraction.extractor import SysMLDataExtractor

HERE = Path(__file__).parent


def dump_members(model, adapter, label):
    print(f"\n=== {label} ===")
    for cd in adapter.elements_of_type(model, "CalculationDefinition"):
        print(f"calc def name={getattr(cd, 'name', '?')!r}")
        for m in cd.owned_members:
            name = getattr(m, "name", None)
            is_attr = adapter.is_instance(m, "AttributeUsage")
            is_ref = adapter.is_instance(m, "ReferenceUsage")
            direction = str(getattr(m, "direction", None))
            fve = getattr(m, "feature_value_expression", None)
            # result-parameter membership/heritage (B4 fallback key)
            memberships = []
            for rel, tgt in (getattr(m, "heritage", []) or []):
                memberships.append(type(rel).__name__)
            owning_mem = type(getattr(m, "owning_membership", None)).__name__
            print(
                f"  member type={type(m).__name__} name={name!r} "
                f"sanitize={sanitize_name(name)!r} is_attr={is_attr} is_ref={is_ref} "
                f"direction={direction} fve={'YES' if fve else 'no'} "
                f"owning_membership={owning_mem} heritage_rels={memberships}"
            )


def load(paths):
    ex = SysMLDataExtractor([Path(p) for p in paths])
    ok = ex.load_models()
    return ex, ok


# ---- Probe 1: anonymous return ----
try:
    ex, ok = load([HERE / "anon.sysml"])
    if not ok:
        print("Probe 1 FAILED to load anon.sysml")
    else:
        dump_members(ex.model, ex.adapter, "Probe 1: anonymous return")
except Exception as e:  # noqa: BLE001
    print(f"Probe 1 EXCEPTION: {type(e).__name__}: {e}")

# ---- Probe 1b: mixed anonymous + named out ----
try:
    ex, ok = load([HERE / "mixed.sysml"])
    print(f"\n=== Probe 1b: mixed anon+named parse: loaded={ok} ===")
    if ok:
        dump_members(ex.model, ex.adapter, "Probe 1b members")
except Exception as e:  # noqa: BLE001
    print(f"Probe 1b EXCEPTION (parse rejection): {type(e).__name__}: {e}")

# ---- Probe 2: named return feature_value_expression ----
try:
    ex, ok = load([HERE / "named.sysml"])
    if not ok:
        print("Probe 2 FAILED to load named.sysml")
    else:
        dump_members(ex.model, ex.adapter, "Probe 2: named return")
except Exception as e:  # noqa: BLE001
    print(f"Probe 2 EXCEPTION: {type(e).__name__}: {e}")

# ---- Probe 3: style D full pipeline safety ----
print("\n=== Probe 3: style-D full-pipeline (build_pipeline_context) ===")
try:
    ex, ok = load([HERE / "styled" / "library.sysml"])
    if ok:
        dump_members(ex.model, ex.adapter, "Probe 3: style-D extraction shape")
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    ctx = build_pipeline_context([HERE / "styled"])
    print("build_pipeline_context: OK (no crash)")
    for cd in ctx.calc_defs:
        print(
            f"  calc_def {cd.name!r}: "
            f"inputs={[a.name for a in cd.input_attributes]} "
            f"outputs={[a.name for a in cd.output_attributes]} "
            f"output_expression_asts_keys={list(cd.output_expression_asts.keys())} "
            f"member_expressions_keys={list(cd.member_expressions.keys())}"
        )
    print(f"  compilation_results keys={list(ctx.compilation_results.keys())}")
except Exception as e:  # noqa: BLE001
    import traceback

    print(f"Probe 3 EXCEPTION: {type(e).__name__}: {e}")
    traceback.print_exc()
