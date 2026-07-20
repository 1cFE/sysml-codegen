# Spec + Design: Lifecycle Item 5 — Whole-Tree Snapshot Portability

**Status:** Draft (combined spec+design; one review pass at audit)
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** MEDIUM (bounded sweep over a measured leak surface; reuses certified machinery)
**Branch:** constraint-exec-epic
**Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — register row 5
**Grounded at:** codegen HEAD `06d6e82` (brief committed above `1ce3247`), agentic-mbse `4c18d61`

---

## Problem

Generate the same model at two checkout roots and the output is not byte-identical. The
generated tree embeds the machine-absolute path of the source `.sysml` files, so two engineers
who check the repo out at different directories — or the same engineer before and after a
move — get different bytes for identical semantics. That breaks the epic's central proof: one
pinned artifact thread whose identity (fingerprints, seal, catalog) is reproducible from a
relocated snapshot.

Item 4 (superseded epic) certified portability for a **bounded manifest** — the constraint
exclusion referents in the model contract catalog. That boundary is real and is not re-opened
here. What Item 5 owns is the **delta discovered since**: every other byte that still carries a
checkout-absolute path, chiefly the calculation source location rendered into generated
docstrings.

This is measured, not assumed. See the inventory below.

---

## Absolute-byte inventory (MEASURED)

Method: license-free. Generate the full tree from a committed snapshot at the real checkout
root (`root A`), then from a copy of the same snapshot with the checkout-root prefix rewritten
to a different absolute directory (`root B`, simulating a genuine second checkout). Diff the two
trees and scan `root A` for the literal checkout-root byte string. Fixture: `catf_mfe_model`
(43 modules, cross-part chains, constraints, multi-file design) — the richest committed
corpus for this seam.

```
uv run sysml-codegen generate --from-snapshot tests/fixtures/catf_mfe_model/extraction_snapshot.json \
      --output <A> --package-name catf_mfe
sed 's#/home/reid/1cfe/sysml-codegen#/tmp/altroot/proj-xyz#g' <snapshot> > <snapshotB>
uv run sysml-codegen generate --from-snapshot <snapshotB> --output <B> --package-name catf_mfe
diff -rq <A> <B> ; grep -rl '/home/reid/1cfe/sysml-codegen' <A>
```

Result: **40 of 81 generated files differ between the two roots.**

| Producer | Files | Leak form | Site |
|---|---|---|---|
| Generated TEAx modules | 18 | `SysML Source: <abs>:<line>` ×4 each | `generation/modules.py:88`, `:488`; `templates/teax_module.py.jinja2:5,40` |
| Handwritten impl stencils | 18 | `SysML Source: <abs>:<line>` ×2 each | `generation/stencils.py:71`, `:143`; `templates/implementation_stencil.py.jinja2`, `auto_implementation.py.jinja2` |
| MultiOutput output schemas | 3 | `SysML Source: <abs>:<line>` ×1 each | `generation/schemas.py:43`, `:86`; `templates/multioutput_model.py.jinja2` |
| Package contract (seal) | 1 | indirect: `artifact_hashes` over the 39 leaking files | `contracts/seal.py` (victim, not source) |

**Clean — verified byte-identical across the two roots:**

- `contracts/model_contract.json` — the constraint catalog. It uses the certified portable
  `root-0/<relpath>:line:col` referent (Item 4 / constraint-wave). This is the machinery to
  reuse, and it already works. Byte-identical across roots, confirmed.
- `pipeline.yaml` — carries semantic dataflow sources (`channel.root`, group QNs), not
  filesystem paths.
- `inputs/*.json` and the `*_params.py` parameter-group schemas — the param-group docstring
  (`entry_point.py:226`, `"Parameters from {group.source_file}"`) renders a bare **basename**
  (`Parameters from magnets.sysml.`), which is root-independent. Portable, but ambiguity-lossy
  (two `physics.sysml` in different dirs collapse) — a fidelity note, not a leak. See design D3.

**Root cause (traced, not inferred).** The snapshot stores `calc_defs[].source_file` and
`calc_usages[].source_file` **relative to the snapshot's own directory** — already portable
(e.g. `library/physics/geometry.sysml`). The loader then **re-absolutizes** every one of them
(`loader.py:_reabsolutize_source_files`, `:923`; `_reabsolutize_source_file`, `:911` —
`os.path.abspath(snapshot_dir / stored)`). The docstring renderers embed that reconstructed
absolute path verbatim. The portable information exists in the snapshot; re-absolutization
destroys it on load.

**Three normalization schemes exist today** (the consolidation target):

- **Branch A — `root-N/<relpath>` canonical referent** (`analysis/source_referent.py`).
  Genuinely checkout-root-independent (anchors on explicit model roots, not the checkout dir).
  Certified. Wired **only** into constraint-exclusion locations at capture
  (`serializer.py:165`, `map_live_source_referent`).
- **Branch B — snapshot-dir-relative Path** (`serializer.py:182-189` forward,
  `loader.py:911-947` reverse). Portable only *contingently*: relative works when the model
  files live under the snapshot's own directory (fixtures do). When a snapshot is written to a
  directory the models are **not** under, `relative_to` fails and it stores an **absolute**
  path — a general-case portability hole the fixture layout hides. This is the branch that
  leaks after re-absolutization.
- **Branch C — `"models/"` substring strip** (`generation/stencils.py:243-247`,
  `generation/test_gen.py:61-65`, duplicated verbatim). Fragile string search; falls back to
  bare basename. Report-only.

**Secondary in-snapshot finding (surfaced, not silently absorbed).** `design_attributes` dict
keys are stored **absolute** in committed snapshots (`serializer.py:214` relativizes keys only
when `relative_to(output_dir)` succeeds; these did not). They did **not** reach `catf_mfe`
output, so they are an input-artifact non-portability, not a proven output leak. Folded into the
Item 5 sweep and gated by the whole-tree two-root diff, which catches any that do reach output.

---

## Success Criteria

- [ ] No checkout-absolute bytes occur anywhere in the generated tree or in the semantic
      artifacts it seals (snapshot loader-reconstructed fields, catalog, contracts, reports,
      generated code, calculation docstrings). Proven by the whole-tree absolute-byte scan
      returning zero hits across the fixture corpus.
- [ ] The same semantic input generated at two real checkout roots produces a byte-identical
      output tree and identity (fingerprints, seal, catalog). Proven by `diff -rq` over two
      real roots — **not** by same-machine relativization that cancels out.
- [ ] Item 1's relocated anonymous-admitted-with-actual leg passes: fixture
      `constraint_occurrence_demand/anonymous`, identity `OccurrenceDemandAnonymous__Admitted`,
      passes live A / live B / relocated replay with the admitted anonymous identity and its
      actual value preserved.
- [ ] Calculation-bearing and anonymous admitted/excluded fixtures pass on both public routes
      (live extraction and from-snapshot).
- [ ] The obsolete path-normalization branches (B reverse-mutation, C) are deleted, not shimmed.
      No same-machine workaround and no new normalization layer is added; the certified
      referent scheme is the one authority.
- [ ] The route-parity invariant (live vs snapshot, same root) is not regressed — no re-audit of
      Item 4, but the relocated replay compares semantic wiring, not just the absence of
      absolute bytes (the multi-hop EXPOSE trap; see Risks).

---

## Known Requirements

- **[INHERITED: epic Item 5 SC / ratified contract row 5]** Remove checkout-absolute paths from
  loader-reconstructed fields, eligible/excluded IDs, fingerprints, catalogs/contracts/reports,
  generated code and docstrings, and the full tree.
- **[INHERITED: ratified contract]** Same semantic input at two checkout roots → byte-identical
  output and identity, proven with two real roots plus an absolute-byte scan over the whole tree.
  No same-machine path cancellation.
- **[INHERITED: Item 1 evidence §8, `evidence.md:398,410`]** Complete Item 1's deferred
  relocated anonymous leg — `OccurrenceDemandAnonymous__Admitted`. Item 1 names it open for
  exactly this item.
- **[INHERITED: ratified contract]** Preserve source referent meaning. The docstring must still
  point a reader at the real source file, line, and column — a portable referent, not a deleted
  or blanked path.
- **[HARD]** Reuse the certified transaction / shape-gate machinery
  (`analysis/source_referent.py`, the constraint-wave fixture-transaction test harness). Do not
  re-audit the certified bounded manifest.
- **[HARD]** A snapshot format or field change must bump the format version and gate field/shape
  presence. In-place amendment of v4 is a known trap: Item 4 note N1 reproduced that a field-less
  v4 snapshot loads silently and reintroduces the very bug the field was added to fix. Any Item 5
  format change is v5 with a load-time shape gate, not another silent v4 edit.
- **[OWNER, brief]** No LOC metrics. Simplicity is qualitative: consolidate/delete obsolete
  path-normalization branches rather than adding another normalization layer.
- **[INFERRED]** The freshness check (`loader.py:_check_source_freshness`, `:962`) is the only
  post-load consumer that needs a real on-disk absolute path. Its need must be served without
  re-absolutizing the field that flows into generated output. From a pure snapshot the source
  files may be absent (license-free, possibly relocated); freshness is therefore a live/
  same-machine concern and may skip when no real path is resolvable — it already skips on
  `not source_file.exists()`.

---

## Design

Design content is agent-grade by construction; the owner ratifies at review. Bets are marked and
carry their reasoning.

### The crux

Two consumers read `source_file` after load, with opposite needs:

1. **Docstring rendering** (output) — needs a **portable, root-independent** referent.
2. **Freshness check** (live convenience) — needs a **real, absolute, on-disk** path.

The current loader serves #2 by mutating the stored portable form into an absolute path, which
breaks #1. The fix is to stop conflating them: carry the portable referent to output, and derive
an absolute path for freshness only locally, at its point of use, only when real source files are
present.

### Bet D1 — [AGENT] Generalize the certified `root-N/` referent to every `source_file`; delete Branch B (both directions) and Branch C

**Recommended.** At capture, map `calc_def`, `calc_usage`, aggregation, computed-attribute, and
design-attribute source locations through the **existing** `map_live_source_referent(raw,
model_paths)` — the same call constraint exclusions already use. `model_paths` is already
threaded into the serializer (`serializer.py:69`, `capture.py:69`), so this is reuse, not new
plumbing. The stored `source_file` becomes `root-N/<encoded-relpath>`, identical in shape to the
catalog referents.

On load, **validate** the referent with the certified `validate_snapshot_source_referent` and
keep it as an opaque portable string. Delete `_reabsolutize_source_files` and
`_reabsolutize_source_file` entirely (`loader.py:911-947`). The docstring renderers
(`modules.py:88`, `schemas.py:43`, `stencils.py:71`, the `sysml_source` template vars, and
`entry_point.py:226`) then render the stored referent directly — portable by construction, and
textually consistent with `model_contract.json`. Delete Branch C's two `"models/"` string hacks
(`stencils.py:243-247`, `test_gen.py:61-65`); the referent already carries the directory
structure they were trying to recover.

`PipelineModule.source_file` becomes a `str` referent rather than a `Path`
(`resolution/models.py:111`; the three build sites `graph_builder.py:1198,1720,1921`).

Freshness becomes live-capture-only: with `--models`, the real files exist and the check runs on
the raw parser paths before serialization; from a snapshot there is no absolute path to hash and
the check skips (its existing `not exists()` guard). No absolute path is persisted on the field
that reaches generation.

Format: **v4 → v5**, with a load-time shape gate asserting each `source_file` matches the
`root-N/` canonical pattern (reuse `validate_snapshot_source_referent`; reject a field-less or
absolute value loudly). This is the correct, direct response to Item 4 note N1 — a real version
bump with a presence gate, not another in-place edit.

**Why this over the lighter alternative.** The one-scheme result reuses certified code, is robust
to the general case where models are **not** under the snapshot directory (Branch B's hidden
hole), and makes docstrings and catalog agree. Deletion-biased: three schemes collapse to one.

**Cost, stated plainly.** A v5 bump requires re-capturing every committed snapshot (byte churn
plus `captured_at` rewrite — run the byte-identity gate as a timestamp-only diff then revert, so
only the referent bytes show). This is the same re-capture discipline Item 4 exercised; it is
bounded and mechanical.

### Rejected-lighter alternative (recorded, not adopted)

Out of scope as the chosen design: *stop re-absolutizing on load and render the snapshot-dir-
relative form as-stored, with no format change.* It is byte-identical on the current fixture
corpus and dodges the v5 bump, but it inherits Branch B's contingent portability — it stores an
absolute path whenever the models are not under the snapshot directory, a general-case hole the
fixtures cannot expose. Kept here as the fallback if the owner decides a format bump is not worth
the re-capture this cycle; it would then need its own guard that the stored form is never
absolute.

### D2 — Reuse, don't rebuild, the two-axis proof

Two independent axes, kept separate so neither masks the other:

- **Axis 1 — portability (Item 5 core).** Two real roots, same route → byte-identical tree.
  New whole-tree two-root harness (below).
- **Axis 2 — route parity (inherited, must-not-regress).** Live vs snapshot at one root →
  identical semantic wiring. This is where the multi-hop EXPOSE trap lives (a mis-wire is
  root-portable but semantically wrong; project memory `multihop-expose-offline-parity`). The
  relocated replay compares channel identity and retained producers, not only the absence of
  absolute bytes.

### D3 — [AGENT] Fold the param-group basename onto the same referent

`entry_point.py:226` renders a bare basename today — portable but ambiguity-lossy. Route it
through the same referent so param-group schema docstrings gain the disambiguating relative path
for free. Small, same mechanism; no separate scheme.

---

## Non-Goals

- Snapshot schema expansion unrelated to portable referents.
- Historical-snapshot reproducibility under historical profile semantics.
- Item 7's seal / provenance / trusted-bootstrap work.
- Re-auditing the certified Item 4 bounded manifest (constraint-exclusion referents,
  fixture-transaction harness, shape gates).

---

## Acceptance Coordinates

Each coordinate names both public routes and the open-predecessor state. Item 5's open
predecessors: none (rows 0–4 closed).

| # | Coordinate | Route | Proof |
|---|---|---|---|
| A1 | Rich multi-file fixture (`catf_mfe_model`) | live A / live B / relocated replay | whole-tree `diff -rq` clean across two roots; absolute-byte scan returns zero |
| A2 | `OccurrenceDemandAnonymous__Admitted` (`constraint_occurrence_demand/anonymous`) | live A / live B / relocated replay | admitted anonymous identity + its actual preserved; byte-identical across roots. **Completes Item 1's deferred relocated leg.** |
| A3 | Calculation-bearing + constraint fixtures (`plant_values`, `ife_plant`, one constraint fixture) | live + from-snapshot | portable referent in every docstring; catalog already portable (regression guard) |
| A4 | Route parity (Axis 2) | live vs snapshot, one root | semantic wiring (channel identity, retained producers) identical — guards the multi-hop EXPOSE trap |

The two-root scan is the completeness gate: it does not depend on enumerating every field
correctly by hand. Any checkout-root byte that reaches output shows as a diff.

**Stale-baseline hazard.** `plant_values`, `deep_cross_scope`, `constraint_inline`, and
`dropped_constraints` carry a recorded, unowned stale-baseline class (project memory
`deep-cross-scope-stale-baseline`). If the two-root proof trips one, handle per the recorded
pattern — reproduce the drift on the parent commit to prove it predates this change — and record
it; do not absorb it silently into the Item 5 regeneration set.

---

## Phased Plan (commands + stop conditions)

License-free work uses committed snapshots. Live legs (A1 live A/B, A2) need the SysIDE key:
`set -a; source ~/1cfe/agentic-mbse/.env; set +a` — the valid check is **zero** `no live syside
license` skips in `-rs` output, never pass/collected counts.

**Phase 0 — RED harness (no production change).**
Write the whole-tree two-root portability test: generate a fixture from a snapshot at two
distinct output roots (one via a root-rewritten snapshot copy), `diff -rq`, and assert zero
checkout-absolute bytes. It must fail RED on `catf_mfe` today (40/81 files differ).
*Stop:* harness does not reproduce the 40-file divergence → the harness is wrong, not the code.

**Phase 1 — Referent at capture (Branch A generalized).**
Apply `map_live_source_referent` to the remaining `source_file` fields (+ design-attribute keys)
in `serializer.py`; delete the Branch B forward-relativization for those fields.
*Stop:* any `source_file` field cannot resolve against `model_paths` (a real root the referent
scheme rejects) → surface it; do not fall back to an absolute path.

**Phase 2 — v5 format + shape gate; delete loader re-absolutization.**
Bump `SNAPSHOT_FORMAT_VERSION` to 5; add the `root-N/` shape gate on load
(`validate_snapshot_source_referent`); delete `_reabsolutize_source_files` /
`_reabsolutize_source_file`. Re-point freshness to raw parser paths at capture (live) only.
*Stop:* a field-less or absolute `source_file` loads without a loud rejection → the N1 trap is
not closed; fix the gate before proceeding.

**Phase 3 — Render the referent; delete Branch C.**
Docstring renderers and templates emit the stored referent; delete the two `"models/"` hacks and
fold `entry_point.py:226` (D3).
*Stop:* any generated docstring still contains an absolute path.

**Phase 4 — Re-capture + baselines.**
Re-capture committed snapshots to v5 (`scripts/capture_extraction_snapshots.py`) and regenerate
baselines (`scripts/capture_pipeline_baselines.py`). Run the byte-identity gate as a
timestamp-only diff then revert `captured_at`, so only referent bytes show. Remove the
`capture_pipeline_baselines.py:120` script-side `.replace()` hack — the real output is now
portable, so the baseline no longer needs post-processing.
*Stop:* a baseline changes in a field other than the referent / `captured_at` → an unintended
output shift; investigate before committing.

**Phase 5 — Two-root + route-parity proof.**
Run the Phase-0 harness GREEN across the A1–A4 corpus. Run the live A / live B / relocated legs
for A1 and A2 (licensed). Run Axis-2 parity for A4.
*Stop:* any two-root diff non-empty, any absolute-byte hit, or any live/snapshot wiring
divergence.

**Gates (final):** full suite (licensed, zero license skips), `PYTHONOPTIMIZE=1` parity, mypy
zero added, ruff clean, byte-identity over the regenerated corpus.

---

## Deletion Inventory (name before design; delete what this obsoletes)

| Deleted | File:line | Why obsolete |
|---|---|---|
| `_reabsolutize_source_files` | `snapshot/loader.py:923-947` | referent is portable; no absolute reconstruction needed |
| `_reabsolutize_source_file` | `snapshot/loader.py:911-920` | same |
| Branch B forward-relativize for source_file fields | `snapshot/serializer.py:182-189` (source_file paths) | replaced by `root-N/` referent |
| Branch C `"models/"` strip (stencils) | `generation/stencils.py:243-247` | referent carries directory structure |
| Branch C `"models/"` strip (test-gen) | `generation/test_gen.py:61-65` | duplicate of the above |
| Baseline script `.replace()` post-process | `scripts/capture_pipeline_baselines.py:120` | real output now portable; no strip needed |

**Additions (reuse, not new schemes):** extend the existing `map_live_source_referent` call to
more fields; a v5 shape gate that calls the existing `validate_snapshot_source_referent`. No new
normalization code.

---

## Open Questions / Deferred

- **Format-bump decision (owner may weigh at review).** D1 recommends v5 + full re-capture for a
  single robust scheme. The recorded lighter alternative avoids the bump at the cost of Branch B's
  contingent portability. Recommendation is D1; the alternative is the fallback if re-capture is
  undesirable this cycle.
- **Design-attribute absolute keys** are swept by D1 and gated by the two-root diff; whether any
  reach output beyond `catf_mfe` is answered empirically by running the harness across the corpus,
  not decided here.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 5, row 5)
- **Brief:** `.project/active/constraint-lifecycle-portability/briefs/spec_design.md`
- **Inherited (Item 4, certified):** `.project/active/constraint-lifecycle-diagnostics-defaults/`
  (snapshot v4, note N1 on in-place amendment)
- **Inherited (Item 1):** `.project/active/constraint-lifecycle-occurrence-demand/evidence.md`
  §8 (relocated anonymous leg open for Item 5)
- **Certified referent machinery:** `src/sysml_codegen/analysis/source_referent.py`
- **Project memory:** `multihop-expose-offline-parity`, `deep-cross-scope-stale-baseline`,
  `syside-license-key-explicit-env-needed`

---

**Next Steps:** After owner review of the D1 format-bump recommendation, proceed to `/_my_plan`
(or fold straight into implementation, as the phased plan above is execution-ready).
