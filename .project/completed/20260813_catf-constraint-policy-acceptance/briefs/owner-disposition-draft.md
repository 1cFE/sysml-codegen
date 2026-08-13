# Orchestration brief — all-65 proposal table draft — CONSTRAINT-SEMANTICS Item 5

Draft `.project/active/catf-constraint-policy-acceptance/owner-disposition.md` — the proposal
form of the all-65 CATF disposition table. It goes to the owner for a check-in; nothing in it is
settled until they rule. This is a drafting task, not design: no fixture edits, no code.

## Ground rules (from the item spec — read it first:
`.project/active/catf-constraint-policy-acceptance/spec.md`)

1. **Every disposition is `PROPOSED [AGENT]`.** The header must say the table is a draft and the
   owner's sign-off converts it, row by row, into the authority.
2. **Never write a tolerance number.** Every tolerance cell is `TBD-OWNER [<unit>]` with the unit
   you believe correct. You may add a one-line rationale for what the band protects, never a
   value.
3. **Unit-check column.** The profile does not check units on bindings (spec, Problem limit 1).
   Every band/comparison row carries the expected dimension and unit; the header states that this
   column is human-verified (owner at check-in, design review later), not toolchain-verified.
4. **The 51 calc-def guards may only be `derive-instead` or `awaits-capability`** (spec item5-F2:
   an asserted calc-def guard halts the whole model). No third option may appear.
5. **Intent classes** come from the four-way equality taxonomy (spec, Known Requirements):
   (1) structural identity → derive; (2) cross-check → loose band; (3) feasibility → one-sided,
   fixed value → input; (4) closure → derive by construction, else band.
6. **item5-F1 accounting.** Any `derive-instead` proposal deletes an authored usage from the
   derivative. Close the table with an explicit account: how many usages survive under your
   proposals (65 − derived-away), what the derivative's carrier count would be, and how
   PROVENANCE would reconcile it. Do NOT steer proposals to preserve 65 — classify honestly and
   report the consequence. The owner rules on SC-3 at the check-in.
7. **SC-5 viability check.** Name which proposed asserted gates are executable candidates for the
   valid-candidate + unphysical-mutation proof. If your honest classification leaves zero or one,
   say so loudly (research §3 suggests `ViabilityCheck` may be the only clear one-sided gate).
8. **Self-named bindings:** if any proposed bindings-only rewrite would need `in x = x;`, propose
   the renamed-formal fix; if that cannot work for a row, mark the row `SURFACED` instead of
   proposing.

## Sources (read all)

- `tests/expectations/constraint_population/catf_mfe_d5.json` — the machine census: 65 rows with
  `usage_qualified_name`, `source_file`, `source_line`. Your table must join to it 1:1 — same
  count, no invented rows. Cite each usage by qualified name + file:line.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §3 (the nine-constraint
  table — predicates, current forms, blocking chains) and §§5–7 as needed.
- The actual `.sysml` sources under `tests/fixtures/catf_mfe_d5/` (designs/ + library/) — verify
  each of the nine reaching predicates against source; do not trust the research doc's
  transcription blindly.
- `/home/reid/1cfe/agentic-mbse-item7-rebuild/docs/patterns/constraints.md` — the rendered
  taxonomy and blessed bindings-only pattern.
- `docs/architecture/modeling-assumptions.md` §8 — the one supported unit-carrying spelling.

## Structure of the artifact

- Header: status DRAFT / PROPOSED [AGENT]; what the owner is being asked to decide; the
  unit-check disclaimer; the item5-F1 account pointer.
- **Group A — 9 instance-reaching gates** (one row each): qualified name, file:line, current
  predicate (verbatim from source), proposed intent class with one-line reasoning, proposed
  target form (derive / one-sided assert / band assert, with the concrete constraint-def shape),
  tolerance `TBD-OWNER [unit]` where applicable, unit-check cell, surviving-in-derivative yes/no.
- **Group B — 5 part-def guards** (one row each): proposed typed attachment (name the design part
  you would type, verified against source) or explicit inapplicability, with reasoning. Note the
  L2-2 consequence: an attached-but-vacuous asserted gate holds partial coverage.
- **Group C — 51 calc-def guards**: one row each (grouping by calc def for presentation is fine,
  but all 51 rows must be individually present and joinable to the census). Proposal per row:
  `derive-instead` (say what derivation replaces it) or `awaits-capability`.
- Closing sections: item5-F1 account; SC-5 executable-gate candidates; open points for the owner
  beyond tolerances (anything your classification could not settle).

Work from the census file as the row authority. If your row count disagrees with 65 at any
point, stop and reconcile before writing. End your final message with a 10-line summary of the
proposal profile (counts per disposition kind, F1 account headline, SC-5 candidates) — the
orchestrator relays it to the owner.
