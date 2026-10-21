"""agentic-mbse's subset screen, read in the generator's terms (EXEC-SUBSET-CONTRACT Item 2a).

The screen (``agentic_mbse.sysml.subset_profile``) reports findings by reason. This module
holds the two things codegen owns about them:

- ``REASON_MAPPING``: the code the generator refuses with, for each reason the screen can
  report. A reason whose shape the generator never refuses maps to ``NO_REFUSAL``.
- ``render_finding``: one finding as a ``SubsetDiagnostic``, with that code, the rule
  record's remedy and the finding's location.

Nothing under ``src/`` imports this module; only the agreement tests read it. Importing it
compares the installed screen's ``SUBSET_PROFILE_VERSION`` with the pin in ``_upstream_pins.py``
and raises ``ImportError`` on a mismatch (Item 2a design D12), so a mapping reviewed against
one contract is never read against another.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from agentic_mbse.sysml import subset_profile
from agentic_mbse.sysml.subset_profile import (
    ContextId,
    Outcome,
    Qualification,
    RuleRecords,
    SubsetFinding,
)

from sysml_codegen._upstream_pins import SUBSET_PROFILE_VERSION
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.extraction.source_evidence import ReadinessCode

if subset_profile.SUBSET_PROFILE_VERSION != SUBSET_PROFILE_VERSION:
    raise ImportError(
        f"agentic-mbse's subset profile is {subset_profile.SUBSET_PROFILE_VERSION!r}, but "
        f"REASON_MAPPING was reviewed against {SUBSET_PROFILE_VERSION!r}. Review the mapping "
        "against the new records, then update sysml_codegen/_upstream_pins.py."
    )

#: A refusal code the generator emits. The two enums share some values; codes compare by value.
type Code = ElaborationCode | ReadinessCode


@dataclass(frozen=True)
class NoRefusal:
    """The generator refuses this reason's shape in no context."""

    def codes(self) -> frozenset[str]:
        return frozenset()


@dataclass(frozen=True)
class ReasonMapping:
    """The code the generator refuses a reason's shape with, per context where it differs."""

    default: Code
    by_context: Mapping[ContextId, Code] = field(default_factory=lambda: MappingProxyType({}))

    def code_for(self, context: ContextId) -> Code:
        return self.by_context.get(context, self.default)

    def codes(self) -> frozenset[str]:
        return frozenset(code.value for code in (self.default, *self.by_context.values()))


NO_REFUSAL = NoRefusal()

#: Keyed by every member of ``SUBSET_REASON_CODES``. Every refused pair Item 1 observed carries
#: its record's ``expected_code`` in every context, so no entry has per-context codes yet.
REASON_MAPPING: Mapping[str, ReasonMapping | NoRefusal] = MappingProxyType(
    {
        "calc_owned_asserted_constraint": ReasonMapping(ElaborationCode.SI_CONSTRAINT_UNATTACHED),
        "calc_owned_non_asserted_constraint": ReasonMapping(
            ElaborationCode.SI_CONSTRAINT_UNATTACHED
        ),
        "calc_usage_bare_result_not_executed": NO_REFUSAL,
        "binding_source_expression": ReasonMapping(ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED),
        "binding_source_self_reference": ReasonMapping(ReadinessCode.SI_SELF_BINDING),
        "indexed_reference_unsupported": ReasonMapping(
            ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
        ),
        "part_multiplicity_ordered": ReasonMapping(ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED),
        "part_multiplicity_range": ReasonMapping(ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED),
        "part_multiplicity_unresolved_bound": ReasonMapping(
            ElaborationCode.SI_MULTIPLICITY_UNRESOLVED
        ),
        "invocation_callable_unsupported": ReasonMapping(
            ElaborationCode.SI_EXPRESSION_SOURCE_UNSUPPORTED
        ),
        "conditional_expression_unsupported": ReasonMapping(ElaborationCode.SI_EVIDENCE_INCOMPLETE),
        "conditional_expression_resolved_branches": NO_REFUSAL,
        "constraint_predicate_blocked": ReasonMapping(ElaborationCode.SI_CONSTRAINT_BLOCKED),
        "constraint_predicate_non_numerical": NO_REFUSAL,
        "string_value_not_generated": NO_REFUSAL,
    }
)


@dataclass(frozen=True)
class SubsetDiagnostic:
    """One screen finding in the generator's terms.

    Deliberately not an elaboration ``Diagnostic``: ``Diagnostic.reason`` is a codegen
    ``SiteReason``, and ``subset_reason`` is agentic-mbse's reason vocabulary.
    """

    #: The code the generator refuses this finding with; ``None`` unless the finding is refused.
    code: Code | None
    rule_id: str
    outcome: Outcome
    qualification: Qualification
    subset_reason: str
    remedy: str
    #: The finding's subject; ``None`` for an anonymous element, which its location identifies.
    subject: str | None
    source_file: str | None
    source_line: int | None


def render_finding(finding: SubsetFinding, rules: RuleRecords) -> SubsetDiagnostic:
    """Render one finding, with the refusal code its records predict when it is refused."""
    mapping = REASON_MAPPING[finding.reason]
    code: Code | None = None
    if finding.outcome is Outcome.REFUSED:
        if isinstance(mapping, NoRefusal):
            raise ValueError(
                f"finding {finding.rule_id}/{finding.shape_id} is refused, but its reason "
                f"{finding.reason!r} maps to NO_REFUSAL"
            )
        code = mapping.code_for(finding.context_id)
    return SubsetDiagnostic(
        code=code,
        rule_id=finding.rule_id,
        outcome=finding.outcome,
        qualification=finding.qualification,
        subset_reason=finding.reason,
        remedy=rules.rule(finding.rule_id).remedy,
        subject=finding.subject.qualified_name,
        source_file=finding.location.file,
        source_line=finding.location.line,
    )


__all__ = [
    "NO_REFUSAL",
    "REASON_MAPPING",
    "Code",
    "NoRefusal",
    "ReasonMapping",
    "SubsetDiagnostic",
    "render_finding",
]
