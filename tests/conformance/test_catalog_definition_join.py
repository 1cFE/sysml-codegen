"""Item 8: the entry→definition FK and the admitted-usage tier, against real lowering.

F1 (the FK gate): a catalog entry's ``definition_qualified_name`` is non-None **iff** its
``source_form == "definition_typed"``, and every non-None value resolves to a real
``source_records`` row (INV-1, no dangling FK). Named-inline eligible constraints — whose
effective predicate source is the usage's own QN, not a ``facts.definitions`` entry — carry
``None``, not a dangling self-reference.

INV-2 (the usage tier): one row per distinct ``(usage_qualified_name, source_local_identity)``.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
@pytest.mark.parametrize("fixture", ["constraint_multi_instance", "wi014_toy"])
def test_definition_fk_gated_on_form_and_never_dangles(fixture):
    ctx = build_pipeline_context([FIXTURES_DIR / fixture], lower_constraints_enabled=True)
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None
    definition_qns = {r.definition_qualified_name for r in catalog.source_records}

    for entry in catalog.concrete_entries:
        if entry.source_form == "definition_typed":
            assert entry.definition_qualified_name is not None, (
                f"{entry.constraint_id}: definition_typed entry has no definition FK"
            )
            assert entry.definition_qualified_name in definition_qns, (
                f"{entry.constraint_id}: FK {entry.definition_qualified_name!r} dangles "
                "(no matching source_records row)"
            )
        else:
            assert entry.definition_qualified_name is None, (
                f"{entry.constraint_id}: non-definition_typed entry "
                f"({entry.source_form}) carries a definition FK — the F1 dangling case"
            )


@requires_license
@pytest.mark.parametrize("fixture", ["constraint_multi_instance", "wi014_toy"])
def test_usage_tier_is_one_row_per_full_usage_identity(fixture):
    ctx = build_pipeline_context([FIXTURES_DIR / fixture], lower_constraints_enabled=True)
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None

    keys = [(u.usage_qualified_name, u.source_local_identity) for u in catalog.usage_records]
    assert len(keys) == len(set(keys)), "usage tier has duplicate (usage_qn, local) rows"

    # Every eligible occurrence's usage identity appears exactly once in the usage tier.
    entry_keys = {
        (e.usage_qualified_name, e.source_local_identity) for e in catalog.concrete_entries
    }
    assert entry_keys == set(keys), "usage tier does not cover all admitted occurrences 1:1"

    # Usage-tier identity agrees with its occurrences (B2 invariance).
    by_key = {(u.usage_qualified_name, u.source_local_identity): u for u in catalog.usage_records}
    for entry in catalog.concrete_entries:
        usage = by_key[(entry.usage_qualified_name, entry.source_local_identity)]
        assert usage.source_form == entry.source_form
        assert usage.owner_qualified_name == entry.owner_qualified_name
        assert usage.definition_qualified_name == entry.definition_qualified_name
