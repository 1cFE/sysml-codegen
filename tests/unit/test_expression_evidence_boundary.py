"""Kept tests for Codegen's closed semantic-evidence boundary.

These tests exercise the representation and consumer backstops independently of the
public pre-graph refusal.  A green end-to-end indexed test cannot prove these seams: the
inventory could catch the index while a weakened constructor or consumer still accepts it.
"""

from __future__ import annotations

from dataclasses import replace
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
from sysml_codegen.elaboration.elaborate import (
    ElaborationInvariantError,
    ReadinessCode,
    _ExactElaborator,
)
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
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr


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


def test_closed_bindings_preserve_source_spelling_and_formal_identity() -> None:
    """The closed value carries both identities; Codegen never reconstructs either."""
    exact = _exact_use()
    formal = BoundFormal(
        element_id=exact.path.leaf.element_id,
        qualified_name="Probe::calc::value_in",
        redefined_element_ids=(UUID(int=11),),
        redefined_qualified_names=("Probe::Consumer::value_in",),
    )
    qualified = replace(
        exact,
        form="qualified",
        authored_text="Probe::root::leaf",
        authored_segments=("Probe", "root", "leaf"),
        authored_qualifier="Probe::root",
    )
    source = ExactBindingSource(formal, qualified)

    assert source.formal is formal
    assert source.formal.redefined_element_ids == (UUID(int=11),)
    assert source.use is qualified
    assert source.written_text == "Probe::root::leaf"
    assert source.is_self_binding

    literal = LiteralBindingSource(formal, 3.0)
    expression = ExpressionBindingSource(formal, "a + b", None)
    assert not hasattr(literal, "use")
    assert not hasattr(expression, "use")


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
    monkeypatch.setattr(expression_evidence, "_acquire", lambda _expression, **_kwargs: ())
    with pytest.raises(ExpressionInventoryError, match="was enumerated twice"):
        expression_evidence.build_expression_evidence_inventory(object())


def test_unit_annotated_plain_reference_is_an_alias_site(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Role assignment sees the value inside a unit wrapper, exactly as consumers do."""
    wrapper = object()
    reference = object()
    feature = SimpleNamespace(owning_type=None)
    monkeypatch.setattr(expression_evidence, "unit_annotated_value", lambda value: reference)
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "is_instance",
        lambda value, type_name: value is reference and type_name == "FeatureReferenceExpression",
    )

    assert expression_evidence._role_for_owner(feature, wrapper) is ExpressionSiteRole.ALIAS


def test_inventory_returns_the_authoritative_site_for_a_declaration() -> None:
    """A consumer retrieves its assigned role instead of reconstructing the predicate."""
    site = ExpressionSite(UUID(int=30), ExpressionSiteRole.ALIAS)
    inventory = ExpressionEvidenceInventory({site: (_exact_use(),)})

    assert inventory.site_for(site.declaration_id) is site


def test_inventory_rejects_two_roles_for_one_declaration() -> None:
    declaration = UUID(int=31)
    alias = ExpressionSite(declaration, ExpressionSiteRole.ALIAS)
    computed = ExpressionSite(declaration, ExpressionSiteRole.COMPUTED_ATTRIBUTE)

    with pytest.raises(ExpressionInventoryError, match="has multiple assigned roles"):
        ExpressionEvidenceInventory({alias: (), computed: ()})


def test_binding_consumer_backstop_refuses_an_inventory_bypassed_index() -> None:
    require = getattr(binding_source, "require_exact_binding_use", None)
    assert callable(require), "the binding consumer has no closed-union backstop"
    with pytest.raises(SemanticEvidenceError) as caught:
        require(IndexedBindingSource(_formal(), _indexed_use()))
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
    assert caught.value.reference == "cells#(2).mass"


def test_require_exact_binding_use_switch_is_exhaustive() -> None:
    exact_use = _exact_use()
    assert binding_source.require_exact_binding_use(
        ExactBindingSource(_formal(), exact_use)
    ) is exact_use

    with pytest.raises(SemanticEvidenceError) as caught:
        binding_source.require_exact_binding_use(
            IndexedBindingSource(_formal(), _indexed_use())
        )
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED

    for evidence in (
        ExpressionBindingSource(_formal(), "a + b", None),
        LiteralBindingSource(_formal(), 1.0),
    ):
        with pytest.raises(TypeError, match="not an exact binding source"):
            binding_source.require_exact_binding_use(evidence)

    with pytest.raises(TypeError, match="BindingSourceEvidence"):
        binding_source.require_exact_binding_use(object())


def _consumer_with_inventory(
    site: ExpressionSite,
    use: object,
) -> _ExactElaborator:
    consumer = object.__new__(_ExactElaborator)
    consumer._inventory = ExpressionEvidenceInventory({site: (use,)})
    return consumer


def test_calc_dependency_adapter_refuses_an_inventory_bypassed_index() -> None:
    site = ExpressionSite(UUID(int=32), ExpressionSiteRole.CALC_DEFINITION_DEPENDENCY)
    consumer = _consumer_with_inventory(site, _indexed_use())

    with pytest.raises(SemanticEvidenceError) as caught:
        consumer._calc_dependencies()

    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED


def test_alias_adapter_refuses_an_inventory_bypassed_index() -> None:
    site = ExpressionSite(UUID(int=33), ExpressionSiteRole.ALIAS)
    consumer = _consumer_with_inventory(site, _indexed_use())
    consumer._pending_aliases = [SimpleNamespace(site=site, node=object(), location=None)]

    with pytest.raises(SemanticEvidenceError) as caught:
        consumer._resolve_aliases()

    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED


@pytest.mark.parametrize(
    "role",
    [ExpressionSiteRole.COMPUTED_ATTRIBUTE, ExpressionSiteRole.CONSTRAINT_PREDICATE],
)
def test_expression_adapter_refuses_an_inventory_bypassed_index(
    role: ExpressionSiteRole,
) -> None:
    site = ExpressionSite(UUID(int=34 + list(ExpressionSiteRole).index(role)), role)
    consumer = _consumer_with_inventory(site, _indexed_use())
    consumer._pending_expressions = [
        SimpleNamespace(site=site, consumer=object(), location=None)
    ]

    with pytest.raises(SemanticEvidenceError) as caught:
        consumer._resolve_computed_expressions()

    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED


def test_binding_wiring_adapter_refuses_an_inventory_bypassed_index() -> None:
    consumer = object.__new__(_ExactElaborator)
    consumer._pending_bindings = [
        SimpleNamespace(
            evidence=IndexedBindingSource(_formal(), _indexed_use()),
            consumer=object(),
            port=object(),
            location=None,
        )
    ]

    with pytest.raises(SemanticEvidenceError) as caught:
        consumer._resolve_bindings()

    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED


def test_elaborator_binding_classifier_switch_is_exhaustive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The adapter itself owns one explicit arm for every closed binding variant."""
    import sysml_codegen.elaboration.elaborate as elaborate_module

    member = object()
    declaration = UUID(int=39)
    site = ExpressionSite(declaration, ExpressionSiteRole.BINDING)
    exact = _exact_use()
    indexed = _indexed_use()
    literal_expression = object()
    general_expression = object()

    monkeypatch.setattr(elaborate_module, "bound_formal", lambda _member: _formal())
    monkeypatch.setattr(
        elaborate_module,
        "declaration_id_for",
        lambda _member: SimpleNamespace(value=declaration),
    )
    monkeypatch.setattr(
        elaborate_module,
        "is_literal_node",
        lambda expression: expression is literal_expression,
    )
    monkeypatch.setattr(elaborate_module, "extract_literal_value", lambda _expression: 7.0)
    monkeypatch.setattr(
        elaborate_module.binding_evidence,
        "written_reference_text",
        lambda _expression: "a + b",
    )
    monkeypatch.setattr(
        elaborate_module.SysideAdapter,
        "get_source_location",
        lambda _expression: ("model.sysml", 4),
    )

    literal_consumer = _consumer_with_inventory(site, exact)
    literal_consumer._is_reference_expression = lambda _expression: False
    literal = literal_consumer._binding_evidence(member, literal_expression)
    assert isinstance(literal, LiteralBindingSource)

    expression_consumer = _consumer_with_inventory(site, exact)
    expression_consumer._is_reference_expression = lambda _expression: False
    expression = expression_consumer._binding_evidence(member, general_expression)
    assert isinstance(expression, ExpressionBindingSource)

    exact_consumer = _consumer_with_inventory(site, exact)
    exact_consumer._is_reference_expression = lambda _expression: True
    assert isinstance(exact_consumer._binding_evidence(member, object()), ExactBindingSource)

    indexed_consumer = _consumer_with_inventory(site, indexed)
    indexed_consumer._is_reference_expression = lambda _expression: True
    assert isinstance(
        indexed_consumer._binding_evidence(member, object()), IndexedBindingSource
    )

    unknown_consumer = _consumer_with_inventory(site, object())
    unknown_consumer._is_reference_expression = lambda _expression: True
    with pytest.raises(ExpressionInventoryError, match="unknown reference-use variant"):
        unknown_consumer._binding_evidence(member, object())


def test_elaborator_readiness_switch_names_each_binding_variant() -> None:
    exact = ExactBindingSource(_formal(), _exact_use())
    indexed = IndexedBindingSource(_formal(), _indexed_use())
    expression = ExpressionBindingSource(_formal(), "a + b", None)
    literal = LiteralBindingSource(_formal(), 1.0)

    assert _ExactElaborator._unsupported_code(exact) is None
    assert (
        _ExactElaborator._unsupported_code(indexed)
        is ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED
    )
    assert (
        _ExactElaborator._unsupported_code(expression)
        is ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED
    )
    assert _ExactElaborator._unsupported_code(literal) is None


def test_binding_wiring_switch_refuses_expression_and_unknown_variants() -> None:
    consumer = object.__new__(_ExactElaborator)
    consumer._pending_bindings = [
        SimpleNamespace(
            evidence=ExpressionBindingSource(_formal(), "a + b", None),
            consumer=object(),
            port=object(),
            location=None,
        )
    ]
    with pytest.raises(ElaborationInvariantError, match="readiness screening"):
        consumer._resolve_bindings()

    consumer._pending_bindings = [
        SimpleNamespace(
            evidence=object(),
            consumer=object(),
            port=object(),
            location=None,
        )
    ]
    with pytest.raises(TypeError, match="BindingSourceEvidence"):
        consumer._resolve_bindings()


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


def test_expression_keyed_evidence_failure_gains_authored_site_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expression = object()
    original = SemanticEvidenceError(
        SemanticEvidenceCode.OPERAND_ITERATION_FAILED,
        operation="inspect_reference_uses",
        detail="operand stream failed",
        location=("model.sysml", 8),
        reference=None,
    )
    monkeypatch.setattr(
        expression_evidence,
        "inspect_reference_uses",
        lambda _expression: (_ for _ in ()).throw(original),
    )
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "authored_text",
        lambda _expression: "base_len [m]",
    )
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "get_source_location",
        lambda _expression: ("model.sysml", 8),
    )

    with pytest.raises(SemanticEvidenceError) as caught:
        expression_evidence._acquire(expression)

    assert caught.value.reference == "base_len [m]"
    assert caught.value.location == ("model.sysml", 8)
    assert caught.value.cause is original
    assert caught.value.__cause__ is original


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


def test_deep_path_non_feature_segment_refuses_instead_of_shortening(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, alien, leaf = _deep_segments()
    relationship = SimpleNamespace(chaining_features=(root, alien, leaf))
    monkeypatch.setattr(
        binding_source.SysideAdapter,
        "is_instance",
        lambda value, type_name: type_name == "Feature" and value in (root, leaf),
    )
    monkeypatch.setattr(
        binding_source,
        "resolved_target_fact",
        {root: _fact(55, "root"), leaf: _fact(57, "leaf")}.get,
    )

    with pytest.raises(SemanticEvidenceError) as caught:
        exact_path_from_relationship(relationship)

    assert caught.value.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
    assert "segment 1" in caught.value.detail
    assert "not a Feature" in caught.value.detail


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


def _live_feature(model: object, qualified_name: str) -> object:
    matches = [
        feature
        for feature in binding_source.SysideAdapter.elements_of_type(
            model, "Feature", include_subtypes=True
        )
        if str(getattr(feature, "qualified_name", None)) == qualified_name
    ]
    assert len(matches) == 1, (qualified_name, matches)
    return matches[0]


@requires_license
def test_chain_evidence_names_the_redefining_usage_feature() -> None:
    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    member = _live_feature(
        extractor.model,
        "source_identity_mixed_consumers::Station::chain_calc::value_in",
    )
    inventory = expression_evidence.build_expression_evidence_inventory(extractor.model)
    site = inventory.site_for(binding_source.SysideAdapter.element_id(member))
    [use] = inventory.require_exact(site)

    assert use.path.leaf.qualified_name == (
        "source_identity_mixed_consumers::Station::rig::gain_setting"
    )
    assert use.path.leaf.element_kind == "ReferenceUsage"
    # The definition target need not be a chain segment, so prove its identity from
    # the live model as well as from the frozen redefinition ID.
    definition = _live_feature(
        extractor.model,
        "source_identity_mixed_consumers::Rig::gain_setting",
    )
    assert use.path.leaf.redefined_element_ids == (
        binding_source.SysideAdapter.element_id(definition),
    )


@requires_license
def test_frozen_usage_owner_matches_the_exact_live_part_usage() -> None:
    fixture = FIXTURES_DIR / "usage_owned_reference_consumers"
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    member = _live_feature(
        extractor.model,
        "UsageOwnedReferenceConsumers::Plant::comp_b::area_calc::length_in",
    )
    inventory = expression_evidence.build_expression_evidence_inventory(extractor.model)
    [use] = inventory.require_exact(
        inventory.site_for(binding_source.SysideAdapter.element_id(member))
    )
    live_leaf = _live_feature(extractor.model, str(use.path.leaf.qualified_name))
    live_owner = getattr(live_leaf, "owning_type")

    assert use.path.leaf.owner_element_id == binding_source.SysideAdapter.element_id(live_owner)
    assert binding_source.SysideAdapter.is_instance(live_owner, "PartUsage")


@requires_license
def test_bound_formal_keeps_its_exact_declaration_and_redefinition_identity() -> None:
    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    member = _live_feature(
        extractor.model,
        "source_identity_mixed_consumers::'Stamp Plant'::stamp_calc::value_in",
    )

    formal = binding_source.bound_formal(member)

    assert formal.element_id == binding_source.SysideAdapter.element_id(member)
    assert formal.qualified_name == (
        "source_identity_mixed_consumers::'Stamp Plant'::stamp_calc::value_in"
    )
    assert formal.redefined_qualified_names == (
        "source_identity_mixed_consumers::'Reading Consumer'::value_in",
    )


@requires_license
def test_occurrence_override_node_keeps_the_exact_writer_identity() -> None:
    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    writer = _live_feature(
        extractor.model,
        "source_identity_mixed_consumers::Station::rig::gain_setting",
    )
    graph = elaborate_model_paths([fixture], strict=True)
    node = attr(graph, "source_identity_mixed_consumers__station__rig__gain_setting")

    assert node.value == 42.0
    assert node.declaration_id.value == binding_source.SysideAdapter.element_id(writer)


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


def test_closed_site_enumerator_assigns_every_role_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The site set and its contextual role partition are direct kept contracts."""
    def expression(kind: str) -> object:
        return SimpleNamespace(kind=kind)

    calc_member = SimpleNamespace(
        element_id=UUID(int=71),
        qualified_name="Probe::Calc::out",
        owning_type=SimpleNamespace(kind="CalculationDefinition"),
        feature_value_expression=expression("OperatorExpression"),
    )
    binding_member = SimpleNamespace(
        element_id=UUID(int=72),
        qualified_name="Probe::calc::input",
        owning_type=SimpleNamespace(kind="CalculationUsage"),
        feature_value_expression=expression("FeatureReferenceExpression"),
    )
    alias_member = SimpleNamespace(
        element_id=UUID(int=73),
        qualified_name="Probe::Host::alias",
        owning_type=SimpleNamespace(kind="PartDefinition"),
        feature_value_expression=expression("FeatureChainExpression"),
    )
    computed_member = SimpleNamespace(
        element_id=UUID(int=74),
        qualified_name="Probe::Host::computed",
        owning_type=SimpleNamespace(kind="PartDefinition"),
        feature_value_expression=expression("OperatorExpression"),
    )
    constraint_definition = SimpleNamespace(
        element_id=UUID(int=75),
        result_expression=expression("OperatorExpression"),
    )
    constraint_usage = SimpleNamespace(
        element_id=UUID(int=76),
        result_expression=expression("OperatorExpression"),
    )
    by_type = {
        "Feature": [calc_member, binding_member, alias_member, computed_member],
        "ConstraintDefinition": [constraint_definition],
        "ConstraintUsage": [constraint_usage],
    }
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "elements_of_type",
        lambda _model, type_name, include_subtypes=True: by_type[type_name],
    )
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "element_id",
        lambda declaration: declaration.element_id,
    )
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "is_instance",
        lambda value, type_name: getattr(value, "kind", None) == type_name,
    )
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "authored_text",
        lambda value: value.kind,
    )
    monkeypatch.setattr(
        expression_evidence.SysideAdapter,
        "get_source_location",
        lambda _value: ("model.sysml", 1),
    )
    monkeypatch.setattr(
        expression_evidence,
        "agentic_unit_annotation_value",
        lambda _value: None,
    )

    sites = [site for site, _expression in expression_evidence._enumerate_sites(object())]

    assert [(site.declaration_id, site.role) for site in sites] == [
        (UUID(int=71), ExpressionSiteRole.CALC_DEFINITION_DEPENDENCY),
        (UUID(int=72), ExpressionSiteRole.BINDING),
        (UUID(int=73), ExpressionSiteRole.ALIAS),
        (UUID(int=74), ExpressionSiteRole.COMPUTED_ATTRIBUTE),
        (UUID(int=75), ExpressionSiteRole.CONSTRAINT_PREDICATE),
        (UUID(int=76), ExpressionSiteRole.CONSTRAINT_PREDICATE),
    ]
    assert len({site.declaration_id for site in sites}) == len(sites)


def test_bound_formal_refuses_missing_qualified_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parameter = SimpleNamespace(
        element_id=UUID(int=80),
        name="input_value",
        qualified_name=None,
        owned_redefinitions=(),
    )
    monkeypatch.setattr(
        binding_source.SysideAdapter,
        "element_id",
        lambda value: value.element_id,
    )

    with pytest.raises(SemanticEvidenceError) as caught:
        binding_source.bound_formal(parameter)

    assert caught.value.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
    assert caught.value.reference == "input_value"
