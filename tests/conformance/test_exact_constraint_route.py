"""One constraint decision, made once by UUID, reaching projection unchanged.

The exact route's constraint authority is a chain across both repositories:
agentic-mbse extracts identified facts, decides them by usage UUID, and partitions the
decisions at the gate; sysml-codegen elaborates and projects them. This module asserts the
chain agrees end to end on a live model, and that the sysml-codegen half sources none of
that authority from the legacy lowering module it is meant to replace.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_extraction import (
    IdentifiedConstraintFacts,
    extract_identified_constraint_facts,
)
from agentic_mbse.sysml.executable_profile import (
    Eligibility,
    IdentifiedProfileResult,
    evaluate_identified_profile,
    preflight_identified,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import DeclarationId, elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.resolution.models import ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

LEGACY_CONSTRAINT_MODULE = "sysml_codegen.analysis.constraint_lowering"
EXACT_ROUTE_PACKAGE = "sysml_codegen.elaboration"
EXACT_ROUTE_FILES = (
    Path(__file__).parents[2] / "src/sysml_codegen/elaboration/elaborate.py",
    Path(__file__).parents[2] / "src/sysml_codegen/elaboration/project.py",
)


def legacy_constraint_imports(source: str, package: str) -> set[str]:
    """Every way `source` names the legacy lowering module, as absolute dotted strings.

    Resolves relative imports against `package` and expands `from <parent> import <name>`,
    because both spell the same dependency as a plain string comparison against
    `ImportFrom.module` would miss. `from sysml_codegen.analysis import constraint_lowering`
    is the ordinary way to import a module object and is used further down this file.
    """
    found: set[str] = set()

    def record(dotted: str) -> None:
        if dotted == LEGACY_CONSTRAINT_MODULE or dotted.startswith(
            f"{LEGACY_CONSTRAINT_MODULE}."
        ):
            found.add(dotted)

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                record(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")
                trimmed = base[: len(base) - node.level + 1]
                prefix = ".".join(trimmed + ([node.module] if node.module else []))
            else:
                prefix = node.module or ""
            record(prefix)
            for alias in node.names:
                record(f"{prefix}.{alias.name}" if prefix else alias.name)
    return found


def test_identified_facts_gate_and_projected_constraints_agree_by_usage_id() -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "constraint_shared_polarity"])
    assert extractor.load_models()
    assert extractor.diagnostics is not None

    identified = extract_identified_constraint_facts(extractor.model)
    assert isinstance(identified, IdentifiedConstraintFacts)
    profile = evaluate_identified_profile(identified)
    assert isinstance(profile, IdentifiedProfileResult)
    assert not profile.missing_usage_ids

    gate = preflight_identified(profile)
    assert gate.ok
    assert not gate.blocking
    assert len(gate.admitted) == 2

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


def test_the_exact_route_takes_no_constraint_authority_from_legacy_lowering() -> None:
    """Elaboration and projection import nothing from the legacy lowering module.

    Constraint-ID minting and modeled-default resolution used to come from there, which
    made the legacy module an authority the exact route could not be separated from. Both
    now live in modules the two routes share.
    """
    for path in EXACT_ROUTE_FILES:
        found = legacy_constraint_imports(path.read_text(), EXACT_ROUTE_PACKAGE)
        assert found == set(), f"{path.name}: {sorted(found)}"


@pytest.mark.parametrize(
    "statement",
    [
        "from sysml_codegen.analysis.constraint_lowering import mint_constraint_id",
        "from sysml_codegen.analysis import constraint_lowering",
        "from ..analysis.constraint_lowering import mint_constraint_id",
        "from ..analysis import constraint_lowering",
        "import sysml_codegen.analysis.constraint_lowering",
        "import sysml_codegen.analysis.constraint_lowering as legacy",
    ],
)
def test_the_legacy_import_check_catches_every_spelling(statement: str) -> None:
    """The pin above is only worth its claim if it cannot be walked around.

    Measured: a plain comparison against `ImportFrom.module` catches cases 1, 5 and 6 and
    misses 2, 3 and 4 — including case 2, the idiomatic way to reach a module object.
    """
    assert legacy_constraint_imports(statement, EXACT_ROUTE_PACKAGE)


@pytest.mark.parametrize(
    "statement",
    [
        "from sysml_codegen.analysis.source_referent import map_live_source_referent",
        "from sysml_codegen.analysis import source_referent",
        "from ..analysis import parameter_groups",
        "import sysml_codegen.core.identifier_types",
    ],
)
def test_the_legacy_import_check_does_not_flag_other_analysis_modules(
    statement: str,
) -> None:
    assert legacy_constraint_imports(statement, EXACT_ROUTE_PACKAGE) == set()


def test_the_shared_constraint_identity_and_default_helpers_stay_callable_on_both_routes() -> None:
    """The legacy module keeps serving both names, so nothing is retired ahead of Phase 4."""
    from sysml_codegen.analysis import constraint_lowering
    from sysml_codegen.core.identifier_types import mint_constraint_id
    from sysml_codegen.extraction.modeled_defaults import (
        ModeledDefault,
        resolve_modeled_default,
    )

    assert constraint_lowering.mint_constraint_id is mint_constraint_id
    assert constraint_lowering.resolve_modeled_default is resolve_modeled_default
    assert constraint_lowering.ModeledDefault is ModeledDefault
    assert mint_constraint_id(
        instance_path="Design__c__cell", source_local="nonneg", tuple_=("a", 1)
    ) == mint_constraint_id(
        instance_path="Design__c__cell", source_local="nonneg", tuple_=("a", 1)
    )
    assert resolve_modeled_default(None) == ModeledDefault()
