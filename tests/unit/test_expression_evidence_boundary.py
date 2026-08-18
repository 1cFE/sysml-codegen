"""Kept tests for Codegen's closed semantic-evidence boundary.

These tests exercise the representation and consumer backstops independently of the
public pre-graph refusal.  A green end-to-end indexed test cannot prove these seams: the
inventory could catch the index while a weakened constructor or consumer still accepts it.
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import pytest
from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.data_models import ResolvedTargetFact
from agentic_mbse.sysml.expression_ir import UnsupportedNode
from agentic_mbse.sysml.reference_use import (
    ExactReferenceUse,
    ExactSemanticPath,
    IndexedReferenceUse,
)

from sysml_codegen.elaboration import expression_evidence
from sysml_codegen.elaboration.expression_evidence import (
    ExpressionEvidenceInventory,
    ExpressionInventoryError,
    ExpressionSite,
    ExpressionSiteRole,
    require_exact_use,
)
from sysml_codegen.extraction import binding_source
from sysml_codegen.extraction.binding_source import (
    BoundFormal,
    ExactBindingSource,
    ExpressionBindingSource,
    IndexedBindingSource,
    LiteralBindingSource,
    exact_path_from_relationship,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license


def _fact(ordinal: int, name: str) -> ResolvedTargetFact:
    return ResolvedTargetFact(
        element_id=UUID(int=ordinal),
        owner_element_id=None,
        redefined_element_ids=(),
        qualified_name=f"Probe::{name}",
        element_kind="Feature",
        element_name=name,
    )


def _exact_use() -> ExactReferenceUse:
    root = _fact(1, "root")
    leaf = _fact(2, "leaf")
    return ExactReferenceUse(
        path=ExactSemanticPath(
            root=root,
            segments=(root, leaf),
            leaf=leaf,
            resolved_member_names=("leaf",),
        ),
        form="chain",
        authored_text="root.leaf",
        authored_segments=("root", "leaf"),
        authored_qualifier=None,
        plural=False,
        location=("root-0/model.sysml", 12),
    )


def _indexed_use() -> IndexedReferenceUse:
    return IndexedReferenceUse(
        reference="cells#(2).mass",
        location=("root-0/model.sysml", 15),
    )


def _formal() -> BoundFormal:
    return BoundFormal(
        element_id=UUID(int=10),
        qualified_name="Probe::calc::value_in",
        redefined_element_ids=(),
        redefined_qualified_names=(),
    )


def test_closed_binding_constructors_reject_the_other_reference_variant() -> None:
    """An authored index cannot be represented by relabelling its union variant."""
    with pytest.raises(TypeError, match="ExactReferenceUse"):
        ExactBindingSource(_formal(), _indexed_use())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="IndexedReferenceUse"):
        IndexedBindingSource(_formal(), _exact_use())  # type: ignore[arg-type]


def test_binding_variant_switch_is_exhaustive() -> None:
    """Every closed variant has one disposition and an unknown lookalike fails loudly."""
    classify = getattr(binding_source, "binding_source_kind", None)
    assert callable(classify), "the binding union has no exhaustive classifier"
    assert classify(ExactBindingSource(_formal(), _exact_use())) == "reference"
    assert classify(IndexedBindingSource(_formal(), _indexed_use())) == "indexed_source"
    assert classify(ExpressionBindingSource(_formal(), "a + b", None)) == "expression_source"
    assert classify(LiteralBindingSource(_formal(), 1.0)) == "authored_literal"
    with pytest.raises(TypeError, match="BindingSourceEvidence"):
        classify(SimpleNamespace(formal=_formal(), use=_exact_use()))


def test_inventory_missing_row_is_an_invariant_failure() -> None:
    site = ExpressionSite(UUID(int=20), ExpressionSiteRole.ALIAS)
    with pytest.raises(ExpressionInventoryError, match="absent from the evidence inventory"):
        ExpressionEvidenceInventory({}).require(site)


def test_inventory_duplicate_row_is_an_invariant_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    site = ExpressionSite(UUID(int=21), ExpressionSiteRole.COMPUTED_ATTRIBUTE)
    monkeypatch.setattr(
        expression_evidence,
        "_enumerate_sites",
        lambda _model: [(site, object()), (site, object())],
    )
    monkeypatch.setattr(expression_evidence, "_acquire", lambda _expression: ())
    with pytest.raises(ExpressionInventoryError, match="was enumerated twice"):
        expression_evidence.build_expression_evidence_inventory(object())


@pytest.mark.parametrize("role", list(ExpressionSiteRole))
def test_each_expression_consumer_backstop_refuses_an_inventory_bypassed_index(
    role: ExpressionSiteRole,
) -> None:
    """One bypass test per consumer role, independent of inventory acquisition."""
    site = ExpressionSite(UUID(int=30 + list(ExpressionSiteRole).index(role)), role)
    inventory = ExpressionEvidenceInventory({site: (_indexed_use(),)})
    with pytest.raises(SemanticEvidenceError) as caught:
        inventory.require_exact(site)
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
    assert caught.value.reference == "cells#(2).mass"


def test_binding_consumer_backstop_refuses_an_inventory_bypassed_index() -> None:
    require = getattr(binding_source, "require_exact_binding_use", None)
    assert callable(require), "the binding consumer has no closed-union backstop"
    with pytest.raises(SemanticEvidenceError) as caught:
        require(IndexedBindingSource(_formal(), _indexed_use()))
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
    assert caught.value.reference == "cells#(2).mass"


def test_exact_resolver_rejects_every_non_exact_runtime_shape() -> None:
    exact = _exact_use()
    assert require_exact_use(exact) is exact

    with pytest.raises(SemanticEvidenceError) as indexed:
        require_exact_use(_indexed_use())
    assert indexed.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED

    rejected = (
        SimpleNamespace(target=_fact(3, "legacy")),
        UnsupportedNode("LegacyIR", "not semantic authority", None),
        SimpleNamespace(path=exact.path, authored_text=exact.authored_text),
    )
    for value in rejected:
        with pytest.raises(ExpressionInventoryError, match="requires an ExactReferenceUse"):
            require_exact_use(value)


def test_value_site_policy_delegates_the_complete_annotation_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codegen decides value-site policy; Agentic alone reads metatype/operator/arity."""
    expression = object()
    value = object()
    calls: list[object] = []

    def shared_primitive(candidate: object) -> object:
        calls.append(candidate)
        return value

    monkeypatch.setattr(
        expression_evidence,
        "agentic_unit_annotation_value",
        shared_primitive,
        raising=False,
    )
    assert expression_evidence.unit_annotated_value(expression) is value
    assert calls == [expression]


def test_value_site_policy_contains_no_second_structural_unit_walk() -> None:
    source = expression_evidence.unit_annotated_value.__code__.co_names
    forbidden = {"SysideAdapter", "materialize_operands", "operands", "operator"}
    assert forbidden.isdisjoint(source), f"Codegen still interprets unit structure: {source}"


def _deep_segments() -> tuple[object, object, object]:
    return object(), object(), object()


def _patch_deep_path_facts(
    monkeypatch: pytest.MonkeyPatch,
    segments: tuple[object, ...],
    facts: dict[object, ResolvedTargetFact | None],
    *,
    indexed: object | None = None,
) -> None:
    monkeypatch.setattr(
        binding_source.SysideAdapter,
        "is_instance",
        lambda value, type_name: (
            (type_name == "IndexExpression" and value is indexed)
            or (type_name == "Feature" and value in segments and value is not indexed)
        ),
    )
    monkeypatch.setattr(binding_source, "resolved_target_fact", facts.get)


def test_deep_path_missing_middle_segment_refuses_instead_of_shortening(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, middle, leaf = _deep_segments()
    relationship = SimpleNamespace(chaining_features=(root, middle, leaf))
    _patch_deep_path_facts(
        monkeypatch,
        (root, middle, leaf),
        {root: _fact(40, "root"), middle: None, leaf: _fact(42, "leaf")},
    )

    with pytest.raises(SemanticEvidenceError) as caught:
        exact_path_from_relationship(relationship)
    assert caught.value.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
    assert "segment 1" in caught.value.detail
    assert "no exact target fact" in caught.value.detail


def test_deep_override_mapped_index_refuses_at_the_path_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, indexed, leaf = _deep_segments()
    relationship = SimpleNamespace(chaining_features=(root, indexed, leaf))
    _patch_deep_path_facts(
        monkeypatch,
        (root, indexed, leaf),
        {root: _fact(50, "root"), leaf: _fact(52, "leaf")},
        indexed=indexed,
    )

    with pytest.raises(SemanticEvidenceError) as caught:
        exact_path_from_relationship(relationship)
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
    assert "segment 1" in caught.value.detail


def test_complete_deep_path_retains_every_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    root, middle, leaf = _deep_segments()
    relationship = SimpleNamespace(chaining_features=(root, middle, leaf))
    root_fact = _fact(60, "root")
    middle_fact = _fact(61, "middle")
    leaf_fact = _fact(62, "leaf")
    _patch_deep_path_facts(
        monkeypatch,
        (root, middle, leaf),
        {root: root_fact, middle: middle_fact, leaf: leaf_fact},
    )

    path = exact_path_from_relationship(relationship)
    assert path.root is root_fact
    assert path.segments == (root_fact, middle_fact, leaf_fact)
    assert path.leaf is leaf_fact


@requires_license
def test_real_deep_override_relationships_contain_only_features() -> None:
    """The real parser route structurally excludes IndexExpression path segments."""
    extractor = SysMLDataExtractor([FIXTURES_DIR / "source_identity_mixed_consumers"])
    assert extractor.load_models()

    deep_paths: list[tuple[object, tuple[object, ...]]] = []
    for feature in binding_source.SysideAdapter.elements_of_type(
        extractor.model, "Feature", include_subtypes=True
    ):
        if getattr(feature, "qualified_name", None) is not None:
            continue
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = getattr(relationship, "redefined_feature", None)
            segments = tuple(getattr(redefined, "chaining_features", ()) or ())
            if segments:
                deep_paths.append((redefined, segments))

    assert deep_paths, "fixture contains no parsed deep override relationship"
    for redefined, segments in deep_paths:
        assert all(
            binding_source.SysideAdapter.is_instance(segment, "Feature") for segment in segments
        )
        assert not any(
            binding_source.SysideAdapter.is_instance(segment, "IndexExpression")
            for segment in segments
        )
        assert len(exact_path_from_relationship(redefined).segments) == len(segments)


def test_enumeration_literal_requires_an_exact_referent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from sysml_codegen.elaboration.elaborate import _ExactElaborator

    expression = SimpleNamespace(referent=None)
    monkeypatch.setattr(
        binding_source.SysideAdapter,
        "is_instance",
        lambda value, type_name: type_name == "FeatureReferenceExpression" and value is expression,
    )
    assert _ExactElaborator._enumeration_literal(expression) is None
