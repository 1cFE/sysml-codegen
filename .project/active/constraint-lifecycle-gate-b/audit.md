---
date: 2026-07-19
author: Claude (independent audit agent)
topic: "Audit — Gate B vacuity proof and extension-time V11 deletion"
tags: [audit, gate-b, v11, constraint-extension, lifecycle-item-3]
status: pass-with-notes
branch: constraint-exec-epic
commit: 3df2c34
---

# Audit: Lifecycle Item 3 — Gate B vacuity proof and deletion

**Verdict:** Pass with notes
**Audited:** 2026-07-19
**Branch:** constraint-exec-epic
**Commit:** 3df2c34 (candidate = c5cc1b4 + 3df2c34)

---

## Summary

The deletion is correct and the conclusion survives adversarial attack. I tried to build a
model-producible offender the enumeration misses and could not; the one in-memory offender I
produced is the hand-forged object-layer shape decision.md:64-66 already declares out of
reach. Gates are green at HEAD, the deletion is genuinely 3 lines with no other production
change, and the kept tests are real — reverting the deletion turns 5 of them red.

The notes are against the **written proof**, not the decision. Three of decision.md's
supporting citations are weaker than stated: one named extraction block does not exist in
`src/` in the form the record implies, the corpus counts are off by one in two places, and
the mechanism that actually does structural work for QN disjointness is uncited. None of
these move the verdict, because decision.md already frames disjointness as a conditional
with an explicit re-open trigger (decision.md:101-124). They matter because the next agent
to hit the re-open trigger will read those citations as ground truth.

## Findings

### The vacuity enumeration — holds, with citation defects

I attacked all six links independently rather than re-reading the proof.

- **Step 3, mint-path exhaustiveness: closed.** `ConstraintInputResolution` has exactly three
  members (`resolution/models.py:270-275`); MODULE_OUTPUT yields `module_output`, the other two
  yield `entry_point`; aggregator inputs are `module_output` (`constraint_lowering.py:1465`).
  No third path to an appended entry-point-sourced input.
- **Step 4, single writer: confirmed.** `dependency_backtracker.py:603` is the only mutation of
  `fallback_entry_points`. Every other site is initialization (`:263`, `:298`) or a verbatim copy
  (`:391`, `graph_builder.py:446`, `constraint_lowering.py:1503`).
- **Step 5, corpus sweep: reproduces on the load-bearing part, counts are off.** My independent
  sweep gives **34** snapshot models and **847** design-attribute QNs against the record's 35 and
  846. Fallback QNs (**60**) and the intersection (**zero**, per-model and overall) both reproduce
  exactly. The off-by-one is plausibly `tests/fixtures/shared_producer/extraction_snapshot.json`,
  which emits a stale-source-hash warning (see Gates). **Fix:** correct decision.md:51-52 and
  findings.md:151-153 to 34/847, or state the counting basis that yields 35/846.
- **The reuse path is covered, though the enumeration reads as if it is not.** A DESIGN_ATTRIBUTE
  constraint input whose QN is already an *unwired* valueless fallback EP flips it to wired,
  creating a V11 offender with no new mint at all (`mint`'s early return,
  `constraint_lowering.py:1379-1381`; the wired/unwired partition, `graph_builder.py:855-880`).
  Steps 3-4 reason only about newly minted keys, so this path is invisible to them.
  decision.md:58-62 does route it to the step-4 disjointness block, correctly. But it takes a
  careful read to see that, and an in-memory reproduction of this shape is easy to mistake for a
  counterexample. **Fix:** state the reuse path inside the enumeration rather than in the
  trailing note.

**Finding — decision.md:53-55's block (a) is not in `src/`.** The record says "two same-named
members in one namespace are rejected outright at extraction (a renamed control isolates the
duplicate name as the cause)." I could not find that check in `src/` or in
`/home/reid/1cfe/agentic-mbse/src/`. The nearest guard,
`analysis/parameter_groups.py:157-164`, raises only when `prior_raw != raw_name` — it
*structurally exempts* identical names, and it guards sanitizer collapse (`'a b'` vs `'a-b'`),
not duplicate names. findings.md:170-223 does record probes that observed a rejection, and that
observation is consistent with SysIDE / the SysML language rejecting duplicate names in a
namespace — which is a real block, just not the one the sentence describes and not one the
record cites. **Fix:** attribute the block to where it actually lives, or drop the claim and
lean on the second vector alone.

**Finding — the strongest disjointness evidence is uncited, and cuts both ways.**
`analysis/parameter_groups.py:407`, `:436`, and `:460` each compute
`f"{usage.qualified_name}__{param_name}"` — exactly the `{calc_eqn}__{formal}` fallback shape —
and then `continue` if that string is already in `self._attr_index` (the design-attribute index).
Those three guards are doing real structural work: they stop a colliding calc param from ever
becoming an unbound/fallback entry, which is a stronger argument for disjointness than the
empirical zero-overlap. But their existence also shows the codebase treats this collision as
reachable, which sits awkwardly with the record's "blocked at extraction" framing. **Fix:** cite
these guards in the step-4 argument; they are the mechanism, and the corpus sweep is the
confirmation, not the reverse.

**Note — the resolver ladder does not close the gap on its own.** The design-attribute probes at
`resolution/producer_resolution.py:367-380` try `sanitize_qualified_name(reference)`,
`{owner_def_qn}__{ref}`, and `{instance_path}__{ref}`. None probes `{consumer_eqn}__{param_name}`.
So a lenient terminal miss does not by itself prove the minted fallback QN is absent from
`design_attr_by_qn`. This is consistent with the record's conditional framing; it is worth stating
because it is the reason disjointness needs the parameter_groups guards above.

**Note — path citations.** decision.md:51 and :111 cite `producer_resolution.py`; the file is at
`src/sysml_codegen/resolution/producer_resolution.py`, not under `analysis/`. Both cited lines
(`:561` DESIGN_ATTRIBUTE identity, `:462-474` `entry_point_qualified_name` returning
`f"{consumer_eqn}__{key}"`) check out at that path. Bare filenames are the record's convention
elsewhere, so this is only a navigation cost.

**Note — docstring/record say MODELED_DEFAULT, code mints LIBRARY_DEFAULT.** The MODELED_DEFAULT
branch calls `mint(qn, EntryPointType.LIBRARY_DEFAULT, ...)` at `constraint_lowering.py:1418`,
while the function docstring (`:1358`) and decision.md:44 both name MODELED_DEFAULT. The
enumeration is unaffected — the key shape `{constraint_id}__{formal}` is what matters, not the
EP type — but the naming mismatch will mislead.

**No model-producible offender found.** My reproduction attempt set
`fallback_entry_points={COLLIDE}` and the design-attribute QN by fiat at the object layer. That
is precisely the forged shape decision.md:64-66 excludes, so it is not a counterexample. I did
not construct a `.sysml` fixture that produces an intersection, and the parameter_groups guards
above are a plausible reason none exists.

### Deletion reality — clean

- The full production diff across both commits is **one file**: `constraint_lowering.py`,
  11 insertions / 10 deletions. No other `src/` change.
- The collector call, its `raise`, and its name in the local import are gone; no
  `collect_uncovered_params` reference remains in `constraint_lowering.py`. The docstring was
  rewritten to state the no-check property and cite the proof.
- `collect_uncovered_params` survives at `resolution/graph_builder.py:806`, exported at `:1940`,
  with its generation-gate callers intact at `cli/__init__.py:263` (import) and `:278` (call).
- `_validate_channel_references` on the extended graph is unchanged (LC-E03), as is strict actual
  resolution. Both `extend_graph_with_constraints` call sites are untouched.
- No replacement wrapper, differential, scoped variant, or feature flag was added. Confirmed by
  reading the whole diff, not by grep alone.

### Kept evidence — genuinely RED-able

I restored the 3 deleted lines locally and reran the two kept test files. **5 of 14 flip red**,
covering all three claimed pins:

| Test | Pins |
|---|---|
| `test_preexisting_v11_offender_does_not_block_unrelated_constraint` | (a) pre-existing V11 never blocks extension |
| `test_extension_preserves_the_offender_set_exactly` | (a) offender set preserved exactly |
| `test_extension_does_not_widen_the_fallback_set` | (b) extension is coverage-neutral |
| `test_generation_gate_still_rejects_what_extension_now_allows` | (c) generation gate still rejects |
| `test_gate_is_whole_graph_not_constraint_scoped` | (c) gate stays whole-graph scoped |

All five fail with the restored `CodeGenerationError: V11 coverage violations in extended graph`,
which is the right failure — they fail *because* the deleted check fires, not incidentally. The
gate tests also assert the calc module is named in the error (`lcoe_calc` appears in the message).
Working tree restored to clean afterward.

### Gates at HEAD

- **Full licensed suite: PASS.** `3009 passed, 38 skipped, 17 deselected` in 61.75s, 3047/3064
  collected. License load verified by skip-reason grep rather than by count: **zero** `no live
  syside license` skips, and `tests/conftest.py:24-41` gates `requires_license` on a real live
  `load_models()` probe, so every license-gated test executed. All 38 skips are content-based.
- **Premise correction, worth recording.** A deliberately license-less run
  (`env -u SYSIDE_LICENSE_KEY`) produced *byte-identical* results on this machine — same collected
  total, same 3009/38/17. syside resolves a license from somewhere beyond that env var, so
  "collected count looks full" is **not** a valid license detector here. The skip-reason grep is.
  This contradicts the recorded gate method in auto-memory
  (`syside-license-key-explicit-env-needed`); the gate itself still passes.
- **Assertions-off: PASS.** `PYTHONOPTIMIZE=1` on both touched test files: 14 passed. The kept
  evidence does not depend on bare `assert` in production code.
- **mypy / ruff: PASS, zero delta.** HEAD and parent 27425c0 both give 72 mypy errors in 17 files
  (65 checked) and a clean ruff. Full sorted diagnostic lists diffed identical. The 72 are
  pre-existing.
- **Byte-identity: PASS on line numbers and baselines.** The `shared_producer/model.sysml` edit is
  4 added / 4 removed, all inside the `//` header block, file 51 lines before and after; all
  non-comment content is identical *including line numbers*. It is the only fixture/baseline file
  touched by either commit — no snapshot or `baseline_outputs` file moved. Every source location
  recorded in `shared_producer/extraction_snapshot.json` (lines 26, 31, 33, 39, 42, and one
  location at 47:9) points at byte-identical text before and after; the edit sits at lines 12-15,
  above all of them.

**Finding (low severity) — the snapshot's `source_hash` is now stale.** A comment-only edit still
changes file bytes, so `shared_producer/extraction_snapshot.json`'s recorded whole-file SHA-256
now matches only the *pre-edit* file. `snapshot/loader.py:957-978` emits a warning, not an error
("snapshot may be stale ... Continuing; recapture to refresh"), which is why the suite is green.
The "line count preserved so source lines do not move" claim (decision.md:198-199) is true and was
the right precaution — it just does not cover the hash. **Fix:** recapture the fixture, or record
in PROVENANCE.md that this snapshot's `source_hash` is knowingly stale.

### Records

- **decision.md's enumeration matches findings.md.** Every load-bearing number and citation in
  decision.md:36-66 traces to findings.md, including the corpus block quoted verbatim at
  findings.md:151-153. The counts are wrong in *both* documents consistently (see above), not
  divergent between them.
- **The shared_producer resolution is accurate.** I read `tests/fixtures/shared_producer/PROVENANCE.md`
  directly: it labels the fixture "recorded known-incomplete," states "Contract invariant 21 and
  SR-A02 require them to converge on one QN-keyed typed entry point. **They do not**," gives the
  two QNs decision.md:176-180 quotes, and refers completion to Item 4.
  `.project/active/constraint-lifecycle-shared-resolution/evidence.md:61` (SR-R23, "NOT MET —
  referred to Item 4"), `:88`, `:190` (PC-4), and `:318` agree. Item 2 never certified
  convergence for this shape. "Stale header, not an evidence contradiction" is the correct
  reading, and the correction was line-count-preserving as claimed.
- **Epic Item 3 says the settled branch.** c5cc1b4 flipped four success criteria with per-criterion
  evidence pointers and recorded "Complete — vacuity proven, delete branch executed." No checkbox
  over-reaches; each names a real artifact. **Note:** the epic's Scope step 3 still reads as an
  open conditional ("If impossible, delete… If possible, reject only the introduced violation").
  It is correct as the original decision procedure and is resolved by the Status line below it,
  but a reader skimming Scope alone could think the differential is still on the table.
- **LC-E02 is correctly scoped.** The conditional body was replaced with the settled no-check
  statement, the supersession of lowering INV-6, a path-cite to decision.md, and the precondition
  that vacuity holds only while fallback membership stays `{consumer_eqn}__{key}`. LC-E03 and
  LC-E04 appear in the diff only as unchanged context.

**Finding — upstream-filing.md overstates the filing.** Its front matter says `status: filed` and
`:20-21` says "Filed into: `../fusion-tea-stellarator-mbse-demo` (WI-027)." Reality:

```
 M .project/research/20260719-082509_gate-b-root-cause-...md
?? .project/research/20260719-222000_gate-b-upstream-filing-response-from-sysml-codegen.md
```

**Two** files were written into the fusion repo and **both are uncommitted** — the new response
(untracked) and a 12-line insertion into the root-cause report's recommendation 1. Neither
appears in that repo's last three commits. The brief expected these noted as
written-but-uncommitted; upstream-filing.md names neither destination file, does not mention the
root-cause edit at all, and nowhere states the uncommitted condition. `status: filed` reads as
landed in fusion's history. **Fix:** name both files and mark the state as written-but-uncommitted,
or commit them upstream and leave the status as-is.

### Code integrity

No slop or failure-honesty findings. The change is a deletion; it removes a raise rather than
adding a fallback, adds no optional parameter, no broad except, and no compatibility shim. The
rewritten docstring states the no-check property positively and cites its proof, which is the
right shape — it does not leave a reader guessing why the check is absent.

---

## Certification

Verified and marked:

- The enumeration's structure re-derived independently at HEAD; mint-path exhaustiveness and the
  single-writer claim confirmed in code; corpus sweep rerun (zero intersection reproduces).
- Deletion scope confirmed by reading the entire production diff — one file, no other change.
- Kept evidence confirmed RED-able by local revert; 5 tests flip, all for the right reason.
- All four gates rerun at HEAD with actual command output: licensed suite, assertions-off,
  mypy/ruff vs parent baseline, byte-identity including recorded snapshot source locations.
- Records cross-checked against primary sources — PROVENANCE.md and Item 2's evidence.md read
  directly, not via decision.md's summary of them.

Epic Item 3 checkboxes were already marked by c5cc1b4; I verified each against its cited evidence
and am leaving them marked. LC-E02 verified as settled. No checkbox changed by this audit.

The seven notes above are documentation and hygiene defects, not correctness defects. The
recommended order is: block (a) attribution and the parameter_groups citation first (they change
what a future agent believes about *why* vacuity holds), then upstream-filing.md's status, then
the counts, snapshot hash, MODELED_DEFAULT naming, and epic Scope wording.

**Not checked:**

- **Model-producibility of a QN collision end-to-end.** I did not write a `.sysml` fixture that
  attempts to make a design-attribute QN equal a `{calc_eqn}__{formal}` fallback key. My argument
  that none exists rests on the parameter_groups guards plus the empirical sweep, not on a failed
  construction attempt. This is the one place where a determined adversary could still find
  something, and it is the same gap decision.md's re-open trigger already anticipates.
- **The corpus sweep's model coverage.** 34 snapshots swept; 9 fixtures were structurally
  unbuildable and 2 buildable-live only. Those 11 were not swept by me.
- **Runtime behavior of generated packages.** No real-simkit execution of any generated package;
  the generation gate was verified by unit and conformance tests only.
- **The fusion-repo artifacts' content.** I verified their existence and uncommitted state, not
  whether the filing text correctly describes the finding to that repo's audience.
- **findings.md's probe transcripts.** I re-derived the enumeration from source rather than
  auditing whether each recorded probe run reproduces.
- **The 72 pre-existing mypy errors.** Confirmed unchanged, not assessed.
