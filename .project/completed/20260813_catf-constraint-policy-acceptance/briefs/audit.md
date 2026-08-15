# Orchestration brief — audit stage — CONSTRAINT-SEMANTICS Item 5

Audit the implemented item at `.project/active/catf-constraint-policy-acceptance/` (spec SC-1..SC-8,
plan phases 0–7 all checked, verification.md). You are a fresh, skeptical auditor: reproduce
claims, do not take the implementer's word. The item claims complete; your job is to certify,
certify-with-residuals, or find what's wrong.

## What was built (claims to verify, not trust)

- `tests/fixtures/catf_mfe_gated/` — derivative of `catf_mfe_d5` under the RULED
  `owner-disposition.md`: 47 modules, 58 usage rows, 2 concrete entries, histogram
  `{eligible 2, excluded 3, non_reaching 53}`, coverage `58/2/2/0/0/{}/complete`.
- Accounting identity `65 = 58 carriers + 7 named deletions`, proved by
  `scripts/check_gated_manifest.py --check` (56 by name, 2 by `renamed_from:`).
- SC-6 commit-order proof: expectations at `1247a3b`, fixture at `7369b3e`, strictly parent→child,
  with a deliberate named red window between them; the 6-D amendment commit `e01c3b4` stands alone.
- SC-8: new committed-bytes golden for `constraint_domain_satisfy_calc_def` + regenerate-and-diff
  test, falsified once deliberately (recorded).
- SC-5 through real TEAx (`constraint-semantics-item3` @ `5b70ae9`): authored candidate →
  `reject` (gate-infeasible under the model as authored — finding 6-D, owner-ruled labeling),
  raised-p_fusion exemplar → `feed-strategy`; both persist verdict AND coverage in durable case
  records; three routes gated (licensed live, in-place snapshot, relocated snapshot).
- Final gates claimed: licensed suite 2103/34 zero license-skip; ruff 12; mypy 55;
  `git diff --check` clean; `make_d5_variant.py --check` passes; frozen twins byte-untouched
  except d5's PROVENANCE paragraph.

## Audit emphases (beyond your standard sweep)

1. **Provenance fidelity across the ruling chain.** The table was ruled, then amended twice
   (D-S1/D-S2; B1–B5 recording mechanism, orchestrator-applied; 6-D labeling). Check the grades
   are carried exactly (what is [OWNER] vs [AGENT] ratified vs orchestrator-applied-flagged) and
   nothing got promoted.
2. **SC-6's ordering is real:** verify the commit graph yourself; confirm no expectation file was
   edited after the fixture landed except the standalone 6-D amendment, and that the amendment's
   basis is the source-derived Carnot computation (`cryo_derivation.py` — run it; it claims to be
   self-checking and to reproduce 8396.054399837172 bit-exactly).
3. **The reject leg is the real route:** re-run or re-verify the TEAx evidence — policy `reject`
   at the authored point, coverage identical on both candidates' case records.
4. **Frozen twins:** byte-verify against git history that only d5's PROVENANCE paragraph changed.
5. **The three falsifications** (manifest) + SC-8's golden falsification: confirm they were run
   for real (recorded red output), not narrated.
6. **Deviations ledger honesty:** group 4b, 47-vs-48 modules, 43-vs-42, the `//`-comment
   decision, the A2 `value`→`quantity` rename under O7, the D6 mutation-route substitution
   (typed entry injection). Each should be recorded with reasoning where a reader will find it.

## Hazards — do not touch

- `.project/CURRENT_WORK.md` is modified by a PARALLEL actor (Item 6 work) — read-only for you.
- `.project/active/calcdef-constraint-gate-design/` (untracked) is parallel Item 6 work — do not
  read into your audit scope, do not stage, do not clean.
- The P1 backlog entry `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` was owner-directed from a parallel
  session and then consolidated/corrected by this item's implementer — verify the consolidation
  preserved the owner's priority and rationale, but do not restructure it.
- TEAx checkout stays on `constraint-semantics-item3` @ `5b70ae9`.

## Environment

- `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`; licensed via
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero `no live syside license` skip
  lines is the only licensed proof. Known pre-existing: the real_simkit collection-order failure
  (CURRENT_WORK.md:468-472) is out of the floor.

Write `audit.md` in the item home with verdict (Certify / Certify-with-residuals / Needs work),
findings by ID, and the probe record. End with `ARTIFACT: <path>`.
