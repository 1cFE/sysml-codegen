# Design Review: Silent-Failure Hardening (PIPELINE-TRUTH Item 5)

**Design:** `.project/active/silent-failure-hardening/design.md`
**Spec:** `.project/active/silent-failure-hardening/spec.md`
**Review File:** `.project/active/silent-failure-hardening/design-review.md`
**Date:** 2026-07-06
**Reviewer posture:** skeptical; findings verified against code where reachable.

---

## Fundamental Assessment

**Sound.** The core concept — totality at each load-bearing dispatch/lookup/handler, routing an
unhandled input to a distinct warned sentinel instead of a valid-looking bucket — is the right
frame, it generalizes an invariant the codebase already commits to (doc-19 REQ-AST-08), and it
reuses the existing `warnings`/`ExtractionReport`/Item-4-report plumbing rather than inventing a
subsystem. The four-family decomposition holds against the code. This is not over-engineered.

**The highest-risk claim checks out.** I independently verified the D3-7 reclassification (the one
finding whose whole treatment flips on a probe result). Live execution is blocked by this session's
sandbox (every `python`/`pytest`/`uv run` invocation returns "requires approval"), so I verified by
code trace instead — which for this shape is conclusive:

- Computed-attribute extraction is **per part-def**, not per-usage: `pipeline_builder.py:120-131`
  iterates every `PartDefinition` element and extracts its FORMULA attrs regardless of whether any
  usage references it. So both `D37PkgA::Widget.result` and `D37PkgB::Widget.result` land in
  `computed_attributes`. The `NoopCalc` fixture does **not** short-circuit this — it only satisfies
  the build-context precondition, exactly as intended.
- Phase 1c (`orchestration/output_registry_builder.py:207-231`) then builds
  `key_f = f"{ca.owning_part_name}.{ca.python_name}"` = `"Widget.result"` for **both**, with a
  `canonical` channel whose name embeds `part_qn_python` (line 214) — which differs per package. So
  `register_scoped("Widget.result", channelA)` then `register_scoped("Widget.result", channelB)`
  hits the different-channel branch and **raises** at `core/output_registry.py:72`.
- This raise is inside `build_pipeline_context`, strictly before `graph_builder._build_attribute_
  resolution_map` (the merge site D3-7 claimed was silent) is ever reached.

So B3 holds and the reclassification is real: the reachable FORMULA shape is loud-rejected, not
silently cross-wired. The fixture reaches the guard; the guard is not bypassed by the probe's
scaffolding. Pin-the-guard + state-the-invariant is the correct treatment, and the deferred bare→QN
re-key as optional defense-in-depth (pending a consumer audit) is a defensible call.

The approach is sound, so I proceeded to the detailed review. Two Critical issues and three Major
issues below — none reframe the item, but #1 and #2 must be resolved before implementation.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every CONFIRMED finding has a row in the Appendix fix-map, and I walked the table→fix mapping: no
CONFIRMED site is orphaned to a per-site patch outside its family (priority 2 — coverage is
complete). D3-14 stays in-family with a concrete fix (D6: narrow the `except`, WARNING log,
preserve-on-transient), answering priority 7.

Two compliance gaps:

- **SC-5 vs INV-6 on `plant_value_shapes` (see Major #3).** The spec pins SC-5 on
  `plant_value_shapes`, which is also a committed byte-identical baseline. The design's success
  criteria require both, and the design doesn't reconcile them.
- **SC-4 A1's fail-fast has no named site (see Major #4).** The spec's `[HARD]` requires a
  collision fail-fast at channel/EP key construction; the design names no location for it.

### 2. Pattern Consistency
**Assessment:** Concerns

Reuse of the doc-19 sentinel pattern, the Item-4 report shape, and the `register_scoped` guard is
the right instinct — these are the house patterns, extended not reinvented.

But **D3-8 reaches for the wrong existing map** (Critical #1). Swapping the whole `OPERATOR_MAP` for
`PYTHON_OPERATOR_MAP` at the aggregation walker imports that map's *narrowness* as a side effect,
not just its `^`→`**` entry. That is pattern-borrowing without checking the pattern fits.

Minor path drift: the design cites `resolution/output_registry_builder.py` (Architecture line 148,
Component Overview line 185); the file is `orchestration/output_registry_builder.py`. A plan
following the design would look in the wrong package.

### 3. Abstraction Quality
**Assessment:** Concerns

The "one choke point per family" framing is looser than it reads (see Major #5). Families 1 and 3
are really "one *pattern* applied at N arms," not one code location. The design is honest about this
("five edit clusters"), and the unifying totality concept + per-arm tests + stated invariants is a
legitimate anti-whack-a-mole defense. But the prose oversells a single chokepoint where the reality
is a per-arm discipline backed by an invariant, and nothing structurally prevents a *new* arm from
reintroducing the silent bug.

### 4. Duplication Avoidance
**Assessment:** Pass

No parallel structures introduced. Diagnostics ride existing channels. The D3-12/SC-5 shared
omission-site fix (D4) is the right call — one predicate at the shared site (`parameter_groups.py:
601`), both roots narrowed, avoiding the double-patch the spec warned about.

### 5. Data Structure Clarity
**Assessment:** Pass

No new data structures. The `warnings` list + `ExtractionReport` + `ctx.has_unsupported` flag are
existing, typed, and traceable.

### 6. Route Safety
**Assessment:** Concerns

This item *is* about route safety, and it mostly improves it. The one regression risk is Critical #1:
routing every comparison/logical operator to `has_unsupported` is a new catch-all that mis-classifies
valid inputs. A totality fix that over-rejects is its own route-safety defect.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B3 (D3-7 guard closes every reachable cross-wire) — verified true.** See Fundamental Assessment.
- **B4 (present-vs-absent distinguishable at the raw source string) — sound.** The predicate warns
  on present-but-unparseable, stays silent on genuinely-absent. A legitimate String entry-point that
  can't parse as float *is* present-but-unparseable, so the warn firing on it is the SC-5 contract,
  not a false positive — correct.
- **B2 (totality generalizes with no clean-model regression) — partially false as stated.** Two
  cracks: the `plant_value_shapes` INV-6 tension (Major #3) and the latent comparison-operator
  rejection (Critical #1). B2's "the loud arm is unreachable on any clean corpus fixture" is exactly
  what breaks for `plant_value_shapes` under SC-5.
- **Hidden bet surfaced: the design bets it can edit `_walk_aggregation_ast` in isolation.** It
  can't — Item 8 is editing the same function concurrently (Critical #2). This load-bearing
  assumption is unstated and, as of the `item8 Phase 0` commit, wrong.
- **D3 (map swap) is presented as a decision with a rejected alternative ("leave the pass-through
  fallback"), but the real alternative — a *narrow* fix that keeps comparison/logical translation —
  is never considered.**

### 8. Reader Comprehension
**Assessment:** Pass

The design reads well. Core Concept states the model before the mechanism; the Key Bets each carry
an honest "if false → what fails"; the Appendix fix-map is the right altitude for a plan to consume.
No comprehension-blocking jargon. The one place the prose misleads is the "choke point" language
(Major #5) — a clarity issue, not a blocker.

---

## Issues by Severity

### Critical (must address before implementation)

- **C1 — D3-8's map swap is too broad; it silently drops comparison/logical operator support.**
  `OPERATOR_MAP` (`expression_utils.py:13-30`) contains `and or == != > < >= <= implies not` plus
  arithmetic. `PYTHON_OPERATOR_MAP` (`expression_compiler.py:151-159`) contains **only**
  `+ - * / ** ^ [`. The aggregation walker uses the map generically for *any* binary
  `OperatorExpression` (`hierarchy_resolver.py:367-371, 377-383`). After the swap, a
  `sum(x) > threshold`-style aggregation — which today emits valid Python `(left > right)` — hits
  `PYTHON_OPERATOR_MAP.get(">")` → `None` (absent) → `has_unsupported=True`. That is a **new
  false-positive rejection** of a class of inputs, not just the `^`→`**` fix. The design's
  byte-identity rationale ("the `^` corpus has none") tests the wrong thing: it must also assert no
  corpus aggregation uses any of the dropped comparison/logical operators, *and* decide whether
  rejecting them is intended. **Latent today** (the corpus uses these operators only inside doc
  comments — I grepped every fixture; the real `^` in `solar_battery_model/library.sysml:317,339` is
  doc-comment prose, the actual expressions already use `**`), so no baseline moves right now — but
  the fix instrument is semantically wrong and would bite the first real comparison/logical
  aggregation. **Fix:** don't swap wholesale. Either change `OPERATOR_MAP`'s `^` entry to ` ** ` in
  place and replace the `f" {operator} "` fallback with `has_unsupported`, or merge the maps so
  comparison/logical translation survives and only genuinely-unknown operators trip
  `has_unsupported`.

- **C2 — Missing coordination fence with Item 8, which edits the same function concurrently.**
  Item 8 (cleanup-debt) scope point 3 is the "aggregation-literal dispatch bug: `_walk_aggregation_
  ast` literal-after-invocation ordering … with a byte-identity gate on existing corpora" (epic
  `epic_pipeline_truth.md:653-656`). That is the *same* `_walk_aggregation_ast`
  (`hierarchy_resolver.py:331`) D3-8 edits, and the literal check Item 8 reorders is at line 453 —
  which sits between the operator sites (370, 382) and the unknown-node arm (457) D3-8 references.
  Item 8's `item8 Phase 0` preflight is already committed. The design fences Items 2 and 4 in its
  Non-Goals but says nothing about Item 8. Two concurrent edits to one function, each with its own
  byte-identity gate, will collide and the cited line numbers will shift. **Fix:** add an explicit
  Item-8 fence — decide who lands the walker change first (cleanly, D3-8 rides on Item 8's corrected
  dispatch order), and note that D3-8's line cites are relative to Item 8's reorder.

### Major (should address)

- **M3 — SC-5's warn on `plant_value_shapes` breaks INV-6 unless carved out.**
  `plant_value_shapes` has a committed `tests/fixtures/baseline_outputs/plant_value_shapes/` and is
  the SC-5 pin fixture. SC-5's warn-on-unparseable-present (D4) *will* fire on its enum entry point
  (`wall = 'Wall Kind'::liquid_wall`). The design names only two carve-outs (D3-2, D3-8) and asserts
  "Every clean fixture holds INV-6" (line 227). That assertion is false for `plant_value_shapes`
  once SC-5 lands. Generated *bytes* likely stay identical (the design warns rather than pre-fills,
  so the EP stays omitted), but the **zero-WARNING** clean sweep breaks. **Fix:** declare
  `plant_value_shapes` a trip fixture (expected-warning, excluded from the INV-6 zero-WARNING sweep),
  or add it as a third explicit carve-out. Either way the "every clean fixture holds INV-6" sentence
  needs qualifying.

- **M4 — SC-4 A1's collision fail-fast has no named site.** The Appendix row reads "channel/EP key
  construction | Collision fail-fast (`register_scoped` pattern)" with no file:line. But channels
  *already* fail fast through `register_scoped` (`output_registry.py:72`) — the real gap is
  entry-point key construction, and the design never identifies which EP-key site gets the guard. A
  plan can't add a guard at an unnamed boundary. **Fix:** pin the exact EP-key construction site(s)
  (e.g., the design-attribute / parameter-group EP keying in `parameter_groups.py` / `graph_builder.py`)
  and state the guard boundary is registration/key-construction time, not sanitize time.

- **M5 — "one choke point per family" oversells Families 1 and 3.** These are one *pattern* applied
  at multiple arms (Family 1: six arms across three files; Family 3: three collision-warns at three
  lookup sites + a guard pin), not a single chokepoint. Sanctioned by the spec's Open Questions
  (interim require-unique-or-warn is explicitly allowed, QN re-key deferred), so **acceptable** — but
  the framing hides that the underlying bare-name keying (Family 3) and non-total dispatch (Family 1)
  persist everywhere a warn isn't hand-placed; a newly-added lookup or arm reintroduces the silent
  bug with no structural guard. **Fix:** soften the "choke point" language to "one pattern + stated
  invariant per family," and lean on INV-1/INV-3 as the durable contract (they already say the right
  thing). No code change required.

### Minor (consider addressing)

- **m6 — Path cite drift:** `output_registry_builder.py` is under `orchestration/`, not
  `resolution/` (design lines 148, 185).
- **m7 — "the `^` corpus has none" is imprecise.** The corpus contains `^` (in doc comments at
  `solar_battery_model/library.sysml:317,339`); the precise, defensible claim is "no *aggregation
  expression* uses `^`." State it that way so the carve-out reasoning survives scrutiny.
- **m8 — Live-run gate not met this session.** The design's Design-Open Gate table asserts "every
  probe ran live." I could not reproduce that here — the sandbox denies all Python execution. The
  D3-7 claim is verified by code trace (conclusive for this shape), but if the orchestrator relied
  on a live run elsewhere, note that this reviewer confirmed statically, not by re-execution.

---

## Recommendations

1. **C1:** Replace the wholesale map swap with a narrow D3-8 fix (fix `^` in place + `has_unsupported`
   on genuinely-unknown operators). Re-state the byte-identity test as "no aggregation uses `^` or any
   comparison/logical operator," and confirm it against the corpus.
2. **C2:** Add an explicit Item-8 coordination fence for `_walk_aggregation_ast`; sequence the two
   edits and rebase D3-8's line cites onto Item 8's literal-reorder.
3. **M3:** Reconcile SC-5 with INV-6 — mark `plant_value_shapes` an expected-warning trip fixture (or
   third carve-out) and qualify the "every clean fixture holds INV-6" claim.
4. **M4:** Name the EP-key construction site(s) that receive the SC-4 A1 fail-fast.
5. **M5:** Soften "choke point" to "pattern + invariant"; make INV-1/INV-3 the load-bearing contract.
6. **Minors:** fix the `orchestration/` path cite and the "`^` corpus has none" phrasing.

---

## Resolutions

_Filled in during Stage 4 as the user resolves each issue. Do not edit the design here._

---

**Overall:** Revise
**Next Steps:** Once resolutions are recorded above, re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The reviewer does not edit the
design. C1 and C2 are the two that block implementation; M3–M5 are completeness gaps a plan would
otherwise trip over. The D3-7 reclassification is verified sound and needs no change.

ARTIFACT: .project/active/silent-failure-hardening/design-review.md
