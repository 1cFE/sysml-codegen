"""The stored mutation record covers exactly the planned mutations (Item 2a § B, plan P2.4).

Pure: reads ``mutations.json``, the account and the stored answers. Whether each stored set is
what a live mutation does is ``test_generator_mutations.py``.
"""

from __future__ import annotations

import pytest

from tests.helpers.subset_profile import witnesses

RECORD = witnesses.read_mutations()


def test_every_mutated_site_is_recorded_once():
    assert not RECORD.generator.keys() & RECORD.unwitnessed.keys()
    assert sorted(RECORD.generator.keys() | RECORD.unwitnessed.keys()) == sorted(
        witnesses.mutated_sites()
    )


@pytest.mark.parametrize("site_id", sorted(RECORD.generator), ids=str)
def test_a_generator_mutation_changes_a_witness(site_id):
    assert RECORD.generator[site_id] & witnesses.witnesses_of(site_id), site_id


@pytest.mark.parametrize(
    "site_id", sorted(s for s in RECORD.unwitnessed if s.startswith("sysml_codegen/")), ids=str
)
def test_an_unwitnessed_codegen_site_has_no_witness(site_id):
    assert witnesses.witnesses_of(site_id) == frozenset()
