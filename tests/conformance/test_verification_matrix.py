"""The current matrix recount and authority/citation guards reject real drift."""

import re

from scripts.check_verification_matrix import MATRIX, check, recount


def test_matrix_counts_citations_and_authority_grades_agree() -> None:
    text = MATRIX.read_text()
    errors, families, cited = check(text)
    assert errors == []
    assert text == recount(text, families, cited)


def test_matrix_guard_rejects_count_node_and_authority_drift() -> None:
    text = MATRIX.read_text()
    changed = re.sub(r"(\| Total requirements \| )\d+", r"\g<1>999", text, count=1)
    _, families, cited = check(changed)
    assert changed != recount(changed, families, cited)

    changed = text.replace("::test_baseline_inventory_is_complete", "::test_missing_oracle_node", 1)
    errors, _, _ = check(changed)
    assert any("missing test node" in error for error in errors)

    changed = text.replace("| REQ-SI-01 | [NEED]", "| REQ-SI-01 | [INFERRED]", 1)
    errors, _, _ = check(changed)
    assert any("authority grades" in error for error in errors)
