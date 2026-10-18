"""The exact agentic-mbse package, API, schema, and profile versions consumed here.

Three version strings used to be hand-copied literals scattered across the
downstream repo. A literal buried in the module it guards is a literal a
coordinated bump can slip past: nothing points at it, so nothing tells you the
set is incomplete.

They live here instead, in one place a reviewer can read in full, and
`tests/conformance/test_upstream_pins.py` compares every entry against the value
actually imported from `agentic_mbse`. So an upstream bump fails loudly in a test
that does not depend on a human remembering to edit a string (DD-R14, DD-A07).

Where each pin is read at runtime, after the Item 7 retirement:

- `EXPRESSION_IR_SCHEMA_VERSION` and `PROFILE_SEMANTIC_VERSION` are the v6
  envelope's authority markers (`snapshot/envelope.py`), and the profile version
  also names the admitting profile in `generation/predicate_compiler.py`.
- `SUBSET_PROFILE_VERSION` is checked when `subset_profile_adapter.py` is imported, which
  nothing on the generate route does in EXEC-SUBSET-CONTRACT Item 2a.
- `CONSTRAINT_FACTS_SCHEMA_VERSION` has **no runtime consumer**. Its guard lived
  in the deleted `snapshot/loader.py`, and the v6 envelope seals no
  `ConstraintFacts`, so nothing downstream can be stale against it. It is kept
  because the constraint facts it names are still read live, and the only thing
  that would notice an upstream bump of them is this file plus its reader,
  `tests/conformance/test_upstream_pins.py`.

Bumping a pin is a deliberate act: it means the downstream code has been reviewed
against the new upstream shape, not merely made to import.

The package, semantic-evidence API and installer API pins are independently checked against the
installed distribution.  The editable path remains a developer convenience; it
does not replace either pin or the immutable artifact evidence.
"""

from __future__ import annotations

#: Published agentic distribution containing the semantic-evidence contract.
AGENTIC_MBSE_PACKAGE_VERSION = "0.1.3"

#: `agentic_mbse.SEMANTIC_EVIDENCE_API_VERSION`.
SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"

#: `agentic_mbse.cli.installation.INSTALLER_API_VERSION`: the installer surface
#: `sysml-codegen install-commands` calls (`cli/install.py`). It is read only inside that
#: subcommand, which refuses to install when the installed agentic-mbse lacks it, so an older
#: agentic-mbse breaks no other command.
INSTALLER_API_VERSION = "installer/v1"

#: `agentic_mbse.sysml.constraint_facts.CONSTRAINT_FACTS_SCHEMA_VERSION`.
#: v1 -> v2 at Item 4: `ExtractionDiagnosticFact` gained a severity field and a
#: closed `kind` vocabulary.
#: v2 -> v3 at CONSTRAINT-SEMANTICS Item 2: the closed severity map gained
#: `vacuous_asserted_gate` at ADVISORY grade. Adding a kind is a semantic change to
#: snapshots already on disk, so it costs a schema bump
#: (`docs/architecture/reference/30-diagnostic-severity.md`).
CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v3"

#: `agentic_mbse.sysml.expression_ir.EXPRESSION_IR_SCHEMA_VERSION`.
EXPRESSION_IR_SCHEMA_VERSION = "expression-ir/v1"

#: `agentic_mbse.sysml.executable_profile.PROFILE_SEMANTIC_VERSION`.
PROFILE_SEMANTIC_VERSION = "executable-profile/v4"

#: `agentic_mbse.sysml.subset_profile.SUBSET_PROFILE_VERSION`: the subset screen's decision
#: version, which `subset_profile_adapter.REASON_MAPPING` was reviewed against. It names the
#: contract; the agentic-mbse package version does not (EXEC-SUBSET-CONTRACT Item 2a D12). The
#: adapter refuses to import against any other value.
SUBSET_PROFILE_VERSION = "subset-profile/v1"

__all__ = [
    "AGENTIC_MBSE_PACKAGE_VERSION",
    "CONSTRAINT_FACTS_SCHEMA_VERSION",
    "EXPRESSION_IR_SCHEMA_VERSION",
    "INSTALLER_API_VERSION",
    "PROFILE_SEMANTIC_VERSION",
    "SEMANTIC_EVIDENCE_API_VERSION",
    "SUBSET_PROFILE_VERSION",
]
