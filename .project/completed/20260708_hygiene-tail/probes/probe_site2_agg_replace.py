"""Site 2: resolution/graph_builder.py aggregation-compile `.replace()` collision.

Reproduce: two SingletonTerms whose source_path attribute names are nested
(`cost` is a substring of `cost_total`). The length-sort processes the longer
ref first, but the `inputs.` substitution reintroduces the prefix collision:
`cost` matches inside the already-substituted `inputs.cost_total`.

Gate / reclassification check: scan every SNAPSHOT_MODELS aggregation
expression's ref set for a nested-name pair.
"""

import logging

logging.basicConfig(level=logging.DEBUG, format="LOG %(levelname)s %(name)s: %(message)s")

from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    SingletonTerm,
)
from sysml_codegen.resolution.graph_builder import _build_aggregation_module
from sysml_codegen.snapshot.loader import load_extraction_snapshot
from tests.conftest import snapshot_fixture

SNAPSHOT_MODELS = [
    "sample_model", "solar_battery_model", "catf_mfe_model", "attr_expr_probe",
    "chain_spike_model", "issue22_model", "expression_binding_probe",
    "chain_override_probe", "unresolvable_attr_probe", "alias_agg_probe",
    "wi014_toy", "ife_plant", "self_named_binding_trap",
    "plant_values", "plant_value_shapes",
]

print("=" * 70)
print("REPRODUCE — nested attribute names: 'cost' inside 'cost_total'")
print("=" * 70)

expr = AggregationExpressionData(
    owning_part_qn="Lib__Widget",
    owning_part_name="Widget",
    attribute_name="net",
    raw_expression_text="cost + cost_total",
    transformed_expression="cost + cost_total",
    sum_terms=[],
    singleton_terms=[
        SingletonTerm(source_path="cost"),
        SingletonTerm(source_path="cost_total"),
    ],
    local_terms=[],
    input_channels=[],
    entry_points=[],
    has_unsupported_nodes=False,
)
from sysml_codegen.extraction.data_models import ScopedAggregationData

agg = ScopedAggregationData(expression=expr, instance_path="Design__plant__widget")
module, _ = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)
print(f"  compiled_expression = {module.compiled_expression!r}")
print(f"  expected (correct)  = 'inputs.cost + inputs.cost_total'")
print(f"  CORRUPT: {'inputs.inputs.' in (module.compiled_expression or '')}")

print()
print("=" * 70)
print("CORPUS SCAN — every SNAPSHOT_MODELS aggregation expression's ref set,")
print("checking for a nested-name pair (one ref a substring of another)")
print("=" * 70)


def refs_of(expr: AggregationExpressionData) -> list[str]:
    refs = []
    for t in expr.sum_terms:
        refs.append(f"{t.part_usage_name}.{t.attribute_name}")
    for t in expr.singleton_terms:
        refs.append(t.source_path)
    for t in expr.local_terms:
        refs.append(t.attribute_name)
    return refs


hits = 0
for name in SNAPSHOT_MODELS:
    snap = load_extraction_snapshot(snapshot_fixture(name))
    for scoped_agg in snap.get("aggregation_expressions", []):
        refs = refs_of(scoped_agg.expression)
        for i, a in enumerate(refs):
            for b in refs[i + 1:]:
                if a != b and (a in b or b in a):
                    hits += 1
                    print(f"  {name}: nested pair ({a!r}, {b!r}) in aggregation "
                          f"'{scoped_agg.expression.attribute_name}'")

print(f"\nTotal nested-name pairs across corpus: {hits}")
