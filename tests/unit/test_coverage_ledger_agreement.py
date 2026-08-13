"""The first proof point: the derivation agrees with what the fixtures' authors wrote.

Every expected account here comes from `expected-coverage.md`, whose entries were derived from
each fixture's `.sysml` source against D3's bucket table and committed **before** this file
existed. That ordering is the whole mitigation for bet B1 (Item 2's `usage_records` is a
complete and correct enumeration): an expectation transcribed from a catalog dump or a
generated report would inherit exactly the error B1 names and would falsify nothing.

A mismatch here is triaged three ways before anything else moves — the fixture is wrong, the
ledger is wrong, or B1 is false. The third stops the item.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sysml_codegen.elaboration import project
from sysml_codegen.generation.coverage import coverage_account
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license

#: The ledger's durable home ([OWNER 2026-08-13], Item 4 audit F5): it lives beside the test
#: that reads it, so suite collection never depends on `.project/` archive layout (that broke
#: once, when Item 3's archival moved the file out from under the old hardcoded path). A
#: pointer stub remains at the archived location.
LEDGER_FILE = Path(__file__).resolve().parent / "data" / "expected-coverage.md"


def _parse_histogram(text: str) -> dict[str, int]:
    return {
        token: int(count)
        for token, count in re.findall(r"(\w+)\s*:\s*(\d+)", text)
    }


def _load_ledger() -> list[tuple]:
    """Read the ledger index block out of `expected-coverage.md`.

    Parsed rather than transcribed so the artifact the owner reviews and the table the test
    asserts cannot drift apart. A malformed or missing block fails loudly here.
    """
    body = LEDGER_FILE.read_text()
    block = re.search(r"```ledger\n(.*?)```", body, re.DOTALL)
    assert block, f"no ```ledger``` block in {LEDGER_FILE}"
    rows = []
    for line in block.group(1).strip().splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        assert len(cells) == 10, f"malformed ledger line: {line!r}"
        fixture, authored, applicable, assessed, unassessed, inapplicable = cells[:6]
        histogram, state, headline, entries = cells[6:]
        rows.append(
            (
                fixture,
                {
                    "authored_usage_total": int(authored),
                    "applicable_gate_total": int(applicable),
                    "assessed_gate_count": int(assessed),
                    "unassessed_gate_count": int(unassessed),
                    "inapplicable_gate_count": int(inapplicable),
                    "unassessed_reasons": _parse_histogram(histogram),
                    "coverage_state": state,
                },
                headline,
                int(entries),
            )
        )
    return rows


LEDGER = _load_ledger()


def test_the_ledger_covers_every_shape_the_matrix_needs():
    """A ledger that quietly lost a state would let a state go unproven."""
    states = {row[1]["coverage_state"] for row in LEDGER}
    headlines = {row[2] for row in LEDGER}
    assert states == {"complete", "partial", "none"}
    assert headlines == {"full_satisfaction", "partial_coverage", "not_assessed", "violation"}


@pytest.mark.parametrize(
    "fixture,expected,_headline,_entries", LEDGER, ids=[row[0] for row in LEDGER]
)
@requires_license
def test_derived_account_equals_the_hand_written_account(
    fixture: str, expected: dict, _headline: str, _entries: int
):
    catalog = project(
        elaborate_model_paths([Path(FIXTURES_DIR / fixture)])
    ).constraint_catalog
    assert catalog is not None, f"{fixture} projects no catalog"
    assert coverage_account(catalog).as_mapping() == expected
