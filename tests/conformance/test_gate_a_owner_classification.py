"""Gate A: a constraint owned by a concrete PartUsage is classified as usage-owned.

Item 2, SR-A01 / SR-R20–SR-R23. Gate A is not a missing key form — it is a missing
*scope*. The owning-definition walk stops at the first enclosing definition or package,
so a constraint declared inside a concrete `PartUsage` that sits directly in a package
body reports the *package* as its owner. `_expand_package_owner` then hands resolution
the constraint's own qualified name as the owner instance path, and the
occurrence-materialized design-attribute key overshoots by the constraint's own name:
it asks for `GateA__the_host__viability__gain` where the attribute is really
`GateA__the_host__gain`. Resolution reaches `terminal_disposition(strict=True)` and
generation fails.

These nodes are authored once and run unchanged at the RED coordinate and at GREEN
(SR-R50). At RED, `test_gate_a_*` fail for exactly that terminal raise — verified
against the live route before the fix; the package-owner control passes on both sides,
because it pins preservation rather than a defect.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

from sysml_codegen.analysis.constraint_lowering import prepare_constraint_usages
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from tests.conftest import requires_license

FIXTURES = Path(__file__).parent.parent / "fixtures"

# The attribute's real qualified name, as extraction emits it: the usage segment is
# present exactly once (`parameter_groups.py:140,189-190`).
_GAIN_QN = "GateA__the_host__gain"


def _constraints(fixture: str):
    context = build_pipeline_context([FIXTURES / fixture])
    return {c.usage_qualified_name: c for c in context.concrete_constraints}


@requires_license
def test_gate_a_usage_owned_constraint_takes_the_usage_as_its_owner_instance():
    """SR-R20: the owner instance path is the owning PartUsage, not the constraint.

    This is the classification half of Gate A. At RED the path is
    `GateA__the_host__viability` — the constraint's own QN, which is what makes the
    design-attribute key overshoot.
    """
    constraint = _constraints("gate_a")["GateA::the_host::viability"]
    assert constraint.owner_instance_path == "GateA__the_host"


@requires_license
def test_gate_a_usage_owned_attribute_resolves_under_its_real_qn():
    """SR-A01/SR-R20: the self-named actual resolves to the usage-owned design
    attribute on the public live route, with no passthrough calculation in the model.

    At RED this raises `CodeGenerationError` from `terminal_disposition(strict=True)`.
    """
    constraint = _constraints("gate_a")["GateA::the_host::viability"]
    resolved = {i.formal_name: i for i in constraint.inputs}
    assert resolved["gain"].design_attribute_qn == _GAIN_QN


@requires_license
def test_package_owned_constraint_still_routes_to_the_package_branch():
    """The M6 control: a constraint declared directly in a package body keeps the
    package branch's behavior — its owner instance path is its own qualified name.

    No fixture in the repo covered this shape before Item 2, so the surviving branch
    had zero live coverage while the new one was added ahead of it.
    """
    constraint = _constraints("gate_a_package_owner")["GateAPackageOwner::pkg_check"]
    assert constraint.owner_instance_path == "GateAPackageOwner__pkg_check"


def _package_scoped_usage(owner_kind: str) -> ConstraintFacts:
    """One admitted, package-scoped constraint whose immediate owner has `owner_kind`.

    Inline form with a self-contained numeric predicate, so the usage clears the
    preflight on its own and actually reaches owner dispatch — a `definition_typed`
    usage would block on definition lookup before the branch under test runs.
    """
    identity = IdentityFact(
        kind="AssertConstraintUsage", name="probe", qualified_name="Pkg::host::probe"
    )
    predicate = OperatorNode(
        operator=">=",
        operands=[
            LiteralNode(
                literal=LiteralFact(kind="LiteralRational", value=v, result_type="real"),
                operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
            )
            for v in (2.0, 1.0)
        ],
        operand_type=None,
    )
    usage = ConstraintUsageFact(
        identity=identity,
        location=None,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=IdentityFact(kind=owner_kind, name="host", qualified_name="Pkg::host"),
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Pkg"),
        ),
        scope=identity,
        membership_kind="assert",
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )
    return ConstraintFacts(definitions=[], usages=[usage], contexts=[], diagnostics=[])


def test_unrecognized_owner_kind_raises_rather_than_falling_through():
    """D10: `IdentityFact.kind` is `type(element).__name__`, an open set the syside
    runtime owns. An owner kind outside the allowlist is refused, because falling
    through to the package branch would silently mis-key the constraint's actuals —
    the Gate A defect, reintroduced without a diagnostic.
    """
    with pytest.raises(CodeGenerationError, match="unrecognized immediate owner kind"):
        prepare_constraint_usages(
            _package_scoped_usage("SomeFuturePartUsageSubclass"),
            occ_index=None,
            calc_usages=[],
        )
