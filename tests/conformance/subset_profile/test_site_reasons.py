"""A site's recorded reason is the reason its raise passes (Item 2a E3, PD5 first form).

Pure: the scan reads the ``reason=SiteReason.<member>`` a site passes literally, and the
account's ``reason`` column must name the same member's value, in both directions. Every
witness a stored answer or packaged case names is a scanned site; that each one fires is
``test_witnesses.py``'s licensed check. Requiring
every public row to have a reason and a witness is ``test_site_account_completeness.py``'s job
(P6), so this test stays green while reasons land.

Two kinds of reason are set off a scanned site, so no row carries them: the relayed
``evidence_*`` reasons, read from ``_EVIDENCE_REASONS`` at the relay, and
``generation_constraint_name_unsafe``, set inside the ``constraint_name_safety_error``
factory whose callers' raises are the rows.
"""

from __future__ import annotations

from sysml_codegen.elaboration.diagnostics import SiteReason
from tests.conformance.subset_profile.test_site_reason_reaches_harness import REACH_WITNESSES
from tests.helpers.subset_profile import site_scan, witnesses

_OCCURRENCE = "sysml_codegen/elaboration/occurrence.py"
_ELABORATE = "sysml_codegen/elaboration/elaborate.py"
SCAN = site_scan.scan()
ACCOUNT = site_scan.load_account()
SET_OFF_SITE = {SiteReason.GENERATION_CONSTRAINT_NAME_UNSAFE} | {
    reason for reason in SiteReason if reason.name.startswith("EVIDENCE_")
}


def test_every_recorded_reason_is_a_site_reason():
    values = {reason.value for reason in SiteReason}
    for row in ACCOUNT.rows:
        if row.reason is not None:
            assert row.reason in values, row.site_id


def test_every_row_with_a_reason_is_passed_by_its_raise():
    sites = SCAN.by_id()
    for row in ACCOUNT.rows:
        if row.reason is not None:
            passed = sites[row.site_id].reason
            assert passed is not None and SiteReason[passed].value == row.reason, row.site_id


def test_every_reason_a_site_passes_is_recorded():
    rows = {row.site_id: row for row in ACCOUNT.rows}
    for site in SCAN.codegen():
        if site.reason is not None:
            assert rows[site.site_id].reason == SiteReason[site.reason].value, site.site_id


def test_the_reach_witnesses_reasons_are_recorded_at_their_sites():
    recorded = {row.reason for row in ACCOUNT.rows}
    for witness in REACH_WITNESSES:
        if witness.reason not in SET_OFF_SITE:
            assert witness.reason.value in recorded, witness.branch


def test_every_witness_names_a_scanned_site():
    named = set(witnesses.codegen_witnesses()) | set(witnesses.agentic_witnesses())
    assert sorted(named - SCAN.by_id().keys()) == []


def test_every_codegen_witness_names_an_accounted_site():
    assert sorted(set(witnesses.codegen_witnesses()) - ACCOUNT.ids()) == []


def test_no_two_sites_share_a_reason():
    """A reason names one site, so a shadowing site never passes for the one it shadows (B6).

    The pair the plan names, ES-002's ``build_containment_address`` and ES-009's owner-address
    raise, both refuse ``SI_OCCURRENCE_MISSING``; only their reasons tell them apart.
    """
    by_reason: dict[str, list[str]] = {}
    for row in ACCOUNT.rows:
        if row.reason is not None:
            by_reason.setdefault(row.reason, []).append(row.site_id)
    assert {r: s for r, s in by_reason.items() if len(s) > 1} == {}


def test_es002_and_es009_reasons_distinct():
    rows = {row.site_id: row for row in ACCOUNT.rows}
    es002 = rows[f"{_OCCURRENCE}::build_containment_address::coded::SI_OCCURRENCE_MISSING::1"]
    es009 = rows[
        f"{_ELABORATE}::_ExactElaborator._resolve_semantic_reference::coded::SI_OCCURRENCE_MISSING::4"
    ]
    assert es002.reason is not None and es009.reason is not None
    assert es002.reason != es009.reason
