"""A one-segment leaf the element index does not hold is refused, not routed.

`_resolve_direct_reference` classifies a one-segment reference by its exact leaf's live
owner, and it reads that leaf from `_ExactElaborator._elements`. The index holds every
declaration carrying a reload-stable qualified name, which is every declaration an author
can name, so a leaf missing from it means the resolved fact and the index disagree about
what the model contains.

Before this test's branch existed, that disagreement fell through to `_resolve_leaf` —
the route reserved for a leaf whose owner is a definition or package. That route answers
from the *consumer's* own occurrence lineage, which is exactly the positional guess this
item removed; taking it because owner classification was impossible would have re-created
the defect in the one case nobody could see.

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
        elaborator._resolve_direct_reference(
            UNKNOWN_LEAF,
            scope,
            definition_owner_requires_lineage=True,
        )

    assert excinfo.value.code == ElaborationCode.SI_OCCURRENCE_MISSING
    assert UNKNOWN_LEAF.to_wire() in excinfo.value.detail
