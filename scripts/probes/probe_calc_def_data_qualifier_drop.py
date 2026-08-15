"""Dry run: what dropping the `_by_id` qualifier would do to `CalculationDefinitionData`.

The fifth of the eight retained 3C duals (Gate 4A row L-034). The note describes it the same
way as the rest — "one behavior under two names" — and prescribes deleting the legacy member
and dropping the qualifier from the survivor. Here the members are dataclass fields:

    legacy (name-keyed)          survivor (UUID-keyed)
    output_expression_asts       output_expression_asts_by_id
    member_expressions           member_expressions_by_id
    all_member_names             all_member_ids
                                 member_names_by_id

Dropping the qualifier leaves the survivor's payload reachable under the legacy name, so the
probe does exactly that: every constructed `CalculationDefinitionData` gets its legacy fields
overwritten with the survivor's values, and the consumers run against it.

    python scripts/probes/probe_calc_def_data_qualifier_drop.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import sysml_codegen.extraction.data_models as data_models  # noqa: E402

RENAMES = {
    "output_expression_asts": "output_expression_asts_by_id",
    "member_expressions": "member_expressions_by_id",
    "all_member_names": "all_member_ids",
}

CONSUMERS = [
    "tests/unit/test_data_models.py",
    "tests/conformance/test_data_models.py",
    "tests/conformance/test_extractor.py",
    "tests/conformance/test_return_style_extraction.py",
    "tests/conformance/test_extraction_snapshots.py",
    "tests/conformance/test_calc_compat_parity.py",
    "tests/conformance/test_compile_calc_def_golden.py",
]

_original_init = data_models.CalculationDefinitionData.__init__


def _renamed_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
    _original_init(self, *args, **kwargs)
    for legacy, survivor in RENAMES.items():
        object.__setattr__(self, legacy, getattr(self, survivor))


data_models.CalculationDefinitionData.__init__ = _renamed_init  # type: ignore[method-assign]

raise SystemExit(pytest.main(["-q", *CONSUMERS, "-p", "no:cacheprovider"]))
