"""``SiteReason`` stays a codegen vocabulary of its own (Item 2a D8)."""

from __future__ import annotations

from agentic_mbse import SemanticEvidenceCode
from agentic_mbse.sysml.subset_profile import SUBSET_REASON_CODES

from sysml_codegen.elaboration.diagnostics import SiteReason
from sysml_codegen.orchestration.elaborated_pipeline import _EVIDENCE_REASONS


def test_site_reasons_are_disjoint_from_subset_reason_codes():
    assert {reason.value for reason in SiteReason}.isdisjoint(SUBSET_REASON_CODES)


def test_every_semantic_evidence_code_has_its_own_site_reason():
    assert set(_EVIDENCE_REASONS) == set(SemanticEvidenceCode)
    assert len(set(_EVIDENCE_REASONS.values())) == len(_EVIDENCE_REASONS)
