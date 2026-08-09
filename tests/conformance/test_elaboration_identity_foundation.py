"""Kept SysIDE identity-foundation kill probes for the exact-ID elaborator.

These tests deliberately inspect the live parser surface before codegen wraps it.
They pin the upstream boundary that Phase 2 is allowed to depend on: QN-bearing
declarations and resolved endpoints are reload-stable UUIDv5 values, while
null-QN declarations and relationship objects are not stable identity.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.syside_adapter import get_syside

from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

syside = get_syside()


def _load(files: list[Path]) -> Any:
    model, diagnostics = syside.try_load_model([str(path) for path in files])
    errors = [
        diagnostic for diagnostic in diagnostics.all if str(diagnostic.severity).endswith("Error")
    ]
    assert not errors, errors
    return model


def _fixture_files(name: str) -> list[Path]:
    return sorted((FIXTURES_DIR / name).glob("*.sysml"))


def _all_elements(model: Any) -> list[Any]:
    return list(model.elements(syside.Element, include_subtypes=True))


def _named_declaration_ids(model: Any) -> dict[str, UUID]:
    result: dict[str, UUID] = {}
    for element in _all_elements(model):
        qualified_name = getattr(element, "qualified_name", None)
        if qualified_name is None:
            continue
        element_id = UUID(str(element.element_id))
        assert element_id.version == 5
        result[str(qualified_name)] = element_id
    return result


def _redefinition_facts(
    model: Any,
) -> dict[tuple[str, str, bool], tuple[UUID, UUID, UUID]]:
    facts: dict[tuple[str, str, bool], tuple[UUID, UUID, UUID]] = {}
    for feature in model.elements(syside.Feature, include_subtypes=True):
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = relationship.redefined_feature
            redefining = relationship.redefining_feature
            assert redefined is not None
            assert redefining is not None
            key = (
                str(redefining.qualified_name),
                str(redefined.qualified_name),
                bool(relationship.is_implied),
            )
            facts[key] = (
                UUID(str(redefining.element_id)),
                UUID(str(redefined.element_id)),
                UUID(str(relationship.element_id)),
            )
    return facts


def test_syside_identity_boundary_is_repeatable(tmp_path: Path) -> None:
    source_files = _fixture_files("spec_chain_twolevel")
    first = _load(source_files)
    second = _load(list(reversed(source_files)))

    relocated = tmp_path / "relocated" / "spec_chain_twolevel"
    shutil.copytree(FIXTURES_DIR / "spec_chain_twolevel", relocated)
    design_file = relocated / "design.sysml"
    design_file.write_text(
        "// harmless source offset\n"
        + design_file.read_text()
        + "\npackage IdentityFoundationNoise { attribute unrelated; }\n"
    )
    third = _load(list(reversed(sorted(relocated.glob("*.sysml")))))

    first_ids = _named_declaration_ids(first)
    assert first_ids == _named_declaration_ids(second)
    third_ids = _named_declaration_ids(third)
    assert {name: third_ids[name] for name in first_ids} == first_ids


def test_resolved_referents_are_the_exact_declaration_ids() -> None:
    model = _load(_fixture_files("spec_chain_twolevel"))
    direct_ids = _named_declaration_ids(model)
    checked = 0
    for expression in model.elements(syside.FeatureReferenceExpression, include_subtypes=True):
        referent = getattr(expression, "referent", None)
        qualified_name = getattr(referent, "qualified_name", None)
        if qualified_name is None:
            continue
        assert UUID(str(referent.element_id)) == direct_ids[str(qualified_name)]
        checked += 1
    assert checked >= 5


def test_redefinition_endpoints_are_stable_but_relationship_ids_are_not() -> None:
    files = _fixture_files("spec_chain_twolevel")
    first = _redefinition_facts(_load(files))
    second = _redefinition_facts(_load(list(reversed(files))))

    assert first.keys() == second.keys()
    assert any(key[2] for key in first), "implied redefinitions were not exposed"
    assert any(not key[2] for key in first), "authored redefinitions were not exposed"
    for key in first:
        first_redefining, first_redefined, first_relationship = first[key]
        second_redefining, second_redefined, second_relationship = second[key]
        assert (first_redefining, first_redefined) == (
            second_redefining,
            second_redefined,
        )
        assert first_redefining.version == 5
        assert first_redefined.version == 5
        assert first_relationship.version == 4
        assert second_relationship.version == 4
        assert first_relationship != second_relationship


def test_null_qn_executable_and_containment_ids_are_not_reload_stable() -> None:
    files = _fixture_files("elab_identity_collision_probe")

    def unstable_ids(model: Any) -> dict[tuple[str, str], UUID]:
        result: dict[tuple[str, str], UUID] = {}
        for element in _all_elements(model):
            if getattr(element, "qualified_name", None) is not None:
                continue
            if not (
                element.isinstance(syside.PartUsage) or element.isinstance(syside.AttributeUsage)
            ):
                continue
            key = (type(element).__name__, str(getattr(element, "name", None)))
            result[key] = UUID(str(element.element_id))
        return result

    first = unstable_ids(_load(files))
    second = unstable_ids(_load(files))
    assert ("PartUsage", "None") in first
    assert ("AttributeUsage", "repeated") in first
    assert first.keys() == second.keys()
    for key in first:
        assert first[key].version == 4
        assert second[key].version == 4
        assert first[key] != second[key]
