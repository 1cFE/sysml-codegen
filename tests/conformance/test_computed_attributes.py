"""C05: Computed Attribute Classification conformance tests.

Verifies that computed attribute extraction output conforms to REQ-CA-01
through REQ-CA-07 from design intent doc 16-computed-attributes.md. All
tests use real snapshot data captured in Phase 0 -- no mocks.

Requirements: REQ-CA-01 through REQ-CA-07.
"""

from __future__ import annotations

import ast as ast_mod
from pathlib import Path

import pytest

from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from tests.helpers.registry_compat import registry_register


# ---------------------------------------------------------------------------
# Expected counts from Phase 0 snapshot analysis
# ---------------------------------------------------------------------------

# attr_expr_probe: 14 FORMULA, 1 EXPOSE_COMPUTED, 3 EXPOSE_PURE = 18 total
ATTR_EXPR_PROBE_COUNTS = {
    ComputedAttributeClassification.FORMULA: 14,
    ComputedAttributeClassification.EXPOSE_COMPUTED: 1,
    ComputedAttributeClassification.EXPOSE_PURE: 3,
}

# Known FORMULA compiled expressions for attr_expr_probe (regression guard)
FORMULA_COMPILED_EXPRESSIONS = [
    ("area", "(inputs.length * inputs.width)"),
    ("q_scientific", "(inputs.p_fusion / inputs.p_input)"),
    ("total_dim", "(inputs.length + inputs.width)"),
    ("net_length", "(inputs.length - 1.0)"),
    ("volume", "((inputs.length * inputs.width) * inputs.height)"),
    ("perimeter", "((2.0 * inputs.length) + (2.0 * inputs.width))"),
    ("minor_radius", "(((inputs.r_inner + inputs.r_outer) / 2.0) - inputs.r_major)"),
    ("gross_electric_simple", "((inputs.eta_thermal * inputs.p_fusion) + (inputs.eta_direct * inputs.p_input))"),
    ("p_alpha", "((inputs.p_fusion * 3.52) / 17.58)"),
    ("p_neutron", "((inputs.p_fusion * 14.06) / 17.58)"),
    ("p_blanket_thermal", "(((inputs.m_neutron * inputs.p_fusion) + inputs.p_input) + ((inputs.eta_thermal * ((inputs.f_pump * inputs.eta_pump) + inputs.f_subsystem)) * (inputs.m_neutron * inputs.p_fusion)))"),
    ("cost", "(inputs.area * inputs.rate)"),
    ("marked_up_cost", "(inputs.cost * inputs.markup)"),
    ("cost_density", "(inputs.cost / inputs.volume)"),
]

# Known literal attribute names in attr_expr_probe (stay in design_attributes, not computed_attributes)
LITERAL_ATTR_NAMES = {"length", "width", "height", "rate", "markup", "p_fusion", "p_input",
                      "eta_thermal", "eta_direct", "m_neutron", "f_pump", "eta_pump",
                      "f_subsystem", "r_inner", "r_outer", "r_major", "kappa"}

# Chain attrs that reference computed siblings but NOT themselves
CHAIN_ATTRS = {
    "cost": {"area", "rate"},
    "marked_up_cost": {"cost", "markup"},
    "cost_density": {"cost", "volume"},
}

# All models with extraction snapshots
ALL_MODELS = [
    "sample_model",
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
    "issue22_model",
]


# ---------------------------------------------------------------------------
# REQ-CA-01: Classification is exhaustive and exclusive (5-way enum)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-01")
class TestReqCa01Classification:
    """Computed attribute classification is exhaustive (5 values) and exclusive (one per attr)."""

    def test_classification_exhaustive(self, attr_expr_probe_snapshot):
        """Every ComputedAttributeData has a valid ComputedAttributeClassification enum member."""
        valid = set(ComputedAttributeClassification)
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            assert ca.classification in valid, (
                f"Attribute {ca.python_name} has invalid classification {ca.classification}"
            )

    def test_classification_exclusive(self, attr_expr_probe_snapshot):
        """Each attribute has exactly one classification; verify all 18 attrs each have one value."""
        attrs = attr_expr_probe_snapshot["computed_attributes"]
        assert len(attrs) == 18, f"Expected 18 computed_attributes, got {len(attrs)}"
        for ca in attrs:
            assert ca.classification is not None, (
                f"Attribute {ca.python_name} has None classification"
            )
            assert isinstance(ca.classification, ComputedAttributeClassification), (
                f"Attribute {ca.python_name} classification is {type(ca.classification)}, "
                f"not ComputedAttributeClassification"
            )

    def test_all_five_values_defined(self):
        """The ComputedAttributeClassification enum has exactly 6 members.

        Item 10 added EXPOSE_CHAIN_TENTATIVE (the leaf's structural multi-hop
        candidate, finalized by the confirm pass).
        """
        members = list(ComputedAttributeClassification)
        assert len(members) == 6, (
            f"Expected 6 ComputedAttributeClassification members, got {len(members)}: "
            f"{[m.value for m in members]}"
        )
        expected_values = {
            "formula", "expose_pure", "expose_computed",
            "expose_chain_tentative", "literal", "unresolvable",
        }
        actual_values = {m.value for m in members}
        assert actual_values == expected_values, (
            f"Enum values mismatch: missing={expected_values - actual_values}, "
            f"unexpected={actual_values - expected_values}"
        )

    def test_fixture_coverage(self, attr_expr_probe_snapshot):
        """attr_expr_probe exercises 3 of 5 classifications: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED.

        LITERAL is excluded by design (not in computed_attributes list).
        UNRESOLVABLE absent (coverage gap documented in plan).
        """
        classifications = {ca.classification for ca in attr_expr_probe_snapshot["computed_attributes"]}
        expected_present = {
            ComputedAttributeClassification.FORMULA,
            ComputedAttributeClassification.EXPOSE_PURE,
            ComputedAttributeClassification.EXPOSE_COMPUTED,
        }
        assert expected_present.issubset(classifications), (
            f"Missing classifications: {expected_present - classifications}"
        )

    def test_expose_computed_no_compilation(self, attr_expr_probe_snapshot):
        """EXPOSE_COMPUTED attrs have compiled_expression is None and compilability == MANUAL_REQUIRED."""
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.EXPOSE_COMPUTED:
                assert ca.compiled_expression is None, (
                    f"EXPOSE_COMPUTED {ca.python_name} has non-None compiled_expression: "
                    f"{ca.compiled_expression}"
                )
                assert ca.compilability == Compilability.MANUAL_REQUIRED, (
                    f"EXPOSE_COMPUTED {ca.python_name} has compilability={ca.compilability}, "
                    f"expected MANUAL_REQUIRED"
                )

    def test_expose_pure_no_compilation(self, attr_expr_probe_snapshot):
        """EXPOSE_PURE attrs have compiled_expression is None and compilability == MANUAL_REQUIRED."""
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
                assert ca.compiled_expression is None, (
                    f"EXPOSE_PURE {ca.python_name} has non-None compiled_expression: "
                    f"{ca.compiled_expression}"
                )
                assert ca.compilability == Compilability.MANUAL_REQUIRED, (
                    f"EXPOSE_PURE {ca.python_name} has compilability={ca.compilability}, "
                    f"expected MANUAL_REQUIRED"
                )


# ---------------------------------------------------------------------------
# REQ-CA-02: FORMULA attributes compile to valid Python
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-02")
class TestReqCa02FormulaCompilation:
    """FORMULA attributes produce valid, compilable Python expressions."""

    def test_formula_compiles_to_python(self, attr_expr_probe_snapshot):
        """Every FORMULA attribute has non-None compiled_expression and FULLY_COMPILABLE."""
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.FORMULA:
                assert ca.compiled_expression is not None, (
                    f"FORMULA {ca.python_name} has None compiled_expression"
                )
                assert ca.compilability == Compilability.FULLY_COMPILABLE, (
                    f"FORMULA {ca.python_name} has compilability={ca.compilability}, "
                    f"expected FULLY_COMPILABLE"
                )

    def test_formula_ast_parse(self, attr_expr_probe_snapshot):
        """Every FORMULA compiled_expression passes ast.parse() -- valid Python."""
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.FORMULA:
                assert ca.compiled_expression is not None
                try:
                    ast_mod.parse(ca.compiled_expression, mode="eval")
                except SyntaxError as e:
                    pytest.fail(
                        f"FORMULA {ca.python_name} compiled_expression is not valid Python: "
                        f"{ca.compiled_expression!r} -- {e}"
                    )

    def test_formula_compilation_cross_model_solar_battery(self, solar_battery_snapshot):
        """Every FORMULA in solar_battery has valid compiled_expression that passes ast.parse()."""
        formulas = [
            ca for ca in solar_battery_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.FORMULA
        ]
        assert len(formulas) > 0, "solar_battery should have at least one FORMULA attribute"
        for ca in formulas:
            assert ca.compiled_expression is not None, (
                f"FORMULA {ca.python_name} has None compiled_expression"
            )
            try:
                ast_mod.parse(ca.compiled_expression, mode="eval")
            except SyntaxError as e:
                pytest.fail(
                    f"solar_battery FORMULA {ca.python_name} is not valid Python: "
                    f"{ca.compiled_expression!r} -- {e}"
                )

    def test_formula_inputs_prefix(self, attr_expr_probe_snapshot):
        """Every variable reference in FORMULA compiled_expressions uses inputs. prefix."""
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            if ca.classification != ComputedAttributeClassification.FORMULA:
                continue
            assert ca.compiled_expression is not None
            tree = ast_mod.parse(ca.compiled_expression, mode="eval")
            for node in ast_mod.walk(tree):
                if isinstance(node, ast_mod.Attribute) and isinstance(node.value, ast_mod.Name):
                    assert node.value.id == "inputs", (
                        f"FORMULA {ca.python_name}: attribute reference uses "
                        f"'{node.value.id}.{node.attr}' instead of 'inputs.{node.attr}'"
                    )

    @pytest.mark.parametrize(
        "python_name,expected_expression",
        FORMULA_COMPILED_EXPRESSIONS,
        ids=[name for name, _ in FORMULA_COMPILED_EXPRESSIONS],
    )
    def test_formula_compiled_expressions_known_good(
        self, attr_expr_probe_snapshot, python_name, expected_expression
    ):
        """Each FORMULA attr in attr_expr_probe matches expected compiled_expression (regression)."""
        ca_map = {
            ca.python_name: ca
            for ca in attr_expr_probe_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.FORMULA
        }
        assert python_name in ca_map, (
            f"FORMULA attribute {python_name} not found in computed_attributes"
        )
        actual = ca_map[python_name].compiled_expression
        assert actual == expected_expression, (
            f"FORMULA {python_name} compiled_expression mismatch:\n"
            f"  expected: {expected_expression}\n"
            f"  actual:   {actual}"
        )


# ---------------------------------------------------------------------------
# REQ-CA-03: EXPOSE_PURE produces alias only for PartUsage (not PartDef)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-03")
class TestReqCa03ExposePure:
    """EXPOSE_PURE on PartUsage produces ChannelAlias; on PartDef does NOT."""

    def test_expose_pure_partusage_only(
        self, solar_battery_snapshot, attr_expr_probe_snapshot
    ):
        """solar_battery EXPOSE_PURE on PartDef has no alias; attr_expr_probe EXPOSE_PURE on PartUsage does."""
        # solar_battery: misc_hardware_cost is EXPOSE_PURE on PartDef (is_on_part_definition=True)
        sb_expose_pure = [
            ca for ca in solar_battery_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE
        ]
        assert len(sb_expose_pure) == 1, (
            f"Expected 1 EXPOSE_PURE in solar_battery, got {len(sb_expose_pure)}"
        )
        assert sb_expose_pure[0].is_on_part_definition is True, (
            f"solar_battery EXPOSE_PURE should be on PartDef"
        )
        # No expose_pure alias should exist in solar_battery
        sb_ep_aliases = [
            a for a in solar_battery_snapshot["channel_aliases"]
            if a.source == "expose_pure"
        ]
        assert len(sb_ep_aliases) == 0, (
            f"solar_battery should have 0 expose_pure aliases (PartDef guard), "
            f"got {len(sb_ep_aliases)}"
        )

        # attr_expr_probe: EXPOSE_PURE on PartUsage (is_on_part_definition=False) DO have aliases
        aep_expose_pure = [
            ca for ca in attr_expr_probe_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE
        ]
        assert all(not ca.is_on_part_definition for ca in aep_expose_pure), (
            "attr_expr_probe EXPOSE_PURE should all be on PartUsage"
        )
        aep_ep_aliases = [
            a for a in attr_expr_probe_snapshot["channel_aliases"]
            if a.source == "expose_pure"
        ]
        assert len(aep_ep_aliases) == len(aep_expose_pure), (
            f"attr_expr_probe: expected {len(aep_expose_pure)} expose_pure aliases, "
            f"got {len(aep_ep_aliases)}"
        )

    def test_expose_pure_alias_count(self, attr_expr_probe_snapshot):
        """Number of expose_pure aliases equals number of EXPOSE_PURE attrs with is_on_part_definition=false."""
        expose_pure_on_usage = [
            ca for ca in attr_expr_probe_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE
            and not ca.is_on_part_definition
        ]
        aliases = [
            a for a in attr_expr_probe_snapshot["channel_aliases"]
            if a.source == "expose_pure"
        ]
        assert len(aliases) == len(expose_pure_on_usage), (
            f"Expected {len(expose_pure_on_usage)} expose_pure aliases, got {len(aliases)}"
        )

    def test_expose_pure_alias_canonical_name(self, attr_expr_probe_snapshot):
        """Each EXPOSE_PURE alias has canonical_name format '{instance}.{output}'."""
        aliases = [
            a for a in attr_expr_probe_snapshot["channel_aliases"]
            if a.source == "expose_pure"
        ]
        expected = {
            "scale_result": "scale_calc.result",
            "half_vol": "split.half",
            "quarter_vol": "split.quarter",
        }
        for alias in aliases:
            assert alias.alias_name in expected, (
                f"Unexpected expose_pure alias: {alias.alias_name}"
            )
            assert alias.canonical_name == expected[alias.alias_name], (
                f"Alias {alias.alias_name} canonical_name mismatch: "
                f"expected {expected[alias.alias_name]!r}, got {alias.canonical_name!r}"
            )
            assert "." in alias.canonical_name, (
                f"Alias {alias.alias_name} canonical_name missing '.': {alias.canonical_name}"
            )


# ---------------------------------------------------------------------------
# REQ-CA-04: LITERAL attributes excluded from computed_attributes
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-04")
class TestReqCa04LiteralExcluded:
    """LITERAL classification excluded from computed_attributes list."""

    def test_literal_excluded(self, extraction_snapshots):
        """No ComputedAttributeData in any fixture model has classification == LITERAL."""
        for model_name, snapshot in extraction_snapshots.items():
            for ca in snapshot["computed_attributes"]:
                assert ca.classification != ComputedAttributeClassification.LITERAL, (
                    f"{model_name}: attribute {ca.python_name} has LITERAL classification "
                    f"but should not appear in computed_attributes"
                )

    def test_literal_attr_not_in_aliases(self, attr_expr_probe_snapshot):
        """Known literal attribute names do not appear as alias_name in channel_aliases."""
        alias_names = {a.alias_name for a in attr_expr_probe_snapshot["channel_aliases"]}
        overlap = LITERAL_ATTR_NAMES & alias_names
        assert not overlap, (
            f"Literal attribute names found in channel_aliases: {overlap}"
        )


# ---------------------------------------------------------------------------
# REQ-CA-05: UNRESOLVABLE produces no alias; zero coverage in fixtures
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-05")
class TestReqCa05Unresolvable:
    """UNRESOLVABLE and EXPOSE_COMPUTED do not produce aliases; UNRESOLVABLE absent from fixtures."""

    def test_unresolvable_no_alias(self, extraction_snapshots):
        """Only EXPOSE_PURE (on PartUsage) produces aliases. No aliases for other classifications."""
        for model_name, snapshot in extraction_snapshots.items():
            ep_aliases = [
                a for a in snapshot["channel_aliases"]
                if a.source == "expose_pure"
            ]
            expose_pure_names = {
                ca.python_name
                for ca in snapshot["computed_attributes"]
                if ca.classification == ComputedAttributeClassification.EXPOSE_PURE
                and not ca.is_on_part_definition
            }
            alias_names = {a.alias_name for a in ep_aliases}
            # Every expose_pure alias should correspond to an EXPOSE_PURE attr
            unexpected = alias_names - expose_pure_names
            assert not unexpected, (
                f"{model_name}: expose_pure aliases for non-EXPOSE_PURE attrs: {unexpected}"
            )

    def test_unresolvable_coverage_gap(self, extraction_snapshots):
        """Document: no UNRESOLVABLE attrs in any fixture model (coverage gap)."""
        for model_name, snapshot in extraction_snapshots.items():
            unresolvable = [
                ca for ca in snapshot["computed_attributes"]
                if ca.classification == ComputedAttributeClassification.UNRESOLVABLE
            ]
            assert len(unresolvable) == 0, (
                f"{model_name}: expected 0 UNRESOLVABLE computed_attributes, "
                f"got {len(unresolvable)}: {[ca.python_name for ca in unresolvable]}"
            )


# ---------------------------------------------------------------------------
# REQ-CA-06: AttributeResolutionKind enum and resolution map
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-06")
class TestReqCa06ResolutionKind:
    """AttributeResolutionKind enum and _build_attribute_resolution_map() with real data."""

    def test_resolution_kind_enum(self):
        """AttributeResolutionKind has exactly 3 values: FORMULA, EXPOSE_ALIAS, LITERAL."""
        from sysml_codegen.resolution.graph_builder import AttributeResolutionKind

        members = list(AttributeResolutionKind)
        assert len(members) == 3, (
            f"Expected 3 AttributeResolutionKind members, got {len(members)}"
        )
        expected_values = {"formula", "expose_alias", "literal"}
        actual_values = {m.value for m in members}
        assert actual_values == expected_values, (
            f"Enum values mismatch: missing={expected_values - actual_values}, "
            f"unexpected={actual_values - expected_values}"
        )

    def test_resolution_map_from_real_data(self, attr_expr_probe_snapshot):
        """Build _build_attribute_resolution_map() with real snapshot data.

        Verifies FORMULA attrs produce FORMULA kind, EXPOSE_PURE attrs produce
        EXPOSE_ALIAS kind. Remaining attrs (not in computed_attributes) would
        produce LITERAL kind but are not in the map (only computed attrs are mapped).
        """
        from sysml_codegen.core.output_registry import OutputRegistry
        from sysml_codegen.core.qualified_names import (
            get_channel_name,
            sysml_to_python_qualified_name,
        )
        from sysml_codegen.resolution.graph_builder import (
            AttributeResolutionKind,
            _build_attribute_resolution_map,
        )

        computed_attrs = attr_expr_probe_snapshot["computed_attributes"]
        design_attrs = attr_expr_probe_snapshot["design_attributes"]

        # Build calc_usage_names from snapshot
        calc_usage_names = {u.instance_name for u in attr_expr_probe_snapshot["calc_usages"]}

        # Build a minimal OutputRegistry for EXPOSE_PURE resolution
        registry = OutputRegistry()

        # Register FORMULA output channels (synthetic modules)
        for ca in computed_attrs:
            if (
                ca.classification == ComputedAttributeClassification.FORMULA
                and ca.compilability == Compilability.FULLY_COMPILABLE
            ):
                sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
                module_eqn = sysml_to_python_qualified_name(sysml_qn)
                channel = get_channel_name(module_eqn, ca.python_name)
                registry_register(registry,channel, [])

        # Register EXPOSE_PURE aliases: register the calc usage outputs first
        # so the alias targets exist
        for usage in attr_expr_probe_snapshot["calc_usages"]:
            usage_eqn = usage.qualified_name
            # Register all output attributes from the calc def
            calc_def_name = usage.calc_def_qualified_name
            for cd in attr_expr_probe_snapshot["calc_defs"]:
                if cd.qualified_name == calc_def_name:
                    for out_attr in cd.output_attributes:
                        channel = get_channel_name(usage_eqn, out_attr.name)
                        # Key_B format: instance.output
                        key_b = f"{usage.instance_name}.{out_attr.name}"
                        registry_register(registry,channel, [key_b])

        # Build the resolution map
        result = _build_attribute_resolution_map(
            computed_attrs=computed_attrs,
            design_attrs=design_attrs,
            output_registry=registry,
            calc_usage_names=calc_usage_names,
        )

        # Verify FORMULA attrs produce FORMULA kind
        probe_map = result.get("probe_design", {})
        for ca in computed_attrs:
            if (
                ca.classification == ComputedAttributeClassification.FORMULA
                and ca.compilability == Compilability.FULLY_COMPILABLE
            ):
                assert ca.python_name in probe_map, (
                    f"FORMULA {ca.python_name} not in resolution map"
                )
                assert probe_map[ca.python_name].kind == AttributeResolutionKind.FORMULA, (
                    f"FORMULA {ca.python_name} has kind={probe_map[ca.python_name].kind}, "
                    f"expected FORMULA"
                )

        # Verify EXPOSE_PURE attrs produce EXPOSE_ALIAS kind
        for ca in computed_attrs:
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
                assert ca.python_name in probe_map, (
                    f"EXPOSE_PURE {ca.python_name} not in resolution map"
                )
                assert probe_map[ca.python_name].kind == AttributeResolutionKind.EXPOSE_ALIAS, (
                    f"EXPOSE_PURE {ca.python_name} has kind={probe_map[ca.python_name].kind}, "
                    f"expected EXPOSE_ALIAS"
                )


# ---------------------------------------------------------------------------
# REQ-CA-07: Self-reference excluded from FORMULA compiled expressions
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CA-07")
class TestReqCa07SelfReferenceExcluded:
    """FORMULA expressions do not contain self-references."""

    def test_self_reference_excluded(self, attr_expr_probe_snapshot):
        """For every FORMULA, compiled_expression does not contain inputs.{self_python_name}."""
        for ca in attr_expr_probe_snapshot["computed_attributes"]:
            if ca.classification != ComputedAttributeClassification.FORMULA:
                continue
            assert ca.compiled_expression is not None
            self_ref = f"inputs.{ca.python_name}"
            assert self_ref not in ca.compiled_expression, (
                f"FORMULA {ca.python_name} contains self-reference '{self_ref}' in: "
                f"{ca.compiled_expression}"
            )

    def test_self_reference_chain_attrs(self, attr_expr_probe_snapshot):
        """Chain attrs (cost, marked_up_cost, cost_density) reference computed siblings but NOT themselves."""
        ca_map = {
            ca.python_name: ca
            for ca in attr_expr_probe_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.FORMULA
        }
        for attr_name, expected_refs in CHAIN_ATTRS.items():
            ca = ca_map[attr_name]
            assert ca.compiled_expression is not None

            # Self-reference absent
            self_ref = f"inputs.{attr_name}"
            assert self_ref not in ca.compiled_expression, (
                f"Chain attr {attr_name} contains self-reference in: {ca.compiled_expression}"
            )

            # Expected sibling references present
            for ref_name in expected_refs:
                expected_input = f"inputs.{ref_name}"
                assert expected_input in ca.compiled_expression, (
                    f"Chain attr {attr_name} missing expected reference '{expected_input}' in: "
                    f"{ca.compiled_expression}"
                )


# ---------------------------------------------------------------------------
# Additional conformance tests (not directly REQ-mapped)
# ---------------------------------------------------------------------------


class TestClassificationCounts:
    """Exact classification counts for attr_expr_probe snapshot."""

    def test_classification_counts_attr_expr_probe(self, attr_expr_probe_snapshot):
        """Exact counts: 14 FORMULA, 1 EXPOSE_COMPUTED, 3 EXPOSE_PURE in attr_expr_probe."""
        from collections import Counter

        counts = Counter(
            ca.classification for ca in attr_expr_probe_snapshot["computed_attributes"]
        )
        for cls, expected in ATTR_EXPR_PROBE_COUNTS.items():
            assert counts[cls] == expected, (
                f"{cls.value}: expected {expected}, got {counts[cls]}"
            )
        total = sum(ATTR_EXPR_PROBE_COUNTS.values())
        assert len(attr_expr_probe_snapshot["computed_attributes"]) == total, (
            f"Total computed_attributes: expected {total}, "
            f"got {len(attr_expr_probe_snapshot['computed_attributes'])}"
        )


class TestCrossModelCatfMfe:
    """Cross-model validation on catf_mfe_model."""

    def test_cross_model_catf_mfe(self, catf_mfe_snapshot):
        """catf_mfe computed_attributes all have valid classification; EXPOSE_PURE all on PartUsage."""
        valid = set(ComputedAttributeClassification)
        for ca in catf_mfe_snapshot["computed_attributes"]:
            assert ca.classification in valid, (
                f"catf_mfe {ca.python_name} has invalid classification {ca.classification}"
            )
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
                assert ca.is_on_part_definition is False, (
                    f"catf_mfe EXPOSE_PURE {ca.python_name} unexpectedly on PartDef"
                )


# ---------------------------------------------------------------------------
# C3: Inherited Attribute Classification (unresolvable_attr_probe fixture)
# ---------------------------------------------------------------------------
#
# FINDING (C3, 2026-02-17): The classifier misclassifies inherited attributes
# as EXPOSE_COMPUTED instead of FORMULA. SysIDE resolves inherited attribute
# QNs to the supertype's namespace (e.g., 'Base Component'::base_rate), not
# the subtype's ('Derived Component'::base_rate). The classifier's Step 2b
# check `qn.startswith(owning_part_qn + "::")` fails, and the ref falls
# through to Step 2c as a calc_ref. This pushes classification to
# EXPOSE_COMPUTED.
#
# UNRESOLVABLE was NOT triggered: all refs have non-empty QNs. The empty-QN
# fallback path (Step 2d) is never hit for valid SysML with inheritance.
# ---------------------------------------------------------------------------


# Expected classification results for unresolvable_attr_probe fixture.
# Documents the ACTUAL (misclassified) behavior for regression tracking.
# The "correct" column shows what the result SHOULD be once the classifier
# handles inheritance; the "actual" column shows current behavior.
INHERITED_ATTR_PATTERNS = {
    # (owning_part_name, attr_name): (actual_classification, correct_classification, description)
    ("Derived_Component", "inherited_product"): (
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        ComputedAttributeClassification.FORMULA,
        "L1: only inherited attrs — both refs resolve to supertype namespace",
    ),
    ("Derived_Component", "mixed_product"): (
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        ComputedAttributeClassification.FORMULA,
        "L2: inherited + local — base_rate resolves to supertype, local_multiplier to subtype",
    ),
    ("Design_Derived", "inherited_product"): (
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        ComputedAttributeClassification.FORMULA,
        "D1: only inherited attrs (design-side PartDef inheritance)",
    ),
    ("Design_Derived", "mixed_product"): (
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        ComputedAttributeClassification.FORMULA,
        "D2: inherited + local (design-side)",
    ),
    ("Design_Derived", "mixed_expose"): (
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        "D3: CalcUsage output + inherited attr — EXPOSE_COMPUTED is correct",
    ),
    ("Design_Derived", "inherited_sum"): (
        ComputedAttributeClassification.EXPOSE_COMPUTED,
        ComputedAttributeClassification.FORMULA,
        "D4: multi-term with inherited attrs (design-side)",
    ),
}


class TestInheritedAttrClassification:
    """C3: Inherited attribute classification with unresolvable_attr_probe fixture.

    Documents the classifier's behavior when PartDef-to-PartDef inheritance
    introduces attributes whose QNs resolve to the supertype's namespace.
    """

    def test_fixture_has_expected_count(self, unresolvable_attr_snapshot):
        """unresolvable_attr_probe produces exactly 6 computed attributes."""
        computed = unresolvable_attr_snapshot["computed_attributes"]
        assert len(computed) == 6, (
            f"Expected 6 computed_attributes, got {len(computed)}: "
            f"{[(ca.owning_part_name, ca.python_name) for ca in computed]}"
        )

    def test_all_on_part_definition(self, unresolvable_attr_snapshot):
        """All computed attributes are on PartDefinitions (not PartUsages)."""
        for ca in unresolvable_attr_snapshot["computed_attributes"]:
            assert ca.is_on_part_definition is True, (
                f"{ca.owning_part_name}.{ca.python_name}: expected is_on_part_definition=True"
            )

    def test_no_channel_aliases(self, unresolvable_attr_snapshot):
        """No EXPOSE_PURE patterns exist, so no channel aliases produced."""
        aliases = unresolvable_attr_snapshot["channel_aliases"]
        assert len(aliases) == 0, (
            f"Expected 0 channel_aliases, got {len(aliases)}"
        )

    def test_zero_unresolvable_classifications(self, unresolvable_attr_snapshot):
        """UNRESOLVABLE is NOT triggered by inheritance patterns.

        SysIDE always resolves inherited attribute QNs (to the supertype's
        namespace), so the empty-QN fallback path (Step 2d) is never hit.
        """
        unresolvable = [
            ca for ca in unresolvable_attr_snapshot["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.UNRESOLVABLE
        ]
        assert len(unresolvable) == 0, (
            f"Expected 0 UNRESOLVABLE, got {len(unresolvable)}: "
            f"{[ca.python_name for ca in unresolvable]}"
        )

    @pytest.mark.parametrize(
        "key,expected",
        list(INHERITED_ATTR_PATTERNS.items()),
        ids=[f"{k[0]}.{k[1]}" for k in INHERITED_ATTR_PATTERNS],
    )
    def test_inherited_attr_classification(
        self, unresolvable_attr_snapshot, key, expected
    ):
        """Each inherited-attr pattern produces the documented (mis)classification.

        This test locks down the ACTUAL behavior as a regression guard.
        When the classifier is fixed to handle inheritance, update the
        expected values in INHERITED_ATTR_PATTERNS.
        """
        owning_part, attr_name = key
        actual_cls, correct_cls, description = expected

        ca_match = [
            ca for ca in unresolvable_attr_snapshot["computed_attributes"]
            if ca.owning_part_name == owning_part and ca.python_name == attr_name
        ]
        assert len(ca_match) == 1, (
            f"Expected 1 match for {owning_part}.{attr_name}, got {len(ca_match)}"
        )
        ca = ca_match[0]

        # Assert actual (current) classification
        assert ca.classification == actual_cls, (
            f"{owning_part}.{attr_name}: expected {actual_cls.value}, "
            f"got {ca.classification.value} — {description}"
        )

    @pytest.mark.parametrize(
        "key,expected",
        [
            (k, v) for k, v in INHERITED_ATTR_PATTERNS.items()
            if v[0] != v[1]  # only misclassified patterns
        ],
        ids=[
            f"{k[0]}.{k[1]}" for k, v in INHERITED_ATTR_PATTERNS.items()
            if v[0] != v[1]
        ],
    )
    def test_misclassification_documented(
        self, unresolvable_attr_snapshot, key, expected
    ):
        """Document misclassification: 5 of 6 patterns should be FORMULA but are EXPOSE_COMPUTED.

        Root cause: SysIDE resolves inherited attribute QNs to supertype namespace.
        Classifier Step 2b (owning_part_qn prefix check) fails for inherited attrs.

        This test uses xfail to mark the known-wrong behavior. When the
        classifier is fixed to handle supertype QN resolution, these tests
        will start PASSING (xfail strict=False allows that).
        """
        owning_part, attr_name = key
        actual_cls, correct_cls, description = expected

        ca_match = [
            ca for ca in unresolvable_attr_snapshot["computed_attributes"]
            if ca.owning_part_name == owning_part and ca.python_name == attr_name
        ]
        ca = ca_match[0]

        # This SHOULD be correct_cls, but currently is actual_cls (misclassified)
        if ca.classification != correct_cls:
            pytest.xfail(
                f"KNOWN MISCLASSIFICATION: {owning_part}.{attr_name} is "
                f"{ca.classification.value}, should be {correct_cls.value}. "
                f"Cause: inherited attr QN resolves to supertype namespace. "
                f"Fix scope: C05 classifier or Phase 7 refactor."
            )

    def test_inherited_refs_have_supertype_qn(self, unresolvable_attr_snapshot):
        """Inherited attribute refs have QNs in the supertype's namespace, not the subtype's.

        This is the root cause of the misclassification. SysIDE resolves
        `base_rate` on 'Derived Component' to `'Base Component'::base_rate`,
        not `'Derived Component'::base_rate`.
        """
        for ca in unresolvable_attr_snapshot["computed_attributes"]:
            for ref in ca.references:
                if ref.name in ("base_rate", "base_factor"):
                    assert "'Base Component'" in ref.qualified_name, (
                        f"{ca.owning_part_name}.{ca.python_name}: inherited ref "
                        f"{ref.name} has QN={ref.qualified_name}, expected "
                        f"'Base Component' in QN (supertype namespace)"
                    )
                    assert ca.owning_part_qualified_name not in ref.qualified_name, (
                        f"{ca.owning_part_name}.{ca.python_name}: inherited ref "
                        f"{ref.name} has QN={ref.qualified_name} containing "
                        f"subtype namespace — unexpected (would mean no misclassification)"
                    )

    def test_no_compiled_expressions(self, unresolvable_attr_snapshot):
        """Misclassified attrs have no compiled expression (EXPOSE_COMPUTED skips compilation)."""
        for ca in unresolvable_attr_snapshot["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.EXPOSE_COMPUTED:
                assert ca.compiled_expression is None, (
                    f"{ca.owning_part_name}.{ca.python_name}: EXPOSE_COMPUTED should "
                    f"have compiled_expression=None, got {ca.compiled_expression}"
                )
                assert ca.compilability == Compilability.MANUAL_REQUIRED, (
                    f"{ca.owning_part_name}.{ca.python_name}: EXPOSE_COMPUTED should "
                    f"have compilability=MANUAL_REQUIRED"
                )
