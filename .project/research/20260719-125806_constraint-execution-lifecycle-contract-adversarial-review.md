---
date: 2026-07-19T12:58:06-07:00
researcher: Claude (adversarial design review, six independent lanes)
topic: "Red-team review of the authoritative constraint-execution lifecycle contract"
tags: [research, constraints, lifecycle, architecture, adversarial-review, acceptance-matrix]
status: complete
last_updated: 2026-07-19
---

# Adversarial Review: Constraint Execution Authoritative Lifecycle Contract

**Reviewed artifacts:**
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (the contract),
`.project/active/constraint-execution-lifecycle-contract/spec.md` (the spec),
`.project/research/20260719-111228_constraint-execution-lifecycle-evidence-census.md` (census, non-normative).

**Method:** six independent reviewer lanes — (A) intent/provenance, (B) sysml-codegen
implementation, (C) agentic-mbse extraction/profile, (D) TEAx/consumer repos, (E) acceptance-matrix
counterexample construction, (F) blind lifecycle reconstruction from code with no access to the
contract, spec, census, or CURRENT_WORK. Lanes B, C, D, F verified claims against working trees and
git history, not documentation. Disagreements between lanes are preserved in §4 and §7, not
averaged. Nothing was modified: no contract, spec, production code, or test edits.

Settled owner decisions D-1, D-2, D-3 and the simplification constraint were treated as fixed.
This review assesses whether the architecture carries them faithfully; it does not reopen them.

---

## 1. Executive verdict

**Sound with required corrections — not ratifiable as written.**

The lifecycle description itself is coherent. The blind reconstruction (Lane F) independently
derived the same stage sequence, the same authorities, and most of the same defects the contract
already admits. The contract is unusually honest about its open gaps: Gate A, Gate B, occurrence
defects, evidence mutability, and the verifier bootstrap are all flagged open, and code reading
confirmed each is exactly where the contract says it is. No lane found an internal contradiction
that breaks the architecture's spine (model states meaning / package evaluates / study decides).

Three things block ratification under the owner's own bar ("proves beyond a reasonable doubt"):

1. **The acceptance matrix — the proof instrument — can go green while a real supported model
   still fails end-to-end.** Lane E constructed a small, in-family plant model that defeats the
   matrix as written (§5). Cells pin *observations* but not fixture shapes, routes, or artifact
   identity — the three degrees of freedom through which every known defect historically escaped.
   The "no later row may certify around an earlier open dependency" rule has no enforcement
   mechanism.
2. **Several requirements are written in the present tense about states that do not exist in any
   commit.** The correction register asserts calculation and constraint consumers "share QN-keyed
   positive resolution" (there are three independently drifted resolution ladders today); the
   profile-v4 semantics the contract describes as current exist only in uncommitted working trees,
   and the committed cross-repo pair is mutually unsatisfiable (§4, C-1/C-2, B-3).
3. **D-3 closure is materially under-scoped.** The embedded catalog is missing five fields TEAx
   legitimately consumes, every method currently used to reconstruct them is explicitly forbidden
   by LC-H02A, and re-binding study compatibility to real identity orphans every existing study
   store with no stated migration (§4, D-3/D-4; §7).

All of these are correctable with bounded edits (§8). None requires reopening a settled decision.

---

## 2. End-to-end reconstructed lifecycle (independent, code-derived)

Lane F reconstructed the lifecycle from code alone, forbidden from reading the contract. Its
model matches the contract's stage table in sequence and ownership. The stages, as the code
actually behaves:

1. **Fact extraction** (agentic-mbse, `constraint_extraction.py:112-171`): total sweep of
   `ConstraintUsage` subtypes in location order; six source forms; the effective predicate is
   selected *at extraction time* — downstream only verifies, never re-selects. Unrecognized
   expressions become explicit `UnsupportedNode`s. Extraction almost never raises; malformation is
   represented, not thrown. No identity minted beyond QN + file:line:col.
2. **Executable profile** (agentic-mbse, `executable_profile.py`): pure facts→decision function,
   four outcomes, default-deny, closed reason codes, self-validating `UsageDecision` lattice.
   Consumed independently by L4 (metrics only, never fails), L6 (BLOCK→ERROR, fails), and codegen.
3. **Lowering** (sysml-codegen, `constraint_lowering.py:869-1197`): re-pins profile version,
   re-runs the profile, halts on any BLOCK with a named multi-diagnostic error, warns + excludes
   NON_NUMERICAL/UNASSESSED with validated records, expands ADMIT along the owner axis, resolves
   each formal through the strict ladder that always raises at terminal miss. **This is the main
   identity-minting stage**: `constraint_id`, `evaluation_channel`, `predicate_source_key`.
4. **Demand injection + graph extension** (`pipeline_builder.py:912-934`,
   `constraint_lowering.py:1265-1439`): constraint-bound channels join backtracking roots before
   pruning; extension appends constraint modules + always-one report aggregator, mints
   modeled-default and design-attribute entry points, then re-runs channel validation and —
   today — a *whole-graph* V11 check (the Gate B defect).
5. **Catalog assembly** (`constraint_catalog.py:57-140`): per-definition source records,
   per-occurrence concrete entries, per-usage excluded records; fingerprint over canonical JSON;
   attached to the graph by plain assignment, `exclude=True` (never serialized into baselines).
6. **Generation** (`cli/__init__.py:921+`): name-safety preflight, duplicate-path and V11 checks,
   precomputed frozen plan *before* any tree mutation, compile-once per predicate source with
   byte-agreement checks, polarity applied at runtime by `_finalize_assertion`, exact-schema
   aggregator with baked `CATALOG_FINGERPRINT`.
7. **Contracts + seal** (`model_contract.py:27-77`, `seal.py:93-122`): model contract embeds the
   catalog by value and mints `semantic_fingerprint`; seal hashes every covered file into
   `executable_fingerprint`. Strictly layered — no fingerprint cycle (verified).
8. **Snapshot lane**: capture stores neutral facts + occurrence transcript; the capture-time
   profile run rewrites only *excluded* usages' locations to portable referents (admitted usages
   keep raw absolute paths); rebuild re-runs the same lowering/extension/catalog functions with
   `include_all=True`.
9. **Load + verify** (teax `package_load.py:54-95`): the loader executes the package's own
   unauthenticated `contracts/verify.py` to obtain the verifier it then trusts — circular.
10. **Evaluation** (teax `evaluator.py`): typed entry validation, execution, projection to frozen
    `ModelEvidence` — whose `report` field holds an *unfrozen* generated model. Module failure
    normalized through one shared function (always tagged `MODULE_EXECUTION`).
11. **Study** (teax `study/`): propose→validate→bridge (single-entry)→evaluate→policy→durable
    commit; `assessment_failed` is a distinct evidence-preserving case state *in code*
    (`runner.py:126-143`); compatibility binds eight opaque strings including a stand-in
    catalog-byte hash.
12. **Real consumer** (fusion-tea, private): the catalog materializer and multi-channel evaluator
    wrapper are the only implementations of the package→study join; the deployed IFE package was
    generated by the *previous* generation of the predicate runtime and catalog schema.

**The blind reconstruction's divergences from the contract are the review's findings**, not
misunderstandings — every divergence traced to a spot where the contract overclaims, under-scopes,
or omits (see §4). Load-bearing flow that exists only in the private consumer repo: the catalog
bridge, the multi-channel wrapper, the end-to-end acceptance proof, and the re-seal-after-bridge
recipe — consistent with the contract's own Appendix A "Not proven" row for the public path.

---

## 3. Claim verification table

Verdicts: **S** supported · **U** underdetermined · **C** contradicted · **NH** not implemented,
honestly labeled · **NW** not implemented but written as established. Consolidated to the
load-bearing rows; lane reports carry the full tables.

| Contract claim / invariant | Provenance | Supporting evidence | Contradicting evidence | Verdict | Consequence |
|---|---|---|---|---|---|
| Inv 7–9, 15 profile pure/total/default-deny, four outcomes | agent, ratified | `executable_profile.py:920-975`, closed `REASON_CODES`, 387 tests pass (working tree) | duplicate-QN definitions silently last-win (`:984-990`) | S (working tree) | — |
| Inv 10/12 ordering matrix + polarity (v4 semantics) as current behavior | agent, ratified | working-tree v4: `_ORDERING_NUMERICAL_PAIRS:298-306`, polarity gate `:945-946` | **every committed ref is v3**: boolean/string/enum ordering ADMITs; `is_negated` absent from committed profile entirely | **NW** | Contract's present tense is true of no commit; unfalsifiable without pinned hashes |
| Inv 14 / LC-C11 both skew directions fail closed | inherited | exact-string guard `constraint_lowering.py:898` rejects both directions | committed pair mutually unsatisfiable (codegen HEAD needs ≥0.1.1; companion HEAD is 0.1.0); the fail-closed raise never executed by any test | S mechanism / U evidence | LC-C11 presumes an identifiable candidate pair that exists in no committed form |
| Inv 13 / LC-C10 every fact field has real consumer | inherited | — | enforcing test is key-set equality on the static map — exactly what the invariant forbids; `scope` and `OperandTypeFact.enumeration` have zero consumers; `classify_equality` docstring claims a same-enumeration check the code doesn't perform | NH (Appendix A honest) | Named fields should enter the census |
| Inv 15 / LC-B08 diagnostics classified, fail closed | inferred | — | `ExtractionDiagnosticFact` has **no severity field at all** (`constraint_facts.py:171-177`); channel is write-only in both repos | NH, **under-scoped** | Closure needs a facts-schema bump (couples to Inv 14 skew), not just "a sink" |
| Inv 18 non-finite/recursive blocks loudly, no partial expansion | inherited | `[*]` raises `NonFiniteCardinalityError` (`constraint_lowering.py:404-409`) | recursive containment silently truncates (`part_instance_index.py:158-162`, R-5 live) | NH (owned, row 1) | Acceptance cell satisfiable with the `[*]` fixture while the recursive shape still truncates |
| Inv 19–20 / LC-D06-07 ONE shared positive-resolution procedure | inherited + D-2 | shared `terminal_disposition` only | **three independent ladders** (`constraint_lowering.py:139-296`; `dependency_backtracker.py:562-856`; `input_resolver.py:228-233`); backlog `[CONSTRAINT-ARCH-UNIFY]` records realized drift; Appendix B row 4 states sharing in the present tense | **NW** (register row) / NH (invariant) | The normative rule is fine; the register misstates current fact |
| Inv 21 / LC-D08 Gate A locus + same QN-keyed EP feasible | owner (D-2) | EP minting is QN-deduped (`:1301-1321`) so D-2 is feasible once resolution unifies | constraint rungs are exact-QN over three constructed shapes (`:254-286`); calc ladder additionally matches leaf-unique and ambiguous-first-pick (`dependency_backtracker.py:784-856`) | NH (owned, row 2) | Confirms Gate A as implementation defect, as D-2 says |
| Inv 22 / LC-D09 modeled defaults survive | inherited | `LIBRARY_DEFAULT` EP per formal | `_literal_float:1233-1243` accepts only bare literals — signed/unit defaults silently become `None` (R-9 live) | NH (owned, row 4) | — |
| Inv 24 / LC-E02 differential extension-time V11 | agent, ratified | — | not implemented: extension runs whole-graph V11 and raises on any offender (`:1435-1438`). **Lane B further argues the differential check is vacuous** — minted constraint EPs are never fallback EPs and module-output inputs are channel-validated, so extension cannot introduce a V11 violation; the fix may reduce to deleting the call | NH + open design question | See preserved disagreement, §4 F-15 |
| Inv 26 final V11 zero ⇒ every model-derived value has a producer | owner (D-1) + inferred | `_reconcile_params_coverage` raises pre-clear (`cli/__init__.py:244-290`) | V11 = wired ∧ fell-through ∧ valueless only (`graph_builder.py:800-845`); a defaulted fall-through and an ambiguous first-pick binding (`dependency_backtracker.py:851-856`, WARNING then guess) both pass | **C** (second sentence) | Producer-completeness is enforced only by a narrow proxy; certifying the stellarator repair against "V11 clean" would leave D-1's stronger sentence unproven |
| Inv 27 / LC-D11 executable fingerprint not an ID input (no cycle) | inherited | ID minting precedes sealing; seal hashes files containing IDs — strictly layered | anonymous *eligible* IDs digest the raw absolute `loc.file` (`:483-485`); `tracking_key` has zero writers in src/ and is absent from the catalog | S core / NW (`tracking_key`) | The correlation story the non-goals lean on does not exist |
| Inv 28 / LC-E05 catalog coverage model, gap = admitted per-usage record | inherited | per-def/per-occurrence/per-excluded records exist as described | embedded catalog also lacks `source_form` on eligible entries, usage short name, `owner_qn`-as-QN, and any def↔usage join key — all consumed by TEAx today via forbidden reconstruction | **C — under-scoped** | D-3 closure is additive schema work beyond the one named gap (§7) |
| Inv 29–31 compile-once, collision-proof, plan-before-mutate | inherited | `modules.py:105-178`, `constraint_plan.py:16-59`, clear-after-plan `cli/__init__.py:982-990` | shared-key agreement on `is_negated` taken from first entry, no cross-entry check | S (with the mixed-polarity hole) | Needs the shared-def × mixed-polarity cell (§5) |
| Inv 34 no checkout-absolute paths in fingerprints/contracts/catalogs | inherited | excluded-usage locations portable | **generated calc-module docstrings embed absolute source paths** (`modules.py:88,488`; templates); loader re-absolutizes (`loader.py:906-916`); anonymous eligible IDs digest absolute paths; portability suite compares contract/catalog/report bytes only, not the tree | **C — broader than the named open item** | The relocated-snapshot acceptance cell cannot pass on any calc-bearing model; closing "portable admitted locations" as constraint-scoped will not fix it |
| Inv 35 / LC-F02 live/snapshot equivalence; demand equivalence "judged by retained producers" | inherited | byte/parity suites for the tested manifest | no mechanism compares retained producers between routes — it is a definition, not a check; parity runs on one machine so machine-bound content cancels | S tested / U as criterion | — |
| Inv 36–37 contract layering, seal/verify one symlink policy | inherited | `model_contract.py`, `seal.py:36-57`, `verify.py:57-67` — R-10 fixed in tree | — | S | — |
| Inv 39 / LC-F09 trusted bootstrap required (current loader violates) | inferred | contract admits violation | confirmed: `package_load.py:38-51` execs package-local verifier; the seal hash of `verify.py` is checked only *by* `verify.py` — circular. Lane D: the fix composes with D-3 (verifier owns integrity, catalog owns schema — no new duplicate authority), but verifier-version skew discipline must be added | NH + missing skew rule | — |
| Inv 41 / LC-G01 evidence immutable (admitted violated) | inferred | envelope frozen (`evidence.py:45`) | `report: Any` is an unfrozen generated model; `results` list mutable; runner's pre-policy `model_dump` protects the *persisted* artifact by incidental ordering only | NH (owned, row 11) | The mutation-attempt acceptance cell is satisfiable at the frozen envelope while the real violation lives one level down |
| Inv 42–45 / LC-G02–G05 violation-vs-failure separation, F1 normalization | inherited | strong: `test_f1_arithmetic_normalization.py`, shared normalizer, cause preserved; **d545701/927a9e1 resolved**: F1 code + audit landed in `d545701`; the audit header's `927a9e1` provably lacks the change — contract's account is correct, gap row 6 accurate | phase tag hardcoded `MODULE_EXECUTION`; `OUTPUT_WRITE` never emitted; backend report contents excluded from parity comparison | S (with caveats) | — |
| Inv 46 / LC-G11 file-backed report persistence "unproven" | inferred | — | closer to **absent**: no report registration, no report-JSON persistence keyed to package identity, no harvest step distinct from generic evidence encoding | **NW in scope** | Gap row 12 is machinery to build, not evidence to collect |
| Inv 47 / CE-F2 stock bridge single-entry | inferred | confirmed: `bridge.py:25-26`, single `entry_channel` through config→definition→bridge | closure is a data-model change across three layers, not a bug fix | NH (owned, row 9) | — |
| Inv 48 / LC-G07 / D-3 embedded catalog sole authority | owner (D-3) | codegen never writes the standalone file TEAx requires (zero hits in src/) | TEAx's entire study surface hard-requires the alternate standalone schema; fusion materializer synthesizes `source_form`, splits QNs, substring-searches predicate IR — each individually forbidden by LC-H02A; teax fixture catalog is hand-authored **in a spike-era IR dialect the production codec would reject** | NH + **under-scoped purge list** | §7 |
| Inv 50 / LC-G10 compatibility bound to exact package identity | inherited | 8-field bind, crash-safe atomic commit verified | binds to a stand-in catalog-byte hash (`config.py:79-84`); three competing definitions of "model contract fingerprint" exist and **nothing consumes codegen's real `semantic_fingerprint`**; re-binding orphans every existing store, no migration stated | **C** today / migration unstated | — |
| Zero-constraint inertness (LC-E12) | inherited | codegen side correct (INV-7 guards) | **TEAx unconditionally reads `result.outputs["constraint_report"]`** (`evaluator.py:132`) — a constraint-free package dies with a bare KeyError | **C — missing invariant** | The "Zero constraint usages" cell checks codegen bytes only and would pass while the package is unevaluatable |
| Appendix A "IFE: strong bounded proof" | evidence claim | 2,301 real cases, independent numeric anchors | rests on three private adapters (one since fixed upstream); the deployed package predates the current predicate runtime and catalog schema by one generation | U — overstated shading | Precedent risk for the "no private adapter counted as proof" rule |
| D-1/D-2/D-3 + simplification quotes `[OWNER-VERBATIM]` | owner | authentic owner texture; first-hop chat capture is legitimate under the owner's own rules | zero documentary corroboration anywhere outside contract+spec; D-2/D-3 ratify an **unrecorded "Option A"** — the option lists exist nowhere | U — durability defect | §4 A-1 |
| LC-A03 cites "original concept, Design Principle 5" | inherited | DP5 exists in `-claude.md:64` | the original concept has four principles; only the claude variant has five | C (miscite) | Cosmetic |
| Gate B framing (LC-E02/E04) faithful to the reports | agent, ratified | matches the independent assessment verbatim in substance; correctly rejects the fusion report's "sanctioned seam" overreach | gap row 10 drops the root-cause report's **lead** finding — the capture-time check-scope defect (`constraint_lowering.py:1348-1350`) — and the report's note that fusion finding #8 was never filed upstream | S framing / C gap-row scope | §4 D-13 |

---

## 4. Findings ordered by severity

Naming: lane-of-origin prefix. "Settled-decision impact" states whether the finding changes an
owner decision (none do) or enforces/scopes it.

### Critical

**E-1. The acceptance matrix can pass in full while a real supported model fails end-to-end.**
Cells pin observations but not fixture shape families, routes, or artifact identity. Concrete
demonstrations: the Gate A cell is already satisfiable with the existing *def-owned* fixture
(`tests/fixtures/constraint_inline/model.sysml:16-21`) while the real stellarator shape —
attribute on a concrete PartUsage, self-named actual (`stellarator_plant.sysml:700-753`) — exists
in no fixture; the polarity cell's existing tests passed *while R-2 was live*, because polarity is
injected synthetically at the `ConcreteConstraint` layer and no kept test drives `assert not
constraint` from source to verdict (grep: zero such fixtures in sysml-codegen); the Gate B cell is
unrunnable today yet its observation is satisfiable by a harness that filters the offender out
before extension. All four PR-wave High findings would have slipped the matrix as written; R-4
still does (live at `constraint_lowering.py:450-463`, exercised by zero kept tests, sitting
exactly between two individually-green cells). **Why existing evidence missed it:** every cell was
graded on whether *a* test exists, not whether the test's fixture shape matches the defect
coordinates. **Correction:** every cell must pin (a) fixture shape family — owner kind, polarity
origin, anonymity, actual presence — (b) both routes through public seams only, (c) a
single-revision artifact-identity thread across cells. Enforces the proof standard; changes no
decision.

**C-1/C-2. The contract's profile semantics are true of no commit, and the committed cross-repo
pair cannot be installed together.** Every committed ref (agentic-mbse `4ed2a07`/pushed `05cde35`,
codegen `512786c`) is profile v3: boolean/string/enum ordering ADMITs and `is_negated` is absent
from the committed profile entirely — the two "fixed" PR-wave findings are fixed only in dirty
working trees. Codegen HEAD demands companion ≥0.1.1; companion HEAD is 0.1.0; the only 0.1.1
commit lives on a different branch. Invariants 10/12 and Appendix A row 2 ("predicate matrix
complete") are present-tense claims about an unpinnable state. **Correction:** ratification must
pin exact candidate hashes (or land the wave first) and re-tense the affected invariants. Enforces
LC-C11; changes no decision.

**D-4. D-3 closure is under-scoped: the embedded catalog cannot supply five fields TEAx consumes,
and every current recovery method is individually forbidden by LC-H02A.** Missing from the
embedded per-eligible-entry data: `source_form` (materializer hardcodes `"definition_typed"`),
usage short name (recovered by QN-splitting), `owner_qn` as a real QN (QN-splitting; the entry
carries `owner_instance_path`, different semantics), a def↔usage join key (recovered by
substring-searching serialized predicate IR — self-documented to break when one definition serves
two usages), and `definition_qn` on the concrete entry. LC-E05 admits only the admitted-per-usage
record gap. Additionally: re-binding study compatibility from the stand-in catalog-byte hash to
real identity raises `IncompatibleStore` for every pre-existing store (`store.py:147-151`) — no
migration path exists or is specified. **Correction:** expand gap row 8 to name the five fields as
required embedded-catalog schema additions, add a store-migration requirement, and surface the
additive schema work under LC-I08's net-LOC accounting. Enforces D-3; changes no decision.

**B-3. Appendix B row 4 states shared positive resolution as established fact.** Three
independently drifted resolution ladders exist (constraint, calculation, aggregation), sharing
only `terminal_disposition`; the repo's own backlog (`[CONSTRAINT-ARCH-UNIFY]`,
`BACKLOG.md:778-800`) records that the predicted drift already happened. The normative invariant
(19/LC-D06) is correct as a requirement; the correction-register row reads as current behavior.
This is precisely the class of error the review question "are implementation gaps written as
established behavior" targets. **Correction:** re-tense the register row and give resolver
unification an explicit owned gap-register row (it is currently implied by rows 1–2 but never
named). Enforces D-2.

**D-1. Verifier bootstrap counterexample confirmed end-to-end.** A package whose
`contracts/verify.py` returns `ok=True` unconditionally passes the loader, because the only code
that checks `verify.py`'s recorded hash is `verify.py` itself (`package_load.py:38-51,74-84`).
Both kept tamper tests mutate other files and rely on the honest verifier. The contract admits the
defect (invariant 39, honestly labeled), but the acceptance cell as worded ("a malicious
package-local verifier cannot bypass rejection") is satisfiable by a stub authentication.
Lane D also answers a review question: fixing this does **not** create a second catalog authority
— the verifier owns package integrity, the catalog owns schema; the same canonical verifier module
relocates from package-trusted to runtime-trusted. What is missing is a verifier-version skew rule
(if teax vendors a copy, drift against codegen's sealer must fail closed). **Correction:** add the
skew rule to LC-F09 and make the cell require a specific bypass attempt to fail.

### High

**B-2 (F also). Relocated-snapshot byte parity is broken more broadly than the contract's named
open item.** Generated calc-module docstrings embed checkout-absolute source paths (`modules.py:88,
488`; `teax_module.py.jinja2:5,40`); the snapshot loader re-absolutizes `source_file` against the
current directory (`loader.py:906-916`); anonymous *eligible* IDs digest the raw absolute path
(`constraint_lowering.py:483-485`). Relocating a snapshot therefore changes generated bytes and
the executable fingerprint on any calc-bearing model. The portability suite compares
contract/catalog/report bytes only (`test_constraint_snapshot_portability.py:160-176`), so CI
cannot see it, and the open item is framed around *constraint* locations only. The "Relocated
snapshot" acceptance cell cannot pass today, and closing the item as scoped would not make it pass.

**B-4. Invariant 26's second sentence (producer-completeness) is enforced only by a proxy that
does not check it.** V11 flags a parameter only when wired ∧ fell-through ∧ valueless
(`graph_builder.py:800-845`). Two silent pass-throughs: a fell-through entry point that acquired
any default, and the calc ladder's ambiguous design-attribute resolution, which logs a WARNING and
picks `candidates[0]` (`dependency_backtracker.py:851-856`) — a wrong-attribute binding passes V11
and channel validation. "Exact-QN resolution succeeding against the wrong occurrence while V11
passes" is structurally possible. D-1's "every model-derived value has a producer when the graph
is built" needs its own check (or an explicit downgrade to goal status with the proxy named);
otherwise the stellarator repair (gap row 10) can be certified against "V11 clean" while the D-1
sentence remains unproven.

**A-2. D-2 silently reverses a same-day owner ruling that another repo still records as settled.**
WI-027 D7 (stellarator repo: `work/active/WI-027_demo-constraint-execution/design.md:31,229,261`)
is an owner-ruled, recorded-as-settled decision to route literals through `'Scalar Value'`
passthrough calcs. The contract supersedes the *claim* (Appendix B row 4's passthrough sentence)
but never records that the superseded position was itself an owner ruling, and the stellarator
artifact carries no pointer back. Under the owner's surfacing rule this cross-repo owner-vs-owner
conflict must be recorded on both sides, and the stellarator acceptance must state explicitly that
the D7 passthroughs are to be removed. Enforces D-2 (the reversal is the owner's own later call);
the defect is the silent carriage.

**A-1. The three owner decisions and the simplification constraint have zero documentary
corroboration, and D-2/D-3 ratify an unrecorded "Option A."** The quotes exist only in the
contract and spec; no document records what Option A and Option B were for either decision. If the
agent's reconstruction of its own option list drifted, nothing in the record can catch it — and
two same-day decisions both quoted as "100% Option A" invite future cross-wiring. **Preserved
lane-A position:** the quotes should stand (authentic owner texture; first-hop chat capture is
what the owner's rules prescribe) — the fix is appending the option lists under each decision at
ratification, not demoting the grades.

**F-4. TEAx cannot evaluate a constraint-free package at all.** `PreparedEvaluator.evaluate`
unconditionally reads `result.outputs["constraint_report"]` (`evaluator.py:132`); codegen emits
the aggregator only when constraint facts lowered. A package from an assert-free model dies with a
bare KeyError. The "Zero constraint usages" acceptance cell observes codegen bytes only and would
pass while the product is unevaluatable. Missing invariant: either TEAx tolerates report absence
or codegen always emits the channel — the contract must pick one.

**F-2. Re-sealing launders foreign content into the "verified" set.** `sysml-codegen seal`
re-hashes whatever is on disk (`cli/__init__.py:728-768`); the deployed IFE package's seal covers
the consumer-fabricated standalone catalog. "Sealed by sysml-codegen" does not mean "generated by
sysml-codegen," and no invariant or cell distinguishes seal integrity from seal *provenance*.
Under D-3 the bridge file disappears, but the laundering seam remains for any future foreign file.

**D-2 (lane D). Evidence mutability is real and the acceptance cell is satisfiable without
touching it.** `evidence.report.results[0].status = "satisfied"` succeeds today; the persisted
artifact is protected only by the runner's incidental encode-before-policy ordering
(`runner.py:130-132`). The mutation cell must name the nested generated models, not the frozen
envelope.

**D-5. Gap row 12 (file-backed report persistence) is machinery to build, not evidence to
collect.** No report registration, no report-JSON persistence keyed to package identity, no
harvest step exists; the study store encodes a runtime-owned projection instead. The contract's
"unproven" framing understates the work class.

**D-13. Gap row 10 drops the Gate B root-cause report's lead finding.** The report's primary
conclusion is a codegen *check-scope defect* — the capture-time whole-graph
`collect_uncovered_params` call (`constraint_lowering.py:1348-1350`) re-audits coverage the
generation gate already owns — with the cost-rollup representation gap second. The contract's row
10 carries only the representation half. The report also records that fusion finding #8 was never
filed upstream. Both belong in the register.

**E-18. No acceptance row exists for resume/query across incompatible fingerprints** (invariant
50 / LC-G10 is acceptance-orphaned), and kept compatibility tests never vary
`executable_fingerprint` or `model_contract_fingerprint` — in tests the latter is the literal
string `"contract-fp-A"`. The matrix can be fully green with cross-package resume unguarded.

**E-15. No catalog/schema skew cell exists in any direction**, and the profile-skew fail-closed
raise (`constraint_lowering.py:898-900`) has never been executed by any test. TEAx fixtures are
TEAx-local files, so a codegen catalog rename passes every TEAx test unchanged.

### Medium

- **A-3. Silently dropped owner-era rules.** (a) `assessment_failed` as a distinct
  evidence-preserving case state — dropped from the contract **but implemented in teax**
  (`runner.py:126-143`): the contract drops a rule the code already honors; restoring it is free.
  (b) Margin discipline (sign respects polarity, no invented aggregate margin, boundary-zero
  semantics) reduced to "optional signed margin." (c) Aggregator exit-ancestry as a structural
  guarantee. Each needs a register row or an explicit non-goal.
- **A-4. Appendix B has no source column**; three rows ("profile is codegen-only," "snapshot
  freezes decisions") supersede claims that exist in no document — conversational supersessions
  indistinguishable from doc-sourced ones. Census correction C-5 (catalog "source record"
  vocabulary) is missing from the register entirely.
- **A-5. LC-E02's surviving rationale is unstated.** Ratified against a late-fill pattern D-1 has
  since removed; what it still buys (capture of incomplete graphs; failure attribution) is real
  but appears nowhere — the register's one motivation-orphaned rule and a relitigation target.
- **C-3. Diagnostics closure requires a facts-schema bump** — `ExtractionDiagnosticFact` cannot
  express severity — which couples gap row 4 to a version/skew event. The register should say so.
- **B-6. Grandfathered skip-lowering snapshots fail open in the product**: one WARNING, then a
  sealed package indistinguishable from a constraint-free model (`graph_rebuild.py:233-241`).
  Contract excludes them from acceptance but the product path silently drops asserted constraints.
- **B-10/F. `tracking_key` is a dead field** (zero writers, absent from the catalog) while the
  non-goals lean on it as the anonymous-correlation story.
- **F-5. `RUNTIME_CONTRACT_VERSION` is duplicated by hand** in codegen and teax with no skew rule;
  a teax-side bump makes every sealed package fatally unloadable under the strict default.
- **D-6. `TEAX_SIMKIT_PATH` invalid-path fallthrough confirmed** — but it is a codegen
  *test-helper*, not the teax runtime; the acceptance row should scope it as test infrastructure.
- **D-8. Failure phase tag is not a faithful phase** — always `MODULE_EXECUTION`; `OUTPUT_WRITE`
  never emitted; backend parity excludes report contents from comparison.
- **B-5. R-8 confirmed live** (warning render can replace the actionable BLOCK diagnostic); R-7
  (demand-overwrite regrouping) and R-9 (signed/unit defaults) also live — all owned by register
  rows; their matrix cells are currently failing cells, correctly unclaimed.
- **E-obs. Stub-satisfiable observations**: row 7's "deterministic" passes on last-wins overwrite;
  row 16's failure-shaped wording structurally cannot see R-3-style silent margin corruption;
  row 12 doesn't demand the `-0.1`/`[MW]` shapes; row 21's "equal normalized failure" is A==B
  through one shared function (both-wrong passes).
- **C-5 (lane C). Mixed-category non-numerical equality** (`boolean == string`) classifies as a
  valid non-numerical statement rather than malformed — an owner question LC-C06's wording leaves
  open; flagged, not decided.
- **F-9. Parameter-group fallback silently invents membership**: unclaimed QNs land in a
  synthesized `system_design` group (`constraint_lowering.py:1246-1262`), where every
  modeled-default EP lives — a modeled threshold becomes an editable JSON input with no marker
  distinguishing it from a design attribute.

### Low

- LC-A03 miscites which concept holds Design Principle 5 (only `-claude.md` has five).
- Stale comment `pipeline_builder.py:1007-1009` (catalog "returns None") describes superseded
  behavior; `predicate_compiler.py:150,201` error strings still say v3 in a v4 tree.
- Inline eligible `predicate_source_key` degrades to file *basename* under the legacy snapshot
  branch (`constraint_lowering.py:986-996`) — collision-prone, though failure is loud via same-IR.
- `_walk_comparison` surfaces only the first failing operand fact per side.
- agentic-mbse `docs/constraint-facts-and-expression-ir.md:70-71` omits NON_NUMERICAL from the
  outcome list.
- `UsageDecision.effective_predicate` aliases the mutable facts object — decision "immutability"
  holds by convention (same family as invariant 41, one repo earlier).

### Preserved disagreements

- **F-15 / Gate B shape.** Lane B: under current semantics extension *cannot* introduce a V11
  violation (minted EPs are never fallback EPs; module-output inputs are channel-validated), so
  the "differential" check is vacuous and the correct fix is deleting the extension-time call,
  keeping channel validation. The contract (and Lane E's cell analysis) frame Gate B as
  implementing a differential check. These lead to different Item 3B implementations. Resolution
  belongs to the Gate B item: first prove or refute "extension can introduce a new V11 violation"
  with a constructed case; if refuted, LC-E02 should be reworded from "rejects only new
  violations" to "performs no coverage validation; final generation owns coverage."
- **A-1 quote handling.** Lane A defends keeping the `[OWNER-VERBATIM]` grades (with option-list
  appendices) against any harder line that unverifiable quotes should be demoted. This review
  adopts Lane A's position but records that it was contested.
- **Contract honesty.** Lane B judges the contract "unusually honest" (every admitted gap
  verified to be exactly where it says); Lane E judges the proof layer "vibes." Both are true at
  their layers: the *invariants* are honest; the *matrix* is not yet a proof instrument. The
  verdict in §1 reflects both.

---

## 5. Acceptance-matrix holes

Lane E's full 18-attack table is in its lane report; the consolidated holes:

**Missing cells (concrete, each with a live failure mode):**

1. Anonymous-admitted-with-actual × snapshot route — the exact R-4 crash coordinates; the one
   still-live known bug falls between two green cells.
2. Shared definition × mixed polarity — `compile_shared_predicates` takes `is_negated` from the
   first entry with no agreement check.
3. Negated × anything, live — no `assert not constraint` exists in any codegen fixture; negated ×
   modeled-default, × occurrence expansion, × snapshot are all uncovered.
4. Recursive containment as distinct from `[*]` — same cell, different fixture shape, opposite
   outcome (R-5).
5. Symlink policy at seal/verify (invariant 37 is acceptance-orphaned).
6. Malformed snapshot shapes (LC-F03 orphaned; R-11).
7. Catalog schema skew, both directions (E-15).
8. Resume across incompatible fingerprints (E-18).
9. Headline precedence under a mixed result population (invariant 33 orphaned).
10. Violated/indeterminate file-backed persistence (row 22 says "successful" only; backend parity
    excludes the report).
11. Zero-entry-channel package; excluded-only × entry channels (LC-I03 names the axis; matrix has
    one and multiple only).
12. Def-owned assert reached through a redefining usage (2 of the stellarator's 5 verdicts) —
    exists only inside the monolithic blocked stellarator row.
13. Per-occurrence distinct override values — occurrence collapse is observationally invisible
    when all occurrences share one value.
14. Constraint-free package **evaluated by TEAx** (F-4) — the current cell stops at codegen bytes.
15. A fact-consumer cell operationalizing invariant 13 (the only current mechanism is the static
    map the invariant disqualifies).

**Tests that appear to cover a case but exercise a weaker shape:** Gate A cell ← def-owned
fixture (real shape is usage-owned, self-named actual); polarity cell ← synthetic
`ConcreteConstraint(is_negated=True)` (never source-driven); shared-producer cell ← self-scoped
de-indexed collapse (never one genuine producer feeding N occurrences); demand-retention cell ←
non-public `include_all=False` harness (public route never prunes); relocation cell ← same-machine
parity (machine-bound content cancels); tamper cells ← mutations that spare `verify.py`; both-
backend cell ← A==B through one shared normalizer; runtime cells ← private `_generate_*` +
`sys.path` import, precisely the seam LC-H02 disallows as proof.

**The ordering rule ("no later row may certify around an earlier open dependency") is
unenforceable as written**: cells carry no revision column, no dependency binding, and no
machine-checkable definition of "workaround." The precedent cuts the wrong way — Appendix A
already grades IFE "Strong bounded proof" while recording it ran through private adapters. The
only binding mechanism is a single-revision, single-artifact composed run — which is itself the
last register row. Cells need the revision/route/shape pinning of E-1 for the rule to bind.

---

## 6. Simplification and purge map

Direction check first, because the owner's constraint demands it: **most of the map is genuine
deletion, but D-3 closure requires additive embedded-catalog schema work (five fields, D-4) and a
store-migration path.** Under LC-I08 this must be surfaced as a justified increase inside an
otherwise net-negative remediation — it should not surprise anyone mid-implementation.

**Consolidate (safe, replacement seam named):**

| Target | Location | Replacement seam | Est. effect |
|---|---|---|---|
| Three resolution ladders → one registry-owned ordered strategy, strict/lenient terminal | `constraint_lowering.py:139-296` + `dependency_backtracker.py:562-856` + `input_resolver.py` | already scoped by `[CONSTRAINT-ARCH-UNIFY]`; precedence pins exist in `test_constraint_resolver.py` | −300 to −500 lines; closes Gate A and B-4(b) as a family |
| Triple-layer repeated validation (10 CLI preflight seams + re-validation inside pipeline-YAML/registry/model-contract) | `cli/__init__.py:311-963` (10 sites), `pipeline.py:55`, `registry.py:207`, `model_contract.py:36` | one plan-boundary check once the plan is the sole semantic carrier (consistent with invariant 31) | ~15 call sites |
| Three `evaluate_profile` runs per capture+generate | `serializer.py:149`, `constraint_lowering.py:450,903` | thread one decision set | drift-surface removal |
| Duplicated module-kind path dispatch | `cli/__init__.py:152-173` vs `modules.py:39-57,465-468` | single helper | ~40 lines |
| `RUNTIME_CONTRACT_VERSION` + verifier duplication | codegen `contracts/versions.py:11` ↔ teax `package_load.py:22` | single-source with a fail-closed skew rule (extends LC-C11 discipline to the verifier per D-1 finding) | small, load-bearing |

**Delete (superseded / dead):**

| Target | Location | Risk |
|---|---|---|
| Legacy `compile_predicate` + `legacy_policy` + `load_predicate` (polarity-baked compiler; no production caller) | `predicate_compiler.py:338-397,415-423` | none found; the deployed IFE package was built with it — regeneration, not compatibility, is the answer |
| Dead constraint branch in `generate_teax_module` + alias | `modules.py:395-434,502` | none |
| Extension-time whole-graph V11 call | `constraint_lowering.py:1436-1438` | **contested** — see F-15; resolve the vacuity question first |
| fusion catalog materializer | `exploration/ife_e2e/study/materialize_constraint_catalog.py` | deletable only after D-4's five fields land |
| fusion `MultiChannelEvaluator` wrapper | `run_viability_study.py:68-90` | deletable only after CE-F2's multi-entry data model lands |
| TEAx standalone catalog schema + consumers | `study/config.py:79-84`, `query.py:46-65`, `cli.py:98` | store-migration break (D-3 finding) must be handled |
| TEAx hand-authored fixture catalog (spike-era IR dialect the production codec rejects) + tests reading it | `simkit/tests/evaluation/fixtures/sealed_package/.../constraint_catalog.json`, `study/test_query.py` | **missing from the contract's purge list** — must be regenerated from real codegen artifacts |
| Stand-in `_model_contract_fingerprint` | `study/config.py:79-84` | replacement must consume codegen's real `semantic_fingerprint` — which today has zero consumers |
| Grandfathered snapshot fail-open branch | `graph_rebuild.py:233-241` | product decision: fail closed or explicit CLI opt-in |
| `tracking_key` dead field (or implement it) | `resolution/models.py:386` | non-goals lean on it; pick one |

**Dangerous compression (do not merge):** seal/verify glob duplication is deliberate,
documented, stdlib-only (D7) — keep. Lowering's halt-before-mutation staging and the
plan-before-clear boundary are distinct semantic stages; consolidation must not collapse them.
The profile's two consumers (L4/L6 vs codegen) are an intentional independence property, not
duplication.

---

## 7. Decision assessment

**D-1 (no late-fill; graph-complete at construction): consistently carried, incompletely
enforced.** No public late-fill seam exists in codegen (verified); the fusion bridge is correctly
classified as private, stale, non-certifying. LC-H04's external-input carve-out is clean. The gap:
invariant 26's producer-completeness sentence has no enforcement mechanism beyond the V11 proxy
(B-4), so D-1's strongest sentence is currently unfalsifiable — the stellarator acceptance can be
"passed" without proving it. Required carry-through: a producer-completeness check distinct from
V11, or an explicit downgrade with the proxy named. Also: gap row 10 must carry the check-scope
defect (D-13) or the D-1 acceptance will be built on the wrong fix.

**D-2 (direct literal actuals; one resolver; strictness at terminal only): faithfully stated,
overclaimed as current, and carrying an unsurfaced owner-conflict.** Gate A's code seat is exactly
where the contract says; the QN-keyed entry-point mechanism the decision requires already exists
on the minting side, so D-2 is feasible. Defects in carriage: Appendix B row 4's present tense
(B-3); resolver unification has no named gap-register row of its own; and the WI-027 D7 reversal
is unrecorded on both sides (A-2). None of these touches the decision's substance.

**D-3 (embedded catalog sole authority; purge the alternates): correctly directed,
under-scoped.** The purge list correctly names the materializer, the alternate schema, and the
reconstruction techniques. It misses: the five embedded-catalog fields TEAx legitimately needs
(D-4), the stand-in compatibility fingerprint and the store-migration break its replacement
causes, the hand-authored teax fixture catalog acting as a contract definition, and the fact that
codegen's real `semantic_fingerprint` currently has zero consumers anywhere. The verifier-bootstrap
fix composes with D-3 (no new duplicate authority) provided a verifier-version skew rule is added.
D-3 closure will be net-additive on the codegen schema side; LC-I08 must absorb that as a surfaced,
justified increase.

---

## 8. Required corrections before ratification

### Architecture corrections (edits to the contract/spec)

1. **Pin the candidate.** Name exact hashes for the revisions the contract describes (or land the
   PR wave first). Re-tense invariants 10/12 and Appendix A row 2 to "candidate" until then.
   [C-1/C-2]
2. **Re-tense Appendix B row 4** ("consumers share QN-keyed positive resolution") to the required
   end-state, and add an explicit gap-register row for resolver unification. [B-3]
3. **Add the matrix pinning rule** (E-1): every cell names its fixture shape family (owner kind,
   polarity origin, anonymity, actual presence), requires both routes through public seams only,
   and is bound to one revision set; certification records the fixture and route. Without this,
   the ordering rule stays unenforceable.
4. **Add the missing cells** listed in §5 (fifteen), at minimum: anonymous-admitted-with-actual ×
   snapshot; shared-def × mixed polarity; live negated source-to-verdict; recursive containment;
   seal/verify symlinks; malformed snapshot; catalog skew both directions; resume across
   fingerprints; mixed-population headline precedence; violated file-backed persistence;
   zero-entry channels; def-owned assert through redefining usage; per-occurrence distinct
   overrides; TEAx evaluation of a constraint-free package; a fact-consumer cell.
5. **Expand D-3 closure scope** (gap row 8): the five embedded-catalog fields as required schema
   additions; a store-compatibility migration requirement; the hand-authored teax fixture and
   stand-in fingerprint as named purge targets; the expected net-additive schema work surfaced
   under LC-I08. [D-4]
6. **Broaden the portability item**: absolute paths in generated calc-module docstrings, loader
   re-absolutization, and anonymous eligible ID digests join "portable admitted locations";
   the relocated-snapshot cell adds a no-absolute-path assertion over the full generated tree.
   [B-2]
7. **Resolve invariant 26**: add a producer-completeness check requirement distinct from V11, or
   downgrade the second sentence to a goal with the proxy named. [B-4]
8. **Record the WI-027 D7 supersession** in Appendix B with owner-ruling provenance, and require a
   pointer in the stellarator artifact; state in the stellarator acceptance that the D7
   passthroughs are removed. [A-2]
9. **Append the option lists** (or a conversation path-cite) under D-1, D-2, D-3 so "100% Option
   A" has a referent. [A-1]
10. **Split gap row 10** into (a) the capture-time check-scope defect and (b) the cost-rollup
    representation item, restoring the root-cause report's lead finding; file fusion finding #8.
    [D-13]
11. **Add missing invariants**: TEAx tolerates constraint-free packages or codegen always emits
    the report channel (pick one) [F-4]; `runtime_contract_version` and the verifier are
    single-sourced with fail-closed skew [F-5/D-1]; seal provenance — re-sealing cannot launder
    ungeneratable files, or the seal records a generation manifest [F-2]; grandfathered snapshots
    fail closed in the product or require explicit opt-in [B-6].
12. **Rescope gap rows 4 and 12**: row 4 requires a facts-schema bump (severity field) with its
    skew consequence stated [C-3]; row 12 is persistence machinery to build, not evidence to
    collect [D-5].
13. **Register housekeeping**: add census C-5 to Appendix B; add a source column (or mark
    conversational rows as such); restore or explicitly non-goal the dropped rules —
    `assessment_failed` (already implemented in teax; restoring is free), margin discipline,
    aggregator exit-ancestry [A-3/A-4]; state LC-E02's surviving rationale [A-5]; resolve the
    Gate B vacuity question inside Item 3B before implementing a differential check [F-15].
14. **Strengthen stub-satisfiable observations** (§4 E-obs): row 7 pins which group survives;
    row 12 pins the `-0.1` and `[MW]` shapes; row 16 adds a silent-corruption (margin-sign)
    probe; row 21 compares report contents across backends; row 24 mutates the nested generated
    models; row 23 requires a concrete bypass attempt to fail.

### Implementation backlog (not contract edits; mostly already owned)

- R-4, R-5, R-7, R-8, R-9 remain live in the working tree — owned by register rows 1 and 4;
  their cells are currently failing cells, correctly unclaimed.
- `tracking_key`: implement or delete, and update the non-goals accordingly.
- `TEAX_SIMKIT_PATH` helper fix (test infrastructure; rescope the acceptance row's wording).
- Emit `OUTPUT_WRITE` phase honestly or collapse the enum.
- Stale comments and v3 literals in the v4 tree; duplicate-QN last-win in the profile's
  definition index; first-fact-only diagnostic truncation in `_walk_comparison`.

---

## 9. Final answers

**Would implementing this contract as written prove the full lifecycle?** No. Implementing every
requirement would produce the right system, but the proof instrument as written cannot
demonstrate it: the matrix is satisfiable by the same weaker-shape evidence that certified the
components while the composition was broken. With the §8 corrections (cell pinning, missing
cells, revision binding), the proof standard is achievable.

**Can the acceptance matrix pass while a real supported model still fails?** Yes — demonstrated
constructively. Lane E's composed counterexample (a small in-family plant: usage-owned literal,
live negated assert, anonymous admitted-with-actual, `value`-named formal, recursive part
elsewhere) fails five ways against the current trees while every cell is certifiable the way the
current test corpus certifies them.

**Are any implementation gaps incorrectly written as established behavior?** Yes, four: shared
positive resolution (Appendix B row 4); profile-v4 semantics as current (invariants 10/12,
Appendix A row 2 — true of no commit); "sharing recorded" for shared producers (graph-visible
only, catalog-invisible); and LC-F02's "demand equivalence judged by retained producers" (a
definition with no comparing mechanism). File-backed persistence is honestly labeled open but
mis-classed as proof work when it is build work.

**Are all load-bearing gaps owned and correctly ordered?** Mostly owned; six omissions: the five
embedded-catalog fields and store migration (D-3 scope); portability beyond constraint locations;
the capture-time check-scope defect; verifier/runtime-version skew; TEAx's constraint-free-package
crash; resolver unification as its own row. The ordering rule itself is sound in intent but
unenforceable without revision-pinned cells.

**Is any consumer adapter or private bridge still being treated as proof?** The contract's rules
say no and Appendix A is mostly honest — but "IFE: strong bounded proof" shades it: that proof
rests on three private adapters (one since fixed upstream), and the deployed IFE package predates
the current predicate runtime and catalog schema by a generation. The runtime test suites also
certify execution cells through private `_generate_*` + `sys.path` imports — the exact seam
LC-H02 disallows as proof — so the precedent inside the kept corpus still cuts against the rule.

**Does the design create one coherent system, or merely document several components?** The
contract describes one coherent system, and the blind reconstruction confirms the described
system is the one the code is converging on. What exists today is several components joined by
private bridges at exactly the boundaries the contract flags — catalog, multi-entry, verification
bootstrap. The contract knows this better than any prior artifact in the record; its remaining
sin is not incoherence but an unproven proof layer and a handful of present-tense claims about a
future state. Correct those, and it is ratifiable.
