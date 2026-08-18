"""What the model actually wrote, read once from the concrete syntax.

Resolution discards the authored spelling, and two of this repository's rules need it
back: the elaborator's no-prefix handling, and the occurrence index's written-form
checks.  Nothing here resolves, classifies, or interprets a reference — it reads bytes
out of the source document at a CST span.

The four binding-evidence builders that used to live here are gone.  A binding's source
is now the closed union in :mod:`sysml_codegen.extraction.binding_source`, built from the
pre-graph inventory rather than from a per-consumer walk of the live AST.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_mbse.sysml.helpers import get_source_file

__all__ = [
    "WRITTEN_UNKNOWN",
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
