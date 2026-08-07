"""Probe 0b: constraint bindings via adapter iteration + aggregation term evidence."""

from pathlib import Path

from agentic_mbse.sysml.expression import feature_chain_facts, resolved_target_fact
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"


def dump(pkg: str) -> None:
    extractor = SysMLDataExtractor([FIXTURES / pkg])
    assert extractor.load_models(), pkg
    model = extractor.model

    print(f"=== {pkg}: constraint usages ===")
    for cu in SysideAdapter.elements_of_type(model, "ConstraintUsage"):
        qn = getattr(cu, "qualified_name", None)
        print(f"  {type(cu).__name__} {qn!r}")
        for param in getattr(cu, "owned_members", None) or []:
            expr = getattr(param, "feature_value_expression", None)
            if expr is None:
                continue
            if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                root, leaf, _qns, members, _idx = feature_chain_facts(expr)
                print(
                    f"    {getattr(param, 'name', None)}: CHAIN root="
                    f"{root.qualified_name if root else None!r} members={members!r}"
                )
            elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                fact = resolved_target_fact(getattr(expr, "referent", None))
                print(
                    f"    {getattr(param, 'name', None)}: REF "
                    f"{fact.qualified_name if fact else None!r} owner_is_def="
                    f"{fact.owner_is_definition if fact else None}"
                )

    hier = extract_hierarchy_data(model)
    print(f"=== {pkg}: aggregation expressions ===")
    for agg in hier.aggregation_expressions:
        print(f"  owner={agg.owning_part_qn!r} attr={agg.attribute_name!r}")
        for t in agg.sum_terms:
            rt = t.resolved_target
            cr = t.chain_root
            print(
                f"    SUM {t.part_usage_name}.{t.attribute_name}: leaf="
                f"{rt.qualified_name if rt else None!r} root="
                f"{cr.qualified_name if cr else None!r} members={t.resolved_member_names!r}"
            )
        for t in agg.singleton_terms:
            rt = t.resolved_target
            cr = t.chain_root
            print(
                f"    SINGLETON {t.source_path}: leaf={rt.qualified_name if rt else None!r} "
                f"root={cr.qualified_name if cr else None!r} members={t.resolved_member_names!r}"
            )
        for t in agg.local_terms:
            rt = t.resolved_target
            print(f"    LOCAL {t.attribute_name}: leaf={rt.qualified_name if rt else None!r}")


dump("source_identity_mixed_consumers")
dump("nested_occurrence_override_probe")
