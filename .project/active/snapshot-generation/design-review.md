# Design Review: Snapshot-Driven Generation (SC-9 + SC-10)

**Design:** `.project/active/snapshot-generation/design.md`
**Spec:** `.project/active/snapshot-generation/spec.md`
**Review File:** `.project/active/snapshot-generation/design-review.md`
**Date:** 2026-07-05

---

## Fundamental Assessment

**Sound, with one Critical de-risk that must land before the build.**

The approach is right and admirably restrained. The item promotes machinery that
already works (900+ conformance tests exercise the snapshot round-trip and the
graph rebuild), threads the one missing piece (`compilation_results`), and adds a
version/provenance/`source_file` contract on top. It does not invent abstractions:
one new package (`snapshot/`), one new assembly function
(`build_pipeline_context_from_snapshot`), one CLI subcommand. Each earns its place.
The `ComputationGraph`-is-the-only-generation-input boundary is preserved, so a
snapshot run genuinely exercises the same resolution/generation code as live.

Two of the three Key Bets check out against the code:

- **B1 (no generation path reads `ctx.extractor` / `ctx.backtracker`) — CONFIRMED.**
  A grep of all of `src/` for `.extractor` / `.backtracker` field reads returns
  only a function-local `import` in `pipeline_builder.py:469` — not a context read.
  Generation reads only `ctx.computation_graph` and `module.auto_impl_context`.
  This is a real strength; the design's null-fields plan is safe.
- **B3 (`compilation_results` is plain dataclasses of strings) — plausible as
  stated;** consistent with the spec-review's trace of `expression_compiler.py`.

But the design's **third foundational claim — that the promoted package is
"syside-free" — is contradicted by the code as written** (see Critical C1). That
claim is the entire justification for the item (license-free CI generation), and
the design records it as already-Fixed ("Fixed: the package layout (D3)") with a
verification method (static import grep) that would *disprove* it. This does not
make the approach wrong. It makes one load-bearing premise unproven, and the
design presents it as settled. That must be resolved empirically before the plan
proceeds — alongside B2, not after it.

Verdict: proceed to detailed review; **Revise**, not Rework.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Pass (with the C1 caveat)

Every spec HARD requirement maps to a design element: the `tests/helpers` → `src`
move (D3), `FIXTURES_DIR`-as-parameter (loader signature change), no-two-copies
(D3 + INV-3), `build_pipeline_context_from_snapshot` as new assembly (D2 + INV-4),
the CLI mutually-exclusive group (INV-7), version-as-hard-error (INV-2),
`compilation_results` serialization + degrade (SC-10 / INV-5), `source_file`
capture-time normalization (D1), provenance-never-in-output (INV-6), atomic
loader + 10-snapshot landing. The three resolved spec-review rulings are all
carried faithfully. The dead `pydantic_schema.py.jinja2` timestamp trap is
correctly demoted to a guard-and-leave-unwired note.

The one spec requirement the design asserts but does not actually establish is
the syside-free move (spec: "The move must not introduce a syside runtime import
into the `src` package"). See C1.

### 2. Pattern Consistency
**Assessment:** Pass

The CLI mechanism (mutually-exclusive required group, `cmd_snapshot` subcommand
mirroring `cmd_generate` / `cmd_install_commands`, `set_defaults(func=...)`)
matches the existing `cli/__init__.py` structure. Integer version constant in the
package `__init__` is a normal convention. The license-skip pattern (SC-1 skips on
`ImportError` from `load_models`) reuses the established
`test_extractor.py:851-864` idiom. New package layout is consistent with the
existing `analysis/`, `resolution/`, `orchestration/` split.

### 3. Abstraction Quality
**Assessment:** Pass

Nothing is over-wrapped. `build_pipeline_context_from_snapshot` lives in its own
module specifically to keep the `orchestration → snapshot` import edge
one-directional (D2) — a real, stated reason, not ceremony. Promoting the two
graph-rebuild helpers out of a test file into `snapshot/graph_rebuild.py` is the
right home. The `snapshot/` package boundary is justified by the syside-free goal
(pending C1).

### 4. Duplication Avoidance
**Assessment:** Pass

INV-3 (delete `tests/helpers/` copies, grep returns zero, no re-export shim) is
the correct no-two-copies guard and matches the spec HARD. The conftest
`snapshot_fixture(name)` helper (Appendix B) does **not** violate no-shims — see
M4; it is a path-building convenience, not a second copy of the promoted logic.

### 5. Data Structure Clarity
**Assessment:** Pass

The snapshot format additions (top-level `snapshot_format_version`,
`compilation_results` block, relativized `source_file`) are explicit and typed.
`compilation_results` reuses the generic serializer because the payload is already
plain dataclasses — no new schema. The `"unknown"` / `"hierarchy"` sentinel
carve-out for `source_file` re-absolutization is called out (Implementation Notes).

### 6. Route Safety
**Assessment:** Pass

INV-7 covers the CLI decision surface exhaustively via one argparse construct:
both flags → error, neither → error, `--from-snapshot` + `--design-path-filter` →
error. Version guard runs before any field deserialization (INV-2). No wildcard or
silent-fallback routing.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets are honest bets (each has a real "if false → what fails"), and B1
is verified. B2 is correctly named as the riskiest and given a de-risk-first plan.
The problem is a **hidden bet the design states as a fact**:

- **Hidden bet: `import sysml_codegen.snapshot` succeeds when no syside license /
  JVM is present.** The design asserts this as settled (D3, Research line 41: the
  helpers "import only analysis/, resolution/, orchestration/ — no syside";
  "Fixed: the package layout (D3)"). It is not settled — the code contradicts the
  literal claim (C1), and the underlying property (can `agentic_mbse.sysml.syside_adapter`
  be imported license-absent?) is unverified. This belongs in Key Bets with its
  own de-risk, next to B2. Right now it is invisible, which is the most expensive
  failure mode.

Decisions are mostly clean (each names the rejected alternative). D1 has a real
gap (M1). D6 (warn-only, defer `--strict`) is a sound YAGNI call.

### 8. Reader Comprehension
**Assessment:** Pass

Core Concept states the mental model plainly before mechanism ("a snapshot is a
versioned JSON capture of the extraction boundary"). The two-path architecture
diagram is clear. The V1–V6 error catalog and INV-1..7 are decomposed, not block
text. A tired engineer can skim this once and know what is being built and why.
The one comprehension cost is that the syside-free claim reads as proven when it
is not — but that is a correctness issue (C1), not a prose issue.

---

## Issues by Severity

### Critical

- **C1 — "syside-free" is asserted as settled but contradicted by the import
  chain; its own verification method would disprove it.** The promoted
  graph-rebuild body imports (via `test_entry_point_classifier.py:29-39`)
  `analysis.dependency_backtracker`, `analysis.parameter_groups`, and
  `extraction.usage_extractor`. All three import agentic-mbse **at module level**:
  `parameter_groups.py:15,23` (`evaluate_true_static_expression`, `SysideAdapter`),
  `usage_extractor.py:17,22,25` (`SysideAdapter`, helpers, `BindingType`),
  `dependency_backtracker.py:20` (`BindingType`). So `import sysml_codegen.snapshot`
  transitively imports `agentic_mbse.sysml.syside_adapter` — the design's Research
  claim "no syside" (line 41) and INV-1's proposed "static import grep" are
  self-contradicting: the grep would fail.

  Whether this **breaks the item** depends on an unverified fact: does
  `import agentic_mbse.sysml.syside_adapter` succeed when the syside license / JVM
  is absent (license checked only at `load_models()` runtime), or does it fail at
  import (pulling in the licensed JVM bridge eagerly)? Research line 63 (the
  `ImportError` is caught from `load_models()`, not from `import`) is *suggestive*
  that import is safe — but the design must **prove** it, license-absent, not infer
  it. I could not run the import in-sandbox to confirm.

  Required before build (de-risk, equal priority to B2):
  1. Empirically import the promoted package with syside unavailable / unlicensed
     and show it succeeds (a real CI-like condition, not the current licensed dev
     env where 900 tests already import this chain and prove nothing about the
     license-free case).
  2. Reword INV-1 to the **actual** invariant: *"`import sysml_codegen.snapshot`
     and a full `--from-snapshot` generation both succeed with no live syside
     session"* — not "imports no syside," which is false as written. The
     verification is a license-absent import+generate test, not a grep.
  3. If step 1 fails (import pulls in the JVM), the item needs a design change
     (lazy/deferred agentic-mbse imports in the rebuild chain, or a narrower
     promoted surface) — surface that now, not in implementation.

### Major

- **M1 — D1 silently breaks when `--output` writes the snapshot outside
  models-root.** D1 defines models-root *as* "the directory the snapshot file is
  written into" and re-absolutizes via `(snapshot_path.parent / stored).resolve()`.
  That is exact only when the snapshot lands in models-root — the D5 default. But
  D5 also offers `--output <file>` to an arbitrary location. Then capture
  relativizes against models-root while the loader re-absolutizes against a
  *different* `snapshot_path.parent`, reconstructing a wrong absolute `source_file`
  — silently (the freshness hash would warn at most, and generation continues with
  a wrong `SysML Source:` header, breaking byte-identity). Fix: relativize at
  capture against **`output_path.parent`** (wherever the snapshot actually lands),
  not models-root. Then `(snapshot_path.parent / stored)` is exact by construction
  for any `--output`, even one far from the sources (the relative path just gains
  `../` segments, which resolve fine). This also makes D1 robust rather than
  coupled to D5's default.

- **M2 — B2's `.resolve()` is the symlink-unsafe primitive, and CI is exactly
  where that bites.** The loader's `(... / stored).resolve()` resolves symlinks.
  If the live parser emits an absolute path *without* resolving symlinks (macOS
  runners symlink `/var`→`/private/var`; some CI checkouts sit under symlinked
  paths), live and snapshot diverge on the `SysML Source:` header and SC-1 fails —
  on CI, the stated target, not on the dev box. The design flags this under B2
  risk ("don't `resolve()` symlinks") but still specifies `.resolve()` as the
  mechanism. Recommend: the B2 de-risk must run on a **symlinked** path, and the
  loader should use a lexical absolute (`Path.absolute()` / `os.path.abspath`,
  no symlink resolution) matched to whatever form the parser actually emits —
  determined during de-risk, not assumed. Note the byte-identity-on-CI logic is
  otherwise coherent: both sides run on the same machine, both go absolute, and
  nothing machine-specific is committed (the snapshot stores only the relative
  path) — *provided* M1 and M2 are fixed so the two absolute forms actually match.

- **M3 — The "Item 1 emits unversioned snapshots concurrently" premise is
  inaccurate, and the design hangs a sequencing constraint on it.** Item 1's plan
  (`baseline-diagnostics/plan.md:71-72,200-206`) commits **no extraction
  snapshots**: Phase 0 explicitly "no snapshot committed for either new fixture,"
  and Phase 3 re-captures only `baseline_yaml/*.yaml` and
  `baseline_outputs/<model>/{computation_graph.json,registry_init.py}` (solar_battery
  ×3, catf_mfe ×2) — it never runs `capture_extraction_snapshots.py` into a commit.
  So there is no "unversioned fresh capture" from Item 1 for the versioned loader
  to meet. The design's Potential-Risk "Item 1 collision" and the Handoff
  "sequence after Item 1's re-captures" rest on a false dependency and could
  needlessly block Item 2. The **atomic landing** of the loader version-guard +
  10-snapshot regeneration is still independently required (all 10 committed
  snapshots are unversioned today) — keep that. Drop or correct the Item-1
  ordering coupling; the only real cross-item interaction is not colliding on the
  same files, which the two plans already don't.

### Minor

- **M4 (clears — recorded for the design agent) — `snapshot_fixture(name)` does
  NOT contradict no-shims.** The spec's no-shim HARD forbids a re-export copy of
  the promoted *loader/serializer logic*. `snapshot_fixture(name)` returns
  `FIXTURES_DIR / name / "extraction_snapshot.json"` — a test-only path builder
  that encapsulates the fixtures-path convention the loader used to hardcode
  (`snapshot_loader.py:39,58`). It reintroduces no second copy of any promoted
  code; it is the correct place for fixtures-path knowledge once the loader becomes
  path-general. Legitimate. Keep it.

- **M5 — `REQ-SNAP-01..07` already exist; the new REQ table must continue from
  08.** The verification matrix already has `REQ-SNAP-01..07` mapped to
  `test_extraction_snapshots.py` (round-trip / typed-fields / AST-None). The
  design proposes a "REQ-SNAP-* table" in new doc 27 without noting the existing
  family. Number the new requirements `REQ-SNAP-08+`, and have D7 reconcile: doc 27
  is a *new* reference doc for an *existing* REQ family, not a fresh namespace.
  Doc numbering (27) is free — highest present is 26.

- **M6 — Freshness warnings (V3) can scroll past mid-load; consider an
  end-of-run summary.** Per-file V3/V4 warnings emit during load, while the
  provenance banner (V5) emits once. On a multi-file model a stale-source or
  degrade warning can be buried above hundreds of lines of generation output. D6's
  warn-only choice is fine for this item (no `--strict` — good YAGNI), but the
  warning is the only signal a stale snapshot is masking a model edit. Recommend:
  count stale/degrade warnings and re-emit a one-line summary next to the V5 banner
  at run end, so the operator cannot miss "N source files no longer match this
  snapshot." Cheap; makes warn-only actually safe.

---

## Recommendations

1. **De-risk C1 before anything else, jointly with B2.** Prove `import
   sysml_codegen.snapshot` (and a full `--from-snapshot` generation) succeed with
   syside unlicensed/unavailable. Reword INV-1 to that behavioral invariant and
   make its verification a license-absent import+generate test, not a grep. If the
   import pulls in the JVM, redesign the rebuild chain's imports now.
2. **Fix D1 (M1): relativize `source_file` at capture against `output_path.parent`,
   not models-root** — makes reconstruction exact for any `--output`.
3. **Refine B2 (M2): de-risk on a symlinked path; use a lexical absolute matched
   to the parser's emitted form, not `.resolve()`.**
4. **Correct the Item-1 sequencing premise (M3):** Item 1 commits no extraction
   snapshots; keep only the atomic loader + 10-snapshot regeneration constraint.
5. **Number new REQs `REQ-SNAP-08+` (M5); summarize freshness warnings at run end
   (M6).**

---

## Resolutions

*To be filled in as the reviewer resolves each finding. Keyed by ID.*

- **[C1]** _pending_
- **[M1]** _pending_
- **[M2]** _pending_
- **[M3]** _pending_
- **[M4]** _pending (clears — no design change needed unless reviewer disagrees)_
- **[M5]** _pending_
- **[M6]** _pending_

---

**Overall:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to
the design-agent session) and point it at this review to incorporate. The reviewer
does not edit the design. The load-bearing edits are C1 (prove syside-free import,
reword INV-1) and M1/M2 (`source_file` reconstruction correctness); M3/M5/M6 are
tightening. C1 and B2 are the two things to prove with the license still live —
do both in the same de-risk session before building capture/CLI/migration on top.
