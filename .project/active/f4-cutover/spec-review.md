# Spec Review: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Spec:** `.project/active/f4-cutover/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/f4-cutover/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound.** The spec is pointed at the right work item and is unusually faithful to its evidence
base. Every code-facing claim I checked is true against the current tree: the def at
`graph_builder.py:1212`, the `__all__` export at `:1925`, the three call sites at
`1444 / 1539 / 1640`, the `param_groups` bindings at `:228`/`:331`, the two `type: ignore`s at
`:408`/`:412`, Strategy D's `return None` stub and its "future extensibility" docstring at
`input_resolver.py:200-214`, and the fallback's leaf-only key at `input_resolver.py:270-271`. The
design-review's M3/M4/M5 resolutions are carried into the spec's [HARD] requirements. Tags are
honest and deferrals are genuine design-stage questions.

This is a **Revise**, not a Rework. The findings below are sharpenings on a correct contract. Two
are must-fix because they are places where a reader could over-trust a safety net that does not
actually cover the risk it appears to cover — and that gap sits exactly on the load-bearing M4
blocker the item exists to defuse.

I could not independently re-run `mypy`/`ruff` in this sandbox (both are approval-gated). The
104/17 ceilings are asserted from the PIPELINE-TRUTH close gate; implement must re-confirm the live
counts at pickup. Not a spec defect — the spec already treats them as a baseline to hold.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (positive):** All code-facing claims verified true. The fallback divergence
is exactly as the probe states: `resolve_input` builds `{module_eqn}__{leaf}` (leaf =
`ref.rsplit(".", 1)[-1]`, `input_resolver.py:270`), while the live SumTerm site builds
`{module_eqn}__{part_usage}_{attr}` (`param_name = f"{part_usage_name}_{attribute_name}"`,
`graph_builder.py:1442/1467`). For the probe's `permitting.raw_material_cost` that is
`…__raw_material_cost` vs `…__permitting_raw_material_cost` — the collision the probe names. No
faithfulness defect here; this lens is clean.

**L1-2 · Direct claim:** The Problem section says the pipeline "resolves aggregation inputs …
through an inline function, `_resolve_aggregation_input_channel`." That function resolves the
**channel only** — it returns a channel string or `None` (see the `if channel:` / `if resolved:`
guards at `graph_builder.py:1448/1542/1644`). The entry-point construction — the part that diverges
(M4) — is **not** in that function; it is inline `else:` code at each of the three call sites
(`1453-1493`, `1562-1608`, `1650-1666`). The spec's M4 bullet does say "the live call sites build
the … entry point," so it is not wrong — but the Problem's framing ("resolves … through the
function") blurs the exact boundary that makes M4 hard. See L3-1, which is the load-bearing version
of this.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim (positive):** The bet is sound and the sequencing is right. The item is the
churn item (R3), lands first, and the [HARD]/[INFERRED] split is defensible — the two INFERRED
items (delete Strategy D; remove the dead Step-5 computation) are correctly tagged as forks the
evidence closed, not guesses. No approach-level objection.

**L2-2 · Question to the user:** SC #4 accepts the aggregation baseline as "byte-identical **OR**
one reviewed capture diff." But the entire point of the M4 reconciliation is to reproduce the live
EP construction faithfully, which by construction yields a **byte-identical** aggregation baseline.
The spec itself says "a non-byte-identical aggregation diff is a signal the fallback reconciliation
is incomplete." So for *this* item, is a reviewed aggregation diff really an acceptable pass state,
or should byte-identity be the hard bar — any aggregation diff blocks the cutover pending
root-cause, rather than being reviewed-and-accepted? The "OR reviewed diff" escape is precisely
where a real regression could ride in under the cover of "expected churn." Recommend the spec state
that aggregation byte-identity is the expected outcome and a diff is a defect to explain, not a
deliverable to sign off.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix):** The M3 parity gate has a structural blind spot on the M4 risk.
The spec's [HARD] M3 requires comparing `resolve_input(AGG_STRATEGIES)` against
`_resolve_aggregation_input_channel` **directly** (function-to-function). But the replaced function
returns a channel-or-`None` and never builds an entry point, while `resolve_input` returns an
`InputSource` that is *either* a channel *or* an entry_point and never `None`. So a function-level
parity gate can only compare the **channel-resolution** cases (where the old function returns
non-`None`). On the fallback cases — the entry-point key that actually diverges (M4) — the two are
not comparable, and the gate is silent. The result: the spec presents M3 as "the cutover's own
safety net," but that net covers the half that was never at risk and is blind to the half that is.
The M4 fallback is then guarded by baseline byte-identity **alone**.

Recommend the spec require the parity gate (or a companion test) to compare the **full
`InputSource` the call-site block produces** — old inline block vs new `resolve_input` path,
including entry-point outputs — not just the channel the deleted function returned. Otherwise a
green M3 gate reads as "cutover is safe" when the load-bearing reconciliation is unverified except
by a baseline diff.

**L3-2 · Direct claim (must-fix):** The reconciliation target under-specifies the fallback's
**side effects**, not just its key format. The inline fallbacks do four things beyond minting the
EP string:
- set `compilability = Compilability.MANUAL_REQUIRED` when a term is unresolved and has no literal
  default (`graph_builder.py:1465`, `:1579`);
- register the EP into `new_entry_points` with a dedup guard (`if ep_qn not in entry_points and
  ep_qn not in new_entry_points`);
- backfill a literal default onto an EP created earlier without one (`:1477-1487`, `:1591-1602`);
- classify `param_group` via `group_deriver.classify(ep_qn)` and build the multiplicity EP.

`resolve_input`'s fallback returns a bare `InputSource(entry_point, qualified_name=ep_qn)` and does
**none** of these. The spec's M4 bullet names the key format, `_find_literal_redefinition` defaults,
param-group classification, DESIGN_ATTRIBUTE typing, and multiplicity EPs — good — but it does
**not** name the `Compilability.MANUAL_REQUIRED` signal. If the cutover moves the fallback into
`resolve_input` and loses that assignment, a genuinely-unresolved aggregation term would be silently
marked compilable and get a wrong auto-impl — a silent regression, exactly the failure class this
epic exists to kill. Add the compilability signal (and the register/dedup/backfill semantics) to the
reconciliation target so design must preserve it.

**L3-3 · If-then tradeoff:** The scope framing "replace `_resolve_aggregation_input_channel` with
`resolve_input(AGG_STRATEGIES)`" understates the edit. Because `resolve_input` never returns `None`,
swapping the three calls **necessarily deletes the three inline `else:` fallbacks** and shifts
fallback ownership into `resolve_input`. That is the real change — and it is why M4 exists. **If**
design intends to keep the inline fallbacks and use `resolve_input` only for channel resolution
(discard its entry_point result), then M4 is moot but the module's fallback is dead code and the
"reconciliation" is unnecessary. **If** design intends `resolve_input` to own the fallback (the
spec's evident intent), then all of L3-1/L3-2 apply. The Open Question "where the reconciliation
lives" gestures at this, but the spec should state plainly which shape the cutover is: the deleted
function is channel-only; `resolve_input` does strictly more.

**L3-4 · Question to the user:** The "SingletonTerm Try 2 direct-channel construction"
(`graph_builder.py:1548-1560`) is listed in the reconciliation target, but it produces a
**module_output channel** (`get_channel_name(...)` checked against `canonical_channels`), not an
entry point. It belongs in a **strategy** (the channel half), not the fallback. Is Try-2 already
covered by one of the four `AGG_STRATEGIES` (ScopedRegistryLookup / ChainRedefinitionFollow /
SysMLQNLookup / DesignAttributeLookup)? If not, replacing the SingletonTerm block with
`resolve_input` loses Try-2 unless a strategy reproduces it. The spec should flag this as an open
design question rather than fold it into "fallback" construction, where it will be mis-placed.

**L3-5 · Direct claim (contradiction):** Two [HARD] items pull in opposite directions on the typing
fix. The R4 item says the type-ignore's stated cause "looks stale … reproduce the actual mypy error
… before choosing the split; do not fix against the comment's account of the cause." The
Gate-ceilings item says "the fix **is** the two-named-variable split, not a re-annotation." One
defers the fix pending reproduction; the other pre-commits to a specific fix. Likely the split is
right — but the spec cannot both mandate reproduce-first-then-choose and name the answer as [HARD].
Reconcile: state the split as the *expected* fix while keeping the choice contingent on what the
reproduced mypy error shows.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** SC #7 and Scope item 6 call this a `param_groups`
"double-binding." The variable is actually assigned at `:228`, `:331`, and `:413` and mutated at
`:335/362/373/408` — a bind-mutate chain, not two bindings. The real fix is "isolate the discarded
Step-5 result (`:228`) so the live variable carries one type from `:331` onward." Minor; the R4
reproduce-first requirement already covers the mechanics.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The reconciliation is the crux of the item, and a reader currently has
to reverse-engineer from the [HARD] M4 bullet that (a) the deleted function is channel-only and (b)
`resolve_input` owns the fallback. Leading the Problem or the M4 requirement with that two-line
mental model — "the deleted function resolves the channel; the entry-point fallback is separate
inline code at each call site; the cutover moves that fallback into `resolve_input`, which is why
the keys must reconcile" — would let a tired reader grasp the whole shape on one pass. This is the
same content as L1-2/L3-3, framed as a comprehension fix.

---

## Engagement Summary

**Overall take:** This is a strong, faithful spec — every line number and code claim checks out,
and it correctly encodes the design-review's M3/M4 resolutions as [HARD] requirements. The gap is
not direction; it is that the two safety nets (M3 parity, R3 byte-identity) are described as if each
covers the cutover, when in fact the M3 function-level parity gate is structurally blind to the M4
fallback divergence — the one thing most likely to churn the baseline. Fix the two must-fix items
and I would bet design on this.

**Here's what I need you to weigh in on:**

1. **[L3-1] (must-fix)** The M3 parity gate compares the deleted channel-only function against
   `resolve_input`, so it cannot see the entry-point/fallback divergence (M4) at all. Require the
   gate to compare the full `InputSource` the call site produces, or the cutover's headline safety
   net covers the wrong half.
2. **[L3-2] (must-fix)** The reconciliation target lists the EP key format, defaults, param-group,
   DESIGN_ATTRIBUTE, and multiplicity — but omits the `Compilability.MANUAL_REQUIRED` signal (and
   the EP register/dedup/backfill) the inline fallback sets. Losing it silently mis-marks an
   unresolved term as compilable. Add it to the target.
3. **[L3-3, L1-2] (should-fix)** State the true scope plainly: the deleted function is channel-only;
   `resolve_input` additionally owns the fallback, so the cutover necessarily deletes the three
   inline fallbacks. This asymmetry is the reason M4 exists.
4. **[L2-2] (should-fix)** Should aggregation byte-identity be the **hard** acceptance bar (any diff
   blocks pending root-cause), given the reconciliation is designed to yield exactly zero
   aggregation churn? The "OR reviewed diff" escape is where a real regression could hide.
5. **[L3-5] (should-fix)** The typing fix is both deferred to reproduction (R4) and pre-named as the
   two-variable split (Gate-ceilings). Reconcile — expected fix, contingent on the reproduced error.
6. **[L3-4] (note)** Confirm whether SingletonTerm "Try 2" is covered by an existing `AGG_STRATEGY`;
   it is a channel construction, not a fallback, and could be dropped by the cutover if no strategy
   reproduces it.

**Notes (lower stakes):**
- LocalTerm-EXPOSE is correctly excluded from the reconciliation target — its ref is undotted, so
  `resolve_input`'s leaf equals the live `{module_eqn}__{attr}` key (`graph_builder.py:1652`) and
  they already agree. State *why* it is excluded so design does not "reconcile" it and break the
  agreement; and confirm its call site (`:1640`) is still in the 3-site deletion scope.
- Snapshot baselines: the spec's byte-identity gate names "aggregation" and "non-aggregation"
  baselines but not snapshot fixtures. If any snapshot-generation baseline carries aggregation EP
  construction, include it in the gate scope (memory: `multihop-expose-offline-parity`).
- Could not re-run mypy/ruff here (approval-gated); the 104/17 counts are from the prior close gate
  and must be re-confirmed live at implement.

---

## Resolutions

*(To be filled during Stage 5 as the user resolves each finding. The spec agent reads this section
to incorporate the review; the reviewer does not edit `spec.md`.)*

- **[L3-1]** _pending_
- **[L3-2]** _pending_
- **[L3-3, L1-2]** _pending_
- **[L2-2]** _pending_
- **[L3-5]** _pending_
- **[L3-4]** _pending_

---

**Verdict:** Revise. The work item is correct, the evidence is verified, and the direction is sound.
Two must-fix findings close a blind spot where the described safety nets do not cover the M4 risk
they appear to; three should-fix findings sharpen scope and remove a [HARD] contradiction. None
touch the spec's direction.

**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) and point it at this review to incorporate. The reviewer does not edit the spec.
