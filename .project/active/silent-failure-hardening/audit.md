# Audit: Item 5 — Silent-Failure Hardening (Loud Extraction & Resolution)

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commit:** dc29cb0 (Phase 6 close-out) — full item span: Phases 0–5 + `25f3a7a`, `e62c67f`, `891620a`, `41c99d6`, `dc29cb0`

---

## Summary

The four family choke-point fixes all landed and the suite is green at the claimed
numbers (2031 passed / 4 skipped / 5 xfailed; ruff 17; mypy 104). The headline
diagnostics — D3-1, D3-2, D3-8, D3-10, D3-14, D3-16, SC-4 A1/A2, SC-5 — each carry an
independently-anchored fires-on-shape test and (mostly) a silent-on-clean test, and all
three implement-time deviations are documented with rationale. INV-6 holds: clean
fixtures generate zero WARNINGs; SC-5 fires only on `plant_value_shapes`. No reference-doc
claim is factually wrong. The central doc-19 invariant doc is updated.

Three real gaps keep this from a clean PASS, none of them code-breaking:
1. **D3-5, D3-6, D3-15 have no fires-on-shape test** — fixes are landed and code-reviewed
   only. This is a direct miss against the R1 [HARD] "every CONFIRMED finding gets a
   fires-on-shape test" contract.
2. **D3-12's own shape is only DEBUG-logged, not warned** — the loud WARN covers the
   non-numeric-type (SC-5) root; a numeric-typed default that fails to eval is still
   silently omitted with a debug-log. Partial family fix.
3. **The register §D3 disposition column is 14/16 discharged** — D3-9, D3-13, the
   pattern-3 block, and the hygiene-tail block still read "Item 5", so the epic SC
   "disposition column fully discharged" is not fully met.

The deferred per-component reference-doc sweep (docs 01/10/12/13/14/16/17/23/27 + matrix
rows) is sanctioned (scoped to Items 7/10) and is NOT a fail — verified no deferred doc
now makes a false claim.

---

## Findings

### Gates (priority 8) — all match claimed

- Full suite: **2031 passed / 4 skipped / 5 xfailed** (ran live). ✓
- `ruff check src/`: **17** (≤ baseline 19; the item's stated gate, not zero). ✓
- `mypy src/`: **104** (= baseline). ✓

### Verification-table contract (priority 1)

Walked every row against the commits. Fix + anchored fires-on-shape + silent-on-clean
present for: **D3-1, D3-2, D3-4, D3-8, D3-10, D3-14, D3-16, SC-4 A1, SC-4 A2, SC-5**.
Closed-by-construction get an invariant + guard-pin, correctly no fires-on-shape:
**D3-3** (`usage_extractor.py`, SysIDE resolved-referent invariant), **D3-7**
(`test_silent_failure_family3.py::test_d37_scoped_key_collision_raises_loudly` +
invariant at `graph_builder._build_attribute_resolution_map`). Reclassified with
guard/sentinel + silent pin: **D3-9** tripwire, **D3-13** sentinel.

Anchoring verified by reading each test body — assertions use hand-transcribed literals
(warning substring, param name, constructed input), never a value computed by re-calling
the production function. Examples: D3-2 asserts the literal chain
`station.array.derived_calc.derived_value`; D3-8 asserts `" ** "` present / `" ^ "`
absent; SC-5 asserts `"SC-5/D3-12"` + `"wall"` (the fixture's enum param).

**GAP — missing fires-on-shape tests (R1 [HARD]):**
- **D3-5** (`output_registry_builder.py:167` unknown-calc-def skip warn) — no test. plan:370
  admits "Test deferred (needs full registry scaffolding); simple log-add, code-reviewed."
- **D3-6** (`snapshot/loader.py:424` malformed `usage_type_map` key logged) — no test.
  plan:388 admits "Test deferred (needs a full hierarchy-dict scaffold)."
- **D3-15** (`pipeline_builder.py` design-prefix >1 collision warn) — no test. plan:379
  admits "Test deferred (needs aggregation-scoping fixture setup)."
  The fixes are present in src and code-reviewed, but no test proves the diagnostic fires
  or stays silent on clean. Against the spec's cross-cutting R1 contract, these three are
  incomplete.

**GAP — D3-12 partial:** `parameter_groups.py` narrowed the eval `except Exception:
return None` to a specific tuple + a **debug**-log, and routed the *non-numeric-type*
hazard to the emission-time WARN (`_warn_nonfloat_entry_points`). But a numeric-typed
design default that fails to eval still returns `None` and is silently omitted with only
a DEBUG line — not the "loud skip-with-warning" the family [HARD] requires, and no
D3-12-specific fires-on-shape test exists. The register calls this row "FIXED"; it is a
partial fix for D3-12's own shape.

**Minor:** D3-11b and D3-16 lack a dedicated silent-on-clean pin (D3-16 relies on
documented corpus-inertness; D3-8 relies on byte-identity/agg conformance rather than an
explicit zero-warn count). Low risk.

**Deviations — all recorded with rationale (verified):**
- **D3-1** loud-EP disposition: ADR-003 forecloses a distinct "dropped" disposition; `x`
  stays a now-loud entry point. plan:353, plan:425 + in-code at `usage_extractor.py`. ✓
- **D3-2** truncated-chain offenders → warned EPs (deep_cross offender set collapses):
  plan:354, plan:362-363, plan:427. ✓
- **D3-14** flipped `test_req_sr_03_decision_tree_case2_unparseable`: plan:390, plan:428 +
  the test's own docstring ("Was (True, 'Could not parse'); now preserved"). ✓

### INV-6 clean-sweep (priority 2)

Ran `test_warning_reconciliation.py` (the item's reused INV-6 harness, an inclusion
list): green — `attr_expr_probe`, `sample_model`, `chain_spike_model` generate zero
WARNINGs; `solar_battery` scoped to this item's categories. The three expected-warning
trip fixtures (`deep_cross_scope_probe`, `plant_value_shapes`, the D3-8/10/16/ep-key
fixtures) are excluded **by omission** from the inclusion list — correct by construction,
though the "exactly the named set" is not positively asserted anywhere. Acceptable per
the plan's design (Phase 0 note, plan:346).

### D3-8 enum-operator fix (priority 3)

- Root cause confirmed: `operator` is a SysIDE `Operator` enum, so the old
  `OPERATOR_MAP.get(enum, f" {enum} ")` always hit the enum-stringifying fallback — the
  `^`→XOR mechanism. Fix normalizes via `str(operator)` then looks up `AGG_PYTHON_OPS =
  {**OPERATOR_MAP, "^": " ** "}` (`hierarchy_resolver.py:60,362`).
- **Byte-identity for non-^ operators:** backed by committed aggregation operator pins
  (e.g. `test_agg_literal_dispatch.py:51` pins `sum(module.cost) + 5.0`) plus the full
  green agg conformance / e2e corpus — a `str()`-normalization regression would break
  these. The corpus has no `^`-bearing aggregation, so the change is vacuous on it.
- **^ fixture pin:** `d38_caret` + `test_d38_caret_aggregation_compiles_to_power_not_xor`
  (asserts `" ** "` present, `" ^ "` absent, `has_unsupported` False). ✓

### SC-4 (priority 4)

- **A2** (`sanitize_name`): full `keyword.kwlist` guard, `n_` leading-digit prepend,
  `unnamed` empty/all-symbol fallback (`qualified_names.py`). Pins:
  `test_naming_conventions.py:195-196` (`sanitize_name("2nd stage").isidentifier()`,
  `not iskeyword(sanitize_name("class"))`, `""`/`None`/`"$$$"`→`"unnamed"`) +
  `test_qualified_names.py:29`. `'lambda'`/`'global'` are covered by the full-kwlist guard
  and `'123'` by the digit prepend, by construction. (Note: one sub-agent flagged the
  leading-digit pin as missing — that was a false alarm; the pin exists in
  `tests/conformance/test_naming_conventions.py`.) ✓
- **A1**: `extract_design_attributes` raises `ValueError("Entry-point key collision")` on
  two siblings sanitizing to one key; `test_sc4a1_sibling_key_collision_fails_fast` fires
  on `ep_key_collision_probe` (`'a b'`/`'a-b'`→`a_b`). Ran green. ✓

### SC-5 (priority 5)

Ran `test_silent_failure_sc5.py` (11 tests, green). The emission-time
`_warn_nonfloat_entry_points` fires on `plant_value_shapes`' `wall : 'Wall Kind'` enum EP
(`"SC-5/D3-12"` + `"wall"`), stays silent on `attr_expr_probe`'s chain-reference defaults,
and — via the INV-6 clean sweep, which exercises `derive_groups` through `run_codegen` —
stays silent on the whole clean corpus. The `_is_numeric_sysml_type` discriminator is unit-
pinned (Real/Integer/Power numeric; enum/string non-numeric; None/"" conservative-numeric).
✓

### Register discharge (priority 6)

- **§D3 disposition — 14/16 discharged.** FIXED / closed-by-construction on D3-1..8,
  D3-10, D3-11, D3-12, D3-14, D3-15, D3-16; D3-7 correctly reclassified CONFIRMED →
  closed-by-construction (guard already loud), guard-pinned. **GAP:** D3-9 (`:88`) still
  reads `Item 5 (tripwire)` and D3-13 (`:92`) `Item 5 (sentinel)` — neither moved to a
  discharge outcome (should be "reclassified (fixed)"). The pattern-3 block (`:102`) and
  hygiene-tail block (`:108`) still point `→ Item 5`, and the verdicts sentence (`:133`,
  "cells stay 'Item 5' … discharged at item close") is now stale. The *code and tests* for
  D3-9/D3-13/pattern-3 are all landed; only the register bookkeeping is stale. This leaves
  the epic SC "disposition column fully discharged" not fully met.
- **[D3-HYGIENE-TAIL]** (`BACKLOG.md:317`) — filed with content; all four sub-sites named;
  points to register §D3; cross-refs dead `_check_semantic_match` to Item 8. ✓
- **[MULTIHOP-CHAIN-PARSE]** (`BACKLOG.md:318`) — filed with content (D3-2 full-parse
  follow-on, argued cheap/unblocks). ✓
- **Item-9 impact list** (`BACKLOG.md:319`) — INV-1..5 review rules, `extract_feature_refs`
  under-report (D3-9), `str(direction)`/SC-5 anti-patterns. ✓

### Docs residue (priority 7)

- **doc-19** (`19-ast-dispatch-invariant.md:181-209`) — new "Totality generalized —
  Silent-Failure Hardening" section with INV-1..5 + SC-5, explicitly framed as
  new-dispatch/lookup-site code-review-checklist additions, plus the sanctioned doc-sweep
  scope note. ✓
- **Factual-wrongness check (the fail condition):** none found. `13-aggregation-scoping.md`
  makes no operator-translation claim; `14-expression-compiler.md:211` lists `^` as a
  supported operator and never claims it XORs (the compiler always mapped `^`→`**`; the
  D3-8 bug was the *aggregation* path only); `01-extraction.md:147` defines UNBOUND
  correctly and is merely silent on the now-loud unknown-type disposition (incomplete, not
  false). The per-component doc sweep deferral is sanctioned — not a fail.

### Code integrity

No slop or failure-honesty regressions introduced. Spot-checks:
- `_agg_operator_str` (`hierarchy_resolver.py:362`) is a clean, single-purpose helper;
  unknown operator sets `has_unsupported` + warns (mirrors the unknown-node arm) rather
  than silently passing through — the correct direction for this item.
- `sanitize_name` (`qualified_names.py`) reads as a total function; every branch yields a
  legal identifier; policy (the collision fail-fast) lives at the call site
  (`extract_design_attributes`), not buried in the utility.
- D3-14 preserve-vs-regenerate **policy moved to the call site**
  (`should_regenerate_stencil`), with `_extract_signature_from_impl` returning `None` on a
  narrowed transient error — the design's intent.
- The one residual honesty gap is D3-12's numeric-typed shape (DEBUG, not WARN), noted
  above.

---

## Certification

**Verified and marked:**
- Gates match claimed (2031/4/5; ruff 17; mypy 104) — ran live.
- Verification-table contract satisfied for the 11 headline findings + 4 closed/reclassified.
- INV-6 clean sweep green; SC-5 scoped to `plant_value_shapes`; SC-4 A1/A2 pinned; D3-8
  root cause + byte-identity + `^` pin.
- doc-19 updated; no factually-wrong reference-doc claim; BACKLOG filings + Item-9 impacts
  present with content.
- Three implement-time deviations documented with rationale.

**Left open (the notes — carry to a follow-on, do not silently drop):**
1. Author fires-on-shape + silent-on-clean tests for **D3-5, D3-6, D3-15** (fixes landed,
   tests deferred — R1 [HARD] not yet met for these three).
2. **D3-12:** raise the numeric-typed unparseable-default shape from DEBUG to a loud WARN
   (or state the invariant that makes it unreachable), and add its fires-on-shape test —
   the shared-omission-site gap the spec's Family-4 [INFERRED] warned against.
3. **Register §D3:** discharge the D3-9, D3-13, pattern-3, and hygiene-tail dispositions to
   their outcomes and retire the stale `:133` "cells stay Item 5" sentence, to close the
   epic SC "disposition column fully discharged."

Epic Item-5 success criteria: **Verification table complete** ✓; **each family one
root-cause fix + fires-on-shape + silent-on-clean** — met except D3-5/6/12/15 (see notes);
**baselines byte-identical (two carve-outs)** ✓; **disposition column fully discharged** —
14/16 (see note 3); **touched docs updated in same change** — central doc-19 ✓,
per-component sweep sanctioned-deferred. Recommend closing the three notes in a short
follow-on before epic-level certification.

ARTIFACT: .project/active/silent-failure-hardening/audit.md
