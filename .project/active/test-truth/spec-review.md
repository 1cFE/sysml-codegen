# Spec Review: Self-Referential Test Remediation (PIPELINE-TRUTH Item 6)

**Spec:** `.project/active/test-truth/spec.md`
**Contract:** `~/.claude/commands/_my_spec.md`
**Review File:** `.project/active/test-truth/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound.** The spec is about the right work item, the Problem section is accurate, and
the core requirements are directionally correct. I spot-checked far more than five
hand-transcribed literals against the committed snapshots and design sources; every one
I checked is correct (details below). The "why it can't fail" diagnosis is accurate for
every test body I read (H2, H5, MF-07, REG-02). This is a strong spec. The findings
below are targeted must-fixes and one honest-scoping question — none of them reworks the
item.

**Literals verified (all correct):**

- **H5** catf USAGE_LITERALs — `gross_electric`→1546.72, `p_neutron`→2079.41,
  `p_thermal_electric`→1104.22 all present as `literal` bindings in
  `catf_mfe_model/extraction_snapshot.json` (e.g. line 2896).
- **H2/H3/H4** group counts — `solar_battery` has exactly **3** entry_point_groups
  (DesignParams, LibraryParams, SystemDesign), `catf_mfe` has exactly **8**
  (Blanket/Heating/Magnets/Physics/RadialBuild/System/Tritium/Vacuum), confirmed in the
  committed `computation_graph.json` baselines. `PARAMETRIZED_MODELS` is exactly those
  two models, so a `{solar:3, catf:8}` map is complete.
- **M3 (PGD-06)** — `child_count`→25.0 and `total_child_mass`→50.0 are `literal`
  bindings (`solar_battery snapshot` lines 3555/3568); `p_net_mw`=0.008 is
  `design.sysml:53`.
- **H6/H7 naming** — `get_module_name` lowercases the *entire* EQN
  (`qualified_names.py:95`), so H6's "design prefix lowercased" is right;
  `get_channel_name` returns `f"{usage_qn}__{output_attr}"` (`qualified_names.py:100`),
  so H7's doubled trailing segment is the correct output for an aggregation module whose
  EQN already ends in the attribute name. The doubling is real and deliberate.
- **MF-07 conversion** — the `idiot_index` aggregation at `solar_array` is
  `capital_cost / raw_material_cost` (`library.sysml:637`), `capital_cost` is itself a
  sibling aggregation at that scope (`:615`), and `misc_hardware_cost` exposes to
  `allocation_model.total_allocation` (`:612`). The proposed anchor and its
  double-attr channel literal are correct.
- **REG-02** — the test only checks `seg.replace("_","").isalnum()`
  (`test_gen_registry.py:312`); it never touches the filesystem or
  `PythonModulePath.from_sysml()` despite its docstring. Spec's diagnosis is exact.
- **SC-6 Pin 1** — `reconstruct_expression` renders a LiteralReal via `str(value)`
  (`expression_utils.py:66`), and `str(1e-06)` is `"1e-06"` in Python. `MockLiteralReal`
  exists (`test_hierarchy_resolver.py:384`). **Pin 2** — line 283 asserts only the
  substring `"sum(" in result`. Both claims accurate.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Rewrite request:** The spec labels the H7/M5–M9 channel literal "doubled" but
never says the doubling is **correct by design** or why. A future reader (or the
implement agent) who sees a hardcoded
`...__capital_cost__capital_cost` will read it as a copy-paste typo and "fix" it,
silently re-breaking the pin. The orchestrator verified this is deliberate: per ADR-003,
`get_channel_name` composes `usage_qn + "__" + output_name` (`qualified_names.py:98-100`),
and an aggregation module's EQN already ends with the attribute name. Add a one-line
note at the H7/M5–M9 rows (and carry it into the plan) stating the doubling is the
ADR-003 channel-PQN of an aggregation output and must not be "corrected." Right now the
only defense against a future de-doubling is the reader noticing the parenthetical
"(doubled)".

**L1-2 · Direct claim (minor line-number drift):** REG-02's count sibling
`test_module_count_matches_inputs` is at `test_gen_registry.py:323`, not "320". Harmless
— the spec already flags line numbers as approximate — noted only so the implementer
keys on the name, not the number.

### Lens 2 — Problem & Approach

**L2-1 · (No finding — bet is sound.)** The bet — replace computed expectations with
literals drawn from license-free snapshots/design sources — is the right one and is
well-matched to the evidence. Recorded here only to be explicit that I tried to argue
the opposite (e.g. "should these be regenerated fixtures instead of hand literals?") and
it falls apart: hand literals are precisely what breaks the tautology, and the
cleared-non-findings list correctly keeps the frozen-artifact regression pins separate.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (highest-stakes):** H6, H7, and M4 anchor by **raw list index**
into `aggregation_data` — "idx 0", "idx 15". That index is a DFS-traversal artifact, not
a stable identity, and I could not verify it offline (the aggregation ordering is
computed at graph-build, not stored in the snapshot). The solar_battery model has many
`idiot_index` aggregations (`library.sysml` has 8 interface-level + 4 assembly-rollup +
redefinitions), so an off-by-one or reordering turns a can't-fail test into a
wrongly-failing one — the exact failure mode this item exists to prevent. The spec's own
MF-07 detail already models the fix: it filters by
`attribute_name == "..." and instance_path == "..."` instead of trusting an index.
**Re-key H6/H7/M4 the same way** — select the aggregation by (instance_path,
attribute_name), then assert the literal name/channel/eqn on it. "Re-confirm line numbers
at implement" does not cover index drift.

**L3-2 · If-then tradeoff:** SC-2's mutation check spot-checks **three** fixed tests
(one count, one naming, MF-07). For the other ~17 fixed tests, nothing demonstrates the
literal actually diverges from a mutated production value. This leaves one hole open: an
implementer who obtains a literal by *running production and pasting the result* produces
a test that is syntactically "anchored" but epistemically circular — it passes today and
its literal is never independently checked. The disposition table cites a real fixture
source for most rows, which is the right defense, but no success criterion **requires**
that per-test provenance to be recorded. Cheap close: require the close-out (or the test
comment) to cite, per fixed test, the fixture `file:line` its literal came from, so
review can confirm it was transcribed from a known element and not lifted from output.
**If** you consider the three-test mutation spot-check plus reviewer diligence
sufficient for a low-risk item, this stays as-is; **if** you want the anti-pattern
provably dead, add the provenance requirement — it's a one-line SC.

**L3-3 · Rewrite request (small):** H2/H3's fix line just says "Assert literal counts
(3, 8)." The tests are parametrized over two models, so the concrete shape is a per-model
expected-count dict (`{"solar_battery_model": 3, "catf_mfe_model": 8}`) indexed by
`model_name`, not a single scalar and not dropping the parametrization. Spell that out so
the implementer doesn't reach for the [INFERRED] "add a non-parametrized assertion"
route where a keyed dict is cleaner. (H4's `entry_fusion` twin in
`test_gen_pipeline_yaml.py` gets the same map.)

### Lens 4 — Hygiene

*(No material findings. The disposition tables are dense but scannable, and the line-ref
convention is stated up front.)*

### Lens 5 — Reader Comprehension

*(No material findings. A tired engineer can read the Problem + the three disposition
tables and know exactly what to change. The MF-07 detail block with its code sketch is
especially clear.)*

---

## Engagement Summary

**Overall take:** This is a strong, faithful spec — I verified well over five
hand-transcribed literals against the committed snapshots and design sources and every
one is correct, and the "can't fail" diagnosis matches every test body I read. It is not
Approve-as-is only because of three targeted must-fixes: index-based anchoring that could
itself introduce a wrongly-failing test, a missing "the doubling is deliberate" note the
orchestrator explicitly asked for, and one honest-scoping question about the LOW set.

**Here's what I need you to weigh in on:**

1. **[L3-1]** Re-key H6/H7/M4 from raw list index ("idx 0", "idx 15") to
   (instance_path, attribute_name) selection — the same robust pattern the spec already
   uses for MF-07. Index order is a computed DFS artifact I can't verify offline; trusting
   it risks the exact wrongly-failing-test outcome this item prevents.
2. **[L1-1]** Add the one-line "channel doubling is the ADR-003 aggregation PQN, not a
   typo — do not de-double" note at H7/M5–M9 and carry it into the plan. Today the only
   guard is a parenthetical.
3. **[L3-2]** Decide whether the 3-test mutation spot-check is enough, or whether to add
   a one-line SC requiring each fixed test to cite the `file:line` of its literal's
   fixture source — the cheap way to prove no literal was lifted from production output.
4. **[Q-1 — question to you]** Is the D5 discovery-session transcript actually
   recoverable? The LOW tier's completeness ("all 25 dispositioned") rests on it: the
   register names H1–H7 and M1–M10 by category and only MF-07 among the 8 LOW, so 7 of
   the 8 LOW identities are *reconstructed*, not register-fixed. The spec's "reconcile
   against transcript, else reconstructed set stands" fallback is sound **if** the
   transcript might exist; if it's already gone, drop the first-step reconciliation to
   "best-effort" and state plainly in SC-1 that the LOW remainder is reconstructed (17
   register-named + 8 reconstructed), so the "25" count isn't read as a fixed register
   set it isn't.

---

## Resolutions

*(Filled in during Stage 5, keyed by finding ID.)*

All six must-fixes incorporated into `spec.md` 2026-07-06.

- **[L3-1] — DONE.** H6, H7, and M4 re-keyed from raw list index ("idx 0/15") to
  selection by `(instance_path, attribute_name)` — the same robust pattern the MF-07
  detail already uses. Each row now says explicitly "select by (instance_path,
  attribute_name), not by index" with the DFS-artifact rationale. A reorder can no
  longer spuriously fail these pins.

- **[L1-1] — DONE.** Added a standalone **[HARD]** requirement stating the
  aggregation/formula channel doubling (`…__capital_cost__capital_cost`) is deliberate
  per ADR-003 (`get_channel_name` = `usage_qn + "__" + output`; an aggregation/CA
  module's EQN already ends in the attr name), verified at `core/qualified_names.py:98-100`,
  and must not be de-doubled — carried into the plan via the requirement text. The H7
  and M5–M9 rows now carry the same note inline and require a code comment on each
  doubled literal.

- **[L3-2] — DONE (provenance requirement adopted).** Per orchestrator ruling, adopted
  per-test literal provenance: added a **[HARD]** requirement and a success criterion
  that every re-anchored literal carries a comment citing its source (snapshot path+line,
  fixture `file:line`, or hand-computation inputs), with the close-out listing provenance
  per fixed test. The 3-test executable mutation spot-check stays on top.

- **[Q-1] — RESOLVED (transcript not recoverable).** Per orchestrator ruling, rewrote
  the LOW-tier preamble: the discovery transcript is NOT recoverable, so the reconstructed
  LOW set is authoritative and each candidate stands on its own inspection at implement —
  no transcript archaeology. SC-1 now states the "25" plainly as 17 register-named + 8
  LOW (1 register-named MF-07 + 7 reconstructed), so it is not read as a fixed register
  set. A struck candidate at implement is recorded with evidence + a count-change note.

- **[L3-3] — DONE.** H2/H3/H4 fixes now specify a per-model expected-count dict
  `{"solar_battery_model": 3, "catf_mfe_model": 8}` keyed by `model_name`, keeping the
  parametrization (not a scalar, not the [INFERRED] non-parametrized route). The H4
  `entry_fusion` twin gets the same map.

- **[L1-2] — DONE (trivial).** REG-02's count sibling reference corrected to
  `test_gen_registry.py:323` with an explicit "key on the name not the line" note.

---

**Verdict:** Revise (APPROVED-WITH-CHANGES)

**Must-fix list:**
1. **[L3-1]** Re-key H6/H7/M4 anchors by (instance_path, attribute_name), not list index.
2. **[L1-1]** Add the "doubling is deliberate per ADR-003 — do not de-double" note at
   H7/M5–M9; carry into the plan.
3. **[L3-2]** (Decide) Add a per-test literal-provenance requirement to the SCs, or
   record the decision to rely on the 3-test spot-check.
4. **[Q-1]** Resolve LOW-set honesty: confirm transcript recoverability and make SC-1's
   "25" wording distinguish the 17 register-named from the 8 reconstructed.
5. **[L3-3]** Make H2/H3/H4's fix concretely a per-model expected-count dict over the
   parametrization.
6. **[L1-2]** (Trivial) REG-02 count sibling is at `:323`, not `:320` — key on the name.

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not
edit the spec. All six items are targeted edits — the work item is sound and the
literals check out, so this is a fast revision, not a rewrite.

ARTIFACT: .project/active/test-truth/spec-review.md
