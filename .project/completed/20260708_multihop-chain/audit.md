# Audit: TRUTH-DEBT Item 2 — Resolved Multi-Hop Chain Bindings

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-07
**Branch:** truth-debt-epic
**Item HEAD:** 30a9bf6 (range 5af442d..30a9bf6)  ·  **Live HEAD:** 42aad15 (Item 4 landed after)

---

## Summary

The item delivers what the spec and design promised. Both deep calc-usage chains wire to their exact
channels; the pins are hardcoded red-first and independently anchored (genuine R1); the loud
diagnostic is preserved at its forced new home (backtracker Step-4, a real WARNING); the climb is
gated and guarded; the re-capture is scoped to the one fixture; docs and matrix moved with the code.
Every HARD requirement is met and the one spec deviation (D3, reject moves from extraction to the
backtracker) is honestly flagged and technically forced.

The audit's load-bearing question — the filed `[TRUTH-DEBT-IFE-PLANT-CHAIN-STALE]` — resolves **in
Item 2's favor**: Item 2 provably cannot affect ife_plant. Its whole source diff is two files, neither
on the attribute/classifier path; ife_plant's calc-usage chain is 2-segment (below Item 2's gates) and
its 3-segment chain is an *attribute* binding on the untouched path. The staleness the note describes is
a pre-existing prior-epic classifier drift, mis-attributed to Item 2. That does **not** violate Item 2's
SC — but the BACKLOG note's attribution should be corrected (Note 2).

The verdict is PASS-WITH-NOTES only because (1) this audit environment blocks all test/lint/type
execution, so the gates were verified statically and from git rather than re-run (Note 1), and (2) the
cross-item misattribution above is worth fixing. Neither is a defect in Item 2's deliverable.

---

## The load-bearing question: `[TRUTH-DEBT-IFE-PLANT-CHAIN-STALE]`

**The filed claim** (BACKLOG.md:314, filed by Item 4): ife_plant's `radial_build.magnet_volume_total`
is committed `expose_pure` but live extraction now classifies it `expose_chain_tentative`; "it is
Item-2 multi-hop-chain machinery that landed without re-capturing `ife_plant`."

**Two questions, answered separately and precisely.**

### 1. Did Item 2's byte-identity gate actually hold? — YES.

The committed ife_plant baseline was **unchanged** at Item 2's HEAD. Its baseline
(`tests/fixtures/baseline_outputs/ife_plant/`) and snapshot last changed at `89e6f80`
(UPSTREAM-FINDINGS, before this epic) — no Item-2 commit touches it. The re-capture commit `1506348`
touched **only** `deep_cross_scope_probe`'s two baselines (plus plan/test), verified by
`git show --stat 1506348`. The full suite was green at Item 2 HEAD (2080 passed per plan), and the
ife_plant conformance test reads the committed snapshot. Byte-identity held literally.

### 2. Is the committed ife_plant baseline stale w.r.t. HEAD behavior, and is Item 2 the cause? — Possibly stale; NOT from Item 2.

**Item 2's entire source diff is two files** (`git diff --stat 5af442d~1 30a9bf6 -- src/`):
- `analysis/dependency_backtracker.py` (+45) — the climb + Step-4 WARN.
- `extraction/usage_extractor.py` (+33/-17) — the `FeatureChainExpression` calc-usage arm.

Neither touches the attribute path. The `expose_pure`/`expose_chain_tentative` classification is
produced entirely by `computed_attribute_extractor.py:181-204`
(`_is_wellformed_multihop_chain` → `EXPOSE_CHAIN_TENTATIVE`), which Item 2 does not modify, and the
`reference_chain` it keys on comes from `extract_feature_chain_segments` (`expression_utils.py`),
also untouched by Item 2. So Item 2 cannot produce an attribute-classification transition.

The distinction the audit hinges on — **does ife_plant exercise a 3+-segment *calc-usage* chain?** —
answers **no**:
- `subsystems.sysml:12` `magnet_volume_total : Real = tf_coil.volume_calc.volume` is a **computed
  attribute** (3-segment, `reference_chain` `["tf_coil","volume_calc","volume"]`) — the attribute
  path, not the reject site Item 2 removed.
- `design.sysml:39` `in magnet_volume = radial_build.magnet_volume_total` is the only ife_plant
  **calc-usage** binding — `source_path` `radial_build.magnet_volume_total`, **one dot / 2 segments**,
  below Item 2's `len(segments) > 2` extraction gate **and** below the backtracker climb gate
  (`source_path.count(".") >= 2`). It never enters either new code path.

So ife_plant is on the attribute path Item 2's design (D2) deliberately declines to touch. The
`EXPOSE_CHAIN_TENTATIVE` gate existed already at the ife_plant capture commit
(`git show 89e6f80:...computed_attribute_extractor.py` contains it), and the file's last modification
(`891cf8e`, prior-epic item5) is an ancestor of Item 2's start
(`git merge-base --is-ancestor 891cf8e 5af442d` → true). Any re-capture flip is therefore a
**pre-existing, prior-epic capture-time drift on the attribute path**, latent because the conformance
suite reads the committed snapshot.

**SC judgment.** Item 2's SC is path-scoped: "no calc-usage-param baseline other than
`deep_cross_scope_probe` changes… no output change for covered models." ife_plant is not a calc-usage
baseline change from the climb/D1, does not exercise a 3+-segment calc-usage chain, and cannot be
altered by Item 2's diff. **No SC violation.** The filed follow-up is a legitimate standalone
re-capture task — but its attribution to "Item-2 multi-hop-chain machinery" is **incorrect**; the
drift predates Item 2 and lives on a path Item 2 never edits (Note 2).

> Caveat on method: I could not run live extraction to observe the flip directly (execution is
> sandbox-blocked here — Note 1). The conclusion does not depend on observing it: Item 2's two-file
> source diff cannot produce an attribute-classification change, whether or not the flip reproduces.

---

## Findings

### Plan completion

All six phases verified complete against the code, tests, baselines, and docs on disk.

- **Phase 1 (pins first).** `test_deep_cross_scope_probe.py` carries both channel-identity pins with
  hardcoded QNs; `test_dependency_backtracker.py` carries the D5 fires-on-shape + silent-on-clean
  pair. The channel constants at `5af442d` (red-first, pre-code) are **byte-identical** to HEAD
  (`git show 5af442d:...` diff) — the oracle was fixed before the code that produces it, exactly the
  R1 independent-anchoring discipline. ✓
- **Phase 2 (extraction, D1).** `usage_extractor.py:717-738` — the 3+-segment arm emits full-path
  CHAIN, N-1 comment present (only `source_path` set), reject warning removed. ✓
- **Phase 3 (climb, D2/D4/M-1).** `dependency_backtracker.py:652-684` — gated
  `source_path.count(".") >= 2`, ancestor-prefix iteration, collect-all distinct hits,
  `_is_self_reference` reuse, M-1 + first-segment-shadowing comment at the site. ✓
- **Phase 4 (Step-4 WARN, D3/M-2).** `dependency_backtracker.py:580-585` — genuine `logger.warning`
  for `"::" not in source_path and count(".") >= 2`, distinct from the sibling DEBUG line, names the
  full untruncated chain + `usage_qn|param`. ✓
- **Phase 5 (re-capture).** Scoped to `deep_cross_scope_probe` only; both wires in the committed
  graph; parity leg added. ✓
- **Phase 6 (docs/R2).** doc 24 CHAIN-dispatch updated (Step CLIMB + Step-4 WARN, lines 76-96);
  matrix REQ-BT-12/13 PASS; `agentic-mbse-impact.md` present. ✓

### Spec conformance

Success Criteria:
- **Both chains resolve to exact channel QNs (independently anchored).** ✓ Committed graph
  `baseline_outputs/deep_cross_scope_probe/computation_graph.json` wires `data_point` →
  `…__derived_calc__derived_value` and `base_metric` → `…__sensor__core__metric_value`
  (lines 199/265); pins assert these exact constants.
- **`deep_cross_scope_probe` pins both as resolved chains.** ✓ `test_pattern_a_..._resolves_to_derived_value_channel`,
  `test_base_metric_..._resolves_to_metric_value_channel`, `test_..._full_path_chain_binding`.
- **Unresolvable deep chain still hard-diagnoses (Item-5 contract).** ✓ D3 home + D5 test.
- **Fires-on-shape + silent-on-clean, both fully tested.** ✓ `test_multihop_fallback_warns_loud_and_untruncated`
  (synthetic dangling chain → WARNING + full untruncated EP) and `test_resolvable_multihop_chain_is_silent`.
  Both are genuine, non-vacuous, scoped to the backtracker logger (avoids the unrelated
  phantom_detector WARN).
- **Live/offline parity.** ✓ `test_live_offline_parity_both_chains` present, `@requires_license`-gated
  as the spec requires; the always-on offline pins are the primary guard.
- **Byte-identity path-scoped.** ✓ Only `deep_cross_scope_probe` moved (Phase-5 commit stat).
- **agentic-mbse impact recorded.** ✓ `agentic-mbse-impact.md` (disposition: no change).

Every `[HARD]` requirement:
- **[HARD] Item-5 loud contract for the unresolvable tail** — met via the approved D3 relocation
  (spec annotated at `:126-132`). Substance (loud WARNING + entry point + never truncated) preserved
  at `dependency_backtracker.py:580-600`.
- **[HARD] Channel-identity for both wires** — met; hardcoded QNs, red-first, `_input_source_qn`
  reads `producer_channel` so a mis-wire to a different channel or a drop to EP both fail the pin.
- **[HARD] Covered baselines byte-identical, path-scoped** — met; only the target fixture changed.
- **[HARD] Three-part re-capture, reviewed** — met; two wires present, stale classification flip
  fully mooted (its two target EPs are exactly the two now-wired params, so zero residue). The
  mooting argument checks out: the flip's substrate (the two unbound EPs) is removed by the wires.
- **[HARD / R1] Every changed diagnostic has fires-on-shape + silent-on-clean** — met (D5 pair).
- **[HARD] Live/offline parity** — met (gated leg + always-on offline pins).
- **[NEED / R2] MODELING_GUIDE impact recorded** — met (in-repo note for later sync).

Non-goals respected: Pattern B untouched (`test_pattern_b_...` unchanged); no shared attribute-path
walk built (D2); no per-hop containment walker; duplicated `unbound_params` cleared by the wires, not
chased separately.

### Design conformance

Implementation follows the design.
- **INV-1** both exact channels — ✓.
- **INV-2 / INV-2b** loud Step-4 WARN + collect-all-and-refuse — ✓ (`:664-682`).
- **INV-3** scoped_lookup-only climb — ✓ (`:678` uses only `scoped_lookup`; ordered after the 1-dot
  `alias_lookup`, and a ≥2-dot chain cannot match a 1-dot alias key, so B3 holds structurally).
- **INV-4** path-scoped byte-identity — ✓.
- **INV-5** three-part reviewed diff — ✓.
- **D1–D5** each realized as specified; the deep-chain arm omits the element refs (N-1) as designed.
- **D3 deviation** from the spec's literal "narrow the reject at extraction" wording is documented in
  spec, design (D3), and design-review (move 6/M-2), and is technically forced (no registry at
  extraction). Honest, not silent.

### Code integrity

No slop or failure-honesty problems in the item's diff.
- The climb is a bounded loop over ancestor prefixes reusing `scoped_lookup` + `_is_self_reference` —
  no new abstraction, no god function, right altitude.
- The Step-4 WARN is a genuine `logger.warning` guarded by an explicit shape test, not a swallowed
  default; the entry-point disposition and fallback QN are unchanged, so the loud+never-truncated
  substance is real.
- The first-segment-shadowing residual is named in a code comment at the climb site
  (`:664-671`), consistent with the filed Non-Goal — a documented assumption, not a hidden silent
  fallback.
- The extraction arm sets only `source_path` with an N-1 comment steering future implementers away
  from re-populating element refs. Clean.

### Test integrity + mutation spot-check

The unit tests are genuine and independently anchored (synthetic registries, no fixture coupling);
the conformance pins compare against constants fixed before the producing code. Not vacuous.

**Mutation spot-check (ambiguity guard).** Target: `dependency_backtracker.py:681-682`
(`if len(climbed) == 1: return next(iter(climbed))`). Mutating to pick-first (`if climbed:` /
`len(climbed) >= 1`) makes `test_climb_refuses_on_two_distinct_channels` fail: that test seeds two
climb-only keys (`a.b.x.y.z`, `a.x.y.z`) reaching **distinct** channels, so `climbed` has two members;
the guard returns `None` (asserted), while pick-first returns one of the channels (non-`None`),
breaking `assert bt._resolve_chain_dispatch("x.y.z", usage) is None`. I traced that Steps 1/1b/1c/2 all
miss on that registry, so the collision is genuinely decided inside the climb. **The guard test
enforces the refuse behavior.**

> Method caveat: this spot-check was performed by tracing the code and test against the mutation
> because test execution is sandbox-blocked (Note 1); it was not run under pytest.

---

## Gates reconciliation

- **Recorded at Item 2 HEAD (30a9bf6):** 2080 passed / 4 skipped / 5 xfailed; ruff 17; mypy 97.
- **Recorded at live HEAD (42aad15):** 2086 passed / 4 skipped / 0 xfailed.
- **Movement:** Item 4 (classifier-fix) landed after Item 2, adding tests and resolving the 5 xfails
  (its plan: "xfail 5->0"). The +6 passed / -5 xfailed delta is consistent with Item 4's documented
  work and unrelated to Item 2. ruff/mypy ceilings (17/97) held across Item 2 per its plan.
- **Independent re-execution:** not possible in this audit environment — see Note 1.

---

## Notes (why PASS-WITH-NOTES, not unqualified PASS)

**Note 1 — Gates verified statically, not re-executed (audit-environment limitation, not an Item-2
gap).** Every `pytest` / `ruff` / `mypy` invocation in this sandbox — via `uv run`, direct venv
binary, or plain `python -c` — requires interactive approval unavailable in a headless run, so no
suite, lint, type-check, or live extraction could be run. All gate claims were verified from committed
artifacts, git history, and code/test reading. The recorded run logs (plan Phase 1-6) are internally
consistent with the code on disk. A follow-up should re-run `uv run pytest tests/`, `ruff check src/`,
`mypy src/` in an environment that permits execution to confirm the live numbers.

**Note 2 — Correct the `[TRUTH-DEBT-IFE-PLANT-CHAIN-STALE]` attribution.** The BACKLOG entry
(`:314-326`) attributes the ife_plant classification drift to "Item-2 multi-hop-chain machinery."
Item 2's source diff is two files, neither on the attribute/classifier path, and ife_plant exercises no
3+-segment calc-usage chain, so Item 2 cannot produce the `expose_pure → expose_chain_tentative`
transition. The drift is a pre-existing prior-epic attribute-path capture staleness (classifier last
changed at `891cf8e`, pre-Item-2; the tentative gate already existed at the `89e6f80` capture). The
follow-up itself (standalone ife_plant re-capture, deliberately not folded into Item 2 or Item 4) is
the right disposition — only the "Item-2 machinery" wording is wrong and should read, e.g.,
"pre-existing attribute-path capture drift, surfaced while checking Item-2/Item-4 baselines." This is a
documentation-honesty fix in a different item's artifact, not an Item-2 defect.

---

## Certification

Verified and certify:
- All six plan phases complete; changes-required and validation items present on disk.
- All spec success criteria and every `[HARD]` requirement met (traced above with file:line).
- Design invariants INV-1..5 and decisions D1..D5 realized; the D3 deviation honestly recorded.
- Independent anchoring genuine (pins byte-identical pre-code); no fake/vacuous tests; the ambiguity
  guard confirmed load-bearing by an analytical mutation spot-check.
- Docs + matrix moved with the code (doc 24 Step CLIMB/WARN; REQ-BT-12/13 PASS, cited).
- Byte-identity held path-scoped; re-capture scoped to the one fixture; three-part diff decomposed.
- Load-bearing ife_plant question adjudicated: no Item-2 SC violation; Item 2 provably cannot affect
  ife_plant.

Left open (not blockers for Item 2):
- Live re-execution of the gates (Note 1) — environment-blocked here.
- Correcting the cross-item BACKLOG attribution (Note 2).
- The filed ife_plant standalone re-capture (`[TRUTH-DEBT-IFE-PLANT-CHAIN-STALE]`) remains a valid P3
  follow-up on its own terms.

**Verdict: PASS-WITH-NOTES.** The item is sound and complete; the notes are transparency about the
audit environment and a mis-attribution in a neighboring artifact, neither of which is a defect in
Item 2's deliverable.

ARTIFACT: .project/active/multihop-chain/audit.md

---

## Orchestrator addendum (post-audit, live execution)

Both notes discharged:

1. **Gates re-run live at HEAD**: 2086 passed / 4 skipped / 0 xfailed; ruff 17; mypy 97.
   (Counts moved from Item 2's own HEAD because Item 4 landed after — reconciled: +6 passed
   from Item 4's new tests/flips, −5 xfailed from the classifier fix.)
2. **Ambiguity-guard mutation executed live**: climb mutated to pick-first →
   `test_climb_refuses_on_two_distinct_channels` FAILS; revert → 4/4 climb tests PASS.
3. **BACKLOG attribution corrected**: [TRUTH-DEBT-IFE-PLANT-CHAIN-STALE] no longer blames
   Item-2 machinery; re-attributed to pre-existing classifier staleness per this audit's
   diff-scope proof.

**Verdict upgraded: PASS** (all notes discharged).
