# Discovery Register: PIPELINE-TRUTH epic evidence base

**Date**: 2026-07-06
**Method**: 8 parallel read-only subagent sweeps (D1–D7 + adversarial) per
`.project/active/NEXT_EPIC_PROMPT.md`, plus orchestrator spot-verification of every
load-bearing claim. Repo at `main` = `4d616ed` (PR #3 + PR #4 merged).
**Consumers**: `.project/backlog/epic_pipeline_truth.md` items cite this register as
Required Reading. Each finding carries a disposition: **Item N** (absorbed into that
epic item), **FILED** (BACKLOG entry), or **DROPPED** (with reason).

**Verification status**: everything below is a **static-read verdict** — established
by reading code and docs, not by executing failure scenarios (exceptions: the items
listed under "Orchestrator verifications" were exercised directly). Per the epic's R4
protocol, no finding is fixed until it is (1) checked against the component's
reference doc for intended behavior and (2) reproduced by a failing test or live
probe. Items 5 and 7 produce verification tables (finding → probe → CONFIRMED /
NOT-REPRODUCED / RECLASSIFIED) and update this register in place; a struck finding
stays in the table with its reclassification evidence.

Orchestrator verifications performed directly (not agent hearsay):
- Whole-plant V11 abort reproduced license-free from the fusion-tea snapshot — exactly
  the 10 documented offenders, byte-matching the report's list.
- `report_dropped_constraints` WARN gates on non-empty list (`extractor.py:123`);
  `constraint_extractor.py:50` uses the same exact-type query its docstring (line 4)
  contradicts; `wi014_toy/toy_plant.sysml:51` carries an untested `assert constraint`.
- REQ-EXT-09 test computes `expected` with the implementation's own query
  (`tests/conformance/test_extractor.py:895-899`).
- `resolve_input` has zero production callers (grep: only two test files).
- Snapshot capture DOES run the constraint report (`capture.py:42` →
  `build_pipeline_context` → `pipeline_builder.py:685`); `generate --from-snapshot`
  does NOT (`snapshot_context.py:24`); constraint data is NEVER serialized
  (`_deserialize_constraint_info`, `loader.py:275`, has zero callers — dead code).
  This corrects BOTH the fusion-tea report (line 74) and NEXT_EPIC_PROMPT item B.

---

## D1 — Filed-but-unlanded sweep (`.project/active/*/`)

Promised in an item's artifacts but absent from BACKLOG/epic-Deferred:

| # | Finding | Source | Disposition |
|---|---------|--------|-------------|
| D1-F1 | SC-11 AST-based import rewrite claimed "filed follow-up", filed nowhere | `identifier-sanitization/close-out.md:31` | Item 8 (implement-if-small-else-file is in its scope) |
| D1-F2 | Two-sanitizer consolidation flagged, never filed | `identifier-sanitization/design.md:118,308` | Item 8 |
| D1-F3 | catf-cleanup chore (fallback EP `pumping_speed_total`) explicitly assigned a BACKLOG owner, never filed | `cross-part-wiring/plan.md:819-823` | Item 8 |
| D1-F4 | snapshot `param_groups` type-ignore annotate/rename | `snapshot-generation/audit.md:186` | Item 8 |
| D1-F5 | snapshot dead `out = subprocess.run` var + unflipped plan checkboxes, routed to "Item 12's sweep" which never captured them | `snapshot-generation/audit.md:120-123` | Item 8 |
| D1-F6 | `deep_cross_scope_probe` silent-drift note ("filed" only in plan) | `plant-prefill/plan.md:194` | Item 1 (capture it alongside new fixtures) |
| D1-F7 | WI-014 offline caplog pin "carried to Item 12's sweep", no matching filed item | `plant-fixtures/audit.md:248` | Item 4 (the wi014 assert pin supersedes it) |

Ambiguous cases A1–A4 (doc-19 deviation note, C2a/C2b agentic-mbse checks,
explainer footnote, nested-EXPOSE subsumption): all resolve to already-filed or
Item-9/Item-10 verification tasks; no separate filing needed.

## D2 — Code-marker sweep

- **DEPRECATED**: `binding_to_entry_point` dual-write maintained at 7 sites in
  `dependency_backtracker.py` (62, 80, 176, 304, 372, 404, 439). → Item 8.
- **TODO**: unit extraction from type annotations (`parameter_groups.py:255`) —
  units are metadata-only per modeling-assumptions §2; leave. → DROPPED (documented
  contract, no consumer demand).
- **xfails (5)**: `test_computed_attributes.py:787` — inherited-attr classification
  (EXPOSE_COMPUTED where FORMULA is correct; supertype-namespace QN defeats the
  Step-2b prefix check). Companion tests lock the wrong behavior in as "expected".
  → Item 7 decides: fix classifier or re-frame REQ; not silently carried.
- **Skips**: 4 `skipif` guards in `test_output_registry.py` (typed-API availability
  — all vacuous at HEAD since the API exists; they never fire) + license guard +
  24 `resolve_input`-availability skipifs in `test_input_resolver.py` (die with F4's
  resolution, Item 7) + fusion-tea-repo-dependent integration skips (legitimate).
- **Warning-promise inventory**: 30+ messages promising behavior, enumerated in the
  D2 agent output; the promises worth converting to tests are absorbed into Item 5's
  diagnostic-truth scope (each new/changed diagnostic gets a fires-on-shape test).

## D3 — Silent-failure hunt (16 real-bug-likely + pattern-3 family)

Top findings by blast radius (all verified with file:line by the agent):

| # | Finding | Site | Disposition |
|---|---------|------|-------------|
| D3-1 | Unknown binding expression type (e.g. InvocationExpression) silently classified UNBOUND → model's binding discarded, param becomes a JSON entry point | `usage_extractor.py:748-753` | FIXED (warn + loud EP; ADR-003 forecloses a 3rd disposition) |
| D3-2 | 3+-segment chain bindings truncate to root segment (`a.b.c` → `a`), no warning; `extract_feature_chain_segments` exists and is unused here | `usage_extractor.py:756-779` | FIXED (LOUD-REJECT 3+-seg chain; deep_cross re-captured) |
| D3-3 | Unresolvable reference → `(None, None)` → param vanishes from both wired and unbound ledgers | `usage_extractor.py:782-798,126` | closed-by-construction (SysIDE resolved-referent invariant + debug-guard) |
| D3-4 | Usage-extraction warning report discarded on the live path (`calc_usages, _report = ...`) — "could not resolve calc def" warnings never surface; usage dropped from pipeline silently | `pipeline_builder.py:688` | FIXED (report rendered live; INV-2 snapshot parity deferred) |
| D3-5 | Registry Phase 1a: usage with unknown calc def → bare `continue`, zero channels, no log | `output_registry_builder.py:166-168` | FIXED (Phase-1a unknown calc-def skip warns) |
| D3-6 | Snapshot loader `except (JSONDecodeError, IndexError): pass` drops `usage_type_map` entries → retype falls to base def, offline-only mis-wire | `snapshot/loader.py:424-429` | FIXED (usage_type_map malformed-key drop logged) |
| D3-7 | **RECLASSIFIED → closed-by-construction (Item 5).** The reachable silent-cross-wire shape (two FORMULA `Widget.result`) is loud-rejected by the OutputRegistry scoped-key collision guard (`core/output_registry.py:72`, raises `ValueError`) BEFORE the resolution-map merge. Any silent cross-wire needs two channel-bearing entries at one `(bare part_name, python_name)`; every such FORMULA entry registers the colliding key so the guard raises first. EXPOSE resolutions are LITERAL/no-channel. Invariant stated at `graph_builder._build_attribute_resolution_map`; guard-pinned (`test_silent_failure_family3.py::test_d37_scoped_key_collision_raises_loudly`). Bare→QN re-key deferred (optional defense-in-depth, no reachable silent failure). | `graph_builder.py:984,1102` / `output_registry.py:72` | closed-by-construction |
| D3-8 | Aggregation `transformed_expression` uses SysML-text `OPERATOR_MAP` (`^`→XOR, unknown ops pass through) instead of `PYTHON_OPERATOR_MAP`, no `has_unsupported` | `hierarchy_resolver.py:370,382` | FIXED (AGG_PYTHON_OPS `^`→`**`; enum-operator root cause) |
| D3-9 | Empty `refs` from a blind ref-extractor indistinguishable from genuine literal → attribute silently dropped as constant | `computed_attribute_extractor.py:92-94` | reclassified → tripwire (non-literal AST root + empty refs warns; classification unchanged) |
| D3-10 | Redefinition matched by leaf name first-wins across all partdefs | `graph_builder.py:1246-1250,1349` | FIXED (leaf-redef collision warns; first-wins preserved) |
| D3-11 | `_usage_by_name` first-wins ambiguous target index (D3-11b, CONFIRMED-conditional). ~~`.output` half never validated~~ (D3-11a — **NOT-REPRODUCED**: live probe shows the target lookup raises `TargetNotFoundError` on a bad output) | `dependency_backtracker.py:248,151-164` | D3-11b FIXED (user-facing ambiguous-target warn); D3-11a NOT-REPRODUCED |
| D3-12 | Default-expression eval `except Exception: return None` → param silently absent from its group | `parameter_groups.py:188-193` | FIXED (eval except narrowed; SC-5 emission-time hazard warn) |
| D3-13 | Phantom detector blindness reads as "no phantoms" (shared failure mode) | `phantom_detector.py:165-173` | reclassified → sentinel (catalog scanned/cataloged/skipped; WARN on unknown calc def) |
| D3-14 | `--smart-regen`: transient read error on a valid handwritten impl → silently regenerated to stub (DEBUG-only log) | `preservation.py:95-96`, `cli:397` | FIXED (preserve-on-transient; empty-only regenerate) |
| D3-15 | `design_prefix` from first virtual usage, first-wins; two designs in one model mis-key aggregations | `pipeline_builder.py:590-598` | FIXED (design-prefix >1 collision warn) |
| D3-16 | EXPOSE_PURE classification and alias production disagree silently (cross-part chain leaves `instance_name=None`, alias skipped, no warning) | `computed_attribute_extractor.py:305-322` | FIXED (cross-part single-hop EXPOSE_PURE else-warn + fixture) |

**Pattern-3 family** (diagnostic gated on a collection sharing the collector's failure
mode — the SC-1 silence shape): scoped-alias registration (`pipeline_builder.py:501-509`),
self-named rescue (`:564-571`), design-override rewrite key-format drift (`:177-187`),
template detection INFO gates (`usage_extractor.py:439-445`), hierarchy_resolver
getattr-default scans (whole module), `_extract_bindings`/`_is_input_parameter`
direction-string matches, empty-render success INFO (`cli:432-442`). → **FIXED/PARTIAL (Item 5):**
scoped-alias registration now carries a "scanned N, registered K" zero-found sentinel +
WARN-on-gap; design-override rewrite and self-named rescue already carried count-summaries
(pipeline_builder INFO). Remaining single-INFO sites (template detection, empty-render) are
low-value noise-discipline follow-on, not landed.

**Hygiene tail** (~20 sites: loader `.get` defaults on load-bearing fields, naive
substring `.replace()` in aggregation compile, `str(expr)` fallbacks feeding channel
names, Phase-4 silent skip where siblings warn, registry alias-rewrite no-not-found
branch, `type_map` "Any" exit-point skip, dead `_check_semantic_match`): → **FILED
(Item 5 close):** one consolidated `[D3-HYGIENE-TAIL]` BACKLOG entry (`.project/backlog/BACKLOG.md`).
Dead `_check_semantic_match` cross-referenced to Item 8's dead-code sweep, not filed twice.
**Item 6 close-out (2026-07-07):** the four-site consolidated tail resolved 3-of-4 — loader
`.get` load-bearing fields HARDENED (WARN 4 fields, RAISE `qualified_name`), aggregation
`.replace()` FIXED (word-boundary substitution), `type_map` "Any" skip HARDENED (latent-only
WARN tripwire). The Phase-4 registry alias-rewrite no-not-found branch **RECLASSIFIED**: the
corpus-scan gate found the shape already firing on 5/15 real fixtures (short-form vs.
full-EQN key mismatch), so a mechanical sibling-copy WARN would break INV-6; filed as
`[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]` (`BACKLOG.md`), tied to the same deferred gap at
`parameter_groups.py:672-682` (SC-5/D3-12 hazard-scoped-WARN note). See
`.project/active/hygiene-tail/probes/verdict.md`.

**Cross-repo pointer**: `extract_feature_refs` traversal coverage and `str(direction)`
repr stability bottom out in agentic-mbse. → Item 9 (companion audit).

### D3 verification verdicts (Item 5 spec pass, 2026-07-06)

Per R4, the 16 D3 sites were verified before design. Full table with intended-behavior
notes, file:line traces, and probes:
`.project/active/silent-failure-hardening/spec.md` (Verification Table) +
`.project/active/silent-failure-hardening/probes/verdict-*.md`. The probes ran live (a
`parents[3]→[4]` fixture-path bug was fixed, commit `a9b3540`): D3-2, D3-4, SC-4, SC-5, and
the drift attribution are **live-confirmed**; the rest are deterministic code-trace verdicts
(three probe fixtures — `d37`/`d38`/`d310` — need a calc def added before they run; that is
a design-open gate). Verdicts (of 16): **14 CONFIRMED** (D3-1/2/3/4/5/6/7/8/10/11/12/14/15/16
— several CONFIRMED-latent; D3-3 closed-by-construction; D3-11 counts via its confirmed
instance-ambiguity half, **D3-11a "`.output` never validated" struck NOT-REPRODUCED** — the
live probe shows the lookup raises `TargetNotFoundError`), **2 RECLASSIFIED** (D3-9 → tripwire
guard, matches documented `not refs → LITERAL` spec; D3-13 → zero-found sentinel). Confirmed
defects group into four families with one choke point each (blind-dispatch fall-throughs;
gated-report silences; name-keyed lookup maps; exception swallows). Scope-beyond: SC-4
sanitizer injectivity + isidentifier CONFIRMED; SC-5 non-float EP CONFIRMED;
`self_named_rescue` reference→chain drift EXPLAINED (Item-10 rescue firing, not a finding).
Per-row Disposition cells stay "Item 5" here and are discharged in full at item close.

## D4 — Exact-type enumeration audit

Ground truth: syside 0.8.4 `Model.elements()` = `nodes(kind, include_subtypes=False)`;
a subtype-aware mode EXISTS and the adapter never passes it (`syside_adapter.py:214`).
Fix surface is one adapter choke point, not N call sites. Type hierarchy read from
syside's own stubs (`syside/core/__init__.pyi`).

| Verdict | Sites | Disposition |
|---------|-------|-------------|
| CONFIRMED-BLIND | `extractor.py:108` (assert constraints invisible to drop report — the filed bug); `constraint_extractor.py:50` (docstring falsely claims assert support; `require constraint` IS visible — plain ConstraintUsage under RequirementConstraintMembership); agentic-mbse `level6_architecture.py:602` (assert constraints never get the non-executable WARN); `level4_constraints.py:113` (undercount) | Item 4 |
| CONFIRMED-BLIND (worst new) | agentic-mbse `level3_dataflow.py:48` queries abstract `Import` → matches nothing → dependency graph always `{}` → **circular-dependency validation structurally always passes** ("Documents analyzed: 0"). Secondary: even fixed, the `imported_namespace` guard skips MembershipImports | Item 4 |
| AT-RISK (live, low stakes) | `EnumerationUsage` invisible to `AttributeUsage` queries at `parameter_groups.py:102` + 4 agentic-mbse sites; enum members with defaults silently not design attributes (two fixtures carry enum defs) | Item 4 (decide + pin) |
| SAFE today / AT-RISK later | PartDefinition (misses connection/interface/view defs), CalculationDefinition/Usage (misses case/analysis types) — no supported model uses these | Item 4 records the decision table; DROPPED as code changes |

`TYPE_MAP` (22 names) contains zero subtype names; `is_instance` IS hierarchy-aware —
the per-element/model-wide asymmetry is the bug pattern. Semantics decision required at
Item 4 spec: flipping `include_subtypes=True` makes RequirementUsage (a ConstraintUsage
subtype) appear in constraint sweeps — decide whether requirement usages count as
"dropped constraints".

## D5 — Self-referential tests (1,433 examined, 25 flagged)

HIGH (structurally unable to fail):
- H1 REQ-EXT-09 (the canonical; → Item 4 re-anchors).
- H2–H4 `test_gen_json_templates.py` REQ-GEN-05 ×2 + REQ-PY-07: `len(generated) ==
  len(input)` over unconditional 1:1 production loops.
- H5 REQ-EPC-03 float conversion: test body IS the production computation
  (`graph_builder.py:506-511`).
- H6–H7 aggregation module naming/channel: expected computed by the same helpers
  production calls.

MEDIUM (M1–M10): LIBRARY_DEFAULT unparseable branch re-invokes the gating call;
PGD-05/06 tests assert production identities; AS-07 rebuilds the `module_eqn`
f-string; five factory-naming tests recompute production calls (composition
unverified); REQ-REG-02 test mis-anchored AND re-implements the selection rule.

LOW (8): circular but content pinned by a sibling literal — except
`test_localterm_sibling_agg_output` (REQ-MF-07), which can pass or **skip** but never
fail (most deceptive single finding).

Fix pattern is mechanical: every flagged test has a correctly-anchored sibling in the
same suite (literal tables); replace computed expectations with hand-transcribed
literals; convert the MF-07 skip to a failure. → Item 6 (all 25). Cleared
non-findings (BT-04, dual_resolution parity, baselines-as-regression-pins) are listed
in the agent output — do not re-flag.

## D6 — Fixture blind spots (fusion-tea models vs fixtures)

The 10 V11 offenders confirmed at `ife_plant.sysml` lines 115–167 and decompose by
value-provision mechanism:
- **(a) 5 refs**: subtype-def literal `:>>` (`hif_driver.sysml:81,83,84`) consumed
  cross-part through a usage-level retype. No fixture wires this end-to-end.
- **(b) 4 refs**: bare `part :>> name { :>> attr = literal; }` override block WITHOUT
  a retype (`hif_plant.sysml:36-49,51-65`). **Zero fixtures contain a no-retype
  `part :>>` block at all** (every fixture `part :>>` carries a type).
- **(c) 1 ref**: `driver.cost_per_joule` — spec_chain_twolevel's known shape.

`spec_chain_twolevel` covers exactly one of ten (calc-output-valued variant only);
the `ife_plant` fixture covers **none** (its lcoe binds plant-local literals).
A single fixture combining: base plant def with `part sub : AbstractBase` + calc AND
assert-constraint usages binding `sub.attr`; a plant part USAGE with both a bare
no-retype `part :>>` block and a usage-level retype whose subtype def carries literal
`:>>`s — reproduces 9 of 10. → Item 1 (the fixture recipe), Item 2 (the mechanism).

Eleven other uncovered shapes (all with fusion-tea file:line exemplars in the agent
output): attribute-def-typed attributes with nested `:>>` (`ife_cost_parameters.sysml:27`,
×14); bare `default 10.0` (no `:=`); def-typed assert constraint with cross-part +
self-named + unbound-defaulted bindings (`ife_plant.sysml:155-169`); quoted enum defs +
usage-level quoted enum `:>>` (`hif_plant.sysml:62`); selective import of quoted names;
doc bodies inside calc usages / on `:>>` redefinitions; in-binding referencing an
inherited attr the same def redefines below it (`hif_driver.sysml:74` vs `:81`); consumer
calc in a part-usage body reaching a subtype-only calc-derived attribute through a
usage-level retyped child (`hif_plant.sysml:200`); 5-deep specialization chain with
abstract ends; constraint def consuming a defaulted param; standalone package-level
instance whose `:>>` literals feed a def-owned calc's bindings. → Item 1 absorbs the
high-value subset; remainder FILED as the fixture-gap register (pointer to this doc).

Reverse diff (fixture shapes fusion-tea doesn't use): return styles, arrays/sum,
expression bindings, deep `::` bindings, units, `default :=` — healthy surplus, no action.

## D7 — Matrix truth (all 248 rows traceability-checked, ~35 deep-read)

- **F4 CONFIRMED + EXTENDED**: entire `input_resolver.py` module is dead production
  code; the whole IR family (7 PASS rows) pins it; REQ-DRA-02/04/05 partially do
  (DRA-04 compares live vs never-runs). Correction: REQ-RES-02 is UNTESTED, not PASS —
  its fraud is doc-text. → Item 7.
- **F2 CONFIRMED + refinements**: Key_A registered Phase 1a
  (`output_registry_builder.py:174-176`), Key_F Phase 1c (`:229-231`); REQ-OR-05/08
  text false with an inline NOTE admitting it; `test_output_registry.py:410` docstring
  wrong about its own body; **REQ-ORCH-04's assertion was weakened**
  (`min(phase1) < min(alias)`) to accommodate the divergence. → Item 7.
- **Divergent-PASS rows**: REQ-CA-05 (vacuous on empty coverage), REQ-PY-01/03/05
  (blacklist/rebuilt-map weaknesses), REQ-GEN-02 (CalcUsage-only, in-memory, no
  filesystem check), REQ-SR-07 (source-text grep, no behavior), REQ-DM-06/07
  (test something categorically different), REQ-GA-07 (identifier grep), REQ-PGD-08
  (cited file doesn't cover the claim), REQ-EXT-09 (part-usage owner leg missing).
  → Item 7.
- **7 PASS rows with no test marker** (BASE-05, BT-11, CA-10, LVP-09, OR-09, PGD-08,
  VBR-11) — coverage exists on inspection for all but PGD-08; nothing binds row to
  test. → Item 7 (add markers).
- **UNTESTED-12 triage**: REQ-CA-08 and REQ-GEN-07 risky-cheap (convert); REQ-RES-08
  riskiest (cross-cutting scoping claim over the historical bug locus; needs Item 1's
  fixtures); RES-01..06 discharge by cross-citing; REQ-RES-02 must be rewritten (names
  the dead path); REQ-DM-08 static check; REQ-GEN-03 cross-cite. → Item 7.
- Matrix footer says "33 test files"; directory holds 45; 9 cited files live outside
  `tests/conformance/`, straining the matrix's own PASS definition. → Item 7.
- **Coverage honesty**: ~175 PASS rows not deep-read. Item 7 execution completes the
  sweep with the D7 triage heuristics.

### D7 close-out — reconciled by PIPELINE-TRUTH Item 7 (2026-07-06)

- **F4 — CONFIRMED, RECLASSIFIED.** Three kill probes fired no kill (see `matrix-truth/r4-verification-table.md`).
  Verdict LAND-with-split: the IR family + DRA-02/RES-02/08 texts reframed from "pins the live
  resolver" to "parity-validated, not-yet-wired capability"; docs 03/04/05 reframed; cutover filed
  `[ITEM7-F4-CUTOVER]`. The "REQ-RES-02 is UNTESTED not PASS" correction landed (RES-02 text now
  names the live `_resolve_aggregation_input_channel`, cross-cited in Phase 5).
- **F2 — CONFIRMED, fix-text-to-code.** The construction-time dict does NOT bypass the typed
  contract (B3). REQ-OR-05/06/08 + doc-10 corrected to the real registrations; **REQ-ORCH-04's
  weakened `min<min` replaced with a red-mutation-gated presence assertion**; both lying docstrings
  fixed. `DOCS-SCRUB-F2`/`F4` retired.
- **Divergent-PASS rows — CONFIRMED, reframed.** EXT-09 (Item 4) and PGD-08 (cited test in
  `tests/unit/`) verified DONE/honest; CA-05, PY-01/03/05, GEN-02, SR-07, DM-06/07, GA-07 reframed
  to what the cited test checks.
- **7 unmarked rows — CLOSED.** Six `# REQ-*` markers added (BASE-05, BT-11, CA-10, LVP-09, OR-09,
  VBR-11); PGD-08 routed through the divergent-row disposition.
- **UNTESTED-12 — dispositioned.** 9 discharged by cross-citation; 3 argued-UNTESTED (DM-08,
  RES-05, RES-08) filed `[ITEM7-MATRIX-TEST-GAPS]`; RES-02 rewritten.
- **Counts — reconciled.** Recount 253 = 249 PASS + 4 UNTESTED + 0 PENDING; footer "33 files"
  corrected to 57 distinct cited (41 conformance + 16 unit/integration), definition stated.
- **~175-row sweep — substantially completed, residue named.** ~167 qualifying rows deep-read; all
  findings PASS-but-pins-narrower (no correctness lies), filed `[ITEM7-MATRIX-SWEEP-RESIDUE]`; ~46
  qualifying rows named as un-deep-read residue there.
- **5 xfails — RECLASSIFIED.** One parametrized contract documented; classifier fix filed
  `[ITEM7-CLASSIFIER-FIX]`.

## Adversarial pass (fusion-tea report attack)

Substrate limits: fusion-tea models have no return (canonical), no aliases, no
aggregation, no conditionals, no units, quoted names only on defs, depth ≤ 3, all
entry literals positive Reals — interactions outside that envelope were structurally
unexercisable by their verification.

| Claim attacked | Standing gaps | Disposition |
|---|---|---|
| SC-2 FIXED | Mixed `out`+`return` form and return-in-quoted-def verified once, by hand, on a throwaway copy — no in-repo test (history: wi014 comment records a `return` form previously removed for zero outputs). `return` + aggregation/nested refs unexercised | Item 1 (Style-E + quoted-return fixture rows), Item 7 (matrix rows) |
| SC-3 FIXED | The recommended end state (instance deleted + re-anchored + anchors passing) was NEVER assembled — verification stopped at graph inspection; the report's own bridge breaks in that state (stale key, exactly-10 guard). Multi-level (3+) retype and diamond specialization unexercised through template expansion | Item 3 (assemble the end state), Item 1 (deep-chain fixture) |
| SC-4 FIXED | Quoted OUTPUT/return param names nowhere in any corpus; `sanitize_name` is many-to-one with NO injectivity guard on channel/EP keys (`'a b'`/`'a-b'` merge silently); leading-digit names emit non-identifiers (keyword guard covers 6 keywords). Quoted+FORMULA+alias largely CLOSED in-repo (`quoted_owner_formula`, `alias_agg_probe`) | Item 5 (injectivity fail-fast + isidentifier pin), Item 1 (quoted-output fixture row) |
| SC-5 FIXED | Non-float literals structurally dropped silently (`float(value_str)`, `parameter_groups.py:710-719`) — fusion-tea already has an enum-valued `:>>` one hop from an entry point; negative/const-expr defaults never value-asserted; **pre-filled values never proven consumed** (every run-C value equals a baked schema default — a JSON-ignoring executor reproduces bit-exactly); None-omission guard now vacuous (zero None-default EPs in parametrized models) | Item 5 (non-float EP diagnostic), Item 3 (perturbed-key run — cheapest closing test in the review), Item 1 (bool/string EP fixture) |
| SC-6 FIXED | "Byte-faithful" proven on the one expression with no numeric literals; scientific-notation renders normalized, unpinned; conditionals fall to the invocation catch-all (garbage render, unasserted); no positive `sum(...)` render pin | Item 6 (pins), DROPPED as bug-fix (render contract documented instead) |
| SC-9/10 FIXED | Live-vs-snapshot parity proven for the ABORT only; full-emission byte parity exists in-repo ONLY on solar_battery (none of fusion-tea's shapes) — against a documented offline mis-wire precedent that was invisible to abort-level checks. Constraints structurally absent from snapshots (serializer never writes them; deserializer dead). Report's capture-path claim factually wrong (see orchestrator verification above) | Item 3 (parity parametrized over shape-bearing fixtures), Item 4 (constraint serialization decision) |
| Anchors REPRODUCED | Bridge validates value-propagation semantics only — if P1 lands as wiring, the 10 params leave the EP groups and `run_anchors_bridged.py` breaks; fan-out collapse (one attr → 3 consumers) untouched by the bridge; feedback-edge ordering un-tripped, not tested | Item 2 (mechanism decision input), Item 3 (fan-out + perturbed-key assertions) |

---

## Findings NOT absorbed into the epic (and why)

1. **PartDefinition/CalculationDefinition subtype blindness for connection/view/case
   defs** (D4 SAFE-today rows) — no supported model can produce them; Item 4 records
   the decision table so the day one appears the query choice is deliberate. Code
   change dropped.
2. **Units extraction TODO** (`parameter_groups.py:255`) — modeling-assumptions §2
   documents units as metadata-only; no consumer demand. Dropped.
3. **D3 hygiene tail** (~20 benign-leaning sites) — triaged at Item 5 spec; the
   residue gets one consolidated BACKLOG entry at item close. Deferred by triage, not
   silently.
4. **SC-6 scientific-notation/source-text fidelity** — cosmetic; the normalized-float
   render becomes the *documented* contract with a pin (Item 6) instead of a
   source-text-preservation feature. Dropped as a feature.
5. **Inherited-attr classifier fix (5 xfails)** — carried as an explicit Item 7
   decision (fix vs re-frame), not pre-committed: the misclassification produces
   EXPOSE_COMPUTED *rejections* (loud), not silent wrong output, and no fusion-tea
   model hits it.
6. **Supertype-chain template inheritance for plain usages, EXPOSE_COMPUTED, function
   calls/conditionals, non-uniform arrays, body-assignment capture, hierarchical
   output** — remain deferred (see epic Deferred section for the argument each way).
7. **~175 matrix PASS rows not deep-read in discovery** — Item 7's execution completes
   the sweep; discovery established the triage heuristics and the divergence rate.
8. **agentic-mbse `extract_feature_refs` traversal / `str(direction)` repr stability
   audit** — cross-repo; Item 9 carries it as a companion-audit task.

Full agent outputs (with every file:line) are preserved in the session transcript;
this register is the durable summary. Where a number here disagrees with an item's
spec-time probe, the probe wins — re-verify before building on any single line number.
