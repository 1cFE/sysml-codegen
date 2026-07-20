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
- **Leaf-name guess** — a model-derived value resolved through a name-based lenient row
  (``leaf_unique`` / ``bare_name_unique`` / ``dotted_pair``) rather than exact identity.
  These resolve a design attribute by matching its bare name, not its qualified name;
  invariant 26 names "leaf-name guess" as non-conformant.

What it does NOT flag — the exemptions:

- A clean ``ENTRY_POINT`` with no ties and no name-based key form is a **legitimate
  external typed design input** (a formal the model declares as an input with no producer).
  It is exempt by declaration, not by leniency — external inputs stay ordinary typed entry
  channels (invariant 26; owner decision D-1).
- ``MODULE_OUTPUT`` and exact-QN ``DESIGN_ATTRIBUTE`` (rows ``occurrence_materialized_qn``
  / ``target_qn`` / ``owner_def_qn``) are exact-identity resolutions — the conformant path.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sysml_codegen.resolution.producer_resolution import (
    CapturedResolution,
    Outcome,
)

__all__ = [
    "CompletenessViolation",
    "CompletenessViolationKind",
    "NAME_BASED_KEY_FORMS",
    "check_producer_completeness",
]

# The tier-2 name-based lenient rows (KEY_FORMS rows 19-21). Resolving a model-derived
# value through one of these is a leaf-name match, not exact-QN identity.
NAME_BASED_KEY_FORMS: frozenset[str] = frozenset(
    {"dotted_pair", "leaf_unique", "bare_name_unique"}
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

        # Leaf-name guess: resolved via a name-based lenient row rather than exact identity.
        if res.outcome is Outcome.DESIGN_ATTRIBUTE and res.key_form in NAME_BASED_KEY_FORMS:
            violations.append(
                CompletenessViolation(
                    kind=CompletenessViolationKind.LEAF_NAME_GUESS,
                    consumer_eqn=req.consumer_eqn,
                    reference=req.reference,
                    detail=(
                        f"resolved by name match ({res.key_form}) to {res.identity}, "
                        "not under exact qualified identity"
                    ),
                )
            )

        # Clean ENTRY_POINT (no ties, no name-based form) = legitimate external declared
        # input — exempt. MODULE_OUTPUT / exact-QN DESIGN_ATTRIBUTE = conformant — exempt.

    return violations
