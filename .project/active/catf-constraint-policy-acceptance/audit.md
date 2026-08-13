# Audit: CATF Derivative and End-to-End Acceptance (CONSTRAINT-SEMANTICS Item 5)

**Verdict:** Needs work — narrow, three defects, everything else certified
**Audited:** 2026-08-13
**Branch:** `item7-rebuild`
**Commit:** `7c076b6`
**Auditor:** fresh session; every claim below was reproduced, not read

---

## The Point

A design search has to be able to trust generated feasibility evidence. That means two things at
once: every applicable asserted physics gate is represented in the evidence, and every other
authored constraint is visibly dispositioned rather than silently absent. `catf_mfe_d5` is the
counter-example the epic exists to close — it carries 65 authored constraint checks and executes
**zero** of them, so it reports `not_assessed` and nothing in it ever contradicts the design
point. Items 1–4 built the contract against purpose-built fixtures. This item is the first time
the contract runs end to end on the richest model in the tree, and the first time a candidate is
either accepted or rejected on executed physics.

A third obligation sits underneath both: **every disposition the item claims must be carried by
the artifact it claims carries it**, not only by the item's own records. The derivative's
PROVENANCE is that artifact — it is what a later reader and the accounting check both trust.

## Summary

The engineering is strong and, in the main, honestly recorded. Every number I re-measured matched:
47 modules, 58 usage rows, 2 concrete entries, `{eligible 2, excluded 3, non_reaching 53}`,
coverage `58 / 2 / 2 / 0 / 0 / {} / complete`, the licensed suite at 2103/34 with zero license-skip
lines, ruff 12, mypy 55. The commit-order argument for SC-6 holds. All four falsifications — three
on the manifest check, one on the SC-8 golden — reproduce for real, with the recorded red output.
The acceptance run re-executes and the authored design point reaches `reject` through the real
TEAx route.

What is wrong is confined to the derivative's PROVENANCE, and it is the same defect twice: the
file states, as fact, two things about the shipped source bytes that the source does not carry.
One of them is an `[OWNER]`-graded structural obligation (finding **A-1**); the other is a rename
the item made for good reason and then did not record where the reader will look (finding **A-2**).
Both are cheap to fix. Neither is a numbers problem — every count in the item survives them
untouched. But SC-2's whole claim is "every derivative change is accounted for", and A-2 is a
derivative change that PROVENANCE misstates rather than accounts for.

## Product Judgment

**Is this the right piece of work?** Yes, emphatically. The item did the thing the epic was
created to do, and it did it the hard way: the first execution of these gates rejected the model's
**own authored design point** on physics, and the item stopped, surfaced it, took a ruling, and
recorded the defect (`[CATF-CRYO-HEAT-LEAK-COEFFICIENT]`, P1) rather than tuning the fixture until
the expected answer came out. That is the founding failure mode demonstrated and closed by the same
item. The 6-D handling is the best thing in the record.

**Product-lens ledger gate: BLOCKED (audit-F1).** Ledger scanned in full (`product-lens.md`, four
runs). The spec-stage `BLOCK` on item5-F1 is resolved by citation — SC-3 was amended by owner
ruling on 2026-08-13 and the amendment is recorded at `spec.md:93-108` per capture-fidelity §3.
The design-stage gate is PROCEED. The audit-stage run blocks on audit-F1, which I re-verified
myself rather than inheriting (§Probe record, P-7).

**Smells fired.**

- **Smell 3 — a special category exempts a case whose user-visible meaning is unchanged.**
  `blocked-by-defect` moves A5/A6/A9 out of the feasibility denominator while what the modeler
  wrote — a physics gate — is unchanged, and nothing in the generated evidence distinguishes them
  from the 48 `awaits-capability` guards. **Resolved here:** this is the D-S1/D-S2 ruling
  (`[AGENT]`, ratified by owner 2026-08-13) working as ruled, not a drift; the derivative's
  manifest states the limitation in its own words, and the follow-on obligation is filed as epic
  Item 9. It does not control the verdict.
- **Smell 1 — two representations manually kept synchronized.** The SC-8 golden reconstructs the
  generation sequence from seven private `_generate_*` seams instead of driving `run_codegen`
  (finding **A-4**). **Not resolved**; recorded as a residual with a named disposition. It does not
  control the verdict on its own — the gate it builds is real and I falsified it successfully —
  but it means the tree's first committed-bytes gate pins a route that is not the shipping route.

**What controls the verdict** is audit-F1 / finding **A-1**: an owner-graded structural obligation
that the shipped artifact asserts is met and is not. That is Needs Work, not a nitpick, because the
artifact making the false claim is the same artifact the accounting check and every later reader
treat as ground truth.

## Findings

### A-1 — [OWNER] derivation documentation obligation unmet in source, and PROVENANCE says otherwise — **BLOCKING**

`owner-disposition.md:37-41`, a structural amendment graded **[OWNER 2026-08-13]**:

> each of the seven derivations carries a doc comment recording the undirected relation and stating
> that the direction is a **chosen basis, not physics** — and the PROVENANCE deletion record
> repeats it. The relation intent must survive the deletion.

Three derivations were authored (A1 and A4 have none, correctly — PROVENANCE says so). Only one
carries the statements:

- ✅ C37 — `tests/fixtures/catf_mfe_gated/library/physics/power_balance.sysml:66-70`
- ❌ A7 — `tests/fixtures/catf_mfe_gated/designs/catf_mfe/shield.sysml:105`, bare:
  `attribute fraction_volume : Real = 1.0 - neutron_shield.fraction_volume;`
- ❌ A8 — `tests/fixtures/catf_mfe_gated/designs/catf_mfe/vacuum.sysml:53`, bare:
  `attribute outer_radius : Real = inner_radius + wall_thickness;`

`tests/fixtures/catf_mfe_gated/PROVENANCE.md` §2 states the opposite twice — "Those statements are
carried in source beside each derivation and repeated below", and, in the recorded `//`-vs-`doc`
deviation, "The verbatim relation and chosen-basis statements are mandatory either way and appear
in both places." The deviation the item recorded is about the *comment form*; the actual gap is
that two of the three comments **do not exist**.

The obligation is not decorative. Its stated purpose is that the relation intent survives the
deletion **in the model** — a reader of `shield.sysml` should be able to see that
`neutron + gamma = 1.0` is the relation and that deriving gamma is a chosen basis. Right now that
survives only in a sidecar document.

**What should change:** author the two missing `//` comment blocks at `shield.sysml:105` and
`vacuum.sysml:53`, matching C37's form, and re-run the fixture's snapshot capture if the bytes
move. Do not weaken the PROVENANCE claim to match the source — the owner ruled the obligation, not
the record of it.

### A-2 — the `value` → `quantity` rename is not accounted for in PROVENANCE — **BLOCKING (SC-2)**

Finding 6-B renamed `PositiveQuantity`'s formal from `value` to `quantity` because `value` is a
reserved generated local (`generation/constraint_name_safety.py:39`). The rename itself is sound
and authorized — open point **O7** records the library's names as provisional and design-owned.

The shipped source is `quantity`:

- `tests/fixtures/catf_mfe_gated/library/constraints/gate_forms.sysml:13` — `in quantity : Real;`
- `tests/fixtures/catf_mfe_gated/designs/catf_mfe/physics.sysml:131` — `in quantity = p_electric_net_out;`

The shipped PROVENANCE says `value`, in four places, and the word `quantity` never appears in it as
a formal name:

- `PROVENANCE.md:42` — quotes the authored form verbatim as
  `assert constraint net_power_viable : PositiveQuantity { in value = p_electric_net_out; }`. This
  is presented as the source and is not the source.
- `PROVENANCE.md:84` — argues the no-bare-self-named-binding property using `value`.
- `PROVENANCE.md:330, 334-335` — the **unit-check** record: "`value` ← `p_electric_net_out`, a
  power in MW … what the human is on the hook for: that `value` is bound to a power." This is the
  human-owned obligation the toolchain explicitly cannot check, hung on a formal that does not
  exist in the fixture.

`owner-disposition.md:99` (the ruled A2 cell) also still spells the definition
`constraint def PositiveQuantity { in value : Real; value > 0 }` with no amendment note or pointer
to 6-B, so a reader arriving at the ruled table has no route to the rename either.

SC-2 says "The derivative's PROVENANCE and a machine-checkable diff account for every change from
`catf_mfe_d5`, with a reason per change." This change is not accounted for; it is misstated. The
rename is recorded only in `verification.md` §6-B, an item-home artifact that will be archived.

**What should change:** correct the four PROVENANCE lines to the shipped spelling and add one
per-change record for the rename citing O7 and finding 6-B; add a one-line amendment note at
`owner-disposition.md:99` pointing at it (an amendment to an agent-provisional name under O7, not a
re-disposition — no ruled content moves).

### A-3 — nothing ties a `derive-instead` deletion to the derivation that replaces it

`scripts/check_gated_manifest.py` is a good check and I falsified it three ways successfully. But
it joins four sources (`catf_mfe_d5.json`, `catf_mfe_gated.json`, `PROVENANCE.md`,
`gated_manifest/catf_mfe_gated.json`) and **never opens a `.sysml`** — see the module docstring at
`scripts/check_gated_manifest.py:9-16` and `run()` at `:145-202`. A deletion record is accepted on
the strength of citing an authorizing row. Whether the derivation the record promises actually
exists in source, and whether it carries its relation statement, is unchecked.

This is precisely why A-1 landed green through Phases 3 through 7. `modeling-assumptions.md` §8's
own standard is that the domain's completeness is proved by evidence from outside the domain; the
deletion side of the identity is owed the same standard.

**What should change:** extend the check so each `derive-instead` record asserts the named
derivation exists in the derivative source and carries its relation + chosen-basis statement.
Not a fix to draft here, but it is the check that would have caught A-1 at Phase 4.

### A-4 — the SC-8 golden does not run the shipping generation route

`tests/conformance/test_zero_entry_package_golden.py:69-87` builds the package by calling seven
private seams directly (`_generate_schemas`, `_generate_modules`, `_generate_stencils`,
`_generate_pipeline`, `_generate_registry`, `_generate_entry_points`, plus
`build_constraint_generation_plan`). `run_codegen` (`src/sysml_codegen/cli/__init__.py:1204-1299`)
runs a preflight block and three further generation steps this sequence omits.

CLAUDE.md states `run_codegen` "is the single public generation entry point and constructs exactly
one way." The tree's first committed-bytes gate therefore pins a hand-maintained parallel route: if
`run_codegen` stopped emitting `schemas/constraint_types.py` for this shape, or a preflight began
refusing it, the golden would stay green.

The gate is nonetheless real — I reproduced its falsification (§Probe record, P-6). This is a
residual on how the gate is wired, not on whether it works.

**What should change:** drive the golden through `run_codegen`, or record in the test's docstring
why the private seams are deliberately the subject.

### A-5 — SC-5's rejection lane has no committed test

`grep -rn catf_mfe_gated tests/ --include=*.py` returns one hit
(`tests/conformance/test_gated_manifest_identity.py:3`, a docstring). The coverage half of the
point *is* durably gated — the population oracle picks the fixture directory up by scan, and
`tests/unit/data/expected-coverage.md` drives `tests/unit/test_coverage_ledger_agreement.py`. The
feasibility half — satisfied path, `reject` through TEAx normalization, policy, durable case
storage — lives only in `probes/acceptance_run.py`, which is in the item home and will be archived
with it.

That is a defensible scope call (the lane needs a licensed environment and the TEAx checkout), but
it is not recorded as one. **What should change:** state in `verification.md` that the TEAx lane is
intentionally manual and name what re-runs it, or file the lane as an `execution`-marked test.

### A-6 — verification.md's SC-6 section names one post-fixture expectation edit; there are two

`verification.md:685-691` says "The one later amendment (`e01c3b4`, the 6-D headline cell) is a
separate, named commit". `git log` shows a second: `3a85d77` also touched
`tests/expectations/gated_manifest/catf_mfe_gated.json` and `tests/unit/data/expected-coverage.md`.

I read the diff. It is a backlog-ID string rename (`[CATF-CRYO-HEATLEAK]` →
`[CATF-CRYO-HEAT-LEAK-COEFFICIENT]`) inside a `_note` field and one prose line. **No expected value
moved**, so SC-6's substance is intact. But the SC-6 argument is a commit-order argument, and an
argument that says "the one later amendment" when there are two is weaker than it needs to be.

**What should change:** one clause in `verification.md`'s SC-6 section naming `3a85d77` and what it
did not change.

### A-7 — the satisfied leg's policy disposition is asserted by the probe, not produced by the policy

`probes/acceptance_run.py:48-54`: `disposition_for` short-circuits `if headline == "satisfied":
return "feed-strategy"` before consulting `_disposition_for`. I checked the reason and it is
legitimate — `_HEADLINE_DISPOSITION` (`teax:packages/teax-simkit/simkit/study/policy.py:146-156`)
deliberately omits `satisfied`, which `ObjectivePolicy` resolves to `feed-strategy` or `penalize`
against `penalty_threshold`. The shortcut is faithful to default configuration.

But it means the exemplar's `feed-strategy` is the probe's own constant, while the authored
candidate's `reject` genuinely comes from the policy table. SC-5's load-bearing half — the
rejection — is the one that goes through the real route, so SC-5 stands. Recorded so a later reader
does not over-read the satisfied leg.

### A-8 — no verification-matrix rows for this item's new gates

`test_gated_manifest_identity.py`, `test_zero_entry_package_golden.py` and the `catf_mfe_gated`
ledger row are not filed in `docs/architecture/verification-matrix.md`. The "Item 5" rows at
`:549-671` belong to a different epic. Low severity, consistent with a known drift class in this
repo. **What should change:** file the rows, or record the matrix as out of scope for this epic.

---

### Plan completion

All eight phases (0–7) are checked in `plan.md` and each one's claimed evidence reproduces. No
placeholder code, no TODOs, no partial implementation found. Six deviations are recorded, each
where a reader will find it, each with reasoning — I checked all six named in the audit brief:

| deviation | recorded at | honest? |
|---|---|---|
| group 4b (A7/A8 usage deletions were a missing step) | `verification.md:162-175` | yes — names it a gap in the plan, not the table |
| 47 vs 48 modules | `verification.md:139-141` | yes — cause given (axis-leg reversal un-mints a module) |
| 43 vs 42 modules | `verification.md:88-91` | yes — 42 identified as the stale figure, cross-checked against four probe deltas |
| `//` vs `doc /* */` comment form | `PROVENANCE.md` §2 deviation block | form is recorded honestly; **the content claim it makes is false — finding A-1** |
| A2 `value` → `quantity` under O7 | `verification.md` §6-B only | **not in PROVENANCE or the ruled table — finding A-2** |
| D6 mutation route → typed entry injection | `verification.md:457-469` + `probes/acceptance_run.py:11-18` | yes — names the refusing test, argues intent preservation |

One more deviation, unlisted in the brief and recorded well: Phase 4's falsifications ran against a
temp copy with a monkeypatched path rather than "mutate then revert" (`verification.md:317-320`).
Same proof, safer. I used the same technique to reproduce them.

### Spec conformance

- **SC-1 — owner approves a table covering exactly 65 usages — MET.** `owner-disposition.md` is
  RULED 2026-08-13, all 65 rows. Row authority joins 1:1 against the d5 population expectation
  (65). Verified at spec stage; not re-litigated here.
- **SC-2 — every derivative change is accounted for — NOT MET.** The machine-checkable half is
  excellent: `check_gated_manifest.py --check` closes `65 = 58 + 7` (56 by name, 2 by
  `renamed_from:`), license-free, and I reproduced all three falsifications. Frozen twins verified
  byte-exact (below). But the PROVENANCE half fails on **A-2**: the `value` → `quantity` rename is
  a derivative change that PROVENANCE misstates in four places rather than accounts for. **A-1** is
  the same failure mode on an owner-graded obligation.
- **SC-3 — accounts for all 65 and shows honest coverage — MET.** Identity closes. Measured from
  the committed snapshot: 58 usage rows, 2 concrete entries, `{eligible 2, excluded 3,
  non_reaching 53}`; `coverage_account` → `58 / 2 / 2 / 0 / 0 / {} / complete`. The denominator
  counts applicable asserted gates only. `catf_mfe_d5` still shows 65/65.
- **SC-4 — dispositions land where the ruled table puts them — MET.** Histogram measured directly
  and matches the ruled derivation row for row. No calc-def-owned guard is asserted (which, per the
  spec's `[INFERRED]` consequence, would have taken SC-3/4/5/7 down together). The five
  `@inapplicable:` markers are correctly recorded in PROVENANCE rather than authored in source —
  the Phase 1 finding (SysIDE drops `doc` bodies inside inline-predicate constraints) is measured,
  filed as `[INLINE-PREDICATE-MARKER-DROP]`, and demonstrated not to move any committed number.
- **SC-5 — a physics rejection through the real TEAx route — MET.** Re-ran
  `probes/acceptance_run.py` against TEAx `constraint-semantics-item3` @ `5b70ae9`. The authored
  design point (`p_fusion = 2600.0`, no overrides) → A2 `violated`, A3 `violated`, headline
  `violation` / runtime `violated` → policy **`reject`**. The raised-`p_fusion` exemplar
  (`20000.0`) → `satisfied` → `feed-strategy`. Both durable case records carry a verdict **and** an
  identical coverage account (`58 / 2 / 2 / 0 / 0 / {} / complete`) plus a `catalog_fingerprint`.
  See **A-7** for a scope note on the satisfied leg.
- **SC-6 — expected outputs precede confirmation tests — MET.** Verified on the commit graph
  myself: both expectation files were added at `1247a3b`, the fixture directory at `7369b3e`, and
  `git rev-parse 7369b3e^` is `1247a3b` — strictly parent → child. The 6-D amendment `e01c3b4`
  stands alone, after the acceptance run, and moves one headline cell. Its basis reproduces:
  `cryo_derivation.py` derives `cooling_power` from source constants I spot-checked against
  `thermal_loads.sysml:52-67` and `magnets.sysml:66,87-92`, and hits `8396.054399837172`
  **bit-exactly** with a real `assert`, exiting 0. See **A-6** for the second, non-substantive
  post-fixture edit.
- **SC-7 — all acceptance gates pass with exact numbers recorded — MET.** Three routes gated with
  exact counts and fingerprints (`verification.md` §Phase 6); routes 2 and 3 byte-identical. The
  live-vs-snapshot catalog fingerprint divergence is chased to
  `resolution/models.py:597-622`, reproduced on the untouched frozen twin, and filed as
  `[CATALOG-FINGERPRINT-ROUTE-PORTABILITY]` — pre-existing, correctly not fixed here, and recorded
  as contradicting the plan rather than quietly dropped.
- **SC-8 — the calc-def-only package shape has a committed byte baseline — MET.** Goldens exist,
  the regenerate-and-diff test passes, and I reproduced the falsification (§P-6). Residual **A-4**
  on how the gate is wired.

**Non-goals respected.** No constraint syntax changed in either frozen twin. No calc-def gate
attachment built. No tolerance or intent class invented — both A3 bounds trace to
`[OWNER 2026-08-13]`. No `[unit]` literal in either surviving predicate body. No bare self-named
binding authored — I confirmed against the shipped source (`quantity` ← `p_electric_net_out`,
`part_power` ← `p_parasitic_total`), so the parked D-2/D-4 conflict is genuinely untouched (note
that PROVENANCE's own statement of this uses the stale spelling — finding A-2).

### Design conformance

Implementation follows the design, with three substitutions each recorded and argued:

- **D6's mutation route** (edit `inputs/*.json`) is refused by the product — the package contract
  covers on-disk bytes and `test_editing_a_sealed_input_and_resealing_is_refused` pins it. Replaced
  by TEAx typed entry injection (`CandidateBridge` + `PreparedEvaluator`). Intent preserved: one
  package, two input sets, a physics *value* mutated. Correct call.
- **D5's library** ships two definitions, not three; `ProductWithinBand` is deliberately not
  authored because its only consumer (A9) is parked. Recorded at `PROVENANCE.md:33-36`. Avoiding
  an unused shipped definition is the right instinct.
- **The A2 formal name** moved under O7's provisional-names allowance — sound, but see **A-2** for
  where it was not recorded.

The atomic-landing invariant held: the derivative was authored group by group with a
re-elaboration after each, and every step ADMITted.

### Code integrity

No slop or failure-honesty findings in the item's own code. `scripts/check_gated_manifest.py` is
notably clean: single responsibility, every regex documented with the exact literal it matches,
`ManifestError` raised with every failing row named, and both half-record cases
(`renamed_from:` with no `**now:**`, deletion with no authorizing row) explicitly refused rather
than skipped. No broad excepts, no silent fallbacks, no optional parameters papering over missing
data. `cryo_derivation.py` asserts rather than prints, which is why it is usable as evidence.

Product-drift smells: two fired, both recorded above under Product Judgment (Smell 3 → **disposed**
by the D-S1/D-S2 ruling; Smell 1 → residual **A-4**).

Auto-memory `feedback_*` constraints checked: no numeric LOC gate was applied anywhere (correct —
those were retired); generated baselines were not ruff-formatted; the verify-then-fix protocol was
followed on 6-B, 6-C and 6-D (doc-intent check → reproduce → family-level fix → record).

---

## Probe record

Every claim in the audit brief's six emphases, reproduced. All probes left the tree clean
(`git status --short` shows only the parallel actor's `.project/CURRENT_WORK.md`).

| # | probe | result |
|---|---|---|
| P-1 | Licensed suite, default markers: `pytest tests/` | **2025 passed / 34 skipped / 79 deselected**, `no live syside license` lines: **0** |
| P-2 | Licensed suite, all markers: `pytest tests/ -m ""` | **2103 passed / 34 skipped / 1 failed**, license-skip lines **0**. The one failure is `test_the_lane_runs_the_real_simkit` — pre-existing collection-order artifact, out of floor per `CURRENT_WORK.md:468-472` |
| P-3 | `ruff check src/` · `mypy src/` · `git diff --check` | **12** · **55 errors in 11 files (71 source files)** · clean. All three match |
| P-4 | Fixture measured from the committed snapshot | modules **47**, usage_records **58**, concrete_entries **2**, excluded **3**, histogram `{eligible 2, excluded 3, non_reaching 53}`, `coverage_account` `58/2/2/0/0/{}` `complete`. All match |
| P-5 | `scripts/check_gated_manifest.py --check` + **all three falsifications**, re-run against a temp-written PROVENANCE and restored | Identity closes `65 = 58 + 7` (56 by name, 2 by `renamed_from:`). All three falsifications reproduce with the **recorded red output**, near-verbatim. Not narrated — real |
| P-6 | SC-8 golden falsification: flip `ships_constraint_machinery` (`resolution/models.py:644`) back to `concrete_entries`, run the golden, restore | **2 failed, 2 passed** — `FileNotFoundError … schemas/constraint_types.py` and `assert 'ConstraintEvaluation' in …`. Matches the record exactly, **including its honest note** that the aggregator golden stays green. Restored; `git diff --stat` empty; 4 passed |
| P-7 | audit-F1: `grep -rn "CHOSEN BASIS\|Relation (undirected)" tests/fixtures/catf_mfe_gated --include=*.sysml` | **`power_balance.sysml` only** (2 hits). `shield.sysml:105` and `vacuum.sysml:53` read as bare initializers. **Finding A-1 confirmed** |
| P-8 | A-2: shipped formal vs PROVENANCE | Source `gate_forms.sysml:13` and `physics.sysml:131` say `quantity`; `PROVENANCE.md:42,84,330,334-335` say `value`; the word `quantity` never appears as a formal name. `owner-disposition.md:99` unamended. **Finding A-2 confirmed** |
| P-9 | SC-6 commit graph, verified independently | `--diff-filter=A` → both expectations at **`1247a3b`**, fixture at **`7369b3e`**; `git rev-parse 7369b3e^` = **`1247a3b`**. Strictly parent → child |
| P-10 | Every commit touching an expectation file | `1247a3b` (add), `e01c3b4` (6-D amendment, standalone), `3a85d77` (backlog-ID rename only — diff read, no expected value moved), `886a11f` (pre-item). **Finding A-6** |
| P-11 | `cryo_derivation.py`, run | Exit 0. `heat_leak` 116.723493 · `thermal_load_cryo` 167.921088 at 20 K · 50.0× · `cooling_power` **8396.054399837172** — reproduces the executed value bit-exactly under a real `assert`. Constants spot-checked against `thermal_loads.sysml:52-67` and `magnets.sysml:66,87-92`: all match |
| P-12 | SC-5 reject leg, re-run: `probes/acceptance_run.py` under the licensed env against TEAx `constraint-semantics-item3` @ `5b70ae9` | Authored point → A2 `violated`, A3 `violated`, headline `violation`, **policy `reject`**. Exemplar (`p_fusion=20000`) → `satisfied` → `feed-strategy`. Both records carry a verdict **and** an identical coverage account. Reproduces |
| P-13 | Frozen twins, byte-verified against git | `git diff --stat 18f51e1 HEAD -- tests/fixtures/catf_mfe_d5/ tests/fixtures/catf_mfe_model/` → **exactly one file**, `catf_mfe_d5/PROVENANCE.md`, 11 insertions / 18 deletions. `catf_mfe_model` untouched. Working tree clean on both |
| P-14 | TEAx checkout state | `5b70ae9` on `constraint-semantics-item3`, clean. Unmoved |
| P-15 | `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` consolidation vs the owner's original filing (`9d4f131`) | **P1 preserved**, "filed at owner direction" preserved, the "Why P1, not P3" search-usefulness rationale preserved **verbatim**, fix-scope rules preserved. The superseded 4.5 K / ×220 figures are corrected with a recorded correction note naming what was wrong and why — capture-fidelity §3 (amend + record), not accretion. Duplicate P3 entry deleted. **Consolidation is faithful** |
| P-16 | Provenance-grade fidelity across the ruling chain (emphasis 1) | Checked. SC-3's amendment is graded `[AGENT] (ratified by owner, 2026-08-13)` with the D-S1/D-S2 restatement flagged as "a mechanical consequence, not a re-disposition" (`spec.md:94-96`). The `//`-comment deviation is marked "Orchestrator-confirmed", not owner-ruled. The malformed-`@inapplicable:` severity is carried as "orchestrator-ratified, **not owner-ruled**". The 6-D labeling ruling is `[AGENT] ratified by owner`. Tolerances are `[OWNER 2026-08-13]`. **Nothing was promoted** |

**Not reproduced from the record** (accepted as written): the Phase 1 group-by-group elaboration
ladder and the Phase 2 red-window suite run — both are historical states of a scratch tree; the
red window is corroborated by the commit graph (P-9/P-10) and by the fixture reproducing the
pre-committed numbers. The three-route generation counts and digests in §Phase 6 — I verified the
projected graph and the coverage account are identical from the committed snapshot (P-4) and
re-ran the acceptance lane (P-12), but did not re-run all three generation routes.

---

## Certification

**Verdict: Needs work.** Two blocking findings, both in the derivative's PROVENANCE, both the same
shape — the file asserts as fact something about the shipped source bytes that the source does not
carry:

- **A-1** — the `[OWNER]` derivation documentation obligation is unmet at `shield.sysml:105` and
  `vacuum.sysml:53`, while PROVENANCE §2 states twice that it is met. Product-lens gate **BLOCKED**.
- **A-2** — the `value` → `quantity` rename is a derivative change PROVENANCE misstates in four
  places rather than accounts for, which is exactly what SC-2 requires. `owner-disposition.md:99`
  carries no pointer either.

Both are small edits. Neither moves a single count: the identity still closes, the coverage account
is unchanged, and every gate I re-ran is green. The verdict is about the artifact a later reader
and the accounting check treat as ground truth being wrong on two points, one of them owner-graded.

**Marked as verified:** SC-1, SC-3, SC-4, SC-5, SC-6, SC-7, SC-8 in `spec.md`; plan phases 0–7 were
already checked and each one's evidence reproduced, so they stand. **SC-2 left unchecked.** The
epic item heading is **not** marked ✅ — SC-2 is open.

In `epic_constraint_semantics_contract.md` Item 5, five of seven criteria are marked. Two are left
unchecked for different reasons:

- The PROVENANCE/machine-checkable-diff criterion — the epic-level twin of SC-2. Open, per A-1/A-2.
- The "generates exactly **65** catalog carriers" criterion — its epic wording is **superseded**.
  The owner authorized the accounting identity `65 = 58 carriers + 7 named deletions` on
  2026-08-13, recorded at `spec.md:93-108`. **The amended criterion is met** (SC-3 above, verified
  at P-4/P-5). The checkbox is left alone because marking it against superseded wording would
  misread, and rewriting epic text is outside an audit's remit — reconciling the epic to the
  amendment belongs to whoever next edits that file.

**Residuals, non-blocking, each with a named disposition:** A-3 (the manifest check never opens a
`.sysml` — the check that would have caught A-1), A-4 (SC-8 golden bypasses `run_codegen`), A-5
(SC-5 lane not regression-protected), A-6 (SC-6 names one post-fixture edit, there are two), A-7
(satisfied leg's disposition is probe-asserted), A-8 (no verification-matrix rows).

**Recommended path:** fix A-1 and A-2 (two comment blocks, four PROVENANCE lines, one per-change
record, one amendment note), re-capture the fixture snapshot if bytes move, re-run
`check_gated_manifest.py --check` and the population oracle, and this certifies. A-3 is worth doing
in the same pass since it is what makes A-1 non-recurring.

**Not checked:**

- `.project/CURRENT_WORK.md` was **not updated** — it is modified by a parallel actor (Item 6) and
  the audit brief fences it read-only. The item's status line there still reads as the implementer
  left it; the orchestrator owns that update.
- `.project/active/calcdef-constraint-gate-design/` (parallel Item 6) was not read, staged, or
  cleaned.
- The three-route generation runs were not re-executed end to end (see Not-reproduced above); the
  raw tree digests and semantic fingerprints in §Phase 6 are taken as recorded.
- The Phase 1 probe ladder and the Phase 2 red-window suite run were not re-executed.
- `owner-disposition.md`'s 65 rows were not re-derived against the SysML source individually — SC-1
  was certified at spec stage and I verified only the 1:1 join against the d5 population
  expectation and the group counts.
- The A3 tolerance values (`0.10` / `0.90`) were confirmed to be owner-stated and to match the
  shipped source; their **physical** appropriateness is a modeling judgment outside an audit's
  reach, and the unit-check column is human-owned by design.
- Item 4's two measured limits were taken as inherited fact, not re-measured.
- TEAx-side code was read only where needed to check the policy mapping (A-7); the branch was not
  audited.

---

# Addendum — cure re-verification, 2026-08-13

**Re-verdict: Certify with residuals.**
**Commit:** `b5f6fd8` · **Auditor:** same session, cures reproduced not read

Four cure commits landed against round 1's findings. I re-ran every probe that produced a finding,
plus the full gate set. Both blocking findings are cured, and the cure for A-3 is the one that
makes A-1 non-recurring.

## A-1 — [OWNER] derivation documentation obligation — **CURED** (`995a058`)

All three derivations now carry both required statements in source:

```
power_balance.sysml:66,68   (C37, already present in round 1)
vacuum.sysml:53,55          (A8, added)
shield.sysml:105,107        (A7, added)
```

The fingerprint shift the cure caused was **surfaced, not absorbed**, and I confirmed the
consequence is recorded everywhere round 1 would have found it stale:

| where | reads true? |
|---|---|
| expectation JSON — A9 `PumpingSpeedConsistency` `source_line` | **169**, and `vacuum.sysml:169` is that constraint's declaration line. Matches |
| snapshot — recomputed catalog fingerprint | `c57127dac35c36563408a7956ad3c7cd2f6b41758bbcef3abc187b6f5d0a6491`, equal to the value recorded in `verification.md` §Phase 6 |
| PROVENANCE + ledger + `verification.md` §Phase 6 | the shift is stated with its mechanical cause (five comment lines above A9 in the same file), the pre- and post- fingerprints on both routes, and the note that `shield.sysml` shifted nothing |
| `verification.md` §SC-6 | the shift is named as the **third** post-fixture expectation edit |

Membership and every count are unmoved: 47 modules, 58 rows, 2 concrete entries,
`{eligible 2, excluded 3, non_reaching 53}`, coverage `58 / 2 / 2 / 0 / 0 / {} / complete`,
A2/A3 evaluation channels unchanged. **Option A is the right call and is recorded as a ruling
rather than a preference:** the obligation exists so a reader of the model sees the relation and
the chosen basis, and preserving a line number by cramming the statements into a trailing comment
would have served the fingerprint at that reader's expense.

## A-2 — the `value` → `quantity` rename — **CURED** (`1869c29`)

All four sites round 1 named now read true against the shipped source:

- `PROVENANCE.md:64` — the verbatim source quote is `in quantity = p_electric_net_out;`, matching
  `physics.sysml`.
- `PROVENANCE.md:106` — the self-named-binding argument reads `quantity` ← `p_electric_net_out`.
- `PROVENANCE.md:352, 356` — the unit obligation is hung on `quantity`, the formal that exists.

The remaining `in value` occurrences (`PROVENANCE.md:38-41`) are the **new per-change record**
quoting the ruled table's original spelling to explain why it cannot generate — correct usage, not
residue. `owner-disposition.md`'s A2 row now carries the pointer: the rename is stated as an
amendment to an agent-provisional name under **O7**, explicitly "not a re-disposition; no ruled
content moves." Provenance grade is preserved exactly.

## A-3 — nothing tied a deletion to its derivation — **CURED** (`b083c47`)

`check_gated_manifest.py` gains a fifth source, the derivative's `.sysml`. Both failure modes
falsified by me, against temp writes, tree restored:

```
statements removed from shield.sysml   -> EXIT 1
  FAIL: …CompositionConsistency: the derivation at designs/catf_mfe/shield.sysml:110 is missing
        the undirected relation and the chosen-basis statement — required by owner-disposition.md:37-41

derivation replaced by a literal        -> EXIT 1
  FAIL: …ThicknessConsistency: derive-instead promises `attribute outer_radius : Real =
        inner_radius + wall_thickness;` in designs/catf_mfe/vacuum.sysml, not found

restored                                -> EXIT 0, identity closes 65 = 58 + 7
```

**The first mode is exactly A-1's shape** — the gate would have caught the original defect at
Phase 4 instead of letting it ship past four phases. That is the cure I care about most: A-1 was a
missing comment, A-3 is why a missing comment can no longer pass. The `DERIVATIONS` table maps A1
and A4 to `None` deliberately, so it states its own coverage rather than silently skipping them.

## A-6 — **CURED** (in `995a058`)

`verification.md` §SC-6 now names all three post-fixture expectation edits — `e01c3b4` (6-D
headline cell), `3a85d77` (backlog-ID rename), and the audit cure's one `source_line` — each with
what it did and did not move. The commit-order argument is now complete rather than nearly so.

## Residuals — dispositions accepted (`b5f6fd8`)

- **A-4** (SC-8 golden bypasses `run_codegen`) and **A-5** (SC-5 TEAx lane not regression-protected)
  are recorded as **stated limits** rather than fixed. Correct: both are scope calls that were
  defensible all along and only lacked being written down. The failure round 1 flagged was silence,
  and the silence is gone.
- **A-7** (satisfied leg's disposition is probe-asserted) stands as recorded; SC-5's load-bearing
  half goes through the real policy table.
- **A-8** (no verification-matrix rows) is deliberately left for an epic-level matrix
  reconciliation. Reasonable — the matrix drift is a known repo-wide class, and filing rows per
  item is how it got inconsistent.

## Gate set, re-run

| gate | measured | claimed |
|---|---|---|
| licensed suite, all markers | **2106 passed / 34 skipped / 1 failed**, license-skip lines **0** | 2106/34 ✓ |
| the one failure | `test_the_lane_runs_the_real_simkit` — pre-existing collection-order artifact, out of floor | — |
| `ruff check src/` | **12** | 12 ✓ |
| `mypy src/` | **55 errors in 11 files (71 source files)** | 55 ✓ |
| `git diff --check` | clean | clean ✓ |
| `check_gated_manifest.py --check` | identity closes `65 = 58 + 7` (56 by name, 2 by `renamed_from:`) | ✓ |
| fixture re-projected | 47 / 58 / 2, `{2, 3, 53}`, coverage `58/2/2/0/0/{}` complete | ✓ |

Suite is up 3 from round 1's 2106-equivalent baseline of 2103, consistent with A-3's two new
falsification tests plus one.

## Re-verdict

**Certify with residuals.** SC-2 is now earned: the derivative's PROVENANCE accounts for every
change from `catf_mfe_d5`, including the rename it previously misstated, and the owner-graded
derivation obligation is carried in the model where the owner ruled it must be — and is now gated
rather than claimed. The product-lens gate audit-F1 is **resolved by citation** to `995a058` and
`b083c47`; audit-F2 is resolved by `b083c47`. audit-F3/F4/F6 (residuals A-5, A-8, A-4) remain open
with stated dispositions and do not block.

**SC-2 marked in `spec.md`.** All eight criteria are now verified. The epic's Item 5 PROVENANCE
criterion is marked; its "exactly 65 catalog carriers" criterion is still left alone, superseded by
the owner-authorized accounting identity as explained above — reconciling that epic wording remains
outside an audit's remit.

**Not checked, this pass:** the three-route generation runs were not re-executed, so the two live
catalog fingerprints recorded in §Phase 6 are taken as recorded (I verified the snapshot-route one
directly). The acceptance TEAx lane was not re-run — no cure touched it, and A-1's line shift does
not reach the executable fingerprint. Round 1's other unchecked areas still stand.
