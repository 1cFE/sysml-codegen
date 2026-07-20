"""The exact agentic-mbse schema and profile versions this repo is written against.

Three version strings used to be hand-copied literals scattered across the
downstream repo — two `RuntimeError` guards in `snapshot/loader.py` and one in
`analysis/constraint_lowering.py`. Each guard is real and load-bearing, but a
literal buried in the module it guards is a literal a coordinated bump can slip
past: nothing points at it, so nothing tells you the set is incomplete.

They live here instead, in one place a reviewer can read in full, and
`tests/conformance/test_upstream_pins.py` compares every entry against the value
actually imported from `agentic_mbse`. So an upstream bump fails loudly in a test
that does not depend on a human remembering to edit a string (DD-R14, DD-A07).

Bumping a pin is a deliberate act: it means the downstream code has been reviewed
against the new upstream shape, not merely made to import.

Rejected: making the `agentic-mbse>=0.1.2` package floor real. The editable path
override in `pyproject.toml` always wins in development, so the floor can never be
the guard (design D9).
"""

from __future__ import annotations

#: `agentic_mbse.sysml.constraint_facts.CONSTRAINT_FACTS_SCHEMA_VERSION`.
#: v1 -> v2 at Item 4: `ExtractionDiagnosticFact` gained a severity field and a
#: closed `kind` vocabulary.
CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v2"

#: `agentic_mbse.sysml.expression_ir.EXPRESSION_IR_SCHEMA_VERSION`.
EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"

#: `agentic_mbse.sysml.executable_profile.PROFILE_SEMANTIC_VERSION`.
PROFILE_SEMANTIC_VERSION = "executable-profile/v4"

__all__ = [
    "CONSTRAINT_FACTS_SCHEMA_VERSION",
    "EXPRESSION_IR_SCHEMA_VERSION",
    "PROFILE_SEMANTIC_VERSION",
]
