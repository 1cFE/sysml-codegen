# Orchestrator brief — design_review stage, CONSTRAINT-SEMANTICS Item 9

Review the design at `.project/active/derivative-upgrade-held-intent/design.md` against the spec
at `.project/active/derivative-upgrade-held-intent/spec.md` (fresh session — you did not write
either). Probe evidence is under the item's `probes/` dir; committed at `2c624cc`.

## Item context, compressed

Item 9 executes already-ruled held intent on `tests/fixtures/catf_mfe_gated`: delete A5/A6
(derive all radii from axis root + 14 thicknesses — basis **[AGENT] ratified by owner
2026-08-13**), assert A9 `ProductWithinBand` at **[OWNER 2026-08-13] 1% relative**, retire
`blocked-by-defect` on the live PROVENANCE only (archive frozen — orchestrator ruling in spec),
restate the identity to 65 = 56 carriers + 9 named deletions. Ruled rows:
`.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` A5/A6/A9.
No re-disposition is authorized anywhere in this item.

## What I most want your judgment on

1. **Ruled-cell fidelity.** Does every design decision trace to a ruled cell, the spec, or a
   recorded orchestrator ruling — and does nothing quietly re-decide owner payload? In
   particular: A9's dimension-specific `ProductWithinBand` def-shape is a NOTED material change
   under the disposition row's own "design notes it" rule — is the note faithful to the row, and
   does the noted shape preserve the ruled semantics (relative form, 1%, band scales under
   resizing)?
2. **The out-of-27 edit.** `tf_coil.thickness`'s trailing comment gains a readable unit because
   the extractor's stop-word list eats `// From line 83`. I ratified this as a mechanical
   consequence in O6's sense (no value, no ruled cell changed; A6's ruled derivation cannot
   build without it). Challenge that reading if you think it is actually a new disposition.
3. **The prover extension** (`check_gated_manifest.py` per-occurrence `DERIVATIONS`): does the
   owning-block anchoring keep BOTH existing failure modes (doc stripped, initializer gone)
   fail-closed per occurrence, for all 30 derivations, with no way for a deleted derivation to
   pass via a sibling's byte-identical initializer?
4. **SC-6 ordering.** Expectations are re-derived from the ruled table and committed BEFORE
   confirmation tests; the design orders snapshot capture/re-seal de-risk FIRST in implement,
   before expectations commit. Is any expectation value in the design actually copied from a run
   rather than derived (the reverse-engineering failure SC-6 exists to stop)? The spec
   pre-committed the headline numbers before the probe ran; the probe then measured the same
   numbers — check the design keeps that derivation-first provenance explicit.
5. **Completeness against spec.** SC-3's two-sided conditional (BACKLOG one-liner), the
   byte-untouched checks (frozen twins + archived item folder), the one-ULP surfaced drift, and
   the unexercised snapshot lane — each present, correctly placed, and none silently resolved.

Verdict + must-fix list (if any), in the pipeline's usual review form. Write the review to
`.project/active/derivative-upgrade-held-intent/design-review.md`. Do not edit the design; do
not commit — the orchestrator routes fixes and commits.
