# Spec: Predicate Defect Hardening (CONSTRAINT-SEMANTICS Item 4)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-13
**Complexity:** MEDIUM
**Branch:** `item7-rebuild` (codegen, tip `7f1b943`) + `/home/reid/1cfe/agentic-mbse-item7-rebuild` (companion, tip `bc69f04`)

---

## Problem

Two reproduced defects sit exactly on the boundary a modeler crosses when writing an asserted
physics gate. Both were isolated in research §6, and both are in-scope must-fixes
**[INHERITED: rulings-20260812.md Q8]**.

**Defect A — a unit-annotated literal in an inline asserted predicate refuses the whole model.**
`assert constraint { bioshield.outer_radius == 8.55 [m] }` produces
`SI_OCCURRENCE_MISSING: leaf declaration <uuid> has no feature slot`. The literal is not a missing
feature occurrence; dropping `[m]` removes the error. The cause is a lane gap, not a new rule. The
product already owns one rule for unit annotations — *a unit annotation contributes its value and
never a reference* (`src/sysml_codegen/extraction/unit_annotation.py:1-28`) — and a prior fix cured
the same category error in two lanes, kept pinned by
`tests/conformance/test_unit_annotation_values.py`. The rule reaches those two lanes at the top of a
feature-value expression (`elaboration/elaborate.py:758`, `:863-878`). It does not reach the
predicate-expression reference walk: `_expression_references`
(`elaboration/elaborate.py:2371-2412`) recurses into every operand of an `OperatorExpression`,
including the `[` annotation's second operand, which is the standard-library element `SI::metre`.
`FeatureSlotIndex` carries only the user model's features, so the walk reaches `_resolve_leaf`
(`elaborate.py:2162-2168`) and raises. This is the *third* lane of a defect class already cured
twice — the fix belongs in codegen.

The research reproduction is a *diagnosis* shape, not an authoring shape: `bioshield.outer_radius
== 8.55 [m]` is unsupported twice over even after this item — a chain in the predicate body (Q4)
and a bare quantity equality (`block_real_equality_requires_tolerance`). It isolated the defect,
and it is not what the cure is demonstrated on. The kept characterization uses a predicate that is
otherwise fully supported — an inequality over an in-scope feature or a bound formal, carrying a
compatible unit-annotated literal — so the pinned end state is a gate that *works*, not an error
code that stopped appearing. Blessing `== <literal> [unit]` as the worked example immediately
before Item 5 copies an authoring shape 65 times would cut against the owner's equality
instruction (`rulings-20260812.md`, Q4 owner-verbatim payload).

**Defect B — the blocked-chain diagnostic tells the modeler nothing.** When the executable profile
blocks a feature chain inside a predicate, the emitted text is literally
`feature_chain: block_feature_chain` — the rendered `reason: message` pair
(`elaborate.py:1097-1108`) with no offending reference, no segment, and no location.
`LayerContinuity` produces 13 identical copies in one detail string. A modeler cannot tell *which*
of a multi-chain predicate's references is at fault, and nothing states the supported rewrite. This
matters now because Item 5's all-65 CATF migration is precisely the exercise of rewriting chains
into bindings; the diagnostic is the instrument that migration is done with. The profile that
decides and phrases the block lives in the companion
(`agentic-mbse: src/agentic_mbse/sysml/executable_profile.py:535-537`, per research Code
References); codegen renders what it is handed.

Neither defect changes what the product admits. Chains stay blocked; equalities stay untoleranced.
A modeler who writes the *supported* form today is stopped by a bug (A), and a modeler who writes an
unsupported form is stopped without being told what to change (B).

## Success Criteria

- [x] An asserted predicate containing a compatible unit-annotated literal elaborates without
      `SI_OCCURRENCE_MISSING`. Incompatible- and unknown-unit behavior remains governed by the
      profile (`block_incompatible_dimensions`, `block_unknown_exact_unit`,
      `block_unit_conversion_required`) — unchanged in both directions.
- [x] That predicate's **end state is a working gate**, pinned positively and not as the absence of
      one error code: an otherwise-supported asserted predicate carrying a unit-annotated literal
      is admitted by the profile, gets a catalog carrier with an assessed (not blocked, not
      non-reaching) disposition, and counts toward feasibility coverage — the landed Item 2 and
      Item 3 contract applied to the cured shape. The demonstration predicate is an inequality; it
      is not `== <literal> [unit]`.
- [x] The published promise Defect B discharges is true after this item:
      `docs/architecture/modeling-assumptions.md:535` — "If the profile BLOCKs an asserted
      constraint, the generation error names the exact construct to fix." It is false today for the
      chain block. If the fix leaves any block reason still unable to keep it, that reason is named
      in the item's record rather than left implied.
- [x] A blocked feature chain names the exact offending written reference, as authored, and states
      the supported rewrite (bind the chain to a formal in the usage; use the formal in the
      predicate body).
- [x] A predicate carrying more than one blocked chain identifies each **distinct** offending
      reference, deterministically — same model, same message, every run and every order.
- [x] Kept failing characterizations for both defects are committed **before** the fixes
      (the epic's de-risking posture), and each is demonstrated red first.
      *(Audit residual F1: one row's assertion was rewritten, not merely unmarked, between red
      and green — disclosed in `plan.md` Phase 2, missing from `verification.md`'s list.)*
- [x] Existing quantity, occurrence, profile, and diagnostic tests do not regress — in particular
      `tests/conformance/test_unit_annotation_values.py` (the two already-cured lanes) and
      `tests/conformance/test_elaboration_payload_identity.py:236-266` (the blocked-guard diagnostic
      shape, which asserts on the rendered detail string and may need a *stated* update rather than
      a silent one).
- [x] Focused companion/codegen tests, full maintained suites, `ruff check src` = 12,
      `mypy src` = 55 (zero-new), and `git diff --check` pass, with exact counts recorded.
      *(Verified independently by the audit's orchestrator addendum, 2026-08-13: R1 — 2010
      passed / 34 skipped / 0 failed, zero license skips; R2 — ruff 12, mypy 55; R3 — the
      companion baseline the spec never stated, established at `bc69f04` directly: ruff 1,
      mypy 108, and the 10 failing node IDs byte-identical to tip. Counts in
      `verification.md`.)*

## Known Requirements

### Defect A — unit-annotated literals in predicates

- **[INHERITED: rulings-20260812.md Q8]** The `[m]`-literal elaboration failure is fixed in this
  item, not deferred.
- **[HARD]** A unit annotation contributes its value and never a reference. This rule already
  exists, has one owner (`extraction/unit_annotation.py`), and applies to both spellings. The cure
  extends its reach; it does not introduce a second rule or a second special case.
- **[INFERRED]** The reproduction shape is an **inline** (bare-bodied) asserted constraint usage,
  because only `source_form in ("inline", "requirement_constraint")` pushes the usage's
  `result_expression` into the reference walk (`elaborate.py:1112-1117`). A definition-typed
  predicate carrying `[m]` does not enter this walk; its unit handling is the profile's and the
  predicate-IR compiler's. The characterization must state which shape it pins and must not claim
  coverage of a lane it does not exercise.
- **[HARD]** The predicate's carried unit semantics survive the fix. The unit text reaches the
  profile and the predicate IR through the companion's expression IR (`UnitAnnotationNode`,
  read by `extraction/modeled_defaults.py:54` and the predicate compiler). Suppressing the unit as
  a *data reference* must not suppress it as a *unit*: the profile's dimension and conversion
  decisions must be reachable from the same predicate after the fix. A cure that strips units to
  silence the walk fails this spec.
- **[INFERRED]** The cure is verified from both ends, as the prior lanes were: the annotated
  predicate elaborates, and no `SI::` library element appears anywhere as a graph dependency
  (`test_unit_annotation_values.py:53-60` is the existing pattern to follow).

### Defect B — the blocked-chain diagnostic

- **[INHERITED: rulings-20260812.md Q8]** The tautological chain-block diagnostic is fixed in this
  item; it must name the offending reference and state the bindings rewrite.
- **[NEED]** (epic Item 4 scope 3–4) The diagnostic carries the blocked chain's **written
  reference** and its **location**, and states the supported rewrite in words a modeler can act on.
  Codegen already carries the same notion for readiness findings
  (`SourceReferenceEvidence.written_text`, rendered at `elaborate.py:1879-1882`) — the diagnostic
  should read as legibly as that one, not as a code repeated.
- **[INFERRED]** Determinism is a property of the *set and order* of identified references, not of
  the string alone: for a multi-chain predicate the identified references must be distinct
  (duplicates for one reference collapse) and ordered by a source-derived key, so two runs over one
  model produce byte-identical text. `_record_readiness`'s `(formal, code)` de-duplication key
  (`elaborate.py:1867-1870`) is the existing precedent for collapsing repeats.
- **[INHERITED: constraint-semantics-contract/spec.md]** The landed Item 2 disposition/severity
  contract is unchanged by this item. A blocked chain in a **plain** constraint still generates and
  catalogs unassessed; in an **asserted** one it still halts (BLOCK). This item changes only what
  the message *says*, never who it stops.
- **[INFERRED]** The message is produced where the block is decided — the companion's executable
  profile — so this defect's fix is expected to be a **paired** companion + codegen change
  (companion enriches the diagnostic payload; codegen renders and de-duplicates it). Which side
  carries which half is design's call; the spec requires only that the modeler-visible text at the
  codegen route satisfies the criteria above.

### Cross-cutting

- **[HARD]** Both defects must have kept, initially-red characterizations landed before their
  fixes (epic de-risking posture, and Item 4 scope item 1).
- **[HARD]** Test interpreter is `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, not
  `uv run` — uv resolves the companion to the wrong checkout.
- **[HARD]** Licensed runs need `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. A green
  run carrying license-skip lines is not a full run and may not be reported as one. Both defects'
  characterizations are license-gated (they load real models), so this is not optional here.
- **[HARD]** Lint baselines are `ruff check src` = 12 and `mypy src` = 55; the gate is zero-new.
- **[HARD]** TEAx is untouched by this item and its checkout stays on `constraint-semantics-item3`.
- **[HARD]** `catf_mfe_model` and `catf_mfe_d5` keep their constraint syntax unchanged
  (`catf_mfe_d5` is byte-reversal-pinned to the ratified corpus row, `test_d5_variants.py:29`). New
  characterizations use new fixtures.

## Non-Goals

- **Admitting feature chains inside predicate bodies.** Q4 is bindings-only now; chain support is
  filed as a future capability. Defect B's fix is a *diagnostic* fix — the block stays a block.
- **First-class tolerance semantics for `==`, or any expansion of the executable profile.** The
  admitted set is unchanged by this item in both directions: nothing newly admitted, nothing newly
  blocked.
- **Migrating the frozen CATF twins**, or authoring any part of Item 5's all-65 disposition table.
- **Changing BLOCK-halts-generation semantics**, or any part of the landed Item 2 disposition and
  severity contract.
- **Unit conversion or constant folding** (DD-R25) — carrying a unit is not applying one.

## Open Questions / Deferred to design

- **A neighboring lane found during this investigation, scope not owner-ruled.** A unit-annotated
  literal *binding* — `in tol = 0.05 [m];` on a constraint usage — is not a literal node, so
  `_binding_evidence` (`elaborate.py:1839-1846`) classifies it `EXPRESSION_SOURCE` and it is refused
  as `SI_EXPRESSION_SOURCE_UNSUPPORTED` rather than accepted as the value `0.05`. This is the same
  category error as Defect A in a fourth lane, and it sits directly on the blessed authoring recipe
  (bindings-only, tolerance bands) that Item 5 will write 65 times. It is **not** in the reproduced
  Q8 set. Recommendation: characterize it in this item (a kept test either way, red or green), and
  cure it only if the cure is the same rule reaching one more lane; otherwise file it. Design should
  price both and say which. Weighing it up (product-lens item4-F2): Defect B's new message will
  *advertise* the bindings rewrite, and a tolerance band's binding is exactly `in tol = 0.05 [m]`,
  so a diagnostic that sends a modeler into a lane that still refuses is a worse outcome than the
  tautology it replaces. If the lane is not cured here, the advertised rewrite must be phrased so it
  does not point at a refused form.
- Where the written-reference text for a blocked chain is captured — companion profile payload vs
  codegen re-derivation from the usage's AST — and therefore how much of Defect B's fix is a
  companion change.
- Whether the multi-chain identification is one diagnostic per distinct reference or one diagnostic
  listing them; either can satisfy the criteria, and the choice interacts with the existing detail
  string that `test_elaboration_payload_identity.py:243` matches on.
- Whether Defect A's cure lands in the reference walk itself (every lane it walks, at once) or only
  on the predicate entry — the narrower fix is smaller, the broader one is the rule's actual scope.

## Surfaced (not resolved here)

**The companion worktree was unreadable from this session.** Every read, list, and grep against
`/home/reid/1cfe/agentic-mbse-item7-rebuild` was refused by the working-directory restriction, so
Defect B's companion-side code was characterized from the research record's Code References
(`executable_profile.py:535-537, 305-308`) and from what codegen consumes, not from the source. The
companion-side statements above are therefore weaker evidence than the codegen-side ones, which were
read directly. Design and implement stages need working access to that checkout before committing to
where Defect B's fix lands.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` — Item 4 (scope authority)
- **Required Reading:**
  - `.project/active/constraint-semantics-contract/spec.md` — Migration, fixtures, and defects;
    Non-Goals (behavioral authority for this item)
  - `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §6 and Code References
  - `.project/active/constraint-semantics-contract/rulings-20260812.md` — Q4 and Q8
- **Boundary authority:** **[AGENT] (ratified by owner, 2026-08-12)**. Nothing in this item is
  owner-originated-settled beyond the Q8 must-fix disposition.
- **Landed context:** Items 1–3 at codegen `546ac20` / companion `bc69f04`; Item 2's catalog
  carrier and severity-follows-cause contract is a constraint on this item, not a target of it.
- **Product lens:** `.project/active/constraint-predicate-hardening/product-lens.md`
- **Design:** `.project/active/constraint-predicate-hardening/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
