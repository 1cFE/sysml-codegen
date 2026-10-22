"""Every public codegen site has a reason and a witness (Item 2a E3, PD5 second form, plan P6).

Pure: reads the account, the stored answers and ``mutations.json``. A public row's reason is
its ``reason`` column, except at a site that builds a ``SemanticEvidenceError``: that reason is
set at the relay, from ``_EVIDENCE_REASONS``, so the row carries none
(``test_site_reasons.py``). A public row's witness is a case that names it; a public site no
valid model reaches is instead recorded ``unwitnessed`` in ``mutations.json``, where
``test_generator_mutations.py`` fails as soon as a case reaches it (the P5 split ruling counts
that as done). That each witness fires is ``test_witnesses.py``'s licensed check.
"""

from __future__ import annotations

import pytest
from agentic_mbse import SemanticEvidenceCode

from sysml_codegen.orchestration.elaborated_pipeline import _EVIDENCE_REASONS
from tests.helpers.refusal_cases import site_scan, witnesses
from tests.helpers.refusal_cases.site_scan import Role

PUBLIC = [r for r in site_scan.load_account().rows if r.role is Role.PUBLIC_CAPABILITY]
UNWITNESSED = witnesses.read_mutations().unwitnessed


def _relayed_reason(code: str) -> str | None:
    if code not in SemanticEvidenceCode.__members__:
        return None
    return _EVIDENCE_REASONS[SemanticEvidenceCode[code]].value


@pytest.mark.parametrize("row", PUBLIC, ids=lambda r: r.site_id)
def test_every_public_row_has_a_reason(row):
    assert row.reason is not None or _relayed_reason(row.code) is not None


@pytest.mark.parametrize("row", PUBLIC, ids=lambda r: r.site_id)
def test_every_public_row_has_a_witness_or_a_reach_guard(row):
    assert witnesses.witnesses_of(row.site_id) or row.site_id in UNWITNESSED


def test_a_relayed_reason_is_never_also_recorded():
    for row in PUBLIC:
        if _relayed_reason(row.code) is not None:
            assert row.reason is None, row.site_id
