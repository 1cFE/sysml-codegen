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
import importlib
from pathlib import Path

import pytest

from sysml_codegen.extraction.extractor import SysMLDataExtractor


def test_shared_feature_unit_precedence_and_exact_text(tmp_path: Path) -> None:
    feature_metadata = importlib.import_module("sysml_codegen.extraction.feature_metadata")
    extract_feature_unit = feature_metadata.extract_feature_unit

    source = tmp_path / "model.sysml"
    source.write_text("attribute flow : Real; // [m³/s] - exact\n", encoding="utf-8")

    class Node:
        start_byte = 0

    class Target:
        name = "Real"
        qualified_name = "ScalarValues::Real"

    class Relationship:
        __class__ = type("FeatureTyping", (), {})

    class DocumentUrl:
        path = str(source)

    class Document:
        url = DocumentUrl()

    class Feature:
        cst_node = Node()
        document = Document()
        heritage = ()
        documentation = ()
        owner = None

    feature = Feature()
    assert extract_feature_unit(feature) == "m³/s"

    source.write_text(
        "attribute flow : Real; // From an external source\n", encoding="utf-8"
    )
    assert extract_feature_unit(feature) is None

    feature.cst_node = None
    feature.documentation = [type("Doc", (), {"body": "[kg/m³] - exact"})()]
    assert extract_feature_unit(feature) == "kg/m³"

    feature.documentation = []
    assert extract_feature_unit(feature) is None


def test_shared_feature_unit_type_precedes_authored_text() -> None:
    feature_metadata = importlib.import_module("sysml_codegen.extraction.feature_metadata")

    class FeatureTyping:
        pass

    class Target:
        name = "Length"
        qualified_name = "ISQ::Length"

    class Doc:
        body = "[cm]"

    class Feature:
        heritage = ((FeatureTyping(), Target()),)
        documentation = (Doc(),)
        cst_node = None
        owner = None

    original = feature_metadata.SysideAdapter.is_instance
    feature_metadata.SysideAdapter.is_instance = staticmethod(
        lambda item, type_name: type(item).__name__ == type_name
    )
    try:
        assert feature_metadata.extract_feature_unit(Feature()) == "m"
    finally:
        feature_metadata.SysideAdapter.is_instance = original

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
# REQ-EXT-03: Every redefinition classified as exactly one RedefinitionType
# ---------------------------------------------------------------------------
# REQ-EXT-04: Aggregation expressions decomposed into typed terms
# ---------------------------------------------------------------------------
# REQ-EXT-05: Template expansion produces virtual CalcUsageData
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
# REQ-EXT-07: exact-ID expression payload preserves raw SysIDE AST nodes
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EXT-07")
class TestReqExt07AstFields:
    """The live compiler payload is keyed only by declaration UUID."""

    def test_live_exact_identity_sidecar_fields_exist(self):
        """Exact calc/member UUID fields are the explicit live compiler payload."""
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

    # ``test_snapshot_ast_fields_nullified_in_raw_json`` stood here. It read a committed
    # ``extraction_snapshot.json`` and asserted the v5 serializer had nullified the SysIDE
    # AST fields that cannot survive a JSON round trip. Serializer and fixtures both retired
    # with the v5 family (retirement step 2), so there is no serialized form left to check.
    # The declaration side of the same rule — which fields are marked ``snapshot_exclude``
    # — is asserted by the sibling node above and is unaffected.


# ---------------------------------------------------------------------------
# REQ-EXT-02 (extended): EXPRESSION binding type coverage
# Closes fixture gap C1 from Phase 2 audit.
# ---------------------------------------------------------------------------
# REQ-EXT-08: Zero-output calc def fails fast at extraction (I3)
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


@pytest.mark.req("REQ-EXT-08")
class TestReqExt08ZeroOutputFailFast:
    """A calc def with zero output attributes raises at extraction, never
    reaching the Jinja module template."""

    def test_zero_output_calc_def_raises(self):
        extractor = _load_live_extractor("zero_output_calc")
        with pytest.raises(ValueError, match="zero output attributes"):
            extractor.extract_calculation_definitions()
