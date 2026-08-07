"""Probe 3: project the instance graph into a ComputationGraph and run the REAL
generation layer on it, untouched (kill criterion c).

Projection scope: calculation nodes only (constraint catalog assembly is Item-4
design scope, out of spike scope by the epic). One parameter group. Entry point
per attribute NODE (that is the whole point: one node = one public input).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elab_prototype import elaborate  # noqa: E402

from sysml_codegen.cli import _get_template_env
from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.generation.registry import generate_registry
from sysml_codegen.resolution.models import (
    Compilability,
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
OUT = Path(__file__).resolve().parent / "projection_out"
OUT.mkdir(exist_ok=True)
PKG = "source_identity_mixed_consumers"

failures: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}{(' — ' + detail) if detail else ''}")
    if not cond:
        failures.append(label)


g = elaborate(FIXTURES / PKG)

# outputs per calc def (from the real extractor)
extractor = SysMLDataExtractor([FIXTURES / PKG])
assert extractor.load_models()
calc_defs = {d.name: d for d in extractor.extract_calculation_definitions()}

calc_nodes = {cid: c for cid, c in g.calcs.items() if c.kind == "calc"}

# ---- entry points: ONE per consumed attribute node --------------------------
consumed_nodes: dict[str, list[tuple[str, str]]] = {}
literal_inputs: list[tuple[str, str, float]] = []
for cid, calc in calc_nodes.items():
    for param, ref in calc.inputs.items():
        if ref[0] == "node":
            consumed_nodes.setdefault(ref[1], []).append((cid, param))
        elif ref[0] == "literal":
            literal_inputs.append((cid, param, ref[1]))

entry_points = []
for node_id in sorted(consumed_nodes):
    node = g.attrs[node_id]
    entry_points.append(
        EntryPoint(
            qualified_name=node_id,
            simple_name=node.attr_name,
            entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            default_value=node.value,
            param_group="design_params",
        )
    )
for cid, param, value in literal_inputs:
    entry_points.append(
        EntryPoint(
            qualified_name=f"{cid}__{param}",
            simple_name=param,
            entry_type=EntryPointType.USAGE_LITERAL,
            default_value=value,
            param_group="design_params",
        )
    )

group = ParameterGroup(
    name="design_params",
    class_name="DesignParams",
    source_file=Path("model.sysml"),
    parameters=entry_points,
)

# ---- modules ---------------------------------------------------------------
modules = []
name_by_cid = {cid: cid.lower() for cid in calc_nodes}
for cid, calc in sorted(calc_nodes.items()):
    cdef = calc_defs.get(calc.calc_def_qn)
    inputs = []
    for param, ref in sorted(calc.inputs.items()):
        if ref[0] == "node":
            src = InputSource(
                source_type="entry_point", param_group="design_params", qualified_name=ref[1]
            )
        elif ref[0] == "literal":
            src = InputSource(
                source_type="entry_point",
                param_group="design_params",
                qualified_name=f"{cid}__{param}",
            )
        elif ref[0] == "output":
            src = InputSource(
                source_type="module_output", producer_channel=f"{ref[1]}__{ref[2]}"
            )
        else:
            raise AssertionError(f"unresolved input in projection: {cid}.{param}: {ref}")
        inputs.append(ModuleInput(param_name=param, python_type="float", source=src))
    outputs = [
        ModuleOutput(
            field_name=o.name, python_type="float", channel_name=f"{cid}__{o.name}"
        )
        for o in (cdef.output_attributes if cdef else [])
    ]
    modules.append(
        PipelineModule(
            name=name_by_cid[cid],
            module_type=derive_module_type(calc.calc_def_qn),
            inputs=inputs,
            outputs=outputs,
            execution_order=0,
            module_kind=ModuleKind.CALCULATION,
            compilability=Compilability.UNKNOWN,
            calc_def_name=calc.calc_def_qn,
            calc_def_qualified_name=cdef.qualified_name if cdef else None,
        )
    )

# topological order: producers before consumers
producer_deps = {
    cid: [ref[1] for ref in calc.inputs.values() if ref[0] == "output"]
    for cid, calc in calc_nodes.items()
}
ordered: list[str] = []
while len(ordered) < len(calc_nodes):
    progressed = False
    for cid in sorted(calc_nodes):
        if cid in ordered:
            continue
        if all(dep in ordered for dep in producer_deps[cid]):
            ordered.append(cid)
            progressed = True
    assert progressed, "cycle"
by_name = {m.name: m for m in modules}
modules = [by_name[name_by_cid[cid]] for cid in ordered]
for i, m in enumerate(modules):
    m.execution_order = i

graph = ComputationGraph(
    modules=modules,
    entry_point_groups=[group],
    execution_order=[m.name for m in modules],
)

# ---- run the REAL generation layer -----------------------------------------
env = _get_template_env()
yaml_text = generate_pipeline_yaml(graph, "spike_pkg", env)
(OUT / "pipeline.yaml").write_text(yaml_text)
registry_text = generate_registry(graph, "spike_pkg", env, OUT / "registry.py", None)
(OUT / "registry.py").write_text(registry_text)

check("pipeline YAML rendered", bool(yaml_text.strip()))
check("registry rendered", bool(registry_text.strip()))

# ---- the product claims, read off the generated YAML ------------------------
avail_node = f"{PKG}__avail_ctx__avail_plant__availability"
check(
    "ONE availability input in the YAML (customer collapse)",
    yaml_text.count(avail_node) >= 1
    and f"{PKG}__avail_ctx__avail_plant__def_authored_calc__value_in" not in yaml_text
    and f"{PKG}__avail_ctx__avail_plant__usage_authored_calc__value_in" not in yaml_text,
)
both_wired = (
    yaml_text.count(avail_node)
)
print(f"    availability node referenced {both_wired}x in YAML")
check(
    "producer channel wired for C24 (no minted input)",
    f"{PKG}__computed_station__source_identity_computed__producer_calc__result" in yaml_text
    and f"{PKG}__computed_station__computed_calc__value_in" not in yaml_text,
)
check(
    "twins have TWO distinct inputs",
    f"{PKG}__twin_bay__sensor_a__reading" in yaml_text
    and f"{PKG}__twin_bay__sensor_b__reading" in yaml_text,
)
n_entry = len(entry_points)
print(f"    modules={len(modules)} entry_points={n_entry}")

if failures:
    print(f"\nFAILURES: {failures}")
    sys.exit(1)
print("\nALL CHECKS PASS")
