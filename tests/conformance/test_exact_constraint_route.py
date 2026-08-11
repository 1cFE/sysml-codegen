"""One identified constraint extraction/profile decision reaches projection unchanged."""

from __future__ import annotations

from agentic_mbse.sysml import constraint_extraction
from agentic_mbse.sysml.constraint_extraction import IdentifiedConstraintFacts
from agentic_mbse.sysml.executable_profile import (
    Eligibility,
    IdentifiedProfileResult,
    evaluate_profile,
    preflight,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import DeclarationId, elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.resolution.models import ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def test_identified_fact_profile_and_projected_constraint_agree() -> None:
    assert "extract_" + "identified_constraint_facts" not in vars(constraint_extraction)
    profile_module = __import__(
        "agentic_mbse.sysml.executable_profile", fromlist=["evaluate_profile"]
    )
    assert "evaluate_" + "identified_profile" not in vars(profile_module)

    extractor = SysMLDataExtractor([FIXTURES_DIR / "constraint_shared_polarity"])
    assert extractor.load_models()
    identified = constraint_extraction.extract_constraint_facts(extractor.model)
    assert isinstance(identified, IdentifiedConstraintFacts)
    profile = evaluate_profile(identified)
    assert isinstance(profile, IdentifiedProfileResult)
    assert not profile.missing_usage_ids

    gate = preflight(profile)
    assert gate.ok
    assert len(gate.admitted) == 2
    assert not gate.blocking

    assert extractor.diagnostics is not None
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=True,
    )
    projected = project(graph)
    decisions = profile.by_usage_id
    live_usage_ids = {
        SysideAdapter.element_id(item)
        for item in SysideAdapter.elements_of_type(
            extractor.model, "ConstraintUsage", include_subtypes=True
        )
    }
    assert set(decisions) == live_usage_ids

    for usage_id, item in decisions.items():
        [node] = [
            candidate
            for candidate in graph.constraints.values()
            if candidate.declaration_id == DeclarationId(usage_id)
        ]
        assert item.effective_definition_id is not None
        assert node.effective_definition_id == DeclarationId(item.effective_definition_id)
        assert node.eligibility is item.decision.eligibility is Eligibility.ADMIT
        matching_modules = [
            module
            for module in projected.modules
            if module.module_kind is ModuleKind.CONSTRAINT
            and module.name.startswith(f"{node.display_path.lower()}__")
        ]
        assert len(matching_modules) == 1
