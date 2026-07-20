# Spec: Producer Completeness and Stellarator Rollup (Lifecycle Item 10)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`, Item 10 (register row 12)

---

## Problem

Two gaps remain between the constraint-execution machinery and the ratified end-to-end claim.
They are one item because they are two faces of the same rule: **every model-derived consumed
value must resolve to one real, intended producer** (invariants 19–26; owner decisions D-1/D-2).

**Gap 1 — V11 is not producer-completeness, and nothing else proves it.** Final generation
requires zero whole-graph V11 uncovered inputs (invariant 26). But V11 passing does not mean each
consumed value found its *intended* producer: a defaulted fallback or an ambiguous first-match
binding (two producers whose leaf names collide) can satisfy V11 while silently feeding the wrong
value. Item 2 already deleted the guessing behaviors from the resolver. This item must *prove* the
property holds — as its own acceptance, independent of whether V11 happens to be clean — so a
future regression that reintroduces a guess is caught by a producer-completeness check, not by
luck.

**Gap 2 — the stellarator still cannot generate publicly; one private bridge stands in the way.**
The stellarator demo package is generated through a private bridge (`bridge_v11_generate.py`,
labeled "LOCAL BRIDGE — NOT A FIX") plus a two-pass harness. The ratified boundary (D-1) forbids
any public late-fill or post-build graph/default mutation seam; a private bridge cannot certify
the lifecycle. Measured at today's chain, the bridge compensates for exactly one thing (below).

**What the bridge still compensates for — measured at today's chain (HEAD `5a6f930`, codegen
post-Items 2/4/8), not WI-027's pre-epic record:**

- **Gate A (constraint actuals) — resolved.** The staged twins already carry the five asserts
  live, reading design attributes directly (`in beta = beta`, `in tbr = tbr`;
  `stellarator_plant.sysml:742-754`). No `Scalar Value` passthrough def exists in any model file.
  D-2's shared resolver (Item 2) accepts literal design-attribute actuals directly. WI-027's D7
  passthrough decision was designed but never landed, and is superseded by D-2.
- **Gate B (extension-time V11 check) — deleted upstream** (Item 3, proven vacuous).
- **The cross-part capital aggregation — the sole remaining gap.** Codegen still cannot compile a
  feature-chain sum across parts in a CalcDef output (`calc_compat_renderer.py:103` raises
  "feature chain expression not supported in CalcDef output"). So the staged twin converts
  `direct_capital` and `total_capital` from their canonical cross-part-sum formulas
  (`mfe_plant.sysml:400-424`) to plain valueless inputs. The bridge fills the three resulting
  keys (`contingency__direct_subtotal`, `indirect__direct_cost`, `lcoe_calc__total_capital`) with
  a placeholder at generation, and the two-pass runner (`run_stellaris.py` glue-2) computes the
  real sums in Python and overwrites them before the canonical pass. That harness arithmetic is
  the consumer mutation this item must replace with a real graph producer.

So: the distance from public generation is one codegen capability — compile the modeled cross-part
capital aggregation into the ordinary graph — plus the cleanup of the workarounds that the missing
capability forced.

## Success Criteria

The ambiguous/defaulted producer counterexample is the **de-risk-first (RED-first) coordinate** —
build and prove it BEFORE the stellarator rollup (epic De-risking note; Risks row "Drive exact-QN
and ambiguous/defaulted counterexamples first").

- [ ] **Ambiguous/defaulted producer acceptance exists and is RED-first.** A model with two
      same-leaf candidate design attributes and a defaulted-fallback shape either fails generation
      with a named ambiguity/producer error, or resolves only under exact QN — and produces **no
      verdict from a guessed or defaulted binding while V11 is clean**. (Invariant 26; acceptance
      matrix row "Ambiguous/defaulted producer resolution".)
- [ ] **Producer completeness is explicit, deterministic, and independent of V11.** Every
      model-derived consumed value resolves to one intended producer under exact identity;
      legitimate external typed design inputs remain ordinary typed entry channels, not flagged as
      missing producers.
- [ ] **Codegen compiles the modeled cross-part capital aggregation as a real graph producer**,
      through the same graph machinery as calculations/aggregations — `direct_capital` and
      `total_capital` are wired producers, with no private bridge, no placeholder default, no D7
      passthrough calculation, and no consumer (harness) mutation of the rollup.
- [ ] **The stellarator generates publicly and its ordinary numerics are unchanged.** A fully
      representable graph builds through the supported public path; the five verdicts appear as
      data; the ordinary numerical anchors below are bit-identical to the WI-025/WI-027 baseline.
- [ ] **WI-027 is amended** with a supersession pointer to D-2; its D7 passthroughs are removed
      (artifact-level; none are in the model); the private bridge, placeholder fill, and two-pass
      rollup glue are retired from the demo package.
- [ ] **Named aggregation/resolver workarounds are deleted; no parallel producer mechanism or
      compatibility wrapper remains** (qualitative simplification mandate; no LOC accounting).

**Ordinary numerical anchors (from WI-027 / WI-025 executed record — the "unchanged numerics"
bar).** Public single-pass generation must reproduce these bit-exactly, now that the rollup comes
from the graph rather than harness Python:

- Total capital $12,638,857,665.74
- LCOE $203.647152/MWh
- p_net 915.081088 MW
- q_eng 6.606662
- rec_frac 0.151362
- magnet $6,323,469,946.33 (50.03% of total)
- Every executed numeric channel matches the pure-Python oracle at rel dev < 1e-9.

**Five constraint verdicts (all `satisfied`, none on a boundary):** `net_positive`,
`recirc_ok`, `beta_ok`, `wall_load_ok`, `tbr_ok`.

## Known Requirements

- **[INHERITED]** Calculation inputs and constraint actuals use one shared positive-resolution
  procedure — real producer channel first, then real design attribute under exact qualified
  identity; an omitted constraint formal takes a modeled default only when the model declares it.
  (Invariants 19–20, contract.)
- **[INHERITED]** A direct literal-valued design attribute is a valid design-attribute actual,
  available during graph construction, reusing the same QN-keyed typed entry point as any
  calculation consumer; a passthrough calculation is a workaround, not conformance. (Invariant 21;
  D-2. This is why D7 is removed, not reimplemented.)
- **[INHERITED]** Final generation requires zero whole-graph V11 uncovered inputs; a **separate**
  producer-completeness check proves every model-derived consumed value resolves to one intended
  producer under exact identity, while legitimate external design inputs remain ordinary typed
  entry channels. V11 is not a substitute — a defaulted fallback or ambiguous first-match can pass
  it. No late-fill, leaf-name guess, ambiguous first-pick, or post-build graph/default mutation
  seam is supported. (Invariant 26.)
- **[INHERITED]** Supported codegen requires a fully representable graph and exposes no late-fill
  or post-build graph/default mutation seam; the fusion bridge is private workaround evidence only,
  never a certification path. (D-1 [OWNER-VERBATIM].)
- **[INHERITED]** WI-027's D7 passthrough decision is superseded by D-2; the WI-027 artifact must
  point to the contract and its passthroughs must be removed before stellarator acceptance.
  (Contract, D-2 note; Appendix B correction register.)
- **[INHERITED]** The stellarator design-point acceptance is a fully representable graph with D7
  passthroughs removed, no post-build mutation / private bridge, five verdicts, unchanged numerics,
  and sealed handwritten content. (Acceptance matrix row "Stellarator design point (D-1/D-2)".)
- **[INHERITED: WI-027 MR-WI027-2]** No hand-coded viability rule anywhere in the demo pipeline —
  grep-provable across the demo package and its harness (oracle, runner, handshake, glue). Removing
  the two-pass rollup glue must not reintroduce or leave any viability comparison in harness code.
- **[NEED]** Deletion over shims: name the superseded aggregation/resolver workarounds before
  design and delete what the cross-part-aggregation capability obsoletes; no compatibility wrapper,
  parallel authority, or duplicate producer route replaces them. Simplicity is judged
  qualitatively by review — **no numeric LOC gate, baseline, or accounting.** (Owner amendment
  2026-07-19, epic Simplification and Deletion Mandate.)
- **[INFERRED]** With the cross-part sum as a real graph producer, the stellarator runner cutover
  is single-pass (or otherwise bridge-free): the two-pass placeholder-then-overwrite structure and
  its glue-2 Python rollup become obsolete and must be deleted, not left dormant. The generated
  graph — not harness arithmetic — must produce the anchor numerics. (Follows from scope items 3/5
  and D-1; the mechanism is design's.)
- **[INFERRED]** The stellarator snapshot must be recaptured from the current staged model: the
  committed snapshot carries zero constraint facts (captured 2026-07-18 from a stripped state) and
  is snapshot-format v3, which predates the Item 4 v4 amendment. Recapture is a prerequisite for
  any regen evidence; the exact format/version handling is design's. (Measured; mechanism deferred.)

## Non-Goals

- **Public late fill or a permanent model placeholder** — barred (D-1; epic firewall).
- **Weakening exact-QN resolution, final V11, or declared external-input semantics** — the
  producer-completeness check is additive; legitimate external typed design inputs stay ordinary.
- **New physics constraints** not already modeled (ISS04 confinement-consistency, etc.) — the
  executing set is the five already modeled; out of scope (WI-027; concept Open Question 3).
- **IFE work** — done; the IFE acceptance is evidence the machinery works, not a surface to change.
- **Item 11 (TEAx constraint evidence durability) semantics** — the report/evidence persistence
  and immutability path is Item 11; this item makes the stellarator produce verdicts, not redefine
  how TEAx stores them.
- **Any cost/account change or numeric re-baseline** — the anchors are frozen; a numeric shift is a
  surface-to-orchestrator event, never a silent re-baseline.
- **Item 1 artifacts** — untouched (in flight; owner ruling).

## Open Questions / Deferred to design

- **How codegen compiles the cross-part capital aggregation.** Whether it routes through the
  existing aggregation machinery (`hierarchy_resolver.py` cross-part handling, the aggregation
  resolver Item 2 unified) or extends feature-chain compilation (`calc_compat_renderer.py:103`,
  `predicate_compiler.py:152`), and whether support is general (any cross-part feature-chain sum)
  or scoped to the stellarator's `direct_capital`/`total_capital` shape. Capture the outcome
  (these become real producers with unchanged numerics); the mechanism is design's, driven with
  the expertise of SysML modeling and codegen graph assembly.
- **Where and how producer-completeness is enforced** — a distinct check separate from V11, its
  identity/keying (exact QN), its error surface (named ambiguity/producer error), and how it
  distinguishes a legitimate external typed design input from a missing producer.
- **The exact ambiguous/defaulted counterexample fixture shape** — the two same-leaf candidate
  design attributes plus the defaulted-fallback construct; on both public routes (live and
  relocated snapshot).
- **The stellarator runner cutover mechanics** — single-pass vs. bridge-free two-pass, how the
  BOP-wiring rewrite (`patch_bop_wiring`) and exit-point handling adapt, and the exact deletion
  set (bridge, placeholder keys, glue-2, offender-count asserts).
- **The deletion inventory** — the named aggregation/resolver workarounds and any
  string-surgery/compatibility surface the new capability obsoletes, listed before design and
  verified deleted (not shimmed) at implement.
- **Cross-repo phasing** — the codegen producer-completeness check + cross-part-aggregation
  capability land in this repo (the one PR-wave landing unit); the WI-027 amendment, bridge
  removal, recapture, and public regen land in the stellarator repo as its own modeling-PM record.
  The de-risk coordinate (ambiguous/defaulted acceptance) is first regardless. Certification stays
  ordered behind open predecessors (Item 9) per the register.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`, Item 10.
- **Required Reading:**
  - Ratified contract D-1/D-2 and invariants 19–26:
    `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
    (invariants `:172-195`, D-1/D-2 `:284-298`, acceptance matrix rows `:435-462`).
  - WI-027 spec/design/plan:
    `../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/`.
  - Gate B independent assessment:
    `.project/research/20260719-103419_gate-b-independent-assessment.md`.
  - Gate B consumer root cause:
    `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`.
- **Stage brief:** `./briefs/spec.md`.
- **Measured state (this spec):** stellarator repo at `43a1d405` (Gate B filing committed as its
  own ratified record before Item 10 work); codegen HEAD `5a6f930`; bridge
  `../fusion-tea-stellarator-mbse-demo/exploration/stellarator_e2e/bridge_v11_generate.py`;
  cross-part rollup `mfe_plant.sysml:400-424` (canonical) → plain inputs (staged `:409/:434`).
- **Design:** `.project/active/constraint-lifecycle-producer-completeness/design.md` (to be created).

---

**Next Steps:** After approval, proceed to `/_my_design`. Independent `/_my_spec_review` in a fresh
session is available before design.
