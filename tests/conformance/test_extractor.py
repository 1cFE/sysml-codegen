"""C03: SysMLDataExtractor conformance tests.

Verifies that extraction output conforms to REQ-EXT-01 through REQ-EXT-09
from design intent doc 01-extraction.md. Most tests use real snapshot data
captured in Phase 0 -- no mocks. REQ-EXT-08/09 exercise the two silent-failure
diagnostics (zero-output fail-fast, constraint-drop reporting) and must load a
real fixture live, so they skip when syside is unavailable (no license).

Evidence: live extraction (``tests/helpers/live_extraction.py``). It was the committed
``extraction_snapshot.json`` files read through the v5 loader; both retire with the v5
family, and the v6 instance-graph snapshot carries no calc-usage bindings and refuses most
of these models. Every node that reads a ``*_facts`` fixture is license-gated by the
fixture itself.

Requirements: REQ-EXT-01 through REQ-EXT-09.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.extraction.constraint_report import (
    DROPPABLE_KINDS,
    ConstraintKind,
)
from sysml_codegen.extraction.data_models import (
    LocalTerm,
    RedefinitionType,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor

# ---------------------------------------------------------------------------
# Expected counts from Phase 0 snapshot capture
# ---------------------------------------------------------------------------

EXPECTED_CALC_DEF_COUNTS = {
    "sample_model": 5,
    "solar_battery_model": 15,
    "catf_mfe_model": 21,
    "attr_expr_probe": 2,
    "chain_spike_model": 3,
    "issue22_model": 2,
    "expression_binding_probe": 3,
    "chain_override_probe": 2,
    "unresolvable_attr_probe": 1,
}


# ---------------------------------------------------------------------------
# REQ-EXT-01: One CalculationDefinitionData per calc def
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-01")
class TestReqExt01CalcDefCount:
    """Extraction produces exactly the expected number of CalculationDefinitionData per model."""

    @pytest.mark.parametrize(
        "model_name,expected_count",
        list(EXPECTED_CALC_DEF_COUNTS.items()),
        ids=list(EXPECTED_CALC_DEF_COUNTS.keys()),
    )
    def test_calc_def_count(self, live_extraction_facts, model_name, expected_count):
        snapshot = live_extraction_facts[model_name]
        calc_defs = snapshot["calc_defs"]
        assert len(calc_defs) == expected_count, (
            f"{model_name}: expected {expected_count} calc_defs, got {len(calc_defs)}"
        )

    def test_calc_defs_have_required_fields(self, live_extraction_facts):
        """Every calc_def has required fields populated."""
        for model_name, snapshot in live_extraction_facts.items():
            for cd in snapshot["calc_defs"]:
                assert cd.name, f"{model_name}: calc_def has empty name"
                assert cd.qualified_name, (
                    f"{model_name}: {cd.name} has empty qualified_name"
                )
                assert cd.source_file is not None, (
                    f"{model_name}: {cd.name} has None source_file"
                )
                assert isinstance(cd.input_attributes, list), (
                    f"{model_name}: {cd.name} input_attributes not a list"
                )
                assert isinstance(cd.output_attributes, list), (
                    f"{model_name}: {cd.name} output_attributes not a list"
                )

    def test_calc_def_names_unique_per_model(self, live_extraction_facts):
        """No duplicate calc_def qualified_names within any model."""
        for model_name, snapshot in live_extraction_facts.items():
            qns = [cd.qualified_name for cd in snapshot["calc_defs"]]
            assert len(qns) == len(set(qns)), (
                f"{model_name}: duplicate calc_def qualified_names: "
                f"{[q for q in qns if qns.count(q) > 1]}"
            )


# ---------------------------------------------------------------------------
# REQ-EXT-02: Every binding has exactly one BindingType
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-02")
class TestReqExt02BindingTypes:
    """Every parameter binding has exactly one BindingType from the enum."""

    def test_all_bindings_have_valid_type(self, live_extraction_facts):
        """Every binding across all models has binding_type in BindingType enum."""
        valid_types = set(BindingType)
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                for binding in usage.bindings:
                    assert binding.binding_type in valid_types, (
                        f"{model_name}/{usage.qualified_name}: "
                        f"binding {binding.param_name} has invalid type {binding.binding_type}"
                    )

    def test_binding_type_exclusivity(self, live_extraction_facts):
        """Each binding has exactly one binding_type (not None)."""
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                for binding in usage.bindings:
                    assert binding.binding_type is not None, (
                        f"{model_name}/{usage.qualified_name}: "
                        f"binding {binding.param_name} has None binding_type"
                    )

    def test_solar_battery_binding_types(self, solar_battery_facts):
        """solar_battery has CHAIN, REFERENCE, LITERAL bindings present."""
        all_types = set()
        for usage in solar_battery_facts["calc_usages"]:
            for binding in usage.bindings:
                all_types.add(binding.binding_type)
        expected_present = {BindingType.CHAIN, BindingType.REFERENCE, BindingType.LITERAL}
        assert expected_present.issubset(all_types), (
            f"solar_battery missing binding types: {expected_present - all_types}"
        )

    def test_catf_mfe_binding_types(self, catf_mfe_facts):
        """catf_mfe has CHAIN, REFERENCE, LITERAL bindings present."""
        all_types = set()
        for usage in catf_mfe_facts["calc_usages"]:
            for binding in usage.bindings:
                all_types.add(binding.binding_type)
        expected_present = {BindingType.CHAIN, BindingType.REFERENCE, BindingType.LITERAL}
        assert expected_present.issubset(all_types), (
            f"catf_mfe missing binding types: {expected_present - all_types}"
        )

    def test_unbound_params_not_in_bindings(self, live_extraction_facts):
        """Params in unbound_params do not also appear in bindings list."""
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                bound_params = {b.param_name for b in usage.bindings}
                unbound = set(usage.unbound_params)
                overlap = bound_params & unbound
                assert not overlap, (
                    f"{model_name}/{usage.qualified_name}: "
                    f"params in both bindings and unbound_params: {overlap}"
                )

    def test_literal_bindings_have_value(self, live_extraction_facts):
        """LITERAL bindings have literal_value set (not None)."""
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                for binding in usage.bindings:
                    if binding.binding_type == BindingType.LITERAL:
                        assert binding.literal_value is not None, (
                            f"{model_name}/{usage.qualified_name}: "
                            f"LITERAL binding {binding.param_name} has None literal_value"
                        )

    def test_chain_bindings_have_source_path(self, live_extraction_facts):
        """CHAIN bindings have source_path containing '.'."""
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                for binding in usage.bindings:
                    if binding.binding_type == BindingType.CHAIN:
                        assert binding.source_path is not None, (
                            f"{model_name}/{usage.qualified_name}: "
                            f"CHAIN binding {binding.param_name} has None source_path"
                        )
                        assert "." in binding.source_path, (
                            f"{model_name}/{usage.qualified_name}: "
                            f"CHAIN binding {binding.param_name} source_path "
                            f"'{binding.source_path}' has no '.'"
                        )

    def test_reference_bindings_have_source_path(self, live_extraction_facts):
        """REFERENCE bindings have source_path set (qualified name)."""
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                for binding in usage.bindings:
                    if binding.binding_type == BindingType.REFERENCE:
                        assert binding.source_path is not None and binding.source_path != "", (
                            f"{model_name}/{usage.qualified_name}: "
                            f"REFERENCE binding {binding.param_name} has empty source_path"
                        )

    def test_solar_battery_total_binding_count(self, solar_battery_facts):
        """solar_battery has exactly 31 bindings and 30 unbound params.

        Guards against silent binding loss — type/field tests pass on
        whatever bindings exist, but this catches dropped bindings.
        """
        usages = solar_battery_facts["calc_usages"]
        total_bindings = sum(len(u.bindings) for u in usages)
        total_unbound = sum(len(u.unbound_params) for u in usages)
        assert total_bindings == 31, (
            f"Expected 31 total bindings, got {total_bindings}"
        )
        assert total_unbound == 30, (
            f"Expected 30 total unbound_params, got {total_unbound}"
        )

    def test_catf_mfe_total_binding_count(self, catf_mfe_facts):
        """catf_mfe has exactly 125 bindings across 42 usages."""
        usages = catf_mfe_facts["calc_usages"]
        total_bindings = sum(len(u.bindings) for u in usages)
        assert len(usages) == 42, (
            f"Expected 42 calc_usages, got {len(usages)}"
        )
        assert total_bindings == 125, (
            f"Expected 125 total bindings, got {total_bindings}"
        )


# ---------------------------------------------------------------------------
# REQ-EXT-03: Every redefinition classified as exactly one RedefinitionType
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-03")
class TestReqExt03Redefinitions:
    """Every :>> redefinition is classified as exactly one RedefinitionType."""

    def test_all_redefinitions_have_type(self, solar_battery_facts):
        """Every redefinition in solar_battery hierarchy_data has a RedefinitionType."""
        valid_types = set(RedefinitionType)
        redefs = solar_battery_facts["hierarchy_data"].redefinitions
        assert len(redefs) == 78, (
            f"Expected 78 redefinitions in solar_battery, got {len(redefs)}"
        )
        for r in redefs:
            assert r.redefinition_type in valid_types, (
                f"Redefinition {r.owning_part_qn}.{r.attribute_name} has "
                f"invalid type {r.redefinition_type}"
            )

    def test_redefinition_type_exclusivity(self, solar_battery_facts):
        """Each redefinition has exactly one redefinition_type (not None)."""
        for r in solar_battery_facts["hierarchy_data"].redefinitions:
            assert r.redefinition_type is not None, (
                f"Redefinition {r.owning_part_qn}.{r.attribute_name} has None type"
            )

    def test_all_three_types_present(self, solar_battery_facts):
        """solar_battery has LITERAL, CHAIN, and EXPRESSION redefinitions."""
        redefs = solar_battery_facts["hierarchy_data"].redefinitions
        types_found = {r.redefinition_type for r in redefs}
        expected = {RedefinitionType.LITERAL, RedefinitionType.CHAIN, RedefinitionType.EXPRESSION}
        assert expected.issubset(types_found), (
            f"solar_battery missing redefinition types: {expected - types_found}"
        )

    def test_literal_redef_has_value(self, solar_battery_facts):
        """LITERAL redefinitions have literal_value set."""
        for r in solar_battery_facts["hierarchy_data"].redefinitions:
            if r.redefinition_type == RedefinitionType.LITERAL:
                assert r.literal_value is not None, (
                    f"LITERAL redef {r.owning_part_qn}.{r.attribute_name} has None literal_value"
                )

    def test_chain_redef_has_source_path(self, solar_battery_facts):
        """CHAIN redefinitions have source_path set."""
        for r in solar_battery_facts["hierarchy_data"].redefinitions:
            if r.redefinition_type == RedefinitionType.CHAIN:
                assert r.source_path is not None and r.source_path != "", (
                    f"CHAIN redef {r.owning_part_qn}.{r.attribute_name} has empty source_path"
                )

    def test_expression_redef_has_text(self, solar_battery_facts):
        """EXPRESSION redefinitions have expression_text set."""
        for r in solar_battery_facts["hierarchy_data"].redefinitions:
            if r.redefinition_type == RedefinitionType.EXPRESSION:
                assert r.expression_text is not None and r.expression_text != "", (
                    f"EXPRESSION redef {r.owning_part_qn}.{r.attribute_name} "
                    f"has empty expression_text"
                )


# ---------------------------------------------------------------------------
# REQ-EXT-04: Aggregation expressions decomposed into typed terms
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-04")
class TestReqExt04AggregationExpressions:
    """Aggregation expressions decomposed into SumTerm, SingletonTerm, LocalTerm."""

    def test_aggregation_expressions_present(self, solar_battery_facts):
        """solar_battery hierarchy_data has 20 aggregation_expressions."""
        agg_exprs = solar_battery_facts["hierarchy_data"].aggregation_expressions
        assert len(agg_exprs) == 20, (
            f"Expected 20 aggregation_expressions, got {len(agg_exprs)}"
        )

    def test_every_expression_has_terms(self, solar_battery_facts):
        """Each aggregation expression has at least one term."""
        for agg in solar_battery_facts["hierarchy_data"].aggregation_expressions:
            total_terms = len(agg.sum_terms) + len(agg.singleton_terms) + len(agg.local_terms)
            assert total_terms > 0, (
                f"Aggregation {agg.owning_part_qn}.{agg.attribute_name} has zero terms"
            )

    def test_all_three_term_types_present(self, solar_battery_facts):
        """solar_battery aggregations collectively contain SumTerm, SingletonTerm, and LocalTerm."""
        has_sum = False
        has_singleton = False
        has_local = False
        for agg in solar_battery_facts["hierarchy_data"].aggregation_expressions:
            if agg.sum_terms:
                has_sum = True
            if agg.singleton_terms:
                has_singleton = True
            if agg.local_terms:
                has_local = True
        assert has_sum, "No SumTerm found in solar_battery aggregations"
        assert has_singleton, "No SingletonTerm found in solar_battery aggregations"
        assert has_local, "No LocalTerm found in solar_battery aggregations"

    def test_sum_terms_have_fields(self, solar_battery_facts):
        """SumTerm has part_usage_name, attribute_name, multiplicity_attr."""
        for agg in solar_battery_facts["hierarchy_data"].aggregation_expressions:
            ctx = f"{agg.owning_part_qn}.{agg.attribute_name}"
            for term in agg.sum_terms:
                assert isinstance(term, SumTerm)
                assert term.part_usage_name, (
                    f"SumTerm in {ctx} has empty part_usage_name"
                )
                assert term.attribute_name, (
                    f"SumTerm in {ctx} has empty attribute_name"
                )

    def test_singleton_terms_have_source_path(self, solar_battery_facts):
        """SingletonTerm has non-empty source_path."""
        for agg in solar_battery_facts["hierarchy_data"].aggregation_expressions:
            for term in agg.singleton_terms:
                assert isinstance(term, SingletonTerm)
                assert term.source_path, (
                    f"SingletonTerm in {agg.owning_part_qn}.{agg.attribute_name} "
                    f"has empty source_path"
                )

    def test_local_terms_have_attribute_name(self, solar_battery_facts):
        """LocalTerm has non-empty attribute_name."""
        for agg in solar_battery_facts["hierarchy_data"].aggregation_expressions:
            for term in agg.local_terms:
                assert isinstance(term, LocalTerm)
                assert term.attribute_name, (
                    f"LocalTerm in {agg.owning_part_qn}.{agg.attribute_name} "
                    f"has empty attribute_name"
                )

    def test_transformed_expression_present(self, solar_battery_facts):
        """Every aggregation has non-empty transformed_expression."""
        for agg in solar_battery_facts["hierarchy_data"].aggregation_expressions:
            assert agg.transformed_expression, (
                f"Aggregation {agg.owning_part_qn}.{agg.attribute_name} "
                f"has empty transformed_expression"
            )


# ---------------------------------------------------------------------------
# REQ-EXT-05: Template expansion produces virtual CalcUsageData
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-05")
class TestReqExt05TemplateExpansion:
    """Template calc usages produce one virtual CalcUsageData per PartUsage instance."""

    def test_virtual_usages_exist(self, solar_battery_facts):
        """solar_battery has calc_usages with owning_part_def_qn set."""
        usages = solar_battery_facts["calc_usages"]
        virtual = [u for u in usages if u.owning_part_def_qn is not None]
        assert len(virtual) > 0, "solar_battery should have virtual usages"

    def test_virtual_usages_not_template(self, solar_battery_facts):
        """All virtual usages have is_template=False (expanded, not original template)."""
        for u in solar_battery_facts["calc_usages"]:
            if u.owning_part_def_qn is not None:
                assert u.is_template is False, (
                    f"Virtual usage {u.qualified_name} has is_template=True"
                )

    def test_virtual_usage_count(self, solar_battery_facts):
        """solar_battery has exactly 10 virtual usages and 5 concrete."""
        usages = solar_battery_facts["calc_usages"]
        virtual = [u for u in usages if u.owning_part_def_qn is not None]
        concrete = [u for u in usages if u.owning_part_def_qn is None]
        assert len(virtual) == 10, f"Expected 10 virtual, got {len(virtual)}"
        assert len(concrete) == 5, f"Expected 5 concrete, got {len(concrete)}"

    def test_virtual_usage_instance_name_equals_qualified_name(
        self, solar_battery_facts
    ):
        """Virtual usages have instance_name == qualified_name.

        _create_virtual_calc_usage sets instance_name to the full
        design-relative qualified_name. Concrete usages have short
        instance_name (e.g. 'lcoe') distinct from their qualified_name.
        """
        for u in solar_battery_facts["calc_usages"]:
            if u.owning_part_def_qn is not None:
                assert u.instance_name == u.qualified_name, (
                    f"Virtual usage instance_name={u.instance_name!r} != "
                    f"qualified_name={u.qualified_name!r}"
                )
            else:
                assert u.instance_name != u.qualified_name, (
                    f"Concrete usage should have short instance_name, "
                    f"got instance_name={u.instance_name!r} == "
                    f"qualified_name={u.qualified_name!r}"
                )

    def test_virtual_usage_count_per_part_def(self, solar_battery_facts):
        """Each owning PartDef produces exactly the expected virtual usages.

        In solar_battery, each PartDef has exactly 1 PartUsage instance
        in the design, so each should produce exactly 1 virtual usage.
        """
        from collections import Counter
        usages = solar_battery_facts["calc_usages"]
        virtual = [u for u in usages if u.owning_part_def_qn is not None]
        counts = Counter(u.owning_part_def_qn for u in virtual)
        # Every owning PartDef should have exactly 1 virtual usage
        for part_def_qn, count in counts.items():
            assert count == 1, (
                f"{part_def_qn} produced {count} virtual usages, "
                f"expected 1 (one PartUsage instance per PartDef)"
            )
        # All 10 expected PartDefs should be present
        assert len(counts) == 10, (
            f"Expected 10 owning PartDefs, got {len(counts)}"
        )

    def test_owning_part_defs_match_known_templates(self, solar_battery_facts):
        """owning_part_def_qn values are known PartDef QNs."""
        known_part_defs = {
            "SolarBatteryLibrary__PV_Module",
            "SolarBatteryLibrary__String_Inverter",
            "SolarBatteryLibrary__Array_BOS",
            "SolarBatteryLibrary__Battery_Pack",
            "SolarBatteryLibrary__Hybrid_Inverter",
            "SolarBatteryLibrary__Battery_BOS",
            "SolarBatteryLibrary__Racking_Mounting",
            "SolarBatteryLibrary__Electrical_Panel",
            "SolarBatteryLibrary__Permitting_Interconnect",
            "SolarBatteryLibrary__Solar_Array",
        }
        found_qns = set()
        for u in solar_battery_facts["calc_usages"]:
            if u.owning_part_def_qn is not None:
                found_qns.add(u.owning_part_def_qn)
        assert found_qns == known_part_defs, (
            f"Mismatch: missing={known_part_defs - found_qns}, "
            f"unexpected={found_qns - known_part_defs}"
        )


# ---------------------------------------------------------------------------
# REQ-EXT-06: Extraction imports nothing from analysis/, resolution/, generation/
# ---------------------------------------------------------------------------


EXTRACTION_PKG = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "extraction"

FORBIDDEN_MODULES = {
    "analysis": {
        "absolute": ["sysml_codegen.analysis"],
        "relative": ["analysis"],
    },
    "resolution": {
        "absolute": ["sysml_codegen.resolution"],
        "relative": ["resolution"],
    },
    "generation": {
        "absolute": ["sysml_codegen.generation"],
        "relative": ["generation"],
    },
}


@pytest.mark.req("REQ-EXT-06")
class TestReqExt06NoCrossBoundaryImports:
    """Static analysis: extraction/ imports nothing from analysis/, resolution/, or generation/."""

    def test_no_analysis_imports(self):
        """No file in extraction/ imports from analysis (absolute or relative)."""
        violations = _find_forbidden_imports(FORBIDDEN_MODULES["analysis"])
        assert not violations, (
            "Forbidden analysis imports:\n" + "\n".join(violations)
        )

    def test_no_resolution_imports(self):
        """No file in extraction/ imports from resolution (absolute or relative)."""
        violations = _find_forbidden_imports(FORBIDDEN_MODULES["resolution"])
        assert not violations, (
            "Forbidden resolution imports:\n" + "\n".join(violations)
        )

    def test_no_generation_imports(self):
        """No file in extraction/ imports from generation (absolute or relative)."""
        violations = _find_forbidden_imports(FORBIDDEN_MODULES["generation"])
        assert not violations, (
            "Forbidden generation imports:\n" + "\n".join(violations)
        )


def _find_forbidden_imports(forbidden_config: dict[str, list[str]]) -> list[str]:
    """Walk AST Import/ImportFrom nodes in extraction/ for forbidden modules.

    Catches both absolute imports (``from sysml_codegen.analysis import ...``)
    and relative imports (``from ..analysis import ...``).
    """
    import ast as ast_mod

    abs_prefixes = forbidden_config["absolute"]
    rel_prefixes = forbidden_config["relative"]

    violations = []
    for py_file in sorted(EXTRACTION_PKG.glob("*.py")):
        source = py_file.read_text()
        try:
            tree = ast_mod.parse(source, filename=str(py_file))
        except SyntaxError:
            violations.append(f"  {py_file.name}: SyntaxError")
            continue
        for node in ast_mod.walk(tree):
            if isinstance(node, ast_mod.Import):
                for alias in node.names:
                    if _matches_any(alias.name, abs_prefixes):
                        violations.append(
                            f"  {py_file.name}:{node.lineno}: "
                            f"import {alias.name}"
                        )
            elif isinstance(node, ast_mod.ImportFrom):
                module = node.module or ""
                if node.level == 0 and _matches_any(module, abs_prefixes):
                    # Absolute: from sysml_codegen.analysis import ...
                    violations.append(
                        f"  {py_file.name}:{node.lineno}: "
                        f"from {module} import ..."
                    )
                elif node.level > 0 and _matches_any(module, rel_prefixes):
                    # Relative: from ..analysis import ...
                    dots = "." * node.level
                    violations.append(
                        f"  {py_file.name}:{node.lineno}: "
                        f"from {dots}{module} import ..."
                    )
    return violations


def _matches_any(module_name: str, prefixes: list[str]) -> bool:
    """Check if module_name equals or starts with any prefix."""
    return any(
        module_name == p or module_name.startswith(p + ".")
        for p in prefixes
    )


# ---------------------------------------------------------------------------
# REQ-EXT-07: output_expression_asts preserves raw SysIDE AST nodes
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-07")
class TestReqExt07AstFields:
    """AST fields exist with correct type annotations. Content verification deferred to C04."""

    def test_field_exists(self):
        """CalculationDefinitionData has output_expression_asts field with type dict[str, Any]."""
        from sysml_codegen.extraction.data_models import CalculationDefinitionData

        fields = {f.name: f for f in dataclasses.fields(CalculationDefinitionData)}
        assert "output_expression_asts" in fields, (
            "CalculationDefinitionData missing output_expression_asts field"
        )
        # Type annotation should be dict[str, Any]
        field_type = fields["output_expression_asts"].type
        # The field is annotated as dict[str, Any]; accept string or type repr
        assert "dict" in str(field_type).lower(), (
            f"output_expression_asts type is {field_type}, expected dict[str, Any]"
        )

    def test_member_expressions_field_exists(self):
        """CalculationDefinitionData has member_expressions field."""
        from sysml_codegen.extraction.data_models import CalculationDefinitionData

        fields = {f.name for f in dataclasses.fields(CalculationDefinitionData)}
        assert "member_expressions" in fields, (
            "CalculationDefinitionData missing member_expressions field"
        )

    def test_all_member_names_field_exists(self):
        """CalculationDefinitionData has all_member_names field (set[str])."""
        from sysml_codegen.extraction.data_models import CalculationDefinitionData

        fields = {f.name: f for f in dataclasses.fields(CalculationDefinitionData)}
        assert "all_member_names" in fields, (
            "CalculationDefinitionData missing all_member_names field"
        )
        field_type = fields["all_member_names"].type
        assert "set" in str(field_type).lower(), (
            f"all_member_names type is {field_type}, expected set[str]"
        )

    def test_live_exact_identity_sidecar_fields_exist(self):
        """Exact-route calc/member UUID fields are explicit live-only sidecars."""
        from sysml_codegen.extraction.data_models import (
            AttributeInfo,
            CalculationDefinitionData,
        )

        calc_fields = {field.name: field for field in dataclasses.fields(CalculationDefinitionData)}
        attr_fields = {field.name: field for field in dataclasses.fields(AttributeInfo)}
        expected = {
            "element_id",
            "output_expression_asts_by_id",
            "all_member_ids",
            "member_expressions_by_id",
            "member_names_by_id",
        }
        assert expected <= set(calc_fields)
        assert all(calc_fields[name].metadata.get("snapshot_exclude") for name in expected)
        assert attr_fields["element_id"].metadata.get("snapshot_exclude") is True

    def test_snapshot_ast_fields_nullified_in_raw_json(self):
        """Raw snapshot JSON has null AST fields (serialization boundary).

        The snapshot serializer nullifies SysIDE Java objects that can't
        survive JSON round-trip. This test reads the raw JSON directly
        (bypassing the loader) to verify the serializer did its job.
        Full AST content verification is deferred to C04.
        """
        import json

        snapshot_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "solar_battery_model"
            / "extraction_snapshot.json"
        )
        raw = json.loads(snapshot_path.read_text())
        for cd in raw["calc_defs"]:
            ast_val = cd.get("output_expression_asts")
            assert ast_val is None or ast_val == {}, (
                f"calc_def {cd['name']}: raw JSON "
                f"output_expression_asts should be null/empty, "
                f"got {ast_val!r}"
            )
            member_val = cd.get("member_expressions")
            assert member_val is None or member_val == {}, (
                f"calc_def {cd['name']}: raw JSON "
                f"member_expressions should be null/empty, "
                f"got {member_val!r}"
            )
            assert "element_id" not in cd
            assert "output_expression_asts_by_id" not in cd
            assert "all_member_ids" not in cd
            assert "member_expressions_by_id" not in cd
            assert "member_names_by_id" not in cd


# ---------------------------------------------------------------------------
# REQ-EXT-02 (extended): EXPRESSION binding type coverage
# Closes fixture gap C1 from Phase 2 audit.
# ---------------------------------------------------------------------------

# Expected EXPRESSION bindings in expression_binding_probe:
# Each tuple is (calc_usage_instance_name, param_name)
EXPECTED_EXPRESSION_BINDINGS = [
    ("cost_calc", "combined_input"),       # Pattern 1: binary op (two refs, +)
    ("adjusted_calc", "combined_input"),   # Pattern 2: ref * literal
    ("full_cost_calc", "combined_input"),  # Pattern 3: 3-term (ref + ref + ref)
    ("delta_calc", "value_a"),             # Pattern 4a: binary op (two refs, +)
    ("delta_calc", "value_b"),             # Pattern 4b: ref * literal
    ("net_calc", "x"),                     # Pattern 5: binary op (ref - ref)
]

# Expected non-EXPRESSION bindings (REFERENCE) in expression_binding_probe
EXPECTED_REFERENCE_BINDINGS_EXPR_PROBE = [
    ("cost_calc", "tax_rate"),
    ("adjusted_calc", "tax_rate"),
    ("full_cost_calc", "tax_rate"),
]


@pytest.mark.req("REQ-EXT-02")
class TestExpressionBindingType:
    """EXPRESSION binding type (OperatorExpression) coverage from expression_binding_probe.

    Closes fixture gap C1: BindingType.EXPRESSION was absent from all 6 original
    fixture models. The expression_binding_probe fixture exercises the code path
    at usage_extractor.py:559-566.
    """

    def test_expression_binding_type_present(self, expression_binding_facts):
        """expression_binding_probe has EXPRESSION bindings."""
        all_types = set()
        for usage in expression_binding_facts["calc_usages"]:
            for binding in usage.bindings:
                all_types.add(binding.binding_type)
        assert BindingType.EXPRESSION in all_types, (
            f"expression_binding_probe missing EXPRESSION binding type. "
            f"Found: {all_types}"
        )

    def test_expression_binding_count(self, expression_binding_facts):
        """expression_binding_probe has exactly 6 EXPRESSION bindings."""
        expr_count = 0
        for usage in expression_binding_facts["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.EXPRESSION:
                    expr_count += 1
        assert expr_count == 6, (
            f"Expected 6 EXPRESSION bindings, got {expr_count}"
        )

    @pytest.mark.parametrize(
        "usage_name,param_name",
        EXPECTED_EXPRESSION_BINDINGS,
        ids=[f"{u}.{p}" for u, p in EXPECTED_EXPRESSION_BINDINGS],
    )
    def test_specific_expression_binding(
        self, expression_binding_facts, usage_name, param_name
    ):
        """Each expected EXPRESSION binding is correctly classified."""
        usages = expression_binding_facts["calc_usages"]
        usage = next((u for u in usages if u.instance_name == usage_name), None)
        assert usage is not None, f"CalcUsage '{usage_name}' not found"

        binding = next((b for b in usage.bindings if b.param_name == param_name), None)
        assert binding is not None, (
            f"Binding '{param_name}' not found in {usage_name}"
        )
        assert binding.binding_type == BindingType.EXPRESSION, (
            f"{usage_name}.{param_name}: expected EXPRESSION, "
            f"got {binding.binding_type.value}"
        )

    def test_expression_binding_has_raw_expression(self, expression_binding_facts):
        """EXPRESSION bindings have raw_expression containing 'OperatorExpression'."""
        for usage in expression_binding_facts["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.EXPRESSION:
                    assert binding.raw_expression is not None, (
                        f"{usage.instance_name}.{binding.param_name}: "
                        f"EXPRESSION binding has None raw_expression"
                    )
                    assert "OperatorExpression" in binding.raw_expression, (
                        f"{usage.instance_name}.{binding.param_name}: "
                        f"raw_expression={binding.raw_expression!r} "
                        f"missing 'OperatorExpression'"
                    )

    def test_expression_binding_source_path_is_none(self, expression_binding_facts):
        """EXPRESSION bindings have source_path=None (no single source reference)."""
        for usage in expression_binding_facts["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.EXPRESSION:
                    assert binding.source_path is None, (
                        f"{usage.instance_name}.{binding.param_name}: "
                        f"EXPRESSION binding should have source_path=None, "
                        f"got {binding.source_path!r}"
                    )

    def test_expression_binding_literal_value_is_none(
        self, expression_binding_facts
    ):
        """EXPRESSION bindings have literal_value=None (not a literal)."""
        for usage in expression_binding_facts["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.EXPRESSION:
                    assert binding.literal_value is None, (
                        f"{usage.instance_name}.{binding.param_name}: "
                        f"EXPRESSION binding should have literal_value=None, "
                        f"got {binding.literal_value!r}"
                    )

    def test_expression_binding_ast_is_a_live_parser_handle_not_data(
        self, expression_binding_facts
    ):
        """EXPRESSION binding expression_ast is a live SysIDE node, not serializable data.

        Extraction stores the parser's own ``OperatorExpression`` object. It is a handle
        into the loaded model, so it carries no JSON form — which is the reason no
        snapshot has ever been able to hold it. Stated here against ``json.dumps``, which
        refuses it on its own account rather than by asking the extractor.

        Repointed from ``test_expression_binding_ast_nullified_in_snapshot``, whose
        oracle was the v5 serializer nulling this field
        (``snapshot/serializer.py``, a deletion row).
        """
        seen = 0
        for usage in expression_binding_facts["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type != BindingType.EXPRESSION:
                    continue
                seen += 1
                assert binding.expression_ast is not None, (
                    f"{usage.instance_name}.{binding.param_name}: "
                    f"EXPRESSION binding lost its parser handle"
                )
                with pytest.raises(TypeError):
                    json.dumps(binding.expression_ast)
        assert seen == len(EXPECTED_EXPRESSION_BINDINGS), (
            f"expected {len(EXPECTED_EXPRESSION_BINDINGS)} EXPRESSION bindings "
            f"in the probe, got {seen}"
        )

    @pytest.mark.parametrize(
        "usage_name,param_name",
        EXPECTED_REFERENCE_BINDINGS_EXPR_PROBE,
        ids=[f"{u}.{p}" for u, p in EXPECTED_REFERENCE_BINDINGS_EXPR_PROBE],
    )
    def test_non_expression_bindings_still_correct(
        self, expression_binding_facts, usage_name, param_name
    ):
        """Non-EXPRESSION bindings in the same CalcUsages are still correctly classified."""
        usages = expression_binding_facts["calc_usages"]
        usage = next((u for u in usages if u.instance_name == usage_name), None)
        assert usage is not None
        binding = next((b for b in usage.bindings if b.param_name == param_name), None)
        assert binding is not None
        assert binding.binding_type == BindingType.REFERENCE, (
            f"{usage_name}.{param_name}: expected REFERENCE, "
            f"got {binding.binding_type.value}"
        )

    def test_mixed_binding_types_on_same_usage(self, expression_binding_facts):
        """CalcUsages can have both EXPRESSION and non-EXPRESSION bindings."""
        usages = expression_binding_facts["calc_usages"]
        cost_calc = next(u for u in usages if u.instance_name == "cost_calc")
        types = {b.binding_type for b in cost_calc.bindings}
        assert BindingType.EXPRESSION in types, "cost_calc missing EXPRESSION binding"
        assert BindingType.REFERENCE in types, "cost_calc missing REFERENCE binding"

    def test_all_bound_binding_types_across_models(self, live_extraction_facts):
        """With expression_binding_probe, all 4 bound BindingType values have fixture coverage.

        Previously EXPRESSION was absent from all 6 original models.
        UNBOUND params go into CalcUsageData.unbound_params (string list),
        not into bindings, so BindingType.UNBOUND doesn't appear in binding lists.
        """
        all_types = set()
        for model_name, snapshot in live_extraction_facts.items():
            for usage in snapshot["calc_usages"]:
                for binding in usage.bindings:
                    all_types.add(binding.binding_type)
        expected_bound = {
            BindingType.CHAIN,
            BindingType.REFERENCE,
            BindingType.LITERAL,
            BindingType.EXPRESSION,
        }
        assert expected_bound.issubset(all_types), (
            f"Missing binding types across all models: {expected_bound - all_types}"
        )

    def test_total_binding_counts(self, expression_binding_facts):
        """expression_binding_probe has 5 CalcUsages with 9 total bindings."""
        usages = expression_binding_facts["calc_usages"]
        assert len(usages) == 5, f"Expected 5 calc_usages, got {len(usages)}"
        total_bindings = sum(len(u.bindings) for u in usages)
        assert total_bindings == 9, (
            f"Expected 9 total bindings (6 EXPRESSION + 3 REFERENCE), "
            f"got {total_bindings}"
        )


# ---------------------------------------------------------------------------
# Live-fixture helper (REQ-EXT-08/09)
#
# The silent-failure diagnostics fire during live extraction, not against a
# committed snapshot (zero_output_calc has no snapshot -- it raises once D3
# lands). These tests load a real fixture and skip when syside is unavailable.
# ---------------------------------------------------------------------------
FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _load_live_extractor(model_name: str) -> SysMLDataExtractor:
    """Load a fixture model with a live extractor.

    Skips (does not fail) when syside cannot load -- e.g. no license in CI --
    mirroring the ``sample_extractor`` fixture convention.
    """
    extractor = SysMLDataExtractor([FIXTURES_DIR / model_name])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:  # syside license not configured
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip(f"Could not load {model_name}")
    return extractor


# ---------------------------------------------------------------------------
# REQ-EXT-08: Zero-output calc def fails fast at extraction (I3)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-08")
class TestReqExt08ZeroOutputFailFast:
    """A calc def with zero output attributes raises at extraction, never
    reaching the Jinja module template."""

    def test_zero_output_calc_def_raises(self):
        extractor = _load_live_extractor("zero_output_calc")
        with pytest.raises(ValueError, match="zero output attributes"):
            extractor.extract_calculation_definitions()


# ---------------------------------------------------------------------------
# REQ-EXT-09: Dropped constraints reported once, structurally (I4)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-09")
class TestReqExt09ConstraintDropDiagnostic:
    """Every dropped predicate the manifest sweep sees — including subtype shapes
    like ``assert`` — has a catalog carrier, with counts anchored independently
    of the production query.

    Re-anchored for Item 14 W2: the drop-manifest report/render surface these
    tests originally pinned is retired (the catalog is now the proven single
    source of truth, `test_constraint_migration_mapping.py`); what survives here
    is the manifest sweep itself (still live, still load-bearing for the mapping
    test) and its catalog/unassessed-carrier counterpart, replacing the report's
    log-line assertions.
    """

    # Independent anchor for catf_mfe_model, transcribed from the fixture source
    # (NOT the production query):
    #   grep -rhE '^\s*constraint\s+[A-Za-z_][A-Za-z0-9_]*\s*\{' \
    #     tests/fixtures/catf_mfe_model --include=*.sysml | wc -l   ->   65
    # 65 plain constraint usages, no assert/require/satisfy, spanning calc-def
    # (51), part-def (5), and part-usage (9) owners — all droppable.
    CATF_DROPPABLE = 65

    # Of those 65, the owner-kind split, transcribed the same way:
    #   calc_def 51, part_def 5, part_usage 9.
    # Only the nine part-usage-owned ones sit on a design instance, so only those
    # nine can reach an instance-path constraint record at all.
    CATF_OWNER_KIND_SPLIT = {"calc_def": 51, "part_def": 5, "part_usage": 9}

    def test_dropped_constraints_span_owner_kinds(self):
        # I4: catf_mfe's 65 droppable usages span all three owner kinds (R1,
        # confirmed empirically — see test_constraint_migration_mapping.py).
        from collections import Counter

        extractor = _load_live_extractor("catf_mfe_model")
        manifest = extractor.collect_constraint_manifest()
        assert len(manifest) == self.CATF_DROPPABLE
        assert Counter(e.owner_kind.value for e in manifest) == self.CATF_OWNER_KIND_SPLIT

    def test_instance_reaching_constraints_all_land_unassessed(self):
        """The nine part-usage-owned constraints all land unassessed, none eligible.

        The second arm of this subject used to read
        ``build_pipeline_context(catf_mfe_model).concrete_constraints`` — 65 records, none
        eligible. That builder retires with the v5 family, and the exact route refuses
        ``catf_mfe_model`` outright (``SI_SELF_BINDING`` on
        ``…catf_vacuum_pumping__pump_load.pumping_speed_total``). It runs on
        ``catf_mfe_d5`` instead — the same model with that one formal renamed, proved a
        rename and nothing else by ``scripts/make_d5_variant.py --check`` and pinned by
        ``test_d5_variants.py`` — and the identical sweep is re-asserted here so the move
        cannot quietly change the subject.

        The exact route records only the constraints that reach a design instance, so the
        count is the nine part-usage-owned ones, not 65. The other 56 are owned by a
        definition and mint no instance-path record. Every one of the nine is excluded as
        an unassessed form; none is silently eligible, which is the claim that mattered.
        """
        from collections import Counter

        from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

        extractor = _load_live_extractor("catf_mfe_d5")
        manifest = extractor.collect_constraint_manifest()
        assert len(manifest) == self.CATF_DROPPABLE, "the d5 rename changed the sweep"
        assert Counter(e.owner_kind.value for e in manifest) == self.CATF_OWNER_KIND_SPLIT

        catalog = build_elaborated_pipeline([FIXTURES_DIR / "catf_mfe_d5"]).constraint_catalog
        assert not catalog.concrete_entries, "no catf_mfe constraint may lower to eligible"
        assert len(catalog.excluded_records) == self.CATF_OWNER_KIND_SPLIT["part_usage"]
        assert {r.exclusion.kind for r in catalog.excluded_records} == {"unassessed_form"}
        assert {reason for r in catalog.excluded_records for reason in r.exclusion.reasons} == {
            "eligibility_unassessed"
        }

    def test_wi014_assert_is_reported(self):
        # wi014_toy's only constraint is `assert constraint affordable` at
        # toy_plant.sysml:51 — an AssertConstraintUsage, invisible to the old
        # exact-type query. Independent literal: exactly 1 droppable assert,
        # carried as an ELIGIBLE catalog entry (lowering succeeds for this shape).
        extractor = _load_live_extractor("wi014_toy")
        manifest = extractor.collect_constraint_manifest()
        asserts = [e for e in manifest if e.constraint_kind is ConstraintKind.ASSERT]
        assert len(asserts) == 1, "wi014_toy must carry exactly one assert constraint"
        assert asserts[0].constraint_name == "affordable"

        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        ctx = build_pipeline_context([FIXTURES_DIR / "wi014_toy"])
        usage_qn = f"{asserts[0].owner_qualified_name}::{asserts[0].constraint_name}"
        eligible_usage_qns = {
            e.usage_qualified_name
            for e in (ctx.computation_graph.constraint_catalog.concrete_entries or [])
        }
        assert usage_qn in eligible_usage_qns, (
            "the assert constraint must be carried as an eligible catalog entry"
        )

    def test_mutation_check_discriminates(self):
        # MF5: flip the injectable policy to exact-type and the assert vanishes.
        # If this ever fails (the assert survives an exact-type sweep), the pin
        # above is a tautology again.
        extractor = _load_live_extractor("wi014_toy")
        blind = extractor.collect_constraint_manifest(include_subtypes=False)
        assert not any(
            e.constraint_kind is ConstraintKind.ASSERT for e in blind
        ), "exact-type sweep must MISS the assert — otherwise the test does not discriminate"


@pytest.mark.req("REQ-EXT-09")
class TestConstraintRequireAndExclusion:
    """`require constraint` is a reported plain predicate; a requirement usage is
    swept-and-excluded and stays observable in the sentinel.

    ``item4_require`` is the only codegen fixture exercising the exclusion path
    live: ``within_budget`` (a ``require constraint``, a plain ConstraintUsage)
    and ``demo_req`` (a RequirementUsage, excluded).
    """

    def test_require_constraint_is_reported_plain(self):
        extractor = _load_live_extractor("item4_require")
        manifest = extractor.collect_constraint_manifest()
        require_entries = [e for e in manifest if e.constraint_name == "within_budget"]
        assert len(require_entries) == 1, "the require constraint must be swept"
        assert require_entries[0].constraint_kind is ConstraintKind.PLAIN
        assert require_entries[0].constraint_kind in DROPPABLE_KINDS

    def test_requirement_usage_is_excluded(self):
        extractor = _load_live_extractor("item4_require")
        manifest = extractor.collect_constraint_manifest()
        req_entries = [e for e in manifest if e.constraint_name == "demo_req"]
        assert len(req_entries) == 1, "the requirement usage is swept (subtype of ConstraintUsage)"
        assert req_entries[0].constraint_kind is ConstraintKind.REQUIREMENT
        assert req_entries[0].constraint_kind not in DROPPABLE_KINDS

    def test_scanned_and_excluded_counts(self):
        # scanned 2, reported 1 (the require constraint), excluded 1 (the
        # requirement usage) — the exclusion is observable in the manifest's own
        # kind tags, not only a retired report's log line.
        extractor = _load_live_extractor("item4_require")
        manifest = extractor.collect_constraint_manifest()
        assert len(manifest) == 2
        droppable = [e for e in manifest if e.constraint_kind in DROPPABLE_KINDS]
        excluded = [e for e in manifest if e.constraint_kind not in DROPPABLE_KINDS]
        assert len(droppable) == 1
        assert len(excluded) == 1


@pytest.mark.req("REQ-EXT-09")
class TestConstraintDroppablePolicyParity:
    """INV-D: codegen's kind-derived droppability equals the adapter's single
    policy source (``is_droppable_constraint``), element by element — so the two
    repos cannot drift on what counts as a dropped predicate."""

    def test_ladder_droppable_equals_adapter_policy(self):
        from agentic_mbse.sysml.syside_adapter import is_droppable_constraint

        extractor = _load_live_extractor("item4_require")
        swept = list(
            extractor.adapter.elements_of_type(
                extractor.model, "ConstraintUsage", include_subtypes=True
            )
        )
        assert swept, "fixture must carry swept constraint usages"
        for elem in swept:
            kind = extractor._classify_constraint_kind(elem)
            assert (kind in DROPPABLE_KINDS) == is_droppable_constraint(elem), (
                f"kind-derived droppability disagrees with the adapter policy for {elem}"
            )
