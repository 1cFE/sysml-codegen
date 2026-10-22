# Spike: can a snapshot carry the screen's facts and replay it? (Item 2b, option 2)

**Date:** 2026-10-20 · **Branch:** `subset-profile-screen` (codegen `eb8d4ca4`; agentic-mbse sibling `e268357f`) · **Upstream:** `spec.md` Open Questions, "How a snapshot carries the screen" and "Scope split trigger"

## Summary of Findings

**Verdict: option 2 is confirmed, with conditions.** Sealing the screen's facts (`SubsetFacts`) and re-running the screen on replay works, and gives live/replay parity once two conditions hold. But under the spec as written, option 2 behaves exactly like option 1 (seal the findings) and costs more. **The split trigger fires.**

What the probes showed:

- **The screen needs nothing but the facts.** `evaluate_subset_profile(facts)` reads only the `SubsetFacts` tree and the packaged rule records. Re-run in a process with `syside` blocked and no license key, it gave byte-identical results on all 269 subjects.
- **The facts round-trip through JSON without loss.** On 269 subjects (all 246 corpus cases and the source trees of all 23 committed snapshots), facts, re-encoded facts, findings and unverified checks all compared equal, 269 of 269. There were no mismatches and no load errors. The tree has 61 types; the runs exercised 59 of them.
- **Size and time.** Facts in a plain named-field JSON form would add about 71% to the 23 envelopes in total (2.95 MB → about 5.0 MB). Per envelope the growth ranges from +19% to +224%. Extraction adds 77% to total capture time (8.2 s → 14.6 s). Almost all of that is the two `catf_mfe` models, about 3 s each.
- **Locations are not portable as captured.** Every file path in the facts is absolute (`///home/...`). `snapshot` capture parses a temporary staged copy, so its paths point at a folder that is deleted after capture. Line numbers are stable.
- **Anonymous elements change identity on every load.** SysIDE gives an anonymous element a new UUID each session. In 1 of 269 subjects, a finding's subject is anonymous, so its result differs between two live runs of the same model. This affects options 1 and 2 alike.

Conditions for option 2 (and, apart from the facts schema, for option 1 too):

1. **Map file paths to portable names on both routes.** Use the same mapper the instance graph uses (`map_live_source_referent`, `analysis/source_referent.py:43`). It already accepts the `///` form and returns `root-0/<file>`.
2. **Compare an anonymous subject by where it is written, not by its UUID.** Parity (Success Criterion 5) must compare by location, not `element_id`.
3. **Version the facts schema.** No version constant exists for `SubsetFacts` today. Codec tests must also build the two types the corpus never produced (`InvocationsFailed`, `ScopeCause`).

**The premise conflict (surfaced, not resolved).** Option 2's one advantage over option 1 is that a replay under a newer profile computes fresh findings. The spec rules that out in two places:

- Success Criterion 8 says a snapshot whose recorded profile version differs from the build reports its findings as not assessed.
- The envelope loader refuses any snapshot whose agentic-mbse or sysml-codegen version differs from the build (`snapshot/envelope.py:455-462`). So facts captured by another release never reach the screen at all.

Under both rules, options 1 and 2 give the same answer on every snapshot. Option 2 still fits the recorded premise that snapshots are a serialization choice (ADR 0011 "Why"): it seals inputs and recomputes, as replay already does for the graph. Its benefit only becomes real if design also changes Success Criterion 8 and the package-version check. That is a design decision that touches an approved criterion.

**Effort and the split trigger.** The snapshot half is about 5.5–6 engineer-days under option 2, 4.5–5 under option 1, and 0.5–1 under option 3. The item's estimate is 6–10 days for all of 2b, and the live half is not small (rough guess 6–8 days; not estimated with care here). The trigger fires on both counts:

- Option 1 or 2 does not fit in the estimate.
- The format decision is still open. The owner's website question has to be answered before any new envelope format is committed (spec R2-5). And the choice between options 1 and 2 depends on the Success Criterion 8 question above.

Recommendation: split the snapshot half into its own item. The live half ships first and reports screen findings on replay as not assessed (option 3), as the spec's trigger already describes.

## Question / Goal

The bet under test was the spec's option 2: "seal the screen's facts (`SubsetFacts`, agentic-mbse `sysml/subset_facts.py`) into the snapshot and re-run the screen on replay" is feasible and gives live/replay parity.

- **What would confirm it:** the screen needs only the facts; the facts survive JSON exactly; a license-free re-run reproduces the live result; and the cost is bounded.
- **What would kill it:** the screen needs live SysIDE state, or the round-trip loses something that changes findings.

## Evidence per question

### 1. What the screen consumes, and where the facts come from

The screen reads only `SubsetFacts`, the packaged rules and the roots it is told to use.

- **Entry point.** `evaluate_subset_profile(facts, rules=PACKAGED_RULES, roots=GENERATOR_ROOTS)` (agentic-mbse `sysml/subset_profile.py:1402`). It reads nothing else: no parse tree, no SysIDE handles, no document paths, no elaborated graph.
- **Rules.** They come from the packaged `subset_profile_rules.toml`, loaded at import (`:1315`).
- **Roots.** Generator roots come from the facts themselves (`facts.occurrence.generator_root_ids`).
- **Constraint count.** One path goes further: `_unassessed` (`:1393`) runs `evaluate_identified_profile` (`executable_profile.py:1048`) over `facts.constraints`. That is also pure data.
- **The module is pure.** Its docstring says it "imports no SysIDE" (`:4`). Its imports match: `errors`, `executable_profile`, `fact_refs`, `occurrence_facts`, `subset_facts`, and the standard library.
- **Extraction needs the live model, and so the license.** Facts are extracted by `extract_subset_facts(model)` (`sysml/subset_extraction.py:480`) from a model loaded by SysIDE. The corpus helper does `SysideAdapter.load_model` and then `extract_subset_facts` (`tests/helpers/subset_profile/observe.py:371-378`).
- **Where capture would run it.** Today `capture_instance_graph_snapshot` (`snapshot/capture.py:17`) loads staged copies through `SysMLDataExtractor` (`orchestration/elaborated_pipeline.py:236`). Extraction would run on that same `extractor.model`, which `time_capture.py` does.
- **One import wrinkle.** Decoding the facts needs the class `IdentifiedConstraintFacts` (the `constraints` field). It is defined in `constraint_extraction.py:147`, which imports `reference_use` and `syside_adapter`. Those modules import `syside` only lazily, so a license-free process with `syside` blocked still decodes and screens (probe below). Blocking the SysIDE-side agentic-mbse modules themselves breaks decoding.
- **Proof:** `replay_unlicensed.py` ran with `env -u SYSIDE_LICENSE_KEY` and `sys.modules["syside"] = None`. It printed `replayed 269: 269 byte-identical, 0 differ` and `syside imported: False`.

### 2. Does the JSON round-trip lose anything?

Nothing was lost on any subject.

- **The codec.** `factcodec.py` is a generic, type-tagged JSON codec, written for the spike only. It covers dataclasses, enums, UUIDs, tuples, frozensets, maps and floats (stored as exact hex). It is not a schema proposal; it only proves the tree can round-trip.
- **The probe.** `probe_roundtrip.py` loads each subject live, extracts facts, screens, encodes, decodes and screens again.
- **Subjects.** 269 in total: all 246 corpus cases (`cases.all_answers()`; 154 packaged in agentic-mbse, 92 in codegen) and the 23 committed snapshots' source trees.
- **Finding the snapshot sources.** `resolve_sources.py` matched each envelope's sealed sha256s. 22 sources are in `tests/fixtures/`. `catf_mfe_d5` has no committed source tree, so it was regenerated byte-for-byte into `regen/` with `scripts/make_d5_variant.py`'s `build_variant_tree` (all sha256s match).

| check (all 269 subjects) | result |
|---|---|
| model loaded without errors | 269 / 269 |
| `facts == decode(encode(facts))` | 269 / 269 |
| `encode(decode(encode(facts))) == encode(facts)` (byte-for-byte) | 269 / 269 |
| `screen(facts) == screen(roundtrip(facts))` (dataclass equality) | 269 / 269 |
| findings, encoded JSON, byte-for-byte | 269 / 269 |
| unverified checks, encoded JSON, byte-for-byte | 269 / 269 |
| `repr` of whole result equal | 269 / 269 |
| license-free replay (SysIDE blocked) equals the live result | 269 / 269 |

There were no mismatches to list.

What the 269 subjects cover:

- **Verdicts.** Corpus: 143 clear, 64 refused, 21 refused-incomplete, 17 incomplete, 1 unconfirmed. Snapshots: 23 clear.
- **Findings.** 376 findings and 72 unverified checks in total. 38 subjects have unverified checks.
- **Types.** `type_coverage.py` walks the type hints from `SubsetFacts`: 61 types are reachable and the runs produced 59. Never produced: `InvocationsFailed` and `ScopeCause`, which are both failure paths. Their round-trip is not demonstrated.
- **What makes order safe.** Every fact tuple is sorted by its `sort_key` and checked in `SubsetFacts.__post_init__`. The only unordered field, `enumerated`, is a frozenset, which the codec sorts.
- **Identity.** Identity is preserved: UUIDs, including the session-local ones, are carried as strings.

### 3. Size and time

**Size** (`size_report.py`, table in `out/size_report.md`):

- The spike codec's tagged form is an upper bound. The "plain" form drops the type tags, which is close to what a named-field schema costs.
- With file paths rewritten to `root-0/...` referents, as condition 1 requires, the plain facts total about 2.09 MB against 2.95 MB of envelopes, or **+71%**.
- Per envelope the growth runs from +19% (`solar_battery_d5`, 1.10 MB envelope) to +224% (`sample_model`, 1.5 KB envelope).
- The largest envelope after the change would be `catf_mfe_gated`, at about 1.48 MB (+102%).
- Expression sites and constraint facts dominate. For `catf_mfe_d5`: sites 400 KB, constraints 152 KB, occurrence 88 KB.

**Time** (`time_capture.py`, table in `out/time_capture.md`; best of 3, after one warm-up capture):

- **How it was measured.** Extraction ran on the same staged model that capture loaded.
- **Totals.** Capture of all 23 trees takes 8.24 s today, and extraction adds 6.33 s (**+77%**).
- **Where the time goes.** Nearly all of it is `catf_mfe_d5` (3.68 s → +3.24 s) and `catf_mfe_gated` (3.30 s → +2.83 s). Everything else adds 0.002–0.08 s, or 12–50% of a capture that takes under 0.7 s.
- **Encoding cost.** Encoding and decoding the facts cost milliseconds and are not counted.
- **Live route.** `generate` and `check` would pay the same extraction cost on every live run under any option, because the screen has to run there.

### 4. Are finding locations stable on another machine?

No, not as captured. With the two fixes below they are.

- **Absolute paths.** `SafeLocation.file` comes from `SysideAdapter.get_source_location` (`syside_adapter.py:576`). That function strips `file:` from the document URL, which leaves `///home/reid/.../model.sysml`. All 4,917 path strings in the facts are absolute. 53 of them sit outside a `file` field, as the `(file, line)` tuple in `InvocationUse.location`. None point outside the subject root: no standard-library paths.
- **Capture paths are temporary.** Capture loads staged copies, so sealed facts would hold paths in a deleted temp folder. The staged run (`runC_staged`) shows `///tmp/spike-stage-.../model.sysml`.
- **The paths can be fixed.** With the root prefix replaced, the staged run and the direct run gave identical results on all 269 subjects, so line numbers and everything else are stable across a move. The graph already solves this for its own `source_file` with `map_live_source_referent` (`analysis/source_referent.py:43`). That function maps both `///home/.../sample_model/simple_calc.sysml` and `/home/.../simple_calc.sysml` to `root-0/simple_calc.sysml` (checked). The live route builds the same kind of map (`_live_source_referents`, `elaborated_pipeline.py:378`), so both routes can map to the same names.
- **Anonymous UUIDs are not stable.** `ElementRef` gives an anonymous element "a session-local UUID" (`fact_refs.py:21-25`). Comparing runs A and B, two separate processes: all 269 results are equal after path normalization except `blocked-predicate-unmapped-code__anonymous_assert_by_reference`, whose one finding's subject is anonymous. With anonymous UUIDs replaced by ordinals, 269/269 are equal. 3 subjects hold anonymous refs in their facts, and only that one carries one into a finding.
- **What that means for parity.** Replayed facts carry the capture session's UUID and a live `check` carries its own, so no option can make them match byte-for-byte. The findings' own sort key already orders by file, line and qualified name before `element_id` (`subset_profile.py:741-750`). So comparing by location works.

### 5. What could make option 2 worse than option 1 or option 3

- **Its advantage is switched off by the spec (premise conflict, surfaced above).** Fresh findings under a newer profile need two things: a snapshot that loads under the newer build, and a criterion that lets the screen run on it. The exact package-version check (`envelope.py:455-462`) blocks the first across releases. Success Criterion 8 blocks the second within one release. With both in place, options 1 and 2 give identical answers.
- **It makes agentic-mbse's fact types part of the snapshot format.** Those 61 types span 9 modules (`subset_facts`, `occurrence_facts`, `fact_refs`, `invocation_allowlist`, `constraint_extraction`, `constraint_facts`, `expression_ir`, `expression_facts`, `errors`), and they are internal to agentic-mbse. Any field change becomes a snapshot format change. The schema needs a version, and no constant exists for it; adding one in agentic-mbse `src/` needs a gate rerun (spec [HARD]). Only the neutral constraint part already has a versioned codec (`constraint_facts.serialize/parse`, `constraint-facts/v3`). Option 1 seals a much smaller surface: findings, unverified checks and the verdict.
- **It is bigger.** +71% total, against small findings for option 1 and nothing for option 3. Only the `catf_mfe` envelopes reach about 1.5 MB.
- **Capture gets slower.** About +3 s on each `catf_mfe` capture. Option 1 pays the same extraction cost, plus a screen run that is cheap. Option 3 adds nothing.
- **Old extraction stays frozen in the snapshot.** Replay re-runs the rules, not the extraction. A fix to how facts are read reaches a snapshot only after recapture, under every option.
- **Shared by options 1 and 2, not a difference between them:** path rewriting, the anonymous-identity comparison, a new envelope version that refuses v6 by name, recapturing all 23 fixtures (`catf_mfe_d5` needs its source tree regenerated first), and the owner's website question (R2-5).
- **What option 3 gives up.** A license-free replay can never report ready. In today's fixtures that matters for all 23 snapshots: every one would come back "not ready" with the whole screen not assessed, including the 19 with no findings. 4 snapshots do have findings: `catf_mfe_d5` (51 admitted, 68 omitted), `catf_mfe_gated` (48 admitted, 68 omitted), `constraint_domain_satisfy_calc_def` (1 admitted) and `constraint_non_numerical` (1 excluded, 1 omitted).

### 6. Effort for the snapshot half, and the split trigger

Engineer-day estimates for the snapshot half. These are judgment, not measured.

| work | option 2 (facts) | option 1 (findings) | option 3 (keep v6) |
|---|---:|---:|---:|
| Explicit, versioned codec and strict decoder, with tests that build every type (including the 2 unexercised) | 1.5–2 | 0.5–1 | — |
| Envelope v7: a screen section covered by the integrity digest, a by-name refusal of v6 with a recapture message, extraction during capture, a not-assessed record on failure or skew | 1.5 | 1.5 | — |
| Referent rewrite on both routes, and the location-based comparison for anonymous subjects | 0.5 | 0.5 | — |
| Recapture 23 fixtures (regenerate `catf_mfe_d5`'s sources), update provenance notes, rerun the study-layer tests that use `station.snapshot.json` | 1 | 1 | — |
| Parity and isolated-artifact tests (Success Criteria 5, 6, 8), licensed lane | 1 | 1 | 0.5–1 |
| **total** | **5.5–6** | **4.5–5** | **0.5–1** |

The item's estimate is 6–10 days for all of 2b, both halves. The live half carries the shared preparation path, `check`, moving `PARAM_FIELD_COLLISION`, handling skew, computing disagreements, sentinel tests across four flag sets, and baseline reruns. I put it at a rough 6–8 days. I did not break it down, so treat that as a guess.

**The split trigger fires**, on both of its conditions:

- **Over the estimate.** The live half plus option 1 or 2 comes to 10.5–14 days, past the 10-day ceiling even at the low end.
- **The format decision is still open.** Committing a new envelope format first needs the owner's answer on the website (spec R2-5). Choosing between options 1 and 2 needs a ruling on Success Criterion 8 and the package-version check.

## Log

Commands were run from the sysml-codegen root with the license sourced: `set -a; source ../agentic-mbse/.env; set +a`.

1. **Read the screen and its inputs:** `subset_profile.py` (the evaluator, `:1402-1481`), `subset_facts.py`, `fact_refs.py`, `occurrence_facts.py`, `subset_extraction.py:480-546`, `syside_adapter.py:576-595`, `constraint_extraction.py:129-153`.
2. **Read capture and the routes:** `snapshot/capture.py`, `orchestration/elaborated_pipeline.py:130-290, 378-392`, `snapshot/envelope.py:430-470`.
3. **Found the snapshot sources:** `python3 resolve_sources.py` gave 22 OK and `catf_mfe_d5` MISSING. Regenerated it with `build_variant_tree(tests/fixtures/catf_mfe_model → regen/catf_mfe_d5, ['pumping_speed_total'])`. Rerun: 23/23 OK (`sources.json`).
4. **Round-trip, run A:** `uv run --extra dev python probe_roundtrip.py out/runA --dump-facts`. 269 ok, in about 9 s.
5. **Run B (second process):** `probe_roundtrip.py out/runB`. **Run C (staged copies, as capture does):** `probe_roundtrip.py out/runC_staged --stage`. Both 269 ok.
6. **Cross-run comparison:** compared `result_normalized_sha` and `result_anonfree_sha` across A, B and C. Normalized: 1 differs (the anonymous subject above). Anonymous-free: 0 differ.
7. **License-free replay:** `env -u SYSIDE_LICENSE_KEY uv run --extra dev python replay_unlicensed.py out/runA`. 269/269 byte-identical. A first attempt that also blocked the SysIDE-side agentic-mbse modules failed in decoding, at the `constraint_extraction` import (see Q1).
8. **Size:** `python3 size_report.py out/runA` (→ `out/size_report.md`), plus an inline rerun with the root prefix replaced by `root-0` (+71% total).
9. **Time:** `uv run --extra dev python time_capture.py` (→ `out/time_capture.md`).
10. **Types:** `uv run --extra dev python type_coverage.py out/runA` reported 61 reachable types, 59 observed.
11. **Path scan:** an inline scan of `out/runA/*.facts.json` found 4,917 path strings, 53 outside a `file` field, and none outside the subject root.
12. **Referent mapper:** an inline call of `map_live_source_referent` on the `///` and `/` forms returned `root-0/simple_calc.sysml` for both.

## Reproduction

Everything is in this folder and is throwaway. `out/run*/` and `regen/` are git-ignored because they hold machine-specific absolute paths (about 14 MB). Regenerate them as follows, from the sysml-codegen root:

```bash
S=.project/active/subset-profile-screen/spike-snapshot
set -a; source ../agentic-mbse/.env; set +a
uv run --extra dev python -c "import sys; sys.path.insert(0,'scripts'); from pathlib import Path; import make_d5_variant as m; m.build_variant_tree(Path('tests/fixtures/catf_mfe_model'), Path('$S/regen/catf_mfe_d5'), m.refused_formals('catf_mfe_model'))"
python3 $S/resolve_sources.py                                              # expect 23 OK
uv run --extra dev python $S/probe_roundtrip.py $S/out/runA --dump-facts   # expect 269 "ok" lines
uv run --extra dev python $S/probe_roundtrip.py $S/out/runB
uv run --extra dev python $S/probe_roundtrip.py $S/out/runC_staged --stage
env -u SYSIDE_LICENSE_KEY uv run --extra dev python $S/replay_unlicensed.py $S/out/runA   # expect 269 byte-identical
python3 $S/size_report.py $S/out/runA
uv run --extra dev python $S/time_capture.py
uv run --extra dev python $S/type_coverage.py $S/out/runA
```

Each run's `summary.json` holds one row per subject: every equality flag, sizes, timings, verdict, counts, and the normalized and anonymous-free result hashes used for the cross-run comparison.

## What I did not check

- **Other fixture roots.** Only the 246 corpus cases and the 23 snapshot sources were run, not the other fixture roots under `tests/fixtures/` (the `model_roots()` set in `fixture_classes.py`).
- **Another machine.** Nothing ran on a second machine. Portability is inferred from the staged-copy run (a different absolute root, same bytes) and from the referent mapper.
- **Live versus snapshot `check`.** `check` does not exist yet. Parity was checked screen against screen, not through `check --from-snapshot` against `check --models`.
- **Replay under a newer profile.** Not tested: there is no newer profile, and the spec currently forbids it (Q5).
- **Two failure types.** `InvocationsFailed` and `ScopeCause` never occurred, so their round-trip is untested.
- **Timing noise.** Timings are from one machine, best of 3, warm. Cold-start SysIDE load is excluded.
- **The live half's effort.** Not estimated in detail; 6–8 days is a guess.
- **The website.** I did not look for the owner's website artifacts; that question stays with the owner (R2-5).

## Open Questions / Follow-ups

- **For the orchestrator or owner: which snapshot option?** It turns on whether replay should recompute findings under a newer profile (option 2's only advantage). If yes, Success Criterion 8 and the package-version check both have to change; if no, option 1 gives the same behaviour for about one day less. Either way it belongs in the split-off snapshot item.
- **Where the facts-schema version lives.** If option 2 is chosen, a version constant is needed. In agentic-mbse it means a gate rerun; in codegen, a hash of the fact types' field lists could stand in.
- **Possible small fix: move `IdentifiedConstraintFacts` and its two sidecar types** out of `constraint_extraction.py` into a pure module, so replay never imports a SysIDE-side module. This would be an agentic-mbse change, with a gate rerun.
