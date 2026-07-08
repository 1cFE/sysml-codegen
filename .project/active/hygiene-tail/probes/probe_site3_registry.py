"""Site 3: generation/registry.py `_collect_exit_point_primitive_types` silent skip.

Reproduce (unit): construct a single-output ("root") exit point with an
unmapped python_type ("Any") and show it is skipped with no diagnostic.

Reproduce (reachability): scan every SNAPSHOT_MODELS built ComputationGraph for
a single-output exit point whose python_type is outside {float,int,str,bool}.
This doubles as the corpus-scan gate for WARN disposition.
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format="LOG %(levelname)s %(name)s: %(message)s")

from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
from sysml_codegen.resolution.models import ModuleOutput, PipelineModule, Compilability
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from tests.conftest import snapshot_fixture

SNAPSHOT_MODELS = [
    "sample_model", "solar_battery_model", "catf_mfe_model", "attr_expr_probe",
    "chain_spike_model", "issue22_model", "expression_binding_probe",
    "chain_override_probe", "unresolvable_attr_probe", "alias_agg_probe",
    "wi014_toy", "ife_plant", "self_named_binding_trap",
    "plant_values", "plant_value_shapes",
]


def _module_with_root_output(python_type: str) -> PipelineModule:
    return PipelineModule(
        name="probe_mod",
        module_type="ProbeModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="root",
                python_type=python_type,
                channel_name="probe_mod__root",
            )
        ],
        execution_order=0,
        compilability=Compilability.FULLY_COMPILABLE,
    )


print("=" * 70)
print("REPRODUCE (unit) — single-output exit point with python_type='Any'")
print("=" * 70)
result = _collect_exit_point_primitive_types([_module_with_root_output("Any")])
print(f"  result: {result}   (expected empty — silently skipped, no diagnostic)")

result_float = _collect_exit_point_primitive_types([_module_with_root_output("float")])
print(f"  float control: {result_float}   (expected ['Float'])")

print()
print("=" * 70)
print("REACHABILITY SCAN — every SNAPSHOT_MODELS built graph's single-output")
print("exit-point python_types")
print("=" * 70)

non_primitive_hits = 0
for name in SNAPSHOT_MODELS:
    try:
        ctx = build_pipeline_context_from_snapshot(snapshot_fixture(name))
    except Exception as e:  # noqa: BLE001 — probe, report and continue
        print(f"  {name}: FAILED TO BUILD ({e!r})")
        continue
    for m in ctx.computation_graph.modules:
        for out in m.outputs:
            if out.field_name == "root" and out.python_type not in ("float", "int", "str", "bool"):
                non_primitive_hits += 1
                print(f"  {name}: module {m.name} root output python_type={out.python_type!r}")

print(f"\nTotal non-primitive single-output exit points across corpus: {non_primitive_hits}")
