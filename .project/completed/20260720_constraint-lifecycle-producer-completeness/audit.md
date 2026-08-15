# Audit: Producer Completeness and Stellarator Rollup (Lifecycle Item 10)

**Verdict:** Certify — with one surfaced Major (completeness-check guarantee gap; owner ruling requested)
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic
**Commit:** codegen `af3a4d2` (fix commits `1f0c47b` + `ce09bb2`; evidence `cfd8295`); stellarator `342cc799` (code frozen at `c2f10960`, `342cc799` is the anticipated diagnostic-snapshot refresh); agentic-mbse `4c18d61`, teax `07eb0ac` unchanged

---

## Summary

The item delivers its acceptance, and I reproduced the load-bearing claims independently rather
than trusting the evidence. The 2956-test corpus is green on this machine; I reran
`run_stellaris_single.py` in the standard exec env and got six bit-exact anchors, five satisfied
verdicts, single-pass, oracle reldev `0.00e+00`; the bridge, glue-2, and handshake rollup glue are
absence-checked gone; WI-027's D7 supersession pointer is in place. The three-part resolver fix
(per-child `:>>` capture → dual-scope row-13 follow → transitive instance-scoping) is real, general,
and byte-clean, and the chained-aggregation fixture asserts channel identity structurally.

One finding stands, and it is exactly the one the audit brief told me to attack. The
producer-completeness check is **not** a guaranteed guard against every leaf-name guess: it flags
the tier-2 design-attribute leaf rows but exempts *all* `MODULE_OUTPUT` outcomes, so a
qualifier-dropping collapse through the **channel-tier** name-based rows (`leaf_parent_scoped` /
`leaf_consumer_scoped`, rows 14–15) resolves to a wrong channel and passes the check. This does not
affect the delivered stellarator acceptance (row 13 fires there, and I reproduced the exact
numerics), and no current fixture trips it — but the "the completeness check is the loud guard, so
the reverted global refusal is unneeded" rationale is not airtight. Surfaced per Capture-Fidelity
Law 4, not resolved.

## Findings

### Plan completion (design's folded-in phased plan)

All four phases verified complete.

- **Phase 0 (RED-first ambiguous/defaulted):** `tests/conformance/test_producer_completeness_acceptance.py`
  drives a genuine two-same-leaf tie through the real `resolve_producer` under capture; the check
  names the ambiguity and the exact-QN escape resolves clean. Passed in the corpus run. The
  snapshot-route fixture (`tests/fixtures/two_same_leaf_producers/`) is authored with its capture
  documented-deferred, not silently skipped.
- **Phase 1 (cross-part aggregation routing):** `_route_crosspart_formula_aggregations`
  (`pipeline_builder.py:750`) is the Step-4.7 routing. The key fires strictly on FORMULA-classified +
  not-compiled + `singleton_terms` present (`:775`, `:790`) — provably disjoint from
  EXPOSE_PURE/tentative (never reach the FORMULA arm) and from `:>>` aggregations (they are
  `RedefinitionData`, not computed attributes). The transitive fixpoint (`:799-814`) pulls
  aggregation-composing local sums (`total_capital = direct_capital + …`) into instance scope; a
  pure-local FORMULA referencing nothing routed is untouched, which is why a cross-part-free corpus
  sees zero reroutes.
- **Phase 2 (capture sink + check):** verified below.
- **Phase 3 (stellarator cutover) + Phase 4 (deletion/evidence):** anchors reproduced; deletions
  absence-checked; WI-027 amended.

### Spec conformance

- **SC1 — Ambiguous/defaulted acceptance exists and is RED-first.** Met. The named error is the
  *check's* (firing on `ambiguous_candidates`), not a new resolver raise — matches Minor-6 intent.
  The consuming reference is the bare-leaf lenient form that actually ties.
- **SC2 — Producer completeness explicit, deterministic, independent of V11.** Met **as mechanism**;
  the guarantee has a documented hole. The check is real, reads the capture sink (no re-resolution),
  and is independent of V11 (a separate reader over resolver outcomes, not the graph scan). But
  "every model-derived consumed value resolves to one intended producer under exact identity" is
  **not fully enforced** — see Major 1. Marked with that caveat, not as a clean pass.
- **SC3 — Cross-part aggregation as a real graph producer, no bridge / placeholder / D7 / harness
  mutation.** Met. `direct_capital` / `total_capital` are `ModuleKind.AGGREGATION` producers; I
  reproduced the rollup numerics from the graph (single execute_pipeline call, no Python rollup).
- **SC4 — Stellarator generates publicly, numerics unchanged.** Met and independently reproduced —
  six anchors bit-exact, oracle reldev `0.00e+00`, five verdicts `satisfied`.
- **SC5 — WI-027 amended, D7 removed, bridge/placeholder/glue retired.** Met.
  `WI-027…/design.md:2,15-20` carries the `superseded-by-Item-10` status and the D7→D-2 supersession
  pointer; bridge/glue absence-checked.
- **SC6 — Named workarounds deleted, no parallel producer / compatibility wrapper.** Met. Only the
  aggregation path produces the rollup; no rollup-specific resolution arm was added (the fix lives in
  the general resolver row 13 + extraction capture).

Non-goals respected: no canonical `models/` viability edit, no new physics constraints, no numeric
re-baseline (anchors reproduced, not moved), Item-1 artifacts untouched.

### Design conformance

Implementation follows the corrected design, and the two review Majors it was resthaped around are
genuinely closed.

- **Capture sink (Major 1) — implemented better than reviewed, honestly.** The review asked for
  per-site threading through the enumerated `resolve_producer` call sites. The implementation
  centralizes capture *inside* `resolve_producer` (`producer_resolution.py:632-636`). I confirmed
  there are exactly five call sites (`constraint_lowering.py:174`, `dependency_backtracker.py:596`,
  `graph_builder.py:1403`, `:1640`, `:1663`) and that `_run_resolution` is called *only* from the
  wrapper — so no site can bypass the sink. This closes the R2 blind spot by construction, a real
  improvement, correctly claimed. (A STRICT miss raises before the sink; that path fails loudly
  anyway — acceptable.)
- **Producer-registration precondition + structural assertion (Major 2).** A7 holds: Phase-1b
  registers aggregation channels before module build, and
  `tests/conformance/test_crosspart_rollup_twolevel.py` asserts the outer inputs wire to
  `source_type == "module_output"` with distinct per-instance `producer_channel` identities
  (bases 3 ≠ 5 rule out a value coincidence). This is the structural proof the design demanded, and
  it now lives in a fixture rather than only on the live stellarator.
- **Decision-1 premise correction (mid-implementation, unreviewed) — verified sound.** The three-part
  fix is real and general: `extract_child_usage_redefinitions` (`hierarchy_resolver.py:102`) captures
  the child part-usage `:>>` CHAIN redefinitions that were absent (the "0 of 22" gap);
  `_chain_redefinition_follow` (`producer_resolution.py:363-413`) follows them per instance and tries
  both child-owned and instance-level sibling scope, neither dropping the qualifier; the transitive
  fixpoint handles the composing sum. The reverted global `_leaf_unique` refusal is documented in
  place (`producer_resolution.py:484-493`) with its rationale — row 13 resolves first, so the refusal
  was unneeded for the stellarator.

### Code integrity

**Major 1 (surfaced — the audit brief's attack, confirmed real). The producer-completeness check
does not guarantee it catches every leaf-name guess; the channel-tier name-based rows are a blind
spot.** `producer_completeness.py:check_producer_completeness` flags `LEAF_NAME_GUESS` only when
`outcome is Outcome.DESIGN_ATTRIBUTE and key_form in {dotted_pair, leaf_unique, bare_name_unique}`.
It treats **every** `MODULE_OUTPUT` outcome as conformant regardless of `key_form`. But rows 14–15,
`_leaf_parent_scoped` / `_leaf_consumer_scoped` (`producer_resolution.py:347-360`), are CHANNEL-tier
lenient rows whose own docstrings say the reference's owner "is never consulted, so `Pkg::PartA::x`
and `Pkg::PartB::x` construct the same key" — i.e. they drop the qualifier and leaf-match, exactly
the defect `_leaf_unique` commits one tier down. Construct the shape the brief asked for: row 13
misses (a cross-part `X.attr` term whose per-child `:>>` was not captured) and a channel named `attr`
exists under the consumer's parent/consumer scope. The term resolves to that **wrong** channel as
`MODULE_OUTPUT` via `leaf_parent_scoped`, and the completeness check passes it as conformant — a
qualifier-drop collapse it is blind to. So the answer to "is the check guaranteed to catch it?" is:
for the design-attribute `leaf_unique` path, yes; for the sibling channel-tier rows, **no**.
*Why this is a surface-and-rule, not a fix-now:* rows 14–15 are relied-upon lenient rows for
legitimate single-instance resolution (the same reason the global `_leaf_unique` refusal was
reverted), so tightening them is a design call, and invariant 26 names "leaf-name guess" without
distinguishing tier. It does **not** affect the delivered acceptance (the stellarator resolves at row
13; I reproduced the exact anchors), and the check is a diagnostic, not a hard generation gate
(evidence acknowledges this). Recommend: state in the check's contract that its guarantee covers the
design-attribute tier only, and route the channel-tier gap to the invariant-26 owner.

No other integrity issues. The sink is inert outside a `capturing_resolutions()` block, so generation
behavior is unchanged; the check reads and does not re-resolve; no broad excepts or compatibility
shims were introduced; the routing key is a structural property, not a name/role special-case.

### Evidence honesty

Accurate, with one stale note to flag (not a defect).

- The anchor table, the "2956 pass," the five-call-site centralization, and the deletion inventory
  all reproduce.
- **CAS10 divergence:** honestly disclosed as a masked simplification now shown, not a regression.
  WI-025 made buildings/precon SysML forward-computed, so the single-pass handshake computes CAS10 at
  1cfe's powers and diverges (+46%), propagating to the handshake's direct/total/lcoe *comparison*
  rows. The six **anchors** are a different surface and are unaffected — I reproduced them bit-exact.
  The disclosure is faithful.
- **Stale note (flag):** the evidence's Phase-3 "🛑 SURFACED" block says
  `handshake_comparison.json` was *not* refreshed pending an owner call. Stellarator commit
  `342cc799` ("refresh handshake_comparison.json for the single-pass handshake") — the
  diagnostic-snapshot commit the audit brief anticipated as landing concurrently with frozen code —
  did refresh it. The evidence text was not updated to reflect that the owner call was made and the
  snapshot regenerated. Cosmetic; the code surfaces are frozen at `c2f10960` as stated.

---

## Certification

Verified and reproduced independently:

- **Byte-identity corpus:** `tests/unit` + `tests/conformance` = 2956 passed / 47 skipped / 0 failed,
  licensed, on this machine.
- **Anchors + verdicts:** reran `run_stellaris_single.py` in the agentic-mbse venv with teax-simkit on
  `sys.path` and the license sourced — six anchors bit-exact, five verdicts satisfied, single-pass,
  oracle reldev `0.00e+00`. No two-pass overwrite exists in the runner.
- **Resolver fix:** per-child `:>>` capture, dual-scope row-13 follow, and the transitive fixpoint read
  and confirmed in source; chained-aggregation structural channel-identity assertion passes.
- **Capture sink:** exactly five `resolve_producer` call sites, all covered by the centralized sink;
  no `_run_resolution` bypass.
- **Deletions:** `bridge_v11_generate.py` absent; `run_stellaris.py` glue-2 gone (glue-1 + shared
  helpers only); `handshake_1costingfe.py` rollup glue retired with no `set_params` call; MR-WI027-2
  viability grep bar returns zero; WI-027 D7 supersession pointer present.
- **Scope:** only four codegen `src/` files touched across the Item-10 commits, all additive Item-10
  surfaces; items 1–9 behavior held by the green corpus.

Marked: spec SC1, SC3, SC4, SC5, SC6 as verified-met. SC2 marked **met-as-mechanism with a documented
guarantee gap** (Major 1) — not a clean pass.

**Not checked:**
- The full 15+-fixture per-fixture byte-diff enumeration (Major 3) was not re-run fixture-by-fixture;
  I relied on the green corpus plus the routing-key disjointness argument in code, not an individual
  generated-byte diff per fixture.
- The stellarator public generation (`sysml-codegen generate --from-snapshot`, EXIT 0, 34 modules) was
  not re-executed from scratch; I reproduced the *downstream* numeric run against the already-generated
  package, not the generation step itself.
- The snapshot recapture (v5, five constraint facts, no Gate B abort) was not re-performed; taken from
  evidence.
- The `two_same_leaf_producers` snapshot-route capture remains deferred (documented), so the
  ambiguous-fixture snapshot path is proven only on the live route.
- agentic-mbse and teax were confirmed unchanged by rev, not re-audited.
- The channel-tier completeness gap (Major 1) was reasoned from the source and the rows' own contracts;
  I did not author a fixture that trips it (none in the corpus does).
