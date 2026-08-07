"""Probe 0: survey the raw inputs the elaborator would consume (scratch).

Dumps, for source_identity_mixed_consumers:
- occurrence structure (InstanceOccurrence.steps / instance_path) incl. multiplicity fan-out
- redefinition capture (design_overrides + redefinitions) with exact value-site identity
- calc-usage template structure + per-binding reference evidence
- constraint usages found by raw AST walk
"""

from pathlib import Path

from sysml_codegen.analysis.part_instance_index import build_part_instance_index
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
PKG = "source_identity_mixed_consumers"

extractor = SysMLDataExtractor([FIXTURES / PKG])
assert extractor.load_models(), "load failed"
model = extractor.model

index = build_part_instance_index(model)

print("=== occurrences: Bank Cell (multiplicity [3]) ===")
for occ in index.occurrences_of_definition(f"{PKG}::'Bank Cell'"):
    print(f"  instance_path={occ.instance_path!r} part_def_qn={occ.part_def_qn!r}")
    for step in occ.steps:
        print(f"    step: {step!r}")

print("=== occurrences: Twin Sensor ===")
for occ in index.occurrences_of_definition(f"{PKG}::'Twin Sensor'"):
    print(f"  {occ.instance_path!r}")

print("=== occurrences: Avail Plant ===")
for occ in index.occurrences_of_definition(f"{PKG}::'Avail Plant'"):
    print(f"  {occ.instance_path!r}")

hier = extract_hierarchy_data(model)
print("=== design_overrides ===")
for ov in hier.design_overrides:
    print(
        f"  owner={ov.owning_part_qn!r} attr={ov.attribute_name!r} type={ov.redefinition_type}"
        f" lit={ov.literal_value!r} deep={ov.is_deep_path} tp={ov.target_path!r}"
    )
    print(f"    member_qn={ov.member_qualified_name!r}")
    print(f"    redefined_target_qns={ov.redefined_target_qns!r}")

print("=== redefinitions (specialized-def / def-member) ===")
for rd in hier.redefinitions:
    print(
        f"  owner={rd.owning_part_qn!r} attr={rd.attribute_name!r} type={rd.redefinition_type}"
        f" lit={rd.literal_value!r} member_qn={rd.member_qualified_name!r}"
        f" targets={rd.redefined_target_qns!r}"
    )

usages, _report = extract_calculation_usages(model)
print("=== calc usages ===")
for u in usages:
    print(f"  qn={u.qualified_name!r} template={u.is_template} owner_def={u.owning_part_def_qn!r}")
    for b in u.bindings:
        ev = b.reference_evidence
        if ev is None:
            print(f"    {b.param_name}: NO EVIDENCE type={b.binding_type} src={b.source_path!r}")
            continue
        ref = ev.referent
        print(
            f"    {b.param_name}: form={ev.source_form.value} referent="
            f"{ref.qualified_name if ref else None!r} owner_is_def="
            f"{ref.owner_is_definition if ref else None} root="
            f"{ev.chain_root.qualified_name if ev.chain_root else None!r} "
            f"members={ev.resolved_member_names!r} self={ev.is_self_binding}"
        )

print("=== constraint usages (raw AST walk) ===")
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.expression import feature_chain_facts, resolved_target_fact


def walk(elem, depth=0):
    for member in getattr(elem, "owned_members", None) or []:
        tname = type(member).__name__
        if tname in ("ConstraintUsage", "AssertConstraintUsage"):
            qn = getattr(member, "qualified_name", None)
            print(f"  constraint {qn!r} ({tname})")
            for param in getattr(member, "owned_members", None) or []:
                if type(param).__name__ not in ("ReferenceUsage", "AttributeUsage"):
                    continue
                expr = getattr(param, "feature_value_expression", None)
                if expr is None:
                    continue
                pt = type(expr).__name__
                if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                    root, leaf, _qns, members, _idx = feature_chain_facts(expr)
                    print(
                        f"    {getattr(param, 'name', None)}: CHAIN root="
                        f"{root.qualified_name if root else None!r} members={members!r} leaf="
                        f"{leaf.qualified_name if leaf else None!r}"
                    )
                elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                    fact = resolved_target_fact(getattr(expr, "referent", None))
                    print(
                        f"    {getattr(param, 'name', None)}: REF referent="
                        f"{fact.qualified_name if fact else None!r} owner_is_def="
                        f"{fact.owner_is_definition if fact else None}"
                    )
                else:
                    print(f"    {getattr(param, 'name', None)}: {pt}")
        walk(member, depth + 1)


for root_ns in model.user_namespaces:
    walk(root_ns)
