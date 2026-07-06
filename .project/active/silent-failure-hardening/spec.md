# Spec: Silent-Failure Hardening — Loud Extraction & Resolution

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** pipeline-truth-epic
**Epic:** PIPELINE-TRUTH · Item 5

---

## Problem

A model shape the pipeline cannot handle should produce a diagnostic. Today, several
shapes produce a **silent drop, mis-wire, or vanished parameter** instead — the generated
package looks healthy and is wrong. Discovery (`§D3`) read 16 such sites plus a
"pattern-3" family of gated reports; those were **static-read verdicts, not confirmed
bugs**. This item's job is to make the real ones loud, at the root, without adding noise
to clean models.

The spec phase is a verification pass first (epic R4). Each floor finding is checked
against its component's reference doc for intended behavior, then reproduced or refuted
against real code. The verification table below is the record. It confirms **14 of 16**
as real defects (several are code-airtight but not yet reachable by any supported model —
a family fix closes them for free), and reclassifies **2** as latent tripwires (a guard or
sentinel, not a diagnostic). D3-11 splits: its instance-ambiguity half is confirmed, its
"`.output` never validated" half is refuted by the live probe (the lookup raises
`TargetNotFoundError` — validation already exists). Two adversarial scope-beyond findings
(sanitizer injectivity, non-float entry points) also confirm; one drift observation
resolves as benign.

The confirmed defects cluster into four families with one choke point each. Design fixes
them per family, not site by site — that is the anti-whack-a-mole contract (R4 step 3).

**Evidence basis (what ran live).** After this spec was first drafted the probes ran live
(a `parents[3]→[4]` fixture-path bug was fixed, commit `a9b3540`). The evidence now stands
in three tiers:

1. **Ran live and confirmed:** D3-2 (committed conformance test), D3-4, SC-5, SC-4 (A1+A2),
   and the self-named drift attribution. D3-11's output-half ran live and was **refuted**.
2. **Code-trace-only, and the trace suffices:** the remaining findings are deterministic
   terminal-arm dispatch bugs — the code path is fully fixed by the AST node type or the
   map contents, with no runtime nondeterminism — so an exact trace is airtight. Three of
   their probe fixtures (`d37`/`d38`/`d310`) carry **no calc def**, so
   `build_pipeline_context` raises before the probe reaches its finding; those probes are
   not runnable until a calc def is added at design-open (see Open Questions). D3-1's probe
   also did not run despite its fixture carrying a calc def — design confirms what it needs.
3. **Refuted live:** D3-11's "`.output` half never validated" — dropped (see the D3-11 row).

## Success Criteria

- [ ] **Verification table complete** (this document): every D3 floor finding CONFIRMED
  (with its probe/trace) or RECLASSIFIED (with evidence). The register's verdict is
  recorded in its verdict block **this pass** (done — see the register's "D3 verification
  verdicts" block); the per-row Disposition cells stay "Item 5" until they are discharged
  (fixed / reclassified / split-filed / hygiene-filed) **at item close** — the one register
  timing, not two.
- [ ] Each CONFIRMED finding's **family has one root-cause fix** at its choke point, and a
  test where the bad shape produces its diagnostic (expectation independently anchored,
  never computed by the code under test — R1 addition) **plus** a silent-on-clean test.
- [ ] **`sanitize_name` is injective at channel/EP key construction and always yields a
  legal Python identifier** — the SC-4 A1 collision fail-fast and the A2 leading-digit/
  keyword/empty unit pin both land and would catch a regression.
- [ ] **A non-float entry-point literal (bool/string/enum) surfaces a diagnostic or a typed
  pre-fill, never a silent `None`-omission** (SC-5) — pinned on `plant_value_shapes`.
- [ ] **Clean fixtures still generate with zero WARNINGs** — the Item-7-of-prior-epic
  property holds; repetitive diagnostics use the count-summary style.
- [ ] **All existing baselines byte-identical**, with two named exceptions:
  - The aggregation-operator fix (D3-8) changes transformed-expression output *only* for a
    `^`-bearing aggregation, of which the corpus has none — so still byte-identical on the
    committed corpus.
  - The D3-2 loud-reject fix emits a new warning on `deep_cross_scope_probe` (a committed
    fixture whose Pattern-A pin currently asserts observed-degraded truncation). That pin
    deliberately flips to a fires-on-shape diagnostic pin; the snapshot may need one
    re-capture (`--fixtures` scoped to it, reviewed diff). No other fixture's generated
    output moves.
- [ ] Touched components' reference docs updated in the same change (R4 step 4).

## Verification Table (required spec artifact — R4)

Verdict key: **CONFIRMED** = real defect, warrants a family fix + fires-on-shape test.
**CONFIRMED-latent** = defect is real and code-airtight but no currently-valid supported
model trips it. Two sub-cases (decided per finding, MF6 criterion): if a real model shape
*can* reach it, the family fix lands with an authored synthetic trip fixture + fires-on-
shape test; if the branch is genuinely **closed-by-construction** (an upstream guarantee
makes it dead), the spec states the invariant that closes it and the fix adds a
comment-level assertion / debug-guard — **not** a fake fires-on-shape test.
**NOT-REPRODUCED** = the claimed defect does not hold against the code; struck.
**RECLASSIFIED** = not a bug as the register stated; becomes a guard/sentinel, not a
diagnostic-on-shape. Evidence basis: **live** = ran live (probe or committed conformance
test), **trace** = deterministic code trace (probe not yet runnable), **git** = committed
git artifacts.

| # | Finding (site) | Intended behavior (doc) | Verdict | Evidence / probe |
|---|---|---|---|---|
| D3-1 | Unknown binding-expr type (InvocationExpression) → silent `UNBOUND`, param becomes JSON entry point. `usage_extractor.py:748-753` | `01-extraction.md:147`: `UNBOUND` = *"no binding expression at all."* REQ-EXT-02: only 5 legal binding types — no "unknown" bucket. | **CONFIRMED** (trace) | Unconditional fall-through at 748; `_extract_bindings:675-676` routes UNBOUND→`unbound_params`; function isn't even passed a warnings list. `probe_d3_1_invocation.py` + authored fixture. |
| D3-2 | 3+-segment CHAIN binding truncates to first segment, silently. `usage_extractor.py:756-779` | Chain source_path should carry all segments (`10-output-registry.md` FCE row: dotted local path). | **CONFIRMED (live)** | `_parse_chain_expression` grabs ≤2 names; `extract_feature_chain_segments` exists, unused. Committed test `test_deep_cross_scope_probe.py:59-75` asserts `station.array.derived_calc.derived_value` → `source_path=="station"`. |
| D3-3 | Unresolvable REFERENCE → `(None,None)` → `REFERENCE` with `source_path=None` → filtered from BOTH ledgers, param vanishes. `usage_extractor.py:782-798,126` | REQ-EXT-02: every param lands in `bindings` xor `unbound_params`; nothing falls between. | **CONFIRMED-latent — closed-by-construction** (trace) | Double-vanish is deterministic (126 filters `source_path=None`; algo-param rescue at 603-618 sees it in `bindings`). **Invariant that closes it:** SysIDE guarantees a resolved `referent` with a non-empty `qualified_name` for any `FeatureReferenceExpression` in successfully-parsed SysML (doc 16:115-119), so `(None,None)` is unreachable without a parser bug/partial SysML. Fix = the family totality sentinel + a debug-guard/assert at the `(None,None)` return; **no fires-on-shape test** (no reachable shape to feed). `probe_d3_3_vanish.py` scans for the signature (finds none). |
| D3-4 | Usage-extraction warning report discarded on live path (`calc_usages, _report = …`); "could not resolve calc def"/"usage dropped" never surface. `pipeline_builder.py:689` | The report exists to surface dropped usages; discarding it defeats its purpose. | **CONFIRMED** (live) | `_report` bound and thrown away at 689; `probe_d3_4_discarded_report.py` ran live and showed the report suppressed. Headline gated-report silence. |
| D3-5 | Registry Phase 1a: usage with unknown calc def → bare `continue`, zero channels, no log. `output_registry_builder.py:167-168` | `10-output-registry.md` Phase 1a: every CalcUsage registers its channels; a skip is a real gap. | **CONFIRMED** (trace) | `if not calc_def: continue` — no logger call. |
| D3-6 | Snapshot loader `except (JSONDecodeError, IndexError): pass` drops `usage_type_map` entries → retype falls to base def, offline-only mis-wire. `snapshot/loader.py:423-424` | `27-snapshot-generation.md`: offline path must reproduce live wiring (INV parity). | **CONFIRMED-latent** (trace) | `except … : pass` at 423-424. Live path correct; from-snapshot diverges silently on a malformed key. Trip needs a corrupt/omitted snapshot entry (offline-parity guard). |
| D3-7 | Attribute-resolution map keyed by bare `owning_part_name`; same-named parts in different packages merge buckets → silent cross-wire passing Step-8. `graph_builder.py:984,1102` | `07-graph-assembly.md`/`15-naming-conventions.md`: two distinct PartDefs must not share a resolution namespace. | **CONFIRMED-latent** (trace) | Bare-name key at 984 (write) and 1102 (`resolution_map.get(ca.owning_part_name,…)`). Needs two same-named parts (authored `d37_partname_merge` fixture). `d37_partname_merge.py`. |
| D3-8 | Aggregation walker uses `OPERATOR_MAP` (`^`→` ^ ` = Python XOR; unknown ops pass through) not the power-emitting map; no `has_unsupported`. `hierarchy_resolver.py:370,382` | `13-aggregation-scoping.md`/`14-expression-compiler.md`: `^` is power → `**`; untranslatable nodes set `has_unsupported`. | **CONFIRMED-latent** (trace) | `OPERATOR_MAP["^"]==" ^ "` (`expression_utils.py:27`); fallback `f" {operator} "` at 370/382, no `has_unsupported`. No corpus aggregation uses `^`. `d38_caret_operator.py` + fixture. |
| D3-9 | Empty `refs` list == genuine literal → computed attr silently dropped as constant. `computed_attribute_extractor.py:92-94` | `16-computed-attributes.md:129`: *"No refs at all → LITERAL"* (then excluded, REQ-CA-04) — the **documented, intended** behavior. | **RECLASSIFIED** (trace) | Matches spec. Silent loss only under an upstream `extract_feature_refs` under-report — no evidence. Becomes a tripwire guard (non-literal AST root + empty refs = suspicious), not a diagnostic-on-shape. `probe_d3_9_16_computed.py`. |
| D3-10 | Redefinition matched by leaf name, first-wins, across all partdefs. `graph_builder.py:1246-1250,1349` | `07-graph-assembly.md`: a redefinition binds to its own part's attribute. | **CONFIRMED-latent** (trace) | `redef.attribute_name==attr` + leaf compare + `break` at 1246-1251. Needs two partdefs sharing a leaf name (`d310_leaf_redef` fixture). |
| D3-11a | `.output` half of a backtracker target never validated. `dependency_backtracker.py:244-254` | `11-analysis-backtracker.md`: target resolution validates the named output. | **NOT-REPRODUCED** (live) | Live `d311_usage_by_name.py`: `find_required_modules(["power_calc.THIS_OUTPUT_DOES_NOT_EXIST"])` **raises `TargetNotFoundError`** — the target lookup already validates. Struck; no fix owed. |
| D3-11b | `_usage_by_name` first-wins on colliding instance names (two `power_calc`). `dependency_backtracker.py:248,151-164` | Target resolution must be unambiguous. | **CONFIRMED-latent** (live-adjacent) | `_usage_by_name.get(instance_name)` collapses same-named usages first-wins. But the code comment at `:151-154` calls these collisions **"expected and benign"** — internal processing keys off qualified names, not this index. So design must first decide whether the *user-facing target lookup* at `:248` warrants require-unique-or-warn **at all** (it may be a non-issue). `d311_usage_by_name.py`. |
| D3-12 | Default-expr eval `except Exception: return None` → param silently absent from its group. `parameter_groups.py:192-193` | `17-parameter-group-deriver.md`: a default that can't be evaluated is a gap to surface, not to swallow. | **CONFIRMED** (trace) | `except Exception: return None` at 192-193; `None` default → param omitted downstream (see D3/SC-5 drop path). |
| D3-13 | Phantom detector blindness reads as "no phantoms" (shared failure mode). `phantom_detector.py:165-173` | `phantom_detector` should distinguish "clean" from "couldn't scan". | **RECLASSIFIED → sentinel** (trace) | `calc_def_map.get(...)` miss silently omits a usage's outputs from the catalog (165-173); broken-scan output == clean output. Not a reproducible wrong-output bug; wants a zero-found sentinel. |
| D3-14 | `--smart-regen`: transient read/parse error on a valid impl → silently regenerated to stub. `preservation.py:93-96`, `cli:397` | `23-smart-regen-preservation.md`: preservation must not lose a valid handwritten impl on a transient error. | **CONFIRMED** (trace) | `except SyntaxError: return None` / `except Exception: return None` at 93-96 (not even DEBUG-logged here) → treated as "nothing to preserve" → stub overwrite. **Split candidate** (see Open Questions). |
| D3-15 | `design_prefix` from first virtual usage, first-wins; two designs in one model mis-key aggregations. `pipeline_builder.py:590-598` | `13-aggregation-scoping.md`: aggregation keys must be scoped to their own design. | **CONFIRMED-latent** (trace) | `design_prefix = segments[0]` first-wins at 597. Needs a two-design model (`d315_two_designs`). |
| D3-16 | EXPOSE_PURE classification vs alias production disagree; cross-part chain leaves `instance_name=None`, alias skipped, no warning. `computed_attribute_extractor.py:305-322` | `16-computed-attributes.md:165-174` + REQ-CA-01: classification and production must agree. | **CONFIRMED-latent — reachable** (trace) | Alias loop 307-322: `instance_name` set only for local calc-usage refs; else guard at 315 fails silently, no `else`. Item-10 tentative gate covers most cross-part chains but **not** a calc-refs single-hop — which *is* a reachable model shape. So D3-16 **does** get a synthetic trip fixture (calc-refs single-hop cross-part EXPOSE_PURE) + fires-on-shape test, not closed-by-construction. `probe_d3_9_16_computed.py`. |

**Scope-beyond (adversarial + drift):**

| Item | Finding | Verdict | Evidence / probe |
|---|---|---|---|
| SC-4 A1 | `sanitize_name` many-to-one, no channel/EP collision guard (`'a b'`/`'a-b'` → `a_b`). `core/qualified_names.py:13` | **CONFIRMED** (live) | Pairs collapse; no fail-fast at key construction. `probe_a_sanitizer.py` ran live. |
| SC-4 A2 | `sanitize_name(x).isidentifier()` fails on leading-digit/empty (`'2nd stage'`→`2nd_stage`); keyword guard covers only 6 of `keyword.kwlist`. | **CONFIRMED** (live) | Guard appends for 6 keywords, never prepends for digits, never handles empty. |
| SC-5 | Non-float entry-point literal (bool/string/enum) dropped by `float(value_str)` → `None` → silently omitted (design-attr path, DEBUG-only) or null-defaulted. `parameter_groups.py:710-719,600-602` | **CONFIRMED** (live) | `plant_value_shapes` enum EP (`wall = 'Wall Kind'::liquid_wall`) vanishes with no diagnostic. Distinct from Item 2's `0.0`-truthiness sites. `probe_b_nonfloat_ep.py` ran live. |
| Drift | `self_named_rescue` binding_type flipped reference→chain (v1→v2 recapture). | **EXPLAINED — not a finding** (live/git) | `raw_expression` byte-identical (still `FeatureReferenceExpression`, `usage_extractor.py:724`); flip is the Item-10 mechanism-D rescue (`_rescue_self_named_bindings:567-568`) firing where the stale v1 snapshot predated it. New `chain` is correct. `probe_c_binding_drift.py`. |

**Count (of the 16 D3 findings):** **14 CONFIRMED** (D3-1,2,3,4,5,6,7,8,10,11,12,14,15,16 —
several CONFIRMED-latent; D3-11 counts once via its confirmed instance-ambiguity half, its
output-half struck NOT-REPRODUCED), **2 RECLASSIFIED** (D3-9 → tripwire guard, D3-13 → zero-
found sentinel). Scope-beyond: SC-4 + SC-5 CONFIRMED, drift explained-benign. Fewer than 16
carry a diagnostic-on-shape (two are closed-by-construction / reclassified) — the protocol
working.

## Known Requirements

Grouped by the four families (R4 step 3). Each family names its choke point; design fixes
the family there, not per site.

### Family 1 — Blind-dispatch fall-throughs (D3-1, D3-2, D3-3, D3-8, D3-16; D3-9 guard)

- **[HARD]** Every AST-dispatch / classifier terminal arm is **total and loud**: an
  unhandled or unresolved input routes to a *distinct* sentinel (not a valid-looking
  category reused) and emits a warning naming the param, part, and node type. This is the
  totality invariant `19-ast-dispatch-invariant.md` (REQ-AST-08) already mandates for
  `reconstruct_expression` — extended from the display dispatch to the extraction/
  classification dispatches whose silent else-arms corrupt the wired/entry-point ledgers.
- **[HARD]** Choke points: `_extract_single_binding` + `_parse_chain_expression` +
  `_parse_reference_expression` (`usage_extractor.py`); the aggregation walker's operator
  map (`hierarchy_resolver.py:370,382`); `_classify_attribute_expression` + the EXPOSE
  alias loop (`computed_attribute_extractor.py`).
- **[HARD]** `_extract_single_binding` distinguishes *legitimately unbound* (no
  `feature_value_expression`, line 693 — correct UNBOUND) from *unhandled binding type*
  (line 748 — warn, do not silently reuse UNBOUND). It must receive the `warnings` list
  its caller `_extract_bindings` already threads.
- **[HARD]** A 3+-segment chain binding is **hard-diagnosed (loud-reject)**, never
  truncated to root (D3-2). Orchestrator ruling: full multi-hop parse via
  `extract_feature_chain_segments` is *new capability*, which the Non-Goals defer — loud
  rejection is this item's contract. The full-parse follow-on is FILED (see Open Questions,
  `[MULTIHOP-CHAIN-PARSE]`). 2-segment paths (the V11/plain-chain path) are unchanged.
- **[NEED]** A `^` (or any op absent from the Python-emitting map) in an aggregation
  compiles to the correct Python operator or sets `has_unsupported` — never silently to
  XOR (D3-8).
- **[INFERRED]** D3-9 becomes a tripwire guard, not a diagnostic: a computed attr with a
  non-literal AST root but empty `refs` is suspicious and warns; the `not refs → LITERAL`
  spec branch stays.

### Family 2 — Gated-report silences / zero-found sentinels (D3-4, D3-5, D3-13, pattern-3)

- **[HARD]** The usage-extraction warning report is **surfaced** on the live path, not
  discarded (D3-4, `pipeline_builder.py:689`).
- **[NEED]** Registry Phase 1a skip on unknown calc def emits a warning (D3-5).
- **[NEED]** Sites whose diagnostic is gated on a collection that shares the collector's
  failure mode get a **"scanned N, matched 0" sentinel**, reusing the house style landed by
  Item 4 in `render_constraint_report` (`constraint_report.py:89-141`: always-present
  scanned/reported/excluded INFO + per-item INFO + summary WARN only when >0). Sites:
  phantom detector (D3-13); pattern-3 — scoped-alias registration
  (`pipeline_builder.py:463-510`), self-named rescue (`:516-572`), design-override rewrite
  (`:259-329`), template detection (`usage_extractor.py:439-445`), empty-render success
  (`cli:432-442`).
- **[INFERRED]** A DEBUG/INFO summary shape is acceptable for the sentinels; the
  requirement is zero-found ≠ silence, not a WARNING per site (noise discipline, RN-7).

### Family 3 — Name-keyed lookup maps (D3-7, D3-10, D3-15; D3-11b conditionally)

- **[HARD]** Resolution maps are keyed so two distinct SysML entities cannot merge. Key by
  qualified name (QN), or — where a leaf-name match is structurally required — enforce
  uniqueness and warn on collision at lookup. Sites: attribute-resolution map
  (`graph_builder.py:984,1102`), redefinition leaf match (`:1246-1250`), `design_prefix`
  first-wins (`pipeline_builder.py:597`).
- **[INFERRED]** `_usage_by_name` first-wins collision (`dependency_backtracker.py:248`,
  D3-11b) is **conditional** — the code comment at `:151-154` calls these collisions
  "expected and benign" (internal processing keys off QNs). Design decides at design-open
  whether the user-facing target lookup warrants require-unique-or-warn **at all**; it may
  be a non-issue. Not a committed `[HARD]`.
- *(Struck: the earlier requirement to add `.output`-half validation — D3-11a is
  NOT-REPRODUCED; the target lookup already raises `TargetNotFoundError` on a bad output.
  Nothing to add.)*

### Family 4 — Exception swallows (D3-6, D3-12, D3-14)

- **[HARD]** A caught exception on a load-bearing path becomes a **loud
  skip-with-warning**, not a silent `pass`/`return None`. Sites: snapshot loader
  `usage_type_map` (`loader.py:423-424`, offline-parity guard); default-expr eval
  (`parameter_groups.py:192-193`); `--smart-regen` preservation parse
  (`preservation.py:93-96`).
- **[HARD]** `--smart-regen` never overwrites a valid handwritten impl to a stub on a
  *transient* error — a read/parse failure is surfaced and the impl preserved, distinct
  from a genuinely-empty impl (D3-14).
- **[INFERRED]** D3-12 and SC-5 share the *same* downstream omission site (a `None` default
  → param dropped from its group, `parameter_groups.py`) but have **different roots** —
  D3-12 is an eval `except: return None`, SC-5 is `float()` rejecting a non-numeric. Design
  fixes both roots without double-patching or leaving a gap at the shared omission site.

### Scope-beyond diagnostics

- **[HARD]** `sanitize_name(x).isidentifier()` holds for all inputs: prepend a safe
  prefix when the result starts with a digit or is empty; broaden the keyword guard to
  `keyword.kwlist` (SC-4 A2). Landed with a unit pin over leading-digit / keyword / empty /
  all-symbol inputs.
- **[HARD]** Two sibling SysML names that sanitize to one channel/EP key **fail fast** at
  key construction, not silently merge (SC-4 A1).
- **[HARD]** A non-float entry-point literal (bool/string/enum) gets a diagnostic or a
  typed pre-fill — never a silent `None`-omission (SC-5). fusion-tea's `wall_type` enum is
  one hop from this hole; `plant_value_shapes` carries the shape.

### Cross-cutting (R1)

- **[HARD]** Every new/changed diagnostic lands with a fires-on-shape test (expectation
  independently anchored, not computed by the code under test) **and** a silent-on-clean
  test — **except closed-by-construction findings**, which get a comment-level assertion /
  debug-guard and a stated invariant instead (no shape to assert on). Per finding:
  - **Reachable → authored synthetic trip fixture + fires-on-shape test:** D3-6, D3-7,
    D3-8, D3-10, D3-15, D3-16. Several trip fixtures exist under `probes/fixtures/` and
    become permanent fixtures in design/impl (see the probe-runnability gate below).
  - **Closed-by-construction → invariant + assert/debug-guard, no fires-on-shape test:**
    D3-3 (SysIDE guarantees a resolved referent + non-empty QN for parsed SysML, so
    `(None,None)` is unreachable).
- **[HARD]** **Probe-runnability gate (design-open).** Three trip fixtures
  (`d37_partname_merge`, `d38_caret_operator`, `d310_leaf_redef`) carry **no calc def**, so
  `build_pipeline_context` raises before the probe reaches its finding — D3-7/D3-8/D3-10
  stay **code-trace-only** until a calc def is added at design-open. D3-1's probe also did
  not run despite its fixture carrying a calc def — design confirms what it still needs.
  Running these probes green is the first design/plan gate.
- **[HARD]** **Baseline corpus entrants.** Latent trip fixtures that become permanent
  corpus fixtures (D3-6/7/8/10/15/16) enter the baseline set with their diagnostic pinned;
  only D3-2 and D3-8 move an *existing* committed fixture's output (both carved out of the
  byte-identical SC above). No other current baseline changes.
- **[HARD]** Reference docs, modeling-assumptions sections, and matrix rows for every
  touched component move in the same change (R4 step 4).

## Non-Goals

- **Implementing support** for the shapes made loud — InvocationExpression execution,
  conditionals/SelectExpression, non-uniform arrays. Loud rejection is this item's
  contract; the features are deferred (epic Deferred section).
- **The two `0.0`-truthiness sites** (`graph_builder.py:425` `_classify_entry_points`,
  `graph_builder.py:1133`) and the `design_overrides` threading — Item 2 owns these; do not
  double-fix. SC-5's `float()`-rejects-non-numeric drop is distinct from `0.0`-falsiness.
- **The level6 swallow** (agentic-mbse) and the **three LiteralReal dead branches** —
  already fixed/deleted by Item 4; cited as specimens of the blind-dispatch family, not
  re-counted as work.
- **The `self_named_rescue` drift** — explained as the intended Item-10 rescue firing; no
  change owed.
- **agentic-mbse changes** (`extract_feature_refs` traversal, `str(direction)` repr) —
  recorded for Item 9, not implemented here.

## Open Questions / Deferred to design

- **`[MULTIHOP-CHAIN-PARSE]` — FILED follow-on (D3-2).** Full multi-hop chain parsing (via
  `extract_feature_chain_segments`, which already exists) is new capability, deferred by the
  orchestrator ruling in favor of loud-reject as Item 5's contract. **File it** at item
  close in the fixture-gap register / BACKLOG, argued: cheap (the helper exists), unblocks
  deep cross-scope chains, and would let `deep_cross_scope_probe`'s Pattern-A pin assert a
  *resolved* chain rather than a rejection. Not this item. The `--smart-regen` preservation swallow is a genuine
  exception-swallow-family member, but its blast radius (regen path, CLI wiring, transient
  vs permanent error distinction) may exceed the family fix. **Recommendation:** keep it in
  Family 4 — the fix is small (narrow the `except`, log at WARNING, preserve on transient
  error). Design decides; if it needs its own item, split explicitly (epic scope note),
  don't drop.
- **Name-keyed family churn (D3-7/10/15; D3-11b conditionally).** Re-keying resolution maps
  to QN may churn more than diagnostics. The epic pre-authorizes design to split these to a
  follow-on if churn is large — **decide explicitly at design**, don't silently defer. A
  cheaper interim is require-unique-or-warn at lookup (loud, no re-key), with the QN re-key
  as the durable fix. D3-11b is separate: design first decides whether its "expected and
  benign" collision (`dependency_backtracker.py:151-154`) needs any fix at all.
- **Sentinel verbosity.** Which pattern-3 sites warrant a per-run INFO sentinel vs a
  build-level count-summary — a usability call for design, bounded by "zero-found ≠ silence"
  and RN-7 noise discipline.
- **Hygiene-tail triage (recorded, not deferred silently).** The ~20 D3 hygiene-tail sites
  split: those adjacent to a confirmed family fold in for free (the Phase-4 silent-skip and
  `str(expr)`-fallback sites ride Families 2 and 1); the rest — loader `.get` defaults on
  load-bearing fields, naive substring `.replace()` in aggregation compile, `type_map`
  "Any" exit-point skip, registry alias-rewrite no-not-found branch — get **one consolidated
  BACKLOG hygiene entry** filed at item close (`[D3-HYGIENE-TAIL]`, pointer to the register
  §D3). Dead `_check_semantic_match` is Item 8's (dead-code) — cross-referenced, not filed
  twice.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 5, R1–R4, SC-D)
- **Required Reading:** `.project/research/20260706_pipeline-truth-discovery.md` §D3 +
  pattern-3 + hygiene tail; RN-7 (`.project/active/warning-reconciliation/release-notes.md`);
  `docs/architecture/reference/10-output-registry.md`;
  `docs/architecture/reference/12-virtual-binding-rewrite.md` (the epic's required-reading
  path `12-usage-extraction.md` is **stale** — no such file; usage extraction lives in
  `01-extraction.md` + `12-virtual-binding-rewrite.md`).
- **Doc-19 totality invariant:** `docs/architecture/reference/19-ast-dispatch-invariant.md`
  (the Family-1 house pattern).
- **Fixtures (Item 1 substrate):** `tests/fixtures/plant_value_shapes`, `plant_values`,
  `ife_plant`, `deep_cross_scope_probe`, `sibling_channel_ambiguity`, `self_named_rescue`.
- **Probes (committed evidence):** `.project/active/silent-failure-hardening/probes/` — four
  per-family verdict docs (`verdict-extraction-silences.md`, `verdict-report-registry.md`,
  `verdict-name-keyed.md`, `verdict-scope-beyond.md`) + scripts + authored trip fixtures.
  Several ran live (D3-2/4, SC-4/5, drift); three fixtures (`d37`/`d38`/`d310`) need a calc
  def before they run — repairing and running them all green is the first design/plan gate.
- **Memory:** `verify-then-fix-protocol`, `plant-idiom-fixtures`,
  `multihop-expose-offline-parity`, `syside-license-via-scripts-not-dashc`.
- **Design:** `.project/active/silent-failure-hardening/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` — design the four family fixes at
their choke points, decide the D3-14 and name-keyed (incl. D3-11b) split questions, repair
the three no-calc-def probe fixtures and run the full probe set green, and add the D3-16
synthetic trip fixture. See this spec-review's Resolutions block for the point-by-point
disposition.

ARTIFACT: .project/active/silent-failure-hardening/spec.md
