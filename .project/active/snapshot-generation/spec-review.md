# Spec Review: Snapshot-Driven Generation (SC-9 + SC-10)

**Spec:** `.project/active/snapshot-generation/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/snapshot-generation/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound.** The spec is about the right work item, frames the license-expiry problem accurately, and correctly narrows SC-10 to the CalcUsage auto-impl path (FORMULA and aggregation already survive a snapshot — verified against the loader/serializer and the research report). I traced the core mechanism through the code: `compilation_results` is genuinely absent from the serializer today (`snapshot_serializer.py:68-85`, and `grep` of the committed `solar_battery` snapshot returns zero), generation consumes only the baked `module.auto_impl_context` (`stencils.py:173`) rather than `ctx.compilation_results`, so threading `compilation_results` into `build_computation_graph(...)` is the right lever and preserves the "generation only sees ComputationGraph" boundary. The spec would not badly mislead design.

The full audit below surfaces one class of problem the spec has wrong — the byte-identical criterion rests on a provenance guard that names the wrong provenance — plus several real gaps (helper-migration scope, the PipelineContext wrapping the spec calls a "reuse," CLI `--models required=True`). These are Revise-level, not Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The provenance-guard `[HARD]` (spec lines 135-140) names the wrong provenance, and its self-assigned verification comes back clean for the wrong reason.

- The guard lists "banner text, `captured_at`, a 'generated at' timestamp" as the artifact-embedded provenance to keep out, and asks design to "verify current generation already embeds no such timestamp."
- I verified the timestamp question: the only generation-time timestamp is `generation_timestamp` in `src/sysml_codegen/templates/pydantic_schema.py.jinja2:8`. That template is **dead** — `grep` for `pydantic_schema` across `src/` and `tests/` returns zero render sites. So no timestamp reaches output today. The guard's stated concern is already satisfied — but by accident, and the template is a latent trap: wire it in and byte-identity breaks silently.
- The provenance that **is** embedded and **does** diverge is the source path. Generated modules, schemas, and stencils all emit `SysML Source: {module.source_file}:{module.source_line}` (`modules.py:78`, `schemas.py:43`, `stencils.py:66`), and `computation_graph.json` serializes `source_file` per module. Live extraction sets `source_file` from the parser's document path (`extractor.py:113`, `pos.file`), while the serializer bakes it **relative to the fixtures dir** at capture (`snapshot_serializer.py:102-108`; the committed `solar_battery` snapshot stores `solar_battery_model/design.sysml`). A live `generate --models <path>` and a `generate --from-snapshot` will embed **different `source_file` strings** unless the design normalizes them.
- Net: the guard should be rewritten to (a) name `source_file` path provenance as the actual byte-identity hazard and require it be normalized or made identical across both paths, and (b) note the dead `pydantic_schema.py.jinja2` timestamp as a trap to remove or leave provably unwired. The timestamp question the spec asked is not the one that matters.

**L1-2 · Direct claim:** "byte-identical solar_battery" is presented as an established fact; it is only established at the snapshot-self-consistency level, not live-vs-snapshot.

- SC-1 (lines 60-65) upgrades the bar to a **full recursive tree diff** of live `generate --models` vs `generate --from-snapshot`.
- The existing evidence for byte-identity is `test_factory_purity.py:498-511` and `test_graph_assembly.py`, which build `computation_graph.json` / `registry_init.py` **from the snapshot** (`build_classifier_inputs_from_snapshot`) and diff against a committed baseline. That is snapshot-built-graph vs committed-baseline — a self-consistency check. No existing test compares **live** generation against **snapshot** generation, and the committed `baseline_outputs/solar_battery/` holds only two files (`registry_init.py`, `computation_graph.json`), not the module/stencil/schema tree that carries the `SysML Source:` headers from L1-1.
- So SC-1 is a genuinely new verification, and combined with L1-1 the full-tree diff is at real risk of failing on `source_file` header differences. The spec should stop presenting byte-identity as solved and frame SC-1 as a claim to be proven — most likely after `source_file` normalization lands.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The spec says `build_pipeline_context_from_snapshot()` "reuses the proven conformance-helper body ... not a reimplementation" (lines 100-104). The helper it points at (`build_full_graph_from_snapshot`, `test_entry_point_classifier.py:136`) returns a **`ComputationGraph` + inputs dict**, and it passes `compilation_results=None`. It does not build a `PipelineContext`.

- `PipelineContext` (`pipeline_context.py:78-104`) additionally requires `extractor`, `backtracker`, `backtracking_result`, `channel_aliases`, `output_registry`. The snapshot builder has to wrap the graph and set `extractor`/`backtracker` to null-equivalents (the fusion-tea path already runs generation with `extractor=None`, so this is plausible).
- This is fine **if** no generation path dereferences `ctx.extractor` or `ctx.backtracker` — I confirmed stencil auto-impl reads `module.auto_impl_context` (the graph), not the context. But the spec's "reuse the body" framing understates two things design must actually do: assemble the full `PipelineContext` wrapper, and prove generation never touches the null fields. **Recommend the spec reword this from "reuse the body" to "promote the helper's graph-assembly logic and wrap it into a `PipelineContext`, verifying no generation path reads the extraction-only fields."** Is there any known generation site that reads `ctx.extractor`/`ctx.backtracker`? If so, name it as in-scope.

### Lens 3 — Pipeline Risk

**L3-1 · If-then tradeoff (good news on the open question):** The Open Question "which expression-bearing fixture proves SC-10" (lines 210-215) is more answerable than the spec implies, which retires a hidden license-deadline risk.

- I checked the committed corpus. `chain_spike_model` has real CalcUsages (`design.sysml:12` `calc area_calc : AreaCalc { in length = length; ... }`) instantiating calc defs with inline output expressions (`library.sysml:8` `out area : Real = length * width`). That is exactly the CalcUsage auto-impl path — not FORMULA, not aggregation. `attr_expr_probe` has the same shape (`ScaleCalc`, `out result = value * factor`).
- **So SC-2's auto-impl-preservation criterion is provable from an existing committed fixture — no new fixture, and therefore no new license-gated capture, is required.** This matters: if the answer had been "no committed fixture qualifies," proving SC-10 would have needed a fresh capture before the 2026-08-06 expiry — a scheduling trap the spec did not flag. It dodges the trap, but by luck, not by having checked.
- Two things to nail at design: (1) confirm `chain_spike_model`'s inline-expression calc def flows specifically through the **CalcUsage** path (it does structurally — verify it produces a non-empty `compilation_results` once the serializer is extended, since today all 10 snapshots have none); (2) the proof only lands **after** that fixture's snapshot is regenerated with the new serializer — which the spec already requires. Recommend the spec name `chain_spike_model` (or `attr_expr_probe`) as the SC-10 fixture and drop the "or a minimal fixture must be added" branch unless design disproves it.

**L3-2 · Direct claim + sequencing note:** The version policy is coherent with the epic — but the missing-version hard-error has a bootstrapping hazard the spec should name.

- Coherence: the epic's "old snapshots degrade to today's behavior with a warning" (epic line 134) is scoped to **SC-10 absence** (missing `compilation_results`), and the spec keeps that distinct from version handling. Present-but-different version → hard error; missing `compilation_results` (additive section) → degrade+warn; missing version field → hard error. That split is sound and the scrutiny-point-1 concern is satisfied — the spec does keep them distinct.
- The hazard: **all 10 committed snapshots currently lack a version field** (verified — `grep` for `snapshot_format_version` returns nothing). If the loader's hard-error-on-missing-version lands before the 10 are regenerated, every conformance test that loads a snapshot hard-errors. The loader change and the 10-snapshot regeneration must land **atomically** (same commit/PR). Also flag the cross-item coupling: Item 1 is concurrently regenerating baselines/snapshots and will emit **unversioned** snapshots (the capture command doesn't exist yet) — coordinate so Item 2's loader doesn't reject Item 1's fresh captures mid-epic. This is a design-sequencing constraint, not a spec defect, but the spec should record it so design doesn't trip on it.

**L3-3 · Rewrite request:** The helper-migration scope leaves the two-copies risk unaddressed (scrutiny point 5).

- The `[HARD]` moves `snapshot_loader.py` / `snapshot_serializer.py` from `tests/helpers/` to `src/` (lines 94-99). Around 25 conformance test files import those helpers (and `build_full_graph_from_snapshot` / `build_classifier_inputs_from_snapshot`, which live in `test_entry_point_classifier.py`). The spec requires the move but says nothing about the ~25 import sites, nor about whether the conformance-helper body moves too.
- Left implicit, this produces exactly the failure the promotion is meant to avoid: either `tests/helpers/` keeps a second copy that drifts, or the src module duplicates logic the tests still exercise separately. The spec should require, as an explicit success criterion: tests migrate to the promoted `src` module; `tests/helpers/` is deleted or becomes a thin re-export; and the conformance-helper graph-assembly body is **promoted, not copied**. Right now "the move must not introduce a syside import into src" is stated, but "the move must not leave two copies" is not.

**L3-4 · Rewrite request:** CLI mutual-exclusion is directionally complete but has two concrete gaps.

- `--models` is currently `required=True` (`cli/__init__.py:513`). "Mutually exclusive with `--models`" (line 108) forces design to relax that — cleanest is an argparse mutually-exclusive group. The spec should say so, or at least name `required=True` as the change point, so design doesn't leave `--models` mandatory and make `--from-snapshot` unreachable.
- The spec states the pairwise rules (both → error; `--design-path-filter` + snapshot → error; all other flags apply) but never states **exactly one of `--models`/`--from-snapshot` is required** — so a bare `generate` with neither has undefined behavior. Add the "exactly one required" rule (a `required=True` mutually-exclusive group gives all three semantics at once).

### Lens 4 — Hygiene

No material findings. Conventions (REQ tags as success criteria, verification-matrix rows, reference-doc requirement, agentic-mbse impact section) are all present and correctly scoped to R1/R2/R3.

### Lens 5 — Reader Comprehension

No material findings. The Open Questions "version-mismatch vs legacy-degrade" bullet is dense but it is the crux and it decomposes the three sub-cases clearly enough for the reviewer to decide on one read.

---

## Engagement Summary

**Overall take:** The bet is sound and the mechanism checks out against the code — this is a Revise, not a Rework. The one thing the spec gets *wrong* is the load-bearing one: the byte-identical criterion rests on a provenance guard that polices timestamps (a dead template) while the provenance that actually diverges between live and snapshot runs — the embedded `source_file` path — goes unaddressed. Fix that and the migration-scope gaps and the spec is a trustworthy contract.

**Here's what I need you to weigh in on:**

1. **[L1-1, L1-2]** The byte-identical guard names the wrong provenance. Generated artifacts embed `SysML Source: {source_file}` (`modules.py:78`, `schemas.py:43`, `stencils.py:66`), and `source_file` is fixtures-relative in the snapshot but parser-derived live — they will differ. The timestamp the spec worries about is in a dead template. Decision: rewrite the guard to require `source_file` normalization across both paths, and reframe SC-1 as a new claim to prove (no existing test compares live vs snapshot at the full-tree level).
2. **[L3-3]** Helper migration leaves the two-copies risk open. ~25 test files import the helpers being promoted. Add an explicit criterion: tests migrate to the `src` module, `tests/helpers/` is deleted or re-exports, and the conformance-helper body is promoted not copied.
3. **[L3-1]** SC-10's proving fixture already exists — `chain_spike_model` (and `attr_expr_probe`) carry inline-expression calc defs instantiated as CalcUsages. This retires a hidden license-deadline risk. Confirm and name the fixture in the spec; drop the "or add a minimal fixture" branch unless design disproves it.
4. **[L2-1]** "Reuse the proven helper body" understates the work: the helper returns a `ComputationGraph`, not a `PipelineContext`, and passes `compilation_results=None`. Reword to "promote the graph-assembly logic and wrap it in a `PipelineContext`, verifying no generation path reads the extraction-only fields (`ctx.extractor`/`ctx.backtracker`)."
5. **[L3-2]** Version policy is coherent (the epic's degrade-with-warning is about SC-10 absence, kept distinct from version handling — good). But all 10 committed snapshots are unversioned today, so the loader's hard-error and the 10-snapshot regeneration must land atomically, and Item 1's concurrent unversioned captures need coordinating. Record as a sequencing constraint.
6. **[L3-4]** State "exactly one of `--models`/`--from-snapshot` is required" (a bare `generate` is currently undefined), and note `--models required=True` (`cli:513`) is the change point.

---

## Resolutions

*To be filled in as the reviewer resolves each finding. Keyed by ID.*

- **[L1-1, L1-2]** Accepted. Provenance guard rewritten around the embedded
  `SysML Source: {source_file}` header (modules/schemas/stencils + `computation_graph.json`),
  which is fixtures-relative in snapshots vs parser-derived live. New HARD: the snapshot
  must preserve/reproduce the exact `source_file` strings live generation emits, normalized
  at **capture time**. Timestamp worry demoted to an INFERRED note (dead `pydantic_schema.py.jinja2`
  template). SC-1 reframed as a claim to prove via a **license-gated live-vs-snapshot recursive
  tree diff**, run at least once while the license is live; snapshot-self-consistency does not count.
- **[L2-1]** Accepted. Context-builder requirement restated honestly: `build_pipeline_context_from_snapshot()`
  is **new assembly** (wraps a full `PipelineContext`, threads `compilation_results`), built on the
  helper's graph-rebuild body — not a rename. Verifying no generation path reads `ctx.extractor` /
  `ctx.backtracker` is in scope.
- **[L3-1]** Accepted. `chain_spike_model` adopted as the SC-10 proving fixture; "or add a minimal
  fixture" branch dropped. Recorded: no new license-gated capture needed for this item.
- **[L3-2]** Accepted. Version policy adopted as proposed (present-but-different **and** missing-version
  → hard error; missing `compilation_results` → degrade+warn). Added HARD: loader hard-error and the
  10-snapshot regeneration land **atomically**; Item 1's concurrent unversioned captures flagged as a
  sequencing constraint.
- **[L3-3]** Accepted. New HARD: all ~26 test files migrate to the promoted `src` module and the
  `tests/helpers/` copies are deleted in the same change; conformance-helper body promoted not copied;
  no re-export shim.
- **[L3-4]** Accepted. New HARD: **exactly one** of `--models` / `--from-snapshot` required (both or
  neither → hard error); `--models required=True` (`cli:513`) named as the change point (argparse
  required mutually-exclusive group); `--design-path-filter` + `--from-snapshot` → hard CLI error.

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec. The load-bearing edits are the provenance guard (L1-1/L1-2) and the helper-migration scope (L3-3); the rest are tightening.
