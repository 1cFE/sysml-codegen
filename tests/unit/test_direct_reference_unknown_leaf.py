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

**No authored model reaches this.** The retained census
(`.project/active/qualified-reference-occurrence-anchoring/verification/absent_leaf_census.py`
and its JSON result) measures every one-segment reference leaf across the frozen corpus
and the promoted fixtures and finds zero absent from the index. The branch is therefore
reached here at the resolver boundary with a declaration ID the index does not hold —
which is precisely the state the branch exists to refuse — rather than through a fixture
that pretends to be an authored shape it is not.
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
        elaborator._resolve_direct_reference(UNKNOWN_LEAF, scope)

    assert excinfo.value.code == ElaborationCode.SI_OCCURRENCE_MISSING
    assert UNKNOWN_LEAF.to_wire() in excinfo.value.detail
