# Design: Subtype-Aware Enumeration & Constraint-Report Truth

**Status:** Draft (revised post-review — MF1–MF5 + minors incorporated)
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** pipeline-truth-epic (agentic-mbse on an Item-4 companion branch — see spec "agentic-mbse landing")
**Base commit:** a7c21df
**Epic:** PIPELINE-TRUTH, Item 4

---

## Overview

Make model-wide constraint enumeration subtype-aware at one adapter choke point, so the
constraint drop report finally sees `assert constraint`; serialize a constraint manifest so the
report is faithful on the `generate --from-snapshot` path; and fix the same blindness in three
agentic-mbse validators. The semantics are fixed by the spec's 8-row decision table; this design
owns the mechanisms.

## Related Artifacts

- **Spec:** `.project/active/subtype-enumeration/spec.md` (decision table = the contract)
- **Spec review:** `.project/active/subtype-enumeration/spec-review.md` (satisfy exclusion, format-bump sequencing)
- **Design review:** `.project/active/subtype-enumeration/design-review.md` (MF1–MF5, minors — incorporated here)
- **Discovery register:** `.project/research/20260706_pipeline-truth-discovery.md` §D4 (evidence base; agentic-mbse rows derive from here — that repo is sandbox-blocked)
- **Architecture:** `docs/architecture/reference/01-extraction.md` (REQ-EXT-09), `reference/27-snapshot-generation.md`, `modeling-assumptions.md` §8
- **R4 probe (deferred):** `.project/active/subtype-enumeration/_probe.py`

---

## R4 Verification Table (design-open, MANDATORY)

Environmental limit recorded plainly: **this autonomous session's approval gate blocks all code
execution** (`uv run`, `.venv/bin/python`, `pytest` all return "requires approval" with no human
to grant it) **and the sandbox blocks every read of `/home/reid/1cfe/agentic-mbse`** (Read + Bash
+ subagent all denied — the exact trap the `agentic-mbse-repo-path` memory and the spec's own
"sandboxed out of that repo" note describe). So the codegen findings are confirmed by **direct
source read of the exact query + gate lines** (stronger than a black-box probe — I read the
precise code), corroborated by the orchestrator's already-executed live/license-free runs
(register L20–33). The live probe is **authored and committed** (`_probe.py`); running it is an
**implement-stage gate** that updates register §D4. Nothing here is claimed as "I ran it and saw X".

| # | Finding | Probe | Verdict |
|---|---------|-------|---------|
| 1 | `extractor.py:107` queries exact-type `ConstraintUsage`; `:123` `if constraints:` gates BOTH the per-item INFO loop and the summary WARN → report totally silent when the only constraint is an `assert`. wi014_toy carries `assert constraint affordable` at `toy_plant.sysml:51`. | `_probe.py` PROBE1: load wi014_toy live, count exact `ConstraintUsage` (=0), `is_instance(assert,"ConstraintUsage")` (=True), assert `report_dropped_constraints` emits 0 records. | **CONFIRMED** (source read: `extractor.py:107,123`; fixture `toy_plant.sysml:51`; register L25). Live run deferred. |
| 2 | `constraint_extractor.py:50` uses the same exact-type `ConstraintUsage` query; docstring line 4 claims "constraint, assert constraint, and require constraint" support. Zero callers in `src/`/`tests/`. | `_probe.py` PROBE2: `extract_all_constraints(wi014_model)` returns 0 total despite the assert. | **CONFIRMED** (source read: `constraint_extractor.py:4,50`; zero-caller grep in register L26 + spec-review L43). Live run deferred. |
| 3 | agentic-mbse `level3_dataflow.py:48` queries abstract `Import` → matches nothing → dep graph always `{}` → circular check structurally always passes. Secondary: `imported_namespace` guard skips MembershipImports even once type is fixed. | Seeded circular-import fixture: assert non-empty graph + circular check FAILS. | **CONFIRMED-BY-REGISTER** (§D4 "worst new"; L125). Live re-verify + line re-check deferred to implement (repo sandbox-blocked). |
| 4 | agentic-mbse `level4_constraints.py:113` exact-type `ConstraintUsage` → undercounts asserts. | assert-bearing fixture: droppable count matches independent literal. | **CONFIRMED-BY-REGISTER** (§D4 L124). Deferred to implement. |
| 5 | agentic-mbse `level6_architecture.py:602` exact-type `ConstraintUsage` → non-executable WARN never fires on asserts; **`:601 except Exception: constraints = []` swallow** collapses any error to "zero constraints" (MF2). | assert-bearing fixture: WARN fires; clean fixture: silent; error-injection: fails loud, not silent. | **CONFIRMED-BY-REGISTER** (§D4 L124; swallow orchestrator-verified). Deferred to implement. |

> The three agentic-mbse rows carry the spec's caveat: "the probe wins — re-verify before building
> on any single line number." Their line numbers (`:48`, `:113`, `:601–602`, adapter `:214`, TYPE_MAP
> `:244–246`) are register-sourced and **must be re-confirmed at implement** when the companion branch
> is checked out.

---

## Core Concept

There is one blindness and one silence, and both collapse to a single idea: **enumeration must
respect the type hierarchy, and the report must be rendered from a serializable manifest.**

- **The blindness** is that syside's model-wide query is exact-type (`nodes(kind,
  include_subtypes=False)`), while `is_instance` on the same adapter is hierarchy-aware. Every
  diagnostic that enumerates then classifies enumerates blind and classifies smart. The fix is one
  adapter parameter (`include_subtypes`), opt-in per call site per the decision table — not a global flip.

- **The silence** is that the report reads the live model directly, so it can't run offline and has
  no serialization carrier. The fix is to split the report into **collect** (live → typed manifest)
  and **render** (pure → logs). The manifest is serialized into the snapshot; the from-snapshot path
  deserializes it and calls the *same* renderer. **Render identity is by construction; round-trip
  fidelity (serialize → deserialize → render) is a matched pair guarded by the INV-B parity test** —
  the honest framing (MF4).

The load-bearing subtlety is the exclusion. `include_subtypes=True` on `ConstraintUsage` sweeps in
`RequirementUsage` (and its `satisfy` subtype), which are requirement-side, not dropped predicates.
So droppability is defined by **one predicate single-sourced in the adapter** —
`is_droppable_constraint`, built on `EXCLUDED_CONSTRAINT_TYPES = ("RequirementUsage",)` — consumed by
both repos (MF3). The manifest keeps the *whole* swept subtree (including excluded requirement/satisfy
entries, tagged by kind) so the sentinel's scanned/reported/excluded breakdown reproduces offline and
a swept-and-excluded `satisfy` stays observable rather than silent.

**The mechanism only works if the type names resolve.** The adapter resolves every `is_instance` /
`elements_of_type` name through a whitelist `TYPE_MAP`, and today that map contains none of the
subtype names the filter and ladder rely on — an unmapped name makes `is_instance` return `False`
*silently*, which would over-report requirements as dropped and collapse every kind to `PLAIN` while
tests ship green (MF1). So this design adds the three names and makes the adapter **hard-error on an
unknown type name in both methods** — turning a silent wrong answer into a loud failure, the epic's
stance on exactly this D3 family.

This composes with existing pieces, adding no parallel machinery: the adapter gains parameters + a
policy constant; `report_dropped_constraints` is refactored in place into collect+render; the
serializer/loader gain one top-level field; the from-snapshot context gains one replay call;
`PipelineContext` gains one field.

## Key Bets

- **B1.** syside `nodes(kind, include_subtypes=True)` returns the full subtype subtree for `kind`,
  and the adapter's `is_instance` is hierarchy-aware. *If false → the sweep still misses asserts, or
  the exclusion filters the wrong set.* (Register §D4 L117,129; live confirmation deferred.)
- **B2. (surfaced per MF1 — the most expensive bet, now closed in-design).** The specific type names
  the filter and ladder resolve on — `AssertConstraintUsage`, `RequirementUsage`,
  `SatisfyRequirementUsage` — are resolvable by the adapter (present in `TYPE_MAP`). *If false →
  `is_instance` no-ops silently, requirements over-report as dropped, kinds collapse to `PLAIN`, and
  the bug ships green on any model without a requirement.* **This bet is false today** (register §D4
  L129) and is closed by D6 (add the names + hard-error), so its failure becomes loud, not silent.
- **B3.** The metamodel hierarchy holds: `AssertConstraintUsage ⊂ ConstraintUsage`;
  `SatisfyRequirementUsage ⊂ RequirementUsage ⊂ ConstraintUsage`; `require constraint` is a *plain*
  `ConstraintUsage` (no distinct metaclass); `Import` is abstract with only
  `MembershipImport`/`NamespaceImport` concrete. *If false → the exclusion drops the wrong things and
  the sentinel counts lie.* (Verified against the syside stub, spec-review L26–28.)
- **B4.** `extract_all_constraints`, `_deserialize_constraint_info`, and the abstract-`Import` query
  have zero real consumers. *If false → a live consumer breaks, or a validator that appeared to
  "pass" regresses loudly.* (Zero-caller grep, register L26,32 + spec-review L43; agentic-mbse leg deferred.)
- **B5.** No supported model currently uses `satisfy`, an enum-valued entry point, or
  connection/view/case subtypes. *If false → excluding satisfy or keeping exact-type on
  AttributeUsage/PartDefinition silently drops a real assertion or entry point.* (Mitigation: the
  sentinel keeps satisfy/requirement observable.)

## Key Decisions

- **D1. Droppable policy single-sourced in the adapter (MF3).** agentic-mbse exposes
  `EXCLUDED_CONSTRAINT_TYPES = ("RequirementUsage",)` and `is_droppable_constraint(elem)` (built on
  `is_instance`). The string `"RequirementUsage"` appears in **exactly one production location**
  (the adapter); both repos import it. agentic-mbse rows 6/7 use `exclude=EXCLUDED_CONSTRAINT_TYPES`;
  codegen's collect partitions with `is_droppable_constraint` (it needs the full swept subtree tagged
  by kind for the manifest/sentinel — INV-C — so it can't take the pre-filtered set). Two *mechanisms*
  (adapter `exclude` vs sweep-and-partition), **one *policy* source**, plus a cross-repo consistency
  pin. *Rejected: three hand-rolled `is_instance("RequirementUsage")` filters (the drift surface);
  exact-type string compare (the original bug).*
- **D2. Serialization carrier = a top-level `dropped_constraints` manifest.** A list of typed records
  `{owner_kind, owner_name, owner_qualified_name, constraint_name, constraint_kind, source_line}`
  covering all three owner kinds. *Rejected: the `PartDefinitionData.constraints` stub — per-part-def,
  cannot carry calc-def- or part-usage-owned constraints.*
- **D3. `report_dropped_constraints` splits into collect (live) + render (pure).** `render` is a
  module-level function over the manifest with no syside import; both paths call it. Collect is
  **single-path** — `capture.py:42` already reuses `build_pipeline_context`, so the manifest built at
  step 2.5 rides on the same `ctx` capture serializes (MF4). *Rejected: a second offline-only report
  implementation (guaranteed drift — the anti-pattern Item 3's parity work catches).*
- **D4. `extract_all_constraints` (row 2) is deleted in this item.** Its false docstring is precisely
  the truth surface Item 4 owns; with zero callers, leaving it for Item 8 would let the false claim
  survive the truth item. `_deserialize_constraint_info` (`loader.py:275`, dead) is deleted alongside.
  *Coordinate with Item 8 so each dies once; implement re-runs the zero-caller grep first.*
- **D5. Snapshot format hard-gates 1→2; all committed snapshots re-captured** (including Item-1's
  additions — M7). A v1 snapshot silently reporting "no constraints" would reintroduce the
  blind-vs-empty ambiguity this item kills. *Rejected: additive-optional manifest (Item 10's
  `reference_chain` mechanism) — leaves old snapshots silently constraint-blind, defeating the criterion.*
- **D6. Adapter hard-errors on an unknown type name in BOTH `elements_of_type` and `is_instance`
  (MF1).** `TYPE_MAP` gains the exact syside classes `AssertConstraintUsage`, `RequirementUsage`,
  `SatisfyRequirementUsage`. `elements_of_type` already raises `ValueError` with the valid-names list;
  `is_instance` currently returns `False` on an unmapped name — itself a D3-family silent failure — and
  is changed to raise the same way. The hard error is gated on **"name not in `TYPE_MAP`" checked
  before the documented mock string-match fallback**, so `is_instance`'s mock path (per its docstring)
  survives. Pinned by a fires-on-unknown-name unit test in the companion. *Rejected: silent `False`
  (the bug); adding names without the guard (leaves the next missing name silently wrong).*
- **D7. The `level6_architecture.py:601 except Exception: constraints = []` swallow is fixed in this
  item (MF2).** It sits at the line row 7 edits; leaving a swallow around a truth fix is self-defeating
  — any error would collapse to "zero constraints" and mask the row-7 fix. Narrow the except (or remove
  it) so the failure is loud. This **absorbs one D3-family site early**; recorded here and noted for
  Item 5's ledger so nothing is double-counted. *Rejected: defer to Item 5 (would ship the row-7 fix
  already masked).*
- **D8. `owner_kind` and `constraint_kind` serialize as stable enum tokens, not display strings (MF6).**
  `OwnerKind`/`ConstraintKind` serialize by a fixed token; render maps token → display wording. So a
  diagnostic reword never changes a snapshot's bytes and the re-capture gate stays "version + manifest
  only." *Rejected: serialize `_constraint_owner_kind`'s display text (couples snapshot bytes to wording).*

## Architecture

One constraint's journey:

```
LIVE:   model --elements_of_type("ConstraintUsage", include_subtypes=True)-->
        swept --collect_constraint_manifest (kind-ladder + is_droppable_constraint,
                 stable-sorted by (owner_qname, constraint_name))--> manifest
        manifest --render_constraint_report(logger)--> logs
                 \--> PipelineContext.constraint_manifest --serialize--> snapshot["dropped_constraints"]

OFFLINE: snapshot["dropped_constraints"] --loader--> snap["constraint_manifest"]
         --render_constraint_report(SAME fn, SAME logger name)--> logs   [pinned == live by INV-B]
```

Boundaries:

- **agentic-mbse `syside_adapter`** — the choke point. `elements_of_type` gains keyword-only
  `include_subtypes: bool = False` (pass-through to `nodes`) and `exclude: Collection[str] = ()`
  (drops any element `is_instance` of a named type). Both `elements_of_type` and `is_instance`
  hard-error on an unknown name (D6). New module-level `EXCLUDED_CONSTRAINT_TYPES` +
  `is_droppable_constraint`. `TYPE_MAP` gains the three constraint classes. One additive change,
  consumed by both repos.
- **`extraction/constraint_report.py` (new)** — pure: `ConstraintKind`/`OwnerKind` enums,
  `ConstraintManifestEntry` frozen dataclass, `render_constraint_report(manifest, logger)`. No syside
  import → license-free offline replay.
- **`SysMLDataExtractor.collect_constraint_manifest(*, include_subtypes=True,
  excluded_types=EXCLUDED_CONSTRAINT_TYPES)` (new; replaces the query in `report_dropped_constraints`)**
  — live sweep + kind-ladder → sorted `list[ConstraintManifestEntry]`. The **policy is an injectable
  parameter defaulting to production** (MF5), so the mutation-check test runs it with
  `include_subtypes=False` and watches the pin fail. Owner kind computed live (is_instance) → `OwnerKind`.
- **`pipeline_builder.build_pipeline_context` step 2.5** — `manifest = extractor.collect_...();
  render_constraint_report(manifest, logger); ctx.constraint_manifest = manifest`.
- **serializer / loader** — one top-level `dropped_constraints` field in/out; loader error message
  names the real recapture command `scripts/capture_extraction_snapshots.py` (M8).
- **`snapshot_context.build_pipeline_context_from_snapshot`** — one added
  `render_constraint_report(snap["constraint_manifest"], logger)` call (the replay).

## Required Invariants

- **INV-A (opt-in).** Adapter defaults `include_subtypes=False`, `exclude=()`. Every existing call
  site is byte-for-byte unchanged unless it opts in; the only behavior deltas are decision-table rows
  1/6/7 (+ row 5's Import fix, + D6's now-loud unknown-name error, + D7's level6 fix). Rows 3/4/8 KEEP
  exact-type deliberately; row-4 sites are unchanged.
- **INV-B (round-trip parity by test).** The INV-B test compares the from-snapshot report's output
  against the **live** report's output for the same model, and pins a **golden serialized manifest
  fragment**. Render identity is by construction; this test guards the serialize→deserialize step.
- **INV-C (full sweep in manifest).** The manifest holds the entire swept `ConstraintUsage` subtree
  including excluded requirement/satisfy entries (tagged by kind), so scanned/reported/excluded
  reproduce offline and satisfy stays observable.
- **INV-D (single droppable-policy source).** Droppability is defined once —
  `is_droppable_constraint` / `EXCLUDED_CONSTRAINT_TYPES` in the adapter. Codegen's kind-ladder marks
  an entry droppable via that same predicate (so ladder-droppable ≡ helper-droppable, pinned). A
  cross-repo consistency test asserts both repos consume the one source.
- **INV-E (hard gate).** `SNAPSHOT_FORMAT_VERSION = 2`; loader rejects any other version; no v1/v2
  coexistence; all committed snapshots re-captured on v2.
- **INV-F (loud resolution).** `is_instance` and `elements_of_type` raise on an unknown type name
  (D6); no `is_instance` call in the ladder can silently no-op. `level6` no longer swallows to `[]` (D7).
- **INV-G (stable order).** `collect_constraint_manifest` stable-sorts by
  `(owner_qualified_name, constraint_name)`; serialize and render preserve that order (M9) — so parity
  bytes are deterministic regardless of swept order.

## Component Overview

- **`elements_of_type` / `is_instance` (agentic-mbse `syside_adapter.py:~214`, TYPE_MAP `~244`)** —
  the two params + D6 hard-error + docstring teaching the decision table (D4-mandated docs home).
  Preserve the current decorator (called both `SysideAdapter.elements_of_type(...)` and
  `self.adapter.elements_of_type(...)` — a `@staticmethod` serves both; confirm at implement).
- **`EXCLUDED_CONSTRAINT_TYPES` + `is_droppable_constraint` (adapter, new)** — the single policy source.
- **`ConstraintKind` / `OwnerKind` / `ConstraintManifestEntry` / `render_constraint_report`** — new
  pure report module. Kinds: `ASSERT`, `PLAIN` (droppable), `REQUIREMENT`, `SATISFY` (excluded).
  Ordered is_instance ladder: assert → satisfy → requirement → plain (satisfy before requirement
  because `SatisfyRequirementUsage ⊂ RequirementUsage`). Owner tokens: `CALC_DEF`, `PART_DEF`,
  `PART_USAGE`, `ELEMENT`, `MODEL`.
- **`collect_constraint_manifest`** — live producer on the extractor, injectable policy (MF5).
- **serializer/loader/snapshot_context/PipelineContext/capture** — thread the manifest through.
- **agentic-mbse `level3_dataflow` / `level4_constraints` / `level6_architecture`** — rows 5/6/7 fixes
  (row 7 also removes the swallow, D7).
- **REQ-EXT-09 test class + docs** — re-anchor and truth updates.

## Non-Goals

Constraint execution; connection/interface/view/case/analysis extraction (row 4);
`EnumerationUsage`-as-entry-point (row 3, Item 5); the D3 silent-failure sites **except the one
level6 swallow this item absorbs (D7)**. Distinguishing `require` from `plain` in the manifest
(folded as `PLAIN`; the require/assume kind lives on the membership — a documented v2 limitation,
revisited by the constraint-execution epic).

## Implementation Notes

- **Zero-found sentinel (row 1).** One always-emitted INFO from `render_constraint_report`:
  `"Constraint drop report: scanned {N} ConstraintUsage (incl. subtypes), reported {M} droppable
  ({K} assert, {J} require/plain), excluded {E} requirement/satisfy."` Then M per-droppable INFO
  lines. Then, only if `M > 0`, the existing summary WARN. **Both paths pass the
  `sysml_codegen.extraction.extractor` logger** (so caplog filters and byte output match — do not let
  render default to its own module logger). N=0 → sentinel all zeros, no WARN; N>0,M=0 → scanned>0 /
  excluded>0, observable, no WARN.
- **REQ-EXT-09 re-anchor** (`tests/conformance/test_extractor.py`, class 888–922; self-referential
  block 895–899): (a) replace `expected = sum(same query)` with a **literal** transcribed from a
  fixture-source grep, commented with the grep; (b) add the **part-usage-owner** leg — needs a fixture
  carrying a part-usage-owned constraint (wi014's assert is part-*def*-owned; confirm catf_mfe covers
  part-usage, else add a small **Item-4-owned** fixture — owned work, per Potential Risks, not a
  quiet drop); (c) **wi014 assert pin** (literal 1 droppable assert `affordable`); (d) **executable
  mutation check** — call `collect_constraint_manifest(include_subtypes=False)` (the injectable policy,
  MF5) and assert the assert is MISSED, proving the test discriminates; (e) **from-snapshot INV-B leg**
  (license-free) asserting the replayed report == the live report and matching the golden manifest
  fragment. No mocks (R1) — live extractor + committed snapshot.
- **House style (R1):** `ConstraintKind`/`OwnerKind` are `Enum`s (V1–V11 idiom); manifest entries are
  a frozen dataclass; the kind-ladder is compute-once (build manifest) then look-up (render). The
  manifest is a list, not a map — no NewType key introduced.
- **agentic-mbse row 5:** prefer `elements_of_type("Import", include_subtypes=True)` (consistent
  mechanism; "Import" is already in TYPE_MAP — queried at `:48` today — so no new TYPE_MAP name needed
  for row 5) over enumerating the concrete subtypes; ALSO fix the `imported_namespace` guard that skips
  MembershipImports. Pins: seeded circular-import fixture FAILS the circular check + non-empty graph
  (fires-on-shape); acyclic fixture PASSES, non-empty graph, no false cycle (silent-on-clean).
- **agentic-mbse row 7 (D7):** narrow/remove `level6_architecture.py:601 except Exception:
  constraints = []`; add an error-injection test row proving it fails loud, not to `[]`.
- **Format bump + re-capture (D5, [HARD]).** Bump `snapshot/__init__.py:12` to 2. Re-capture **all
  committed** `tests/fixtures/*/extraction_snapshot.json` (20 today; **plus Item-1's additions** — M7)
  via the capture script (Item 1's `--fixtures` filter), **one reviewed commit**, license-gated.
  Reviewed-diff gate: every snapshot byte-identical to before EXCEPT the `snapshot_format_version`
  field and, for constraint-bearing models, the new `dropped_constraints` array (stable-ordered).
  Sequencing (spec [HARD]): **Item 1 impl → Item 4 impl → Item 2 impl**, one working tree, one regen
  at a time.
- **Docs (same change):** `modeling-assumptions.md` §8 reworded (report covers `ConstraintUsage`
  incl. `assert`/`require`/plain, excludes `RequirementUsage`+`satisfy`, live + from-snapshot);
  `01-extraction.md` REQ-EXT-09 row (independent anchor + part-usage leg + assert pin, drop the
  "counted structurally" anti-pattern text); decision table published in agentic-mbse adapter docs
  with a pointer here; retire BACKLOG `[CONSTRAINT-SILENCE]`.

## Potential Risks

- **Adapter shape uncertainty (agentic-mbse sandbox-blocked).** I could not read `syside_adapter.py`
  to confirm the decorator/signature of `elements_of_type`/`is_instance`, that `nodes` accepts
  `include_subtypes`, or the exact `TYPE_MAP` shape (`:244–246` per register). Mitigation: the change
  is additive keyword-only params + three map entries + a guarded hard-error; the register (§D4
  L117–118,129) states the subtype mode exists, the map lacks subtype names, and `is_instance` no-ops
  on a miss. **Implement must re-read the adapter first** and adjust the exact `nodes`/`TYPE_MAP` calls.
- **`require` vs `plain` conflation.** Folded to `PLAIN`; a future consumer needing the distinction
  inspects the membership — a documented v2 gap, not a silent loss.
- **Re-capture blast radius.** ~20+ license-gated regenerations in one commit; a stray semantic diff
  means an unintended extraction change slipped in. Mitigation: the reviewed-diff gate; diff every file.
- **Part-usage-owner fixture (owned work).** The re-anchor's part-usage leg may need a new fixture;
  keep it Item-4-owned and minimal so it doesn't entangle Item 1's fixture work.

## Integration Strategy

Extends, replaces nothing structural. `report_dropped_constraints` keeps its name and call site
(`pipeline_builder.py:685`) but delegates to collect+render. The from-snapshot path gains the report
it never had. The adapter change is backward-compatible for value inputs (defaults preserve every
current call) — the one intentional behavior change is D6 making a previously-silent unknown-name
`is_instance` now raise, which is desired (loud-if-wrong). The format bump is the one breaking change,
absorbed by the mandated re-capture.

## Validation Approach

- **Live (license):** REQ-EXT-09 fires on wi014 assert + catf_mfe (independent literal), covers
  calc-def/part-def/part-usage owners, mutation check discriminates (MF5), silent-on-clean holds.
- **Offline (license-free):** INV-B parity — from-snapshot report == live output + golden manifest
  fragment; loader rejects a v1 snapshot (INV-E).
- **Adapter (companion):** `is_instance`/`elements_of_type` **raise on an unknown type name** (D6/INV-F);
  cross-repo policy-source consistency pin (INV-D).
- **agentic-mbse (companion branch):** seeded circular-import FAILS + non-empty graph; acyclic PASSES;
  level4/level6 assert fixtures fire; **level6 error-injection fails loud not `[]`** (D7); enum fixture
  pins row 8.
- **Re-capture gate:** reviewed diff = version field + manifest only.
- **Both suites green** (R2). **R4:** run `_probe.py` live and update register §D4.

## Next-Stage Handoff

- **Fixed:** D1–D8; the collect/render split; manifest shape (typed tokens, stable order); sentinel
  wording + logger; format bump to 2; sequencing Item1→Item4→Item2; TYPE_MAP additions + hard-error;
  level6 swallow absorbed; single-sourced droppable policy; mutation-check via injectable policy.
- **Open (implement resolves):** exact adapter signature/decorator, `nodes` call, and `TYPE_MAP`
  shape (re-read agentic-mbse first); the three agentic-mbse line numbers (re-verify, "probe wins");
  whether catf_mfe carries a part-usage-owned constraint or a fixture is needed; the require/plain
  fold is accepted.
- **De-risk first:** re-read the agentic-mbse adapter, land the TYPE_MAP additions + hard-error (D6),
  and run `_probe.py` live BEFORE touching any call site — every downstream edit assumes B1+B2 (subtype
  mode exists, names resolve, is_instance hierarchy-aware). Then adapter params + policy source →
  codegen report → serialization + re-capture → the three validators.

---
Next Step: After approval → `/_my_plan` (multi-file, cross-repo, sequenced re-capture warrants a checkboxed plan).
