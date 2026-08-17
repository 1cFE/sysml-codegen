"""A one-segment leaf the element index does not hold is refused, not routed.

The one semantic resolver classifies a one-segment reference by its exact leaf's live
owner, and it reads that leaf from `_ExactElaborator._elements`. The index holds every
declaration carrying a reload-stable qualified name, which is every declaration an author
can name, so a leaf missing from it means the resolved fact and the index disagree about
what the model contains.

The state must refuse before any address is built. It cannot fall through to a positional
leaf route because that compatibility route no longer exists.

**Observed corpus boundary.** The retained census
(`.project/completed/20260816_qualified-reference-occurrence-anchoring/verification/absent_leaf_census.py`
and its JSON result) finds zero absent leaves among 770 observed resolver calls. Fifteen
roots retain unmeasured population, so that result does not establish authored reachability
for the whole corpus. This test therefore reaches the state directly at the resolver
boundary. It proves the state refuses instead of guessing; it makes no authorability claim.
"""

from __future__ import annotations

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest
from agentic_mbse.sysml.data_models import (
    ResolvedSemanticReferenceFact,
    ResolvedTargetFact,
)

from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.elaborate import _ExactElaborator, _ReferenceResolutionError
from sysml_codegen.elaboration.identity import DeclarationId
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

FIXTURE = "usage_owner_bare_alias"

#: A well-formed v5 declaration ID for a declaration that is not in the model. Its shape
#: passes every identity check, so the refusal below is about index membership and
#: nothing else.
UNKNOWN_LEAF = DeclarationId(uuid5(NAMESPACE_URL, "https://sysml-codegen.test/absent-leaf"))


@requires_license
def test_direct_reference_refuses_a_leaf_absent_from_the_element_index() -> None:
    extractor = SysMLDataExtractor([Path(FIXTURES_DIR / FIXTURE)])
    assert extractor.load_models(), f"fixture {FIXTURE} failed to load"
    elaborator = _ExactElaborator(
        extractor.model, extractor.extract_calculation_definitions(), strict=False
    )
    graph = elaborator.run()
    scope = next(iter(graph.occurrences))
    assert UNKNOWN_LEAF not in elaborator._elements

    with pytest.raises(_ReferenceResolutionError) as excinfo:
        target = ResolvedTargetFact(
            element_id=UNKNOWN_LEAF.value,
            owner_element_id=None,
            redefined_element_ids=(),
            qualified_name="Absent::leaf",
            element_kind="AttributeUsage",
            element_name="leaf",
        )
        elaborator._resolve_semantic_reference(
            ResolvedSemanticReferenceFact(
                root=target,
                segments=(target,),
                leaf=target,
                resolved_member_names=(),
                has_index_segment=False,
            ),
            scope,
            plural=False,
            no_prefix=True,
        )

    assert excinfo.value.code == ElaborationCode.SI_OCCURRENCE_MISSING
    assert UNKNOWN_LEAF.to_wire() in excinfo.value.detail
