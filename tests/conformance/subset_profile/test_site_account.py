"""The codegen site account is total over the scan and keeps its own schema (Item 2a E1, D7).

A site added under ``src/sysml_codegen/`` without a row, or a row whose site was removed,
fails here by ID. So does a ``CodeGenerationError`` built without a code (design D15).

agentic-mbse's matrix is not readable from here (spec Boundaries), so a row's ``matrix_row``
is checked by form only, and its ``rule`` against agentic-mbse's packaged rule records.
"""

from __future__ import annotations

import re

from agentic_mbse.sysml.subset_profile import PACKAGED_RULES

from tests.helpers.subset_profile import site_scan
from tests.helpers.subset_profile.site_scan import Disposition, Role

SCAN = site_scan.scan()
ACCOUNT = site_scan.load_account()
_MATRIX_ROW_ID = re.compile(r"[A-Z][A-Z0-9]*(-[A-Z0-9]+)*")


def test_every_scanned_site_has_one_row_and_every_row_a_site():
    assert SCAN.ids() - ACCOUNT.ids() == set(), "sites with no row"
    assert ACCOUNT.ids() - SCAN.ids() == set(), "rows with no site"


def test_every_code_generation_error_carries_a_code():
    assert site_scan.code_generation_errors_without_code() == []


def test_row_columns_agree_with_the_scanned_site():
    sites = SCAN.by_id()
    for row in ACCOUNT.rows:
        site = sites[row.site_id]
        assert (row.file, row.channel, row.code) == (site.file, site.channel, site.code), (
            row.site_id
        )


def test_header_counts_the_rows():
    assert f"sites: {len(ACCOUNT.rows)}" in ACCOUNT.header


def test_matrix_rows_have_the_matrix_id_form():
    for row in ACCOUNT.rows:
        for matrix_row in row.matrix_rows:
            assert _MATRIX_ROW_ID.fullmatch(matrix_row), (row.site_id, matrix_row)


def test_a_rule_is_a_packaged_record_sharing_the_row_s_matrix_row():
    for row in ACCOUNT.rows:
        for rule_id in row.rules:
            record = PACKAGED_RULES.rule(rule_id)
            assert set(record.matrix_rows) & set(row.matrix_rows), (row.site_id, rule_id)


def test_an_in_scope_site_is_a_capability_refusal_or_its_relay():
    for row in ACCOUNT.rows:
        if row.disposition is Disposition.IN_SCOPE:
            assert row.role in {Role.PUBLIC_CAPABILITY, Role.RELAY_PLUMBING}, row.site_id


def test_an_internal_invariant_cites_the_guard_that_keeps_valid_input_away():
    for row in ACCOUNT.rows:
        if row.role is Role.INTERNAL_INVARIANT:
            guard = any(
                ".py:" in e or e.startswith("no caller under src/") for e in row.evidence[1:]
            )
            assert guard, row.site_id
