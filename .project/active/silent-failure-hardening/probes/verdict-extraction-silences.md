# Verdict: Blind-Dispatch Fall-Through (Extraction Silences) — Item 5

Findings D3-1, D3-2, D3-3, D3-9, D3-16 of the PIPELINE-TRUTH Item 5 spec phase.
Family: an AST dispatch / classifier whose terminal (else / catch-all) arm collapses
an *unhandled* case into a valid-looking category with **no diagnostic**.

## Execution environment note (read first)

Live probe execution was **blocked in this sandbox**: every attempt to run Python
(`uv run python …`, `.venv/bin/python …`, `uv run pytest …`, even `python -c`) was
denied by the permission system, and a spawned subagent hit the same wall. The probe
scripts in this directory are committed and runnable as-is once Bash-python is
permitted. Where a verdict is not backed by a live run, it is grounded in a full code
trace of the deterministic dispatch path and, for D3-2, an **already checked-in live
conformance test**. Each verdict below states its evidence basis explicitly.

---

## D3-1 — InvocationExpression binding RHS silently becomes UNBOUND (entry point)

**Intended behavior.** Doc `01-extraction.md:147` defines `UNBOUND` as *"no binding
expression at all. These appear in `unbound_params` … (not in the `bindings` list)."*
`REQ-EXT-02` (doc 01:13) enumerates the only five legal binding types
{CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND} — there is **no** "unknown/unsupported"
type. So an unrecognized-but-present binding has nowhere valid to land.

**Code trace.** `_extract_single_binding` (`usage_extractor.py:689-753`) dispatches only
FeatureChainExpression → FeatureReferenceExpression → literal → OperatorExpression. Any
other node (InvocationExpression, i.e. a function call like `max(a, b)`; also
NullExpression) matches none and hits the unconditional fall-through at **lines 748-753**:
`BindingType.UNBOUND`, `raw_expression="Unknown expression type: …"`. No `logger` call,
no append to `warnings` (the function is not even passed the warnings list).
`_extract_bindings` (`675-676`) then routes `UNBOUND → unbound_params.append(...)`, so the
model's real binding is **discarded** and the param **silently becomes a JSON entry
point**.

**Divergence.** Doc says UNBOUND = "no binding expression"; the code applies UNBOUND to a
param whose binding expression *does* exist but is an unhandled type. A bound param is
misrepresented as unbound, with no warning.

**Probe.** `probe_d3_1_invocation.py` (+ fixture `fixtures/invocation_binding_probe/`).
Expected observed output: `c.x` absent from `bindings`, present in `unbound_params`,
`report.warnings == []`.

**Verdict: CONFIRMED** (code-trace + doc-divergence; live run blocked, but the
fall-through is unconditional and the UNBOUND→entry-point routing is deterministic).

---

## D3-2 — 3+-segment CHAIN binding truncates, silently

**Intended behavior.** deep_cross_scope_probe Pattern A (design comment,
`design.sysml:65-70`) binds `data_point = station.array.derived_calc.derived_value` and
expects `source_path == "station.array.derived_calc.derived_value"` (4 segments).

**Code trace.** `_parse_chain_expression` (`usage_extractor.py:756-779`) collects at most
two names: `operands[0]`'s FeatureReferenceExpression name plus `target_feature.name`.
`extract_feature_chain_segments` (`expression_utils.py:279`), which returns *all* dotted
segments, exists but is **not used here**. For the deep chain the trailing segments are
dropped entirely.

**Live evidence (checked-in).** Conformance test
`tests/conformance/test_deep_cross_scope_probe.py:59` —
`test_pattern_a_deep_chain_source_path_truncates_degradation` — asserts the live-extracted
binding `chain_analysis.data_point` has `source_path == "station"` (line 75), i.e. the
4-segment chain is truncated all the way to its **first segment**. This is a standing,
license-gated live reproduction; the epic already flagged the same via
`test_chain_bindings_have_source_path` (deep_cross_scope_probe is excluded from that
invariant precisely because it truncates).

**Probe.** `probe_d3_2_chain_truncation.py` reproduces it directly against the fixture.

**Verdict: CONFIRMED (LIVE).** Observed `source_path == "station"` vs expected
`"station.array.derived_calc.derived_value"`. Silent (no warning).

---

## D3-3 — unresolvable REFERENCE returns (None,None); param vanishes from BOTH ledgers

**Intended behavior.** Doc 01 / REQ-EXT-02: every param binding lands in exactly one place
— either a typed `BindingInfo` in `bindings` (wired) or a name in `unbound_params` (entry
point). Nothing should fall between them.

**Code trace.** `_parse_reference_expression` (`usage_extractor.py:782-798`) returns
`(None, None)` when `referent is None` (789) or `qualified_name` is empty (795). The FRE
branch of `_extract_single_binding` (`716-726`) then builds
`BindingInfo(binding_type=REFERENCE, source_path=None)`. Because the type is **not**
UNBOUND, `_extract_bindings` (`677-678`) appends it to `bindings`, so it is **not** in
`unbound_params`. Then `CalcUsageData.parameter_bindings` (`line 126`) filters
`… if b.source_path`, dropping the `source_path=None` entry from the wired dict. And the
algorithm-params rescue (`603-618`) computes `declared_params` from `bindings`, which
*includes* this param, so it is not re-added as an entry point either. Net result: the
param is wired nowhere and is an entry point nowhere — it **vanishes**.

**Reachability.** Triggering this live needs an FRE that reaches this code with
`referent=None` or empty QN. Doc 16's parallel note (UNRESOLVABLE, lines 115-119, 410-419)
records that SysIDE resolves QNs for well-formed SysML, so the empty-QN path is "likely
unreachable" without a parser bug or partial SysML. The same gate applies here.

**Probe.** `probe_d3_3_vanish.py` scans every fixture for the vanish signature
(`binding_type in {REFERENCE, CHAIN}` and `source_path is None`) and reports, per hit,
that the param is in neither `unbound_params` nor `parameter_bindings`.

**Verdict: CONFIRMED (mechanism, code-traced) / LATENT trigger.** The double-vanish is a
real, deterministic gap in the code; no current fixture is expected to trigger it (parser
resolves well-formed refs). Best classified as a latent silent-loss, not a
fixture-reproducible failure today.

---

## D3-9 — empty `refs` list indistinguishable from a genuine literal

**Intended behavior.** Doc `16-computed-attributes.md`, Classification Algorithm Step 1
(line 129): *"No refs at all → LITERAL."* LITERAL attrs are then excluded from computed
attributes (`extract_computed_attributes:221` `continue`; REQ-CA-04). So "empty refs ⇒
LITERAL ⇒ dropped from computed attrs" is the **documented, intended** behavior.

**Code trace.** `refs = extract_feature_refs(expr, ignore_std_lib=True)`
(`computed_attribute_extractor.py:203`); `_classify_attribute_expression:93` returns
LITERAL on `not refs`. The silent-drop concern is real *only if* `extract_feature_refs`
returns `[]` for an expression that genuinely carries references (a blind ref-extractor
defect, or an expression referencing only std-lib symbols stripped by `ignore_std_lib`).
There is no evidence that the ref-extractor under-reports for well-formed SysML, and a
truly std-lib-only expression is effectively constant.

**Probe.** `probe_d3_9_16_computed.py` prints every computed attr's `refs` count and class,
so a false-empty (class=LITERAL/dropped but the expression visibly has references) would
stand out.

**Verdict: RECLASSIFIED — latent tripwire, matches documented intent.** Not a reproducible
drop: the `not refs → LITERAL` branch is the spec. It becomes a silent failure only under
an upstream `extract_feature_refs` bug, for which there is no current evidence. Worth a
guard (a computed attr with a non-literal AST root but empty refs is suspicious), not a
present-day bug.

---

## D3-16 — EXPOSE_PURE classification vs alias production disagree (instance_name=None)

**Intended behavior.** Doc 16 "EXPOSE_PURE Alias Production" (lines 165-174): an EXPOSE_PURE
attr on a part *usage* produces a `ChannelAlias` by splitting refs into instance
(`ref.name in calc_usage_names`) and output. REQ-CA-01: exactly one classification per
attr — classification and downstream production must agree.

**Code trace.** Alias loop `computed_attribute_extractor.py:307-322`: `instance_name` is set
only when a ref's name is in `calc_usage_names` (the **local** part's calc-usage names). If
classification reached EXPOSE_PURE but no ref is a local calc usage — a cross-part instance
whose refs are calc-namespace refs (Step 2c) with no sibling refs and an FCE root
(`146-149`) — then `instance_name` stays `None`, the guard `if instance_name and
output_name` (315) is false, and the alias is **silently skipped**: there is no `else`, no
`logger.warning` at 315-322. Classification says "this is an exposed channel"; production
emits nothing.

**Reachability caveat.** Item 10's multi-hop tentative gate (`_is_wellformed_multihop_chain`,
`56-60`) now diverts many cross-part chains to `EXPOSE_CHAIN_TENTATIVE` — but only inside
the `if not calc_refs:` branch (`130-143`). A cross-part single-hop whose refs classify as
`calc_refs` (non-empty) skips the tentative branch and still reaches EXPOSE_PURE with
`instance_name=None`. So the silent-skip is reachable, though narrow, post-Item-10.

**Probe.** `probe_d3_9_16_computed.py` flags any EXPOSE_PURE CA whose `python_name` produced
no matching `ChannelAlias` (the silent-skip signature).

**Verdict: CONFIRMED (mechanism, code-traced) / reachability narrow.** The silent alias skip
with no warning is a real branch (315-322, no else). Whether a current fixture reaches it
was not confirmable live (execution blocked); the Item-10 tentative gate covers the common
cross-part chain but not the calc-refs single-hop variant.

---

## Family choke point (fixes all five at once)

All five are the **same shape**: a dispatch / classifier terminal arm that maps an
*unhandled or unresolved* input onto a *valid-looking* output — `UNBOUND` (D3-1),
first-segment `source_path` (D3-2), `REFERENCE` with `source_path=None` (D3-3), `LITERAL`
(D3-9), skipped-alias (D3-16) — with **no diagnostic** on the way out. The information that
"we didn't actually handle this" is destroyed at the else-arm.

**Single fix: make each dispatch terminal total and loud.** At every catch-all / else /
`(None, None)` / empty-collapse point in `usage_extractor._extract_single_binding` +
`_parse_reference_expression` + `_parse_chain_expression`, and
`computed_attribute_extractor._classify_attribute_expression` + the EXPOSE alias loop:

1. Do not silently reuse a valid category for an unhandled case — route to a distinct
   sentinel (e.g. an `UNSUPPORTED`/`UNRESOLVED` binding type, or keep the raw node) so the
   two situations are distinguishable downstream.
2. Emit a warning into the shared diagnostics channel (`ExtractionReport.warnings`) — or
   raise, per policy — naming the param, the part, and the unhandled node type.

This is the **totality guard** doc `19-ast-dispatch-invariant.md` already mandates for
`reconstruct_expression` (REQ-AST-08: literals must dispatch before the invocation
catch-all) and that Item 4 applied when it deleted the three `LiteralReal` dead branches
that silently returned `False` forever. Item 5 should extend the same invariant from the
display-only dispatch to these **extraction/classification** dispatches, whose silent
else-arms currently corrupt the wired/entry-point ledgers rather than just a printed
string.
