"""Producer completeness — every model-derived consumed value has one intended producer.

Item 10 / ratified invariant 26. This check is **separate from and additive to** V11
coverage (``collect_uncovered_params``). V11 proves that no wired input references a
valueless fell-through key — a load-time ``KeyError`` guard. It is *not* producer
completeness: a defaulted fallback or an ambiguous first-match binding can pass V11 while
feeding the wrong value. This check closes that gap by reading the resolver's own recorded
outcomes (the capture sink, ``producer_resolution.capturing_resolutions``) — it does not
re-resolve.

What it flags, from ``ProducerResolution.{outcome, key_form, ambiguous_candidates}``:

- **Ambiguous producer** — a resolution that saw a same-leaf tie
  (``ambiguous_candidates`` non-empty). The resolver refused to guess (``_unique_or_tie``)
  and fell through to a synthesized entry point carrying the tied QNs; producing a verdict
  from either candidate would be a guess. This is the ambiguous/defaulted acceptance
  coordinate (contract acceptance row "Ambiguous/defaulted producer resolution").
- **Leaf-name guess** — a QUALIFIED reference (``part.attr``) resolved through a name-based
  lenient row that dropped its scope qualifier. This spans BOTH the tier-2 design-attribute
  rows (``leaf_unique`` / ``dotted_pair`` / ``bare_name_unique``) AND the tier-1 CHANNEL rows
  (``leaf_parent_scoped`` / ``leaf_consumer_scoped``) — the latter yield a ``MODULE_OUTPUT``
  and were uncaught before audit Major 1 closed the MODULE_OUTPUT exemption. Same defect
  regardless of outcome; invariant 26 names "leaf-name guess" as non-conformant.

What it does NOT flag — the exemptions:

- A clean ``ENTRY_POINT`` with no ties and no name-based key form is a **legitimate
  external typed design input** (a formal the model declares as an input with no producer).
  It is exempt by declaration, not by leniency — external inputs stay ordinary typed entry
  channels (invariant 26; owner decision D-1).
- A ``MODULE_OUTPUT`` or exact-QN ``DESIGN_ATTRIBUTE`` resolved through an EXACT or STRUCTURAL
  row (scoped channels, ``occurrence_materialized_qn`` / ``target_qn`` / ``owner_def_qn``,
  ``chain_redefinition_follow``) consults the reference's own owner — the conformant path.
  Only the name-based rows above, on a qualified reference, are non-conformant.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sysml_codegen.resolution.producer_resolution import (
    CapturedResolution,
)

__all__ = [
    "CompletenessViolation",
    "CompletenessViolationKind",
    "NAME_BASED_KEY_FORMS",
    "check_producer_completeness",
]

# The name-based lenient rows that identify a producer by leaf/bare name rather than by
# exact-QN or structural identity. Two tiers:
#   - tier-2 DESIGN_ATTRIBUTE rows 19-21: dotted_pair / leaf_unique / bare_name_unique
#   - tier-1 CHANNEL rows 14-15: leaf_parent_scoped / leaf_consumer_scoped — these recombine
#     the leaf with the CONSUMER's parent/scope and NEVER consult the reference's own owner,
#     so `PartA::x` and `PartB::x` construct the same channel key (their own docstrings say so).
# Resolving a QUALIFIED term through any of these drops its scope qualifier — the same
# producer-completeness defect whether it lands on a design attribute or a module_output
# channel (audit Major 1: the MODULE_OUTPUT exemption left rows 14-15 uncaught).
# `chain_redefinition_follow` (row 13) is EXCLUDED — it follows `:>>` redefinitions to a
# constructed channel structurally, keyed on the reference's own owner, and refuses ties.
NAME_BASED_KEY_FORMS: frozenset[str] = frozenset(
    {
        "dotted_pair",
        "leaf_unique",
        "bare_name_unique",
        "leaf_parent_scoped",
        "leaf_consumer_scoped",
    }
)


class CompletenessViolationKind(str, Enum):
    """Why a captured resolution fails producer completeness."""

    AMBIGUOUS_PRODUCER = "ambiguous_producer"
    LEAF_NAME_GUESS = "leaf_name_guess"


@dataclass(frozen=True)
class CompletenessViolation:
    """One consumed value that did not resolve to a single intended producer."""

    kind: CompletenessViolationKind
    consumer_eqn: str
    reference: str
    detail: str

    def message(self) -> str:
        return (
            f"{self.consumer_eqn} consumes '{self.reference}': "
            f"{self.kind.value} — {self.detail}"
        )


def check_producer_completeness(
    captured: list[CapturedResolution],
) -> list[CompletenessViolation]:
    """Return every producer-completeness violation among captured resolutions.

    Reads the resolver's recorded outcomes; performs no resolution. An empty return means
    every model-derived consumed value resolved to exactly one intended producer under
    exact identity, and every entry point is a legitimate external declared input.
    """
    violations: list[CompletenessViolation] = []
    for cap in captured:
        res = cap.resolution
        req = cap.request

        # Ambiguous producer: a same-leaf tie was seen. The resolver refused to pick, so
        # the outcome is an entry point carrying the tied candidates. This holds whichever
        # terminal outcome the row landed on, so read ambiguous_candidates directly.
        if res.ambiguous_candidates:
            violations.append(
                CompletenessViolation(
                    kind=CompletenessViolationKind.AMBIGUOUS_PRODUCER,
                    consumer_eqn=req.consumer_eqn,
                    reference=req.reference,
                    detail=(
                        "two or more same-leaf candidates; no exact-QN discriminator "
                        f"({', '.join(res.ambiguous_candidates)})"
                    ),
                )
            )
            continue

        # Leaf-name guess: a QUALIFIED reference (``part_usage.attr``) that resolved via a
        # name-based lenient row by DROPPING its qualifier and matching the bare leaf. This
        # is the scope-collapse defect — e.g. every ``X.capital_cost`` term collapsing to a
        # single producer regardless of ``X``. It is the SAME violation whether the row
        # landed on a design attribute (rows 19-21, ``DESIGN_ATTRIBUTE``) OR a module_output
        # channel (rows 14-15, ``MODULE_OUTPUT`` — audit Major 1: these were uncaught because
        # all module outputs were exempt). Keyed on ``key_form`` membership, not outcome. A
        # BARE reference (no ``.``) matched by ``bare_name_unique`` is NOT flagged: with no
        # qualifier to drop and a unique surviving candidate, that is the intended producer
        # resolved by its only handle (``agg_localterm_probe``'s bare ``markup``). Exact and
        # structural rows (scoped channels, exact-QN attrs, ``chain_redefinition_follow``)
        # remain exempt — they consult the reference's own owner.
        if res.key_form in NAME_BASED_KEY_FORMS and "." in req.reference:
            violations.append(
                CompletenessViolation(
                    kind=CompletenessViolationKind.LEAF_NAME_GUESS,
                    consumer_eqn=req.consumer_eqn,
                    reference=req.reference,
                    detail=(
                        f"qualified reference resolved by name match ({res.key_form}, "
                        f"{res.outcome.value}) to {res.identity}, dropping its scope "
                        "qualifier — not exact or structural identity"
                    ),
                )
            )

        # Clean ENTRY_POINT (no ties, no name-based form) = legitimate external declared
        # input — exempt. MODULE_OUTPUT / exact-QN DESIGN_ATTRIBUTE = conformant — exempt.

    return violations
