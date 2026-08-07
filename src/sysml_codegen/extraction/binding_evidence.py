"""Per-binding source-evidence builders, shared by both front ends.

Factored out of ``usage_extractor`` (ELABORATE-FIRST design D2) so the legacy
extraction front end and the elaborator build identical
:class:`~sysml_codegen.extraction.source_evidence.SourceReferenceEvidence`
records during dual-run. Everything here reads the live AST/CST once and
produces frozen evidence; nothing here resolves, rewrites, or interprets a
reference.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_mbse.sysml.expression import (
    feature_chain_facts,
    resolved_target_fact,
)
from agentic_mbse.sysml.helpers import get_source_file

from sysml_codegen.extraction.expression_utils import (
    extract_feature_chain_segments,
)
from sysml_codegen.extraction.source_evidence import (
    SourceForm,
    SourceReferenceEvidence,
)

__all__ = [
    "WRITTEN_UNKNOWN",
    "bound_formal_facts",
    "chain_evidence",
    "expression_evidence",
    "literal_evidence",
    "reference_evidence",
    "written_qualifier",
    "written_reference_text",
]

# Source bytes, keyed by (path, mtime_ns). The mtime component means a file edited
# between two extractions in one process cannot serve stale bytes — extraction reads
# from disk within a single run today, but keying on mtime removes the single-run
# assumption rather than only documenting it (audit N2).
_SOURCE_BYTES_CACHE: dict[tuple[str, int], bytes] = {}

# Sentinel: recovery of the written form failed, so we do not know whether the
# reference was written qualified or bare. Callers must fail AWAY from the F2 defect
# and treat this as qualified (row-16 safe-miss), never as a bare leaf.
WRITTEN_UNKNOWN = "\x00written-unknown"


def written_reference_text(expr: Any) -> str | None:
    """The reference exactly as the model wrote it, from the concrete syntax tree.

    Resolution discards how a reference was written: `source_path` and the referent
    both hold the *resolved* qualified name, so `in kappa = catf_radial_build::elongation`
    and a bare `in eta = efficiency` are indistinguishable downstream — which is the
    ambiguity that let a scope-qualified reference be re-anchored onto an owner-local
    shadow (audit F2/F2b).

    The written form survives on the CST node as a byte span into the source document,
    which is the same adapter surface extraction already uses for source locations.

    Returns the written text, or ``WRITTEN_UNKNOWN`` when the span cannot be recovered.
    It never returns ``None`` for a failure: a failure is *unknown*, not *bare*, and the
    caller must fail toward safe-miss rather than toward the F2 re-anchor (audit N2). The
    exception handling is narrow on purpose — an ``AttributeError`` from a real adapter
    change should raise here, not be silently absorbed as "unknown".
    """
    cst = getattr(expr, "cst_node", None)
    if cst is None:
        return WRITTEN_UNKNOWN
    start = getattr(cst, "start_byte", None)
    end = getattr(cst, "end_byte", None)
    if not isinstance(start, int) or not isinstance(end, int) or end <= start:
        return WRITTEN_UNKNOWN
    source_file = get_source_file(expr)
    if not source_file:
        return WRITTEN_UNKNOWN
    path = Path(source_file)
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        return WRITTEN_UNKNOWN
    cache_key = (str(source_file), mtime)
    data = _SOURCE_BYTES_CACHE.get(cache_key)
    if data is None:
        try:
            data = path.read_bytes()
        except OSError:
            return WRITTEN_UNKNOWN
        _SOURCE_BYTES_CACHE[cache_key] = data
    if end > len(data):
        return WRITTEN_UNKNOWN
    try:
        text: str = data[start:end].decode("utf-8").strip()
    except UnicodeDecodeError:
        return WRITTEN_UNKNOWN
    return text


def written_qualifier(expr: Any) -> str | None:
    """The scope qualifier the model wrote, or ``None`` for a bare leaf.

    ``catf_radial_build::elongation`` -> ``catf_radial_build``; ``gain`` -> ``None``.
    A qualifier means the reference names its own scope and is therefore **not**
    owner-relative, which is what row 16 needs to know (audit F2).

    Fails toward safe-miss (audit N2): if the written form could not be recovered we
    do not know it was bare, so we return a non-empty marker that makes row 16 miss —
    the reference falls through to exact-identity resolution, which is today's
    behaviour and can never produce a wrong number. Only a written form we actually
    read, with no ``::``, is reported as a bare leaf.
    """
    written = written_reference_text(expr)
    if written is WRITTEN_UNKNOWN:
        # Unknown -> treat as qualified. `_MISS` on row 16; row 17 resolves by identity.
        return WRITTEN_UNKNOWN
    if written is None or "::" not in written:
        return None
    qualifier = written.rsplit("::", 1)[0].strip()
    return qualifier or WRITTEN_UNKNOWN


def bound_formal_facts(param_elem: Any) -> tuple[str, tuple[str, ...]]:
    """The bound formal's own exact QN and the calc-def formals it redefines.

    Both sides of a binding are evidence (SOURCE-IDENTITY Item 4): self-binding
    is an exact comparison of the RHS referent against this formal identity,
    never ``param_name == leaf``.
    """
    formal_qn = getattr(param_elem, "qualified_name", None)
    redefines: list[str] = []
    for redefinition in getattr(param_elem, "owned_redefinitions", None) or []:
        redefined_feature = getattr(redefinition, "redefined_feature", None)
        redefined_qn = getattr(redefined_feature, "qualified_name", None)
        if redefined_qn is not None:
            redefines.append(str(redefined_qn))
    return (str(formal_qn) if formal_qn is not None else "", tuple(redefines))


def _written_text_or_none(expr: Any) -> str | None:
    """The authored text from the CST, or None when it cannot be recovered."""
    written = written_reference_text(expr)
    return None if written is WRITTEN_UNKNOWN else written


def chain_evidence(param_elem: Any, expr: Any) -> SourceReferenceEvidence:
    """Immutable evidence for a FeatureChainExpression binding of any length.

    An ``#(i)`` index operand classifies the whole binding INDEXED_SOURCE with
    no referent — the contract's SRC-02 ruling: no occurrence feature identity
    exists for the trailing segment to anchor to. The index is retained as
    evidence, never flattened into a supported source. The legacy dispatch
    fields are left exactly as before; only evidence is added.
    """
    formal_qn, formal_redefines = bound_formal_facts(param_elem)
    chain_root, leaf_fact, segment_qns, member_names, has_index = feature_chain_facts(expr)
    authored_segments = tuple(extract_feature_chain_segments(expr))
    return SourceReferenceEvidence(
        bound_formal_qn=formal_qn,
        source_form=SourceForm.INDEXED_SOURCE if has_index else SourceForm.FEATURE_CHAIN,
        referent=None if has_index else leaf_fact,
        chain_root=chain_root,
        resolved_segment_qns=segment_qns,
        resolved_member_names=member_names,
        bound_formal_redefines=formal_redefines,
        written_text=_written_text_or_none(expr),
        authored_segments=authored_segments,
    )


def reference_evidence(param_elem: Any, expr: Any) -> SourceReferenceEvidence:
    """Immutable evidence for a FeatureReferenceExpression binding."""
    formal_qn, formal_redefines = bound_formal_facts(param_elem)
    referent_fact = resolved_target_fact(getattr(expr, "referent", None))
    qualifier = written_qualifier(expr)
    if qualifier is WRITTEN_UNKNOWN:
        source_form = SourceForm.REFERENCE_FORM_UNKNOWN
        evidence_qualifier = None
    elif qualifier is None:
        source_form = SourceForm.BARE_REFERENCE
        evidence_qualifier = None
    else:
        source_form = SourceForm.QUALIFIED_REFERENCE
        evidence_qualifier = qualifier
    return SourceReferenceEvidence(
        bound_formal_qn=formal_qn,
        source_form=source_form,
        referent=referent_fact,
        resolved_segment_qns=(referent_fact.qualified_name,) if referent_fact else (),
        bound_formal_redefines=formal_redefines,
        written_qualifier=evidence_qualifier,
        written_text=_written_text_or_none(expr),
    )


def literal_evidence(
    param_elem: Any, literal_value: float | int | str | bool | None
) -> SourceReferenceEvidence:
    """Immutable evidence for an authored usage literal (value-site kind 3).

    No referent exists: an authored literal is its own source. This is what
    keeps authored literals distinguishable from reference-derived literals the
    legacy VBR stamps — a stamped binding keeps its original reference-form
    evidence, an authored one is AUTHORED_LITERAL from birth.
    """
    formal_qn, formal_redefines = bound_formal_facts(param_elem)
    return SourceReferenceEvidence(
        bound_formal_qn=formal_qn,
        source_form=SourceForm.AUTHORED_LITERAL,
        bound_formal_redefines=formal_redefines,
        written_text=str(literal_value) if literal_value is not None else None,
    )


def expression_evidence(param_elem: Any, expr: Any) -> SourceReferenceEvidence:
    """Immutable evidence for an expression-source binding.

    A bare ``#(i)`` IndexExpression RHS is an OperatorExpression subtype and
    lands here; it keeps its distinct INDEXED_SOURCE form. The adapter's closed
    type map has no ``IndexExpression`` entry, so the check is by metatype name.
    """
    formal_qn, formal_redefines = bound_formal_facts(param_elem)
    is_indexed = type(expr).__name__ == "IndexExpression"
    return SourceReferenceEvidence(
        bound_formal_qn=formal_qn,
        source_form=SourceForm.INDEXED_SOURCE if is_indexed else SourceForm.EXPRESSION_SOURCE,
        bound_formal_redefines=formal_redefines,
        written_text=_written_text_or_none(expr),
    )
