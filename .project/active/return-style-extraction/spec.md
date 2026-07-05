# Spec: Return-Style & Bare-Parameter Extraction (SC-2)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 3

---

## Problem

The extractor drops legal calc-def parameter styles. The member-filter in
`_extract_calculation_definition` (`extraction/extractor.py:204`, and again in
the second pass at `:242`) keeps only `AttributeUsage` members and `continue`s
past everything else. But syside represents three common, legal SysML forms as
`ReferenceUsage`, not `AttributeUsage`:

| Form | syside node | Direction | Current behavior |
|------|-------------|-----------|------------------|
| `return y : Real = expr;` | ReferenceUsage | Out | **Invisible → zero outputs** |
| `in x : Real;` (bare) | ReferenceUsage | In | **Invisible → input lost** |
| `return attribute y : Real;` + body `y = x*2;` | AttributeUsage(Out) + direction-None ReferenceUsage | Out (+ none) | Output seen, **body expression lost** |
| `out attribute y : Real = expr;` | AttributeUsage | Out | Fully handled |

Consequences, all verified in the deep-research SC-2 section:

- A calc def written with a named `return` extracts with **zero output
  attributes**. Before Item 1 this crashed deep inside the Jinja module template
  (`teax_module.py.jinja2`). Item 1 added the zero-output fail-fast (REQ-EXT-08,
  V7), so it now raises a clear error — but the calc still can't be used.
- A calc def written fully bare (`in x : Real; return y : Real = expr;`) extracts
  as an empty shell.
- The repo's own docs teach the crashing pattern. `docs/architecture/reference/01-extraction.md:27-32`
  gives a `return total_cost : Real = capacity * unit_cost;` canonical example
  that is **false as documented** — it does not extract today. The
  agentic-mbse sysml-conventions skill stencil teaches the expression-losing
  body-assignment form (register finding A-2).

This is the SC-2 finding. It is a support-vs-reject decision the epic has already
made in favor of support: the `_get_direction` logic already handles `"Return"`
(`extractor.py:296-306`), `_extract_attribute` is member-type-agnostic (the
research probe confirmed ReferenceUsages carry name/typing/expression), and every
other artifact assumes these forms work. Only the member-type filter blocks them.

The one genuinely unsupportable form is **anonymous** `return : Real = expr;` —
with no name there is nothing to build a PQN output channel from. Today it
vanishes and trips the generic zero-output error; it should get a specific,
actionable diagnostic instead.

## Success Criteria

- [ ] A calc def using named `return y : Real = expr;` extracts with `y` in
      `output_attributes` and its expression AST in `output_expression_asts`
      (so CalcUsage auto-impl works, not just a stencil).
- [ ] A calc def using bare `in x : Real;` extracts with `x` in
      `input_attributes`.
- [ ] The `return attribute y : Real;` + body-assignment form extracts `y` as a
      single output with **no double-ingestion** (the direction-None
      ReferenceUsage that carries the body assignment stays out of the attribute
      lists; `y` appears once).
- [ ] `out attribute y : Real = expr;` is unchanged (control style).
- [ ] Anonymous `return : Real = expr;` raises a specific diagnostic (new rule
      V8) that names the fix — give the result a name — rather than the generic
      zero-output message or a crash.
- [ ] A new fixture covering all four legal styles plus the anonymous negative
      case has a captured extraction snapshot and conformance tests.
- [ ] All existing extraction snapshots and the 4 pipeline baselines are
      **byte-identical** after the change (all existing fixtures are
      AttributeUsage-based — the relaxation adds no members for them).
- [ ] `docs/architecture/reference/01-extraction.md` canonical example is now
      true, and the newly legal forms + the anonymous-return diagnostic are
      documented with REQ tags and verification-matrix rows.
- [ ] The six converted IFE calc defs are confirmed to extract in their original
      `return` form (see verification procedure under Open Questions — the
      fusion-tea models are not readable from this workspace).
- [ ] agentic-mbse impact recorded: the A-2 stencil fix is specified exactly, and
      the Level-6 output-style check is recorded for Item 12.

## Known Requirements

- **[HARD]** The relaxed filter MUST accept a member if it is an `AttributeUsage`
  **or** a `ReferenceUsage that carries a direction** (In / Out / Return).
  Direction-None `ReferenceUsage` members MUST stay excluded from
  `input_attributes` and `output_attributes`. This is what prevents
  double-ingestion of the `return attribute` + body-assignment form (the
  body-assignment target is a direction-None ReferenceUsage sharing the output's
  name). *Forced by:* syside's node model and the no-double-ingestion criterion.

- **[HARD]** The relaxation MUST be applied to **both** member-iteration passes
  in `_extract_calculation_definition` — the primary pass (`:203-238`) and the
  second `member_expressions` pass (`:241-248`) — using the same
  direction-carrying predicate, so the two passes agree on which members are
  parameters. *Forced by:* the two passes must not disagree on membership (SC-2
  research risk note).

- **[HARD]** Anonymous `return` (a direction-Out/Return member with no usable
  name after `sanitize_name`) MUST raise a diagnostic naming the fix, before the
  generic REQ-EXT-08 zero-output error fires. *Forced by:* no name → no PQN
  channel; the pipeline cannot synthesize one.

- **[HARD]** Existing behavior for `out attribute` / `in attribute` members and
  for all 10 committed fixtures is unchanged: every existing extraction snapshot
  and the 4 pipeline baselines stay byte-identical. *Forced by:* R1 baseline
  discipline; verified because no committed fixture uses a direction-carrying
  ReferenceUsage member.

- **[NEED]** Named return-style calc defs auto-implement: the output expression
  on the `return y : Real = expr;` ReferenceUsage reaches `output_expression_asts`
  so the expression compiler produces a real body, not a `NotImplementedError`
  stencil. (This falls out of the filter relaxation for free — the AST-capture
  block at `:223-228` runs inside the same loop — and the new fixture must assert
  it, so it is a stated outcome, not left implicit.)

- **[INFERRED]** New requirement IDs and a new validation rule are added to keep
  docs and code in lockstep (R1): REQ-EXT-10 (direction-carrying ReferenceUsage
  members extracted), REQ-EXT-11 (anonymous-return diagnostic, V8), and a
  no-double-ingestion assertion (fold into REQ-EXT-10 or a REQ-EXT-12 — design's
  call). V8 is added to the modeling-assumptions Validation Rules table.

- **[INFERRED]** The new fixture is captured via `scripts/capture_extraction_snapshots.py`
  (registered in its `MODELS` or `EXTRACTION_ONLY_MODELS` map) and added to the
  `MODELS` list in `tests/conformance/test_extraction_snapshots.py`, following the
  established fixture pattern. Capture requires a live syside license — fine now
  (license live until 2026-08-06, R3), and this is exactly the window R3 says to
  use.

## Non-Goals

- **Multi-output `return`.** Not legal SysML — a calc def has at most one result
  parameter. Out of scope by definition.

- **Body-assignment expression capture (restores auto-impl for the
  `return attribute y : Real;` + `y = expr;` stencil form).** **Decision:
  follow-up, not in this item.** Rationale:
  1. Inline `return y : Real = expr;` already gets full auto-impl for free from
     the filter relaxation — the expression lives on the ReferenceUsage and flows
     into `output_expression_asts` through the existing AST-capture block. So the
     *modern* return style loses nothing.
  2. The only form that still loses its expression is the body-assignment form,
     which is exactly the degraded pattern the A-2 stencil fix steers modelers
     *away* from. Restoring auto-impl for a pattern we're simultaneously
     deprecating is low value.
  3. The research scopes it as M-lift (separate from the S-lift filter fix);
     folding it in would blow Item 3's 1-day budget.
  4. The six IFE calc defs use inline return form, so they auto-implement without
     it (to be confirmed by the verification procedure).
  Recorded as a follow-up backlog note (see agentic-mbse Impact). The
  body-assignment form still extracts a correct *output* (just a manual stencil),
  so nothing crashes.

- **Constraint execution, alias surfacing, type indexing, sanitization** — other
  epic items.

## Open Questions / Deferred to design

- **IFE calc-def verification procedure (fusion-tea not readable here).** The
  epic asks to confirm the six converted IFE calc defs work in original `return`
  form. `~/1cfe/fusion-tea` is outside this workspace's sandbox and cannot be
  read. Spec'd procedure for whoever has repo access (before 2026-08-06, license
  live):
  1. Locate the six IFE calc defs in their **original** `return`-style form
     (pre-workaround; fusion-tea converted them to `out attribute` to dodge SC-2).
     If only the converted forms remain, reconstruct the `return` form from the
     conversion diff.
  2. Run each through extraction on the fixed extractor; assert each yields the
     expected `input_attributes` / `output_attributes` and a non-empty
     `output_expression_asts` for the inline-return ones.
  3. Cross-check inputs/outputs/expressions against the current `out attribute`
     converted forms — they must match.
  4. Record the result (pass/fail per calc def) in the Item 3 close-out. If the
     models can't be reached in the license window, capture a small transcribed
     fixture of the same shapes and mark the IFE cross-check as carried to Item 8
     (plant fixtures) / Item 12.
  Design should decide whether this is a live-run gate on Item 3 close or a
  recorded procedure executed opportunistically.

- **Fixture capture mode: full-pipeline vs extraction-only.** The new
  four-styles fixture needs an extraction snapshot regardless. Whether it also
  runs `build_pipeline_context` (needs a design part with a calc usage binding
  the inputs, proving no downstream break) or is extraction-only (like
  `zero_output_calc`) is a design call. Recommendation: give it a design usage so
  it flows the full pipeline and proves auto-impl end-to-end; fall back to
  extraction-only if binding the bare `in` params is awkward.

- **Anonymous-return detection site and exact V8 wording.** Whether the
  diagnostic fires inside the member loop (on first sight of a nameless
  direction-Out member) or in a pre-check, and the precise message text (must
  follow the V1–V7 pattern and name the fix, e.g. *"Anonymous `return` has no
  name, so no output channel can be built. Give the result a name:
  `return result : Real = expr`."*). Left to design.

- **Second-pass `member_expressions` predicate.** The second pass currently
  captures expressions for non-input/non-output members (intermediate locals). It
  should use the same direction-carrying predicate for consistency, but note the
  body-assignment ReferenceUsage is already excluded there because its name
  matches an output (`in output_names → continue`). Design confirms the predicate
  and adds a regression assertion that the body-assignment form does not leak a
  phantom member.

---

## agentic-mbse Impact

Per R2, recorded explicitly. Two items, one done inline in Item 3, one for Item 12.

### Inline in this item — A-2 stencil fix

- **What:** The sysml-conventions skill calc-def stencil teaches the
  expression-losing body-assignment form (deep-research SC-2: `references/stencils.md`
  around lines 39-41, register finding A-2). Replace it with the inline
  return-style form that auto-implements:
  ```sysml
  calc def <Name> {
      in <param> : Real;
      return <result> : Real = <expr>;   // inline expression → auto-implemented
  }
  ```
  (or the equivalent `out attribute <result> : Real = <expr>;`). Do **not** teach
  `return attribute <result> : Real;` followed by a separate body assignment — that
  form loses its expression and degrades to a manual stencil.
- **Where:** agentic-mbse repo at `~/1cfe/agentic-mbse`, the sysml-conventions
  skill `references/stencils.md`. The implementer opens the file and confirms the
  exact line range before editing (research cites 39-41; verify against the live
  file).
- **Why inline:** the epic flags A-2 as an urgent one-liner (R2) — the skill is
  actively teaching modelers to produce the SC-2-broken form.

### Recorded for Item 12 — Level-6 output-style check

- **What:** A Level-6 conventions check for calc-def output style, updated for the
  forms Item 3 makes legal: `out attribute`, named `return` (both inline-expr and
  body-assignment), and bare `in` are all accepted; **anonymous `return`** is a
  FAIL (name the fix), and body-assignment `return attribute` + `x = expr` is a
  WARN (extracts an output but loses auto-impl until the deferred capture lands).
- **Where:** recorded here for Item 12's accumulated impact list; not implemented
  in Item 3.

### Follow-up backlog note

- **Body-assignment expression capture** (deferred above) is filed as a
  sysml-codegen backlog item: wire `member_expressions[y]` (a direction-None
  ReferenceUsage whose name matches output `y`) into `output_expression_asts[y]`
  to restore auto-impl for the body-assignment form. M-lift. Low priority once the
  A-2 stencil steers modelers to inline return.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 3; R1/R2/R3)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-2 section — authoritative)
  - `docs/architecture/modeling-assumptions.md` (§8 constraints, V7 from Item 1)
  - `docs/architecture/reference/01-extraction.md` (canonical example to reconcile)
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` (register; A-2)
- **Code:** `src/sysml_codegen/extraction/extractor.py` (both filter passes; builds on Item 1's REQ-EXT-08/09 at commit 3c42dd1)
- **Design:** `.project/active/return-style-extraction/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
