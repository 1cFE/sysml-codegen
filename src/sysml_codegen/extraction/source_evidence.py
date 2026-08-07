"""Immutable source-reference evidence captured at extraction.

Extraction-layer home for the evidence value types and the pure readiness
screening over them, so the extraction package never imports upward into
``analysis/`` (REQ-EXT-06). This evidence is the elaborator's input
(ELABORATE-FIRST epic): the exact SysIDE-resolved facts, captured while the
AST is live, that later stages may consume but never reconstruct.

Everything here is frozen: virtual-binding rewrite, literal stamping, rescue,
and enrichment reassign legacy ``BindingInfo`` scalars but can never mutate or
replace this evidence. Identity is never derived from a consumer's owner,
parameter name, written leaf, or current value — diagnostic text may show
those, constructors may not use them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_mbse.sysml.data_models import ResolvedTargetFact

__all__ = [
    "ReadinessCode",
    "ReadinessFinding",
    "SourceForm",
    "SourceReferenceEvidence",
    "ValueSiteKind",
    "screen_source_readiness",
]


class SourceForm(str, Enum):
    """The authored form of a binding's right-hand side.

    Captured from the concrete syntax and expression structure at extraction —
    the written form, never the resolved one, because resolution makes a bare
    leaf and a qualified reference indistinguishable. ``REFERENCE_FORM_UNKNOWN``
    is an honest disposition for a reference whose written form could not be
    recovered from the CST; it is never silently collapsed into bare or
    qualified.
    """

    BARE_REFERENCE = "bare_reference"
    QUALIFIED_REFERENCE = "qualified_reference"
    REFERENCE_FORM_UNKNOWN = "reference_form_unknown"
    FEATURE_CHAIN = "feature_chain"
    INDEXED_SOURCE = "indexed_source"
    EXPRESSION_SOURCE = "expression_source"
    AUTHORED_LITERAL = "authored_literal"


class ValueSiteKind(str, Enum):
    """The three modeled value-site kinds (design D2).

    A modeled value site is a model location that supplies a value before
    producer resolution. Computed producer outputs are not value sites.
    """

    DEFINITION_DEFAULT = "definition_default"
    OCCURRENCE_OVERRIDE = "occurrence_override"
    USAGE_LITERAL = "usage_literal"


@dataclass(frozen=True)
class SourceReferenceEvidence:
    """Immutable semantic evidence for one source-bearing binding.

    Records both sides of the binding exactly as SysIDE resolved them:

    - ``bound_formal_qn`` — the bound formal parameter's own qualified name.
      This is a consumer coordinate: it locates the binding and detects
      self-binding, but identity is never constructed from it (design D3).
    - ``referent`` — the exact resolved target of the right-hand side, or
      ``None`` when no single source feature exists (indexed, expression, and
      authored-literal forms).
    - ``chain_root`` / ``resolved_segment_qns`` — the occurrence anchor and the
      full resolved step list for feature chains of any length.
    - ``written_text`` / ``authored_segments`` — the authored spelling, kept for
      diagnostics only.

    Frozen with tuple fields throughout. A stamped literal therefore stays
    distinguishable from an authored one: its evidence keeps the reference form
    it was extracted with.
    """

    bound_formal_qn: str
    source_form: SourceForm
    referent: ResolvedTargetFact | None = None
    chain_root: ResolvedTargetFact | None = None
    resolved_segment_qns: tuple[str, ...] = ()
    resolved_member_names: tuple[str, ...] = ()
    bound_formal_redefines: tuple[str, ...] = ()
    written_qualifier: str | None = None
    written_text: str | None = None
    authored_segments: tuple[str, ...] = ()

    @property
    def is_self_binding(self) -> bool:
        """True when the right-hand side resolved to the bound formal itself.

        The exact semantic comparison the contract requires (SRC-01): referent
        identity against formal identity — not ``param_name == leaf`` and not an
        outer-scope search. A same-named outer feature never changes this
        answer, because the comparison never reads names.
        """
        return (
            self.referent is not None
            and self.referent.qualified_name == self.bound_formal_qn
        )

    @property
    def is_reference_derived(self) -> bool:
        """True when this binding was authored as a reference to another feature."""
        return self.source_form in (
            SourceForm.BARE_REFERENCE,
            SourceForm.QUALIFIED_REFERENCE,
            SourceForm.REFERENCE_FORM_UNKNOWN,
            SourceForm.FEATURE_CHAIN,
        )


class ReadinessCode(str, Enum):
    """Machine-checkable source-readiness dispositions (contract D8).

    The three extraction-detectable form codes. Occurrence-level outcomes
    belong to the elaborator (ELABORATE-FIRST Item 4) and are not enumerated
    here.
    """

    SI_SELF_BINDING = "SI_SELF_BINDING"
    SI_INDEXED_SOURCE_UNSUPPORTED = "SI_INDEXED_SOURCE_UNSUPPORTED"
    SI_EXPRESSION_SOURCE_UNSUPPORTED = "SI_EXPRESSION_SOURCE_UNSUPPORTED"


@dataclass(frozen=True)
class ReadinessFinding:
    """One screened source-readiness disposition for a concrete binding."""

    code: ReadinessCode
    usage_qualified_name: str
    param_name: str
    detail: str


def screen_source_readiness(calc_usages: list) -> list[ReadinessFinding]:
    """Screen extracted calc-usage bindings for unsupported source forms.

    Emits the exact D8 dispositions for the three extraction-detectable forms:
    a binding whose right-hand side resolves to its own formal
    (``SI_SELF_BINDING``), a valid ``#(i)`` indexed source outside the
    executable subset (``SI_INDEXED_SOURCE_UNSUPPORTED``), and a general
    expression source (``SI_EXPRESSION_SOURCE_UNSUPPORTED``).

    Pure classification over the immutable evidence — it reads no names, no
    current values, and no consumer-owner scopes, and it does not alter any
    binding. Findings are deterministic: sorted by usage, parameter, then code.
    Bindings without evidence (snapshot-loaded data has none) are skipped.
    """
    findings: list[ReadinessFinding] = []
    for usage in calc_usages:
        if getattr(usage, "is_template", False):
            continue
        for binding in usage.bindings:
            evidence = getattr(binding, "reference_evidence", None)
            if evidence is None:
                continue
            if evidence.source_form is SourceForm.INDEXED_SOURCE:
                findings.append(
                    ReadinessFinding(
                        code=ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED,
                        usage_qualified_name=usage.qualified_name,
                        param_name=binding.param_name,
                        detail=(
                            "indexed value expression "
                            f"{evidence.written_text or binding.raw_expression!r} is valid "
                            "SysML but unsupported by this executable subset; the index "
                            "segment is never flattened into a supported source"
                        ),
                    )
                )
            elif evidence.source_form is SourceForm.EXPRESSION_SOURCE:
                findings.append(
                    ReadinessFinding(
                        code=ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED,
                        usage_qualified_name=usage.qualified_name,
                        param_name=binding.param_name,
                        detail=(
                            "expression source "
                            f"{evidence.written_text or binding.raw_expression!r} is valid "
                            "SysML but unsupported by this executable subset; no source "
                            "feature identity exists for it"
                        ),
                    )
                )
            elif evidence.is_self_binding:
                findings.append(
                    ReadinessFinding(
                        code=ReadinessCode.SI_SELF_BINDING,
                        usage_qualified_name=usage.qualified_name,
                        param_name=binding.param_name,
                        detail=(
                            f"binding resolves to its own formal {evidence.bound_formal_qn!r}; "
                            "the binding is legal, inert SysML and supplies no enclosing "
                            "feature"
                        ),
                    )
                )
    findings.sort(key=lambda f: (f.usage_qualified_name, f.param_name, f.code.value))
    return findings
