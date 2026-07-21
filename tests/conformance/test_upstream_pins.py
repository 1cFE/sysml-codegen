"""A coordinated upstream bump cannot land without the downstream guard noticing.

DD-A07 / DD-R14. The three version strings this repo pins live in one module
(`sysml_codegen._upstream_pins`); this test compares each against the value actually
imported from `agentic_mbse`. It is the instrument that does not depend on a human
remembering to edit a literal.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.constraint_facts import CONSTRAINT_FACTS_SCHEMA_VERSION
from agentic_mbse.sysml.executable_profile import PROFILE_SEMANTIC_VERSION
from agentic_mbse.sysml.expression_ir import EXPRESSION_IR_SCHEMA_VERSION

from sysml_codegen import _upstream_pins


@pytest.mark.parametrize(
    ("name", "upstream"),
    [
        ("CONSTRAINT_FACTS_SCHEMA_VERSION", CONSTRAINT_FACTS_SCHEMA_VERSION),
        ("EXPRESSION_IR_SCHEMA_VERSION", EXPRESSION_IR_SCHEMA_VERSION),
        ("PROFILE_SEMANTIC_VERSION", PROFILE_SEMANTIC_VERSION),
    ],
)
def test_pin_matches_installed_upstream(name: str, upstream: str) -> None:
    pinned = getattr(_upstream_pins, name)
    assert pinned == upstream, (
        f"{name} moved upstream to {upstream!r} but this repo still pins {pinned!r}. "
        "Review the downstream code against the new upstream shape, then update "
        "sysml_codegen/_upstream_pins.py."
    )


def test_every_pin_is_covered_by_this_test() -> None:
    """A new pin cannot be added without a comparison, which is the whole point."""
    covered = {"CONSTRAINT_FACTS_SCHEMA_VERSION", "EXPRESSION_IR_SCHEMA_VERSION",
               "PROFILE_SEMANTIC_VERSION"}
    assert set(_upstream_pins.__all__) == covered
