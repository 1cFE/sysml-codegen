"""The readiness vocabulary and the modelled value-site kinds.

Extraction-layer home for the dispositions, so the extraction package never imports
upward into ``analysis/`` (REQ-EXT-06).

The permissive ``SourceReferenceEvidence`` record that used to live here is gone.  It
carried ``semantic_reference: ResolvedSemanticReferenceFact | None`` beside a separate
``source_form`` enum, so "a supported reference binding that has no path" and "an indexed
chain that kept a path" were both representable and had to be defended against at every
read.  Binding sources are now the closed union in
:mod:`sysml_codegen.extraction.binding_source`, where neither state can be constructed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "ReadinessCode",
    "ReadinessFinding",
    "ValueSiteKind",
]


class ValueSiteKind(str, Enum):
    """The three modeled value-site kinds (design D2).

    A modeled value site is a model location that supplies a value before
    producer resolution. Computed producer outputs are not value sites.
    """

    DEFINITION_DEFAULT = "definition_default"
    OCCURRENCE_OVERRIDE = "occurrence_override"
    USAGE_LITERAL = "usage_literal"


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
    reference: str | None = None
    source_file: str | None = None
    source_line: int | None = None
