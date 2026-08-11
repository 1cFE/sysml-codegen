# Design Review: Elaborator Atomic Cutover

**Design:** `.project/active/elaborator-cutover/design.md`  
**Census:** `.project/active/elaborator-cutover/cutover-census.md`  
**Spec:** `.project/active/elaborator-cutover/spec.md`  
**Review File:** `.project/active/elaborator-cutover/design-review.md`  
**Date:** 2026-08-10

---

## The Point

One loaded semantic source occurrence must become exactly one runtime source for every and only its
bound calculation, constraint, aggregation, FORMULA, and alias consumers. Live generation and
portable offline generation must preserve that answer. Unsupported authored forms must fail before
capture or generation. Item 7 therefore succeeds only when the validated exact-ID `InstanceGraph`
is the sole shipped semantic authority and no legacy or alternate association route can produce a
different executable answer.

## Fundamental Assessment

**Assessment: Concerns. Overall approach is right; the design is not ready to implement.**

The product-lens result is **CLEAR** and neither design smell 2 nor smell 7 fired. This is the right
piece of work. Elaborate once, validate one exact graph, project it one way, persist that graph, and
delete the string-reconstruction route is the simplest architecture that satisfies the owner
outcome. The v6 envelope, strict capture, one-way projection, in-place Fusion Tea correction, and
one coordinated landing all belong in Item 7.

Four load-bearing claims are not yet made true by the mechanics:

1. The two-field `PipelineContext` can contain or later acquire a `ComputationGraph` that was not
   projected from its `InstanceGraph`.
2. The source manifest can describe bytes other than those SysIDE parsed and does not yet define a
   complete reproducible source-document set.
3. The qualified-name profile adapter still has a conditional final disposition, so Item 6's
   profile dual does not converge to one named owner.
4. “Non-releasable” preparatory commits and owner acceptance of a normalized candidate are process
   statements, not gates bound to the exact final bytes and paired repository states.

These are material design gaps, but they do not invalidate the instance-graph cutover. The design
should be revised and rereviewed rather than reshaped from first principles.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Fail**

#### DR-F1 — The two-field context does not enforce one semantic authority

Design D1 makes `PipelineContext(*, instance_graph, computation_graph)` publicly constructible and
validates only the instance graph before accepting both objects. Generation then consumes
`.computation_graph` directly. The two graphs are not coupled by a projection receipt, source
fingerprint, selection record, or recomputation check.

The `frozen` and `slotted` wrapper does not close this hole. `InstanceGraph` contains mutable dicts
and lists (`src/sysml_codegen/elaboration/graph.py:233`), and `ComputationGraph` is a mutable
Pydantic model (`src/sysml_codegen/resolution/models.py:567`). A caller can construct a valid graph
A beside unrelated computation graph B, or mutate either child after construction. The context
then presents B to generation while claiming A is the sole authority. Retained import aliases are
safe because they are object-identical re-exports; the public constructor and shallow mutability are
the semantic compatibility route.

**Required material correction:** choose and specify one enforceable construction model. Viable
forms include:

- expose the two attributes but make direct construction unavailable; a sole factory accepts the
  `InstanceGraph` plus selection arguments and derives the `ComputationGraph`;
- make the derived graph an `init=False` value created inside a controlled constructor; or
- bind the pair with a checked projection receipt containing the instance-graph fingerprint,
  canonical `targets`/`include_all` selection, projector semantic marker, and computation-graph
  digest, and verify it at every generation boundary.

Whichever form is chosen must also prevent post-construction child mutation through deep
immutability or defensive copies. This changes the public constructor contract and needs design
rereview.

#### DR-F2 — Source certification can bind the wrong bytes or an incomplete file set

D6 and the capture section say the manifest hashes files after SysIDE has loaded them. Nothing
prevents a file or symlink target from changing between parse and hash. That produces a graph from
bytes A and a manifest claiming bytes B. Both inner and outer digests can then be correct while the
source claim is false.

The document population is also undefined at the boundary where it matters:

- whether SysIDE standard-library documents are included, excluded, or represented separately;
- how imported user documents outside a supplied root are handled;
- whether directory-root freshness compares the complete admissible file set, including added and
  removed files, or only rehashes old manifest entries;
- how duplicate/overlapping roots, symlinks, case normalization, and a file named under more than
  one root are canonicalized; and
- how capture proves that its enumerator matches the documents the loader actually admitted.

Checking only recorded files misses a newly added source that a fresh directory load would admit.
Conversely, treating every SysIDE document as user source can make ordinary standard-library use
unmappable by `map_live_source_referent()` (`src/sysml_codegen/analysis/source_referent.py:32`).

**Required material correction:** define one source-document admission algorithm shared by live
load, capture, and optional freshness verification. It must state the standard-library/external
document policy, compare exact referent sets including additions and removals, and pin root and
symlink normalization. Capture must stage immutable input bytes or perform a before/load/after
identity-and-hash check and refuse atomically if anything changes. Add race, added-file,
removed-file, external-import, standard-library, overlap, and symlink cases with the ordered typed
failure. This needs design rereview.

#### DR-F3 — The Item-6 qualified-name profile dual is not closed

Design D10 says a QN surface may remain as validation-only. Census row `PROD-21` says it may remain
only if it accepts an already-decided exact record and cannot select a candidate, otherwise it is
deleted. That is a condition, not a final disposition.

The current surface still constructs a definition map by qualified name and selects a definition
inside `_evaluate_usage()` (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:1042`),
while `evaluate_identified_profile()` performs the exact-ID association at line 1068. Agentic
validation callers still invoke `evaluate_profile()` directly in
`validation/level4_constraints.py:64` and `validation/level6_architecture.py:611`. Calling the
first path “validation-only” limits its blast radius but does not converge association ownership.

**Required material correction:** choose the final agentic public surface now. Either migrate the
validation callers to the one exact association result and delete the QN entry point, or retain a
neutral validation formatter that consumes an already-decided exact record and performs no QN
candidate lookup. Enumerate its callers, exports, return type, and tests. The final design must have
one association owner and one decision core. This cross-repository API choice needs rereview.

#### DR-F4 — Owner acceptance is not bound to the exact atomic candidate

D12 and the migration sequence allow preparatory commits and call them non-releasable. No gate
prevents such a clean commit from being merged, tagged, or released. The owner then reviews a
timestamp-normalized corpus view from dirty working trees, but the design does not bind the
acceptance record to the exact envelope bytes, manifest, code changes, or paired repository state
that are finally committed.

This leaves two gaps. A preparatory commit can escape as a mergeable partial state, and a batch can
change after owner review without invalidating the recorded acceptance.

**Required material correction:** define an immutable candidate identity. The review manifest must
hash every v6 file and refusal record, the normalized semantic diff, both repository bases and
candidate states (commit or patch digests), the census version, and the TEAx evidence revision. The
owner disposition must cite that identity. Any later byte, outcome, code, or paired-repository
change invalidates acceptance and requires a new candidate review. Preparatory work must either stay
unpublished and be squashed into the final paired landing, or carry a hard CI/branch gate that fails
merge/tag/release until the final cutover marker and accepted candidate identity are present. A
rejected candidate can remain temporary and uncommitted; only the accepted bytes enter the final
changeset. This workflow contract needs rereview.

The target/include/filter decisions are otherwise consistent with the spec. Exact-edge target
closure, mandatory constraint roots, a live-only design filter, and digest-bound capture options are
the correct behaviors. DR-F1's projection receipt must include `targets` and `include_all`; otherwise
the context still cannot prove which valid projection it carries.

### 2. Pattern Consistency

**Assessment: Concerns**

The main architecture follows the certified Item-6 pattern: typed IDs inside, strings only at
projection, and `ComputationGraph` downstream-only. Pure re-export aliases also follow the existing
public import pattern without creating another implementation.

The deviations are the two remaining parallel association patterns:

- a context that accepts two independently mutable graph representations; and
- exact-ID and QN-keyed profile association in agentic-mbse.

Correcting DR-F1 and DR-F3 restores the established one-way pattern. No new graph, registry,
resolver, or generic persistence abstraction is justified.

### 3. Abstraction Quality

**Assessment: Concerns**

The v6 envelope, source-manifest helper, exact graph codec, and shared projector each earn their
existence. The inner digest keeps the graph codec independently testable; the outer digest binds the
whole envelope. This is useful defense in depth, not a second semantic model.

The public two-graph context does not yet earn its exact constructor shape. Preserving the
`.computation_graph` capability is justified; preserving arbitrary caller construction of an
uncoupled pair is not. The revised design should keep the smallest public shape that can prove the
derived relationship.

The conditional QN adapter is also an abstraction smell. “Validation-only” is a consumer label,
not a mechanical boundary. Its input type must make semantic reassociation impossible.

### 4. Duplication Avoidance

**Assessment: Fail**

DR-F1 permits two executable graph truths in one object. DR-F3 retains two definition-association
routes. Both can drift while each local validator remains green.

The outer/inner v6 digests do not have this problem because their scopes are nested and explicit.
Keep them, but name the outer-to-inner relationship and failure mapping in the normative schema.

### 5. Data Structure Clarity

**Assessment: Concerns**

#### DR-F5 — The v6 schema is not exact enough to be the test oracle it claims to be

The top-level fields and validation order are strong. The nested schema remains partly prose. For
example, `capture` names “producer versions” without fixing the JSON key and child keys; `roots.kind`
has no closed vocabulary; `source_roots` has no exact public type; and the design does not say which
semantic changes require a bump to `certifiability_profile`. Producer versions are classified as
non-semantic, so the certifiability marker must explicitly cover projector and envelope-validation
semantics or a newer projector can interpret an old graph differently without a compatibility
failure.

**Required localized correction:** add one normative typed v6 schema with every nested key, type,
enum, cardinality, ordering rule, and unknown-key rule. State that
`projectable-instance-graph/v1` covers graph projectability, selection, and projection semantics,
and list the changes that require its bump. If that marker is not intended to carry those semantics,
adding a new compatibility marker is material and needs rereview.

Subject to DR-F2 and this schema correction, the validation order is sound: version rejection
precedes interpretation; exact shape and outer integrity precede compatibility; source consistency
precedes inner decode; graph validation/projectability precedes target selection; and the typed
snapshot failures preserve one broad catch without aliases. Strict capture and the no-v5 rule also
meet the spec.

### 6. Route Safety

**Assessment: Concerns**

Live, in-place-v6, and relocated-v6 all reach the same projector, and snapshot generation rejects a
new design filter. No wildcard or fallback semantic route is proposed. The remaining route hazards
are DR-F1's unbound derived graph, DR-F2's false freshness pass, and DR-F3's validation association
route.

The capture atomic-write sequence is appropriate: validate in memory, write and fsync one sibling
temporary file, then replace. Implementation tests must cover both an absent destination and a
sentinel destination for every pre-replace failure. No v6 artifact may contain diagnostics.

### 7. Bets & Decisions Integrity

**Assessment: Concerns**

The stated bets are genuine and include failure consequences. The riskiest, B1, has credible Item-6
certification and the 29-cell evidence behind it. B4 is testable through unchanged equations,
identifier-only formal renames, direct arithmetic goldens, and real execution.

Three hidden bets need to become explicit design obligations:

- files cannot change between SysIDE parse and manifest hashing;
- the same complete document inventory can be reproduced later from only ordered roots; and
- prose declaring a commit non-releasable and a candidate accepted is enough to bind two Git
  repositories and exact corpus bytes.

DR-F2 and DR-F4 replace those bets with mechanisms. The decisions otherwise name reasonable
alternatives and reject them for relevant reasons.

### 8. Reader Comprehension

**Assessment: Concerns**

The design explains the core model clearly. A reader can understand live elaboration, capture,
offline loading, projection, and deletion in one pass.

The document becomes misleading where it says the context has one authority and the census is
closed. Those conclusions are stronger than the recorded mechanics. The conditional QN row and the
grouped census rows require the implementer to choose scope during implementation. Correcting the
findings below will make the handoff auditable without adding more architecture prose.

---

## Census, Proof, and Gate Corrections

These corrections are objectively verifiable and do not require a full design rereview unless the
mechanical inventory exposes a new keep/delete/migrate decision.

### DR-F6 — The census is not mechanically closed

The closure method says grouped rows have explicit member lists, but the live symbol population is
larger than those lists. Confirmed omitted examples include:

- `tests/conformance/test_catalog_definition_join.py`, which calls the live builder with the
  deleted lowering flag;
- `tests/unit/test_occurrence_roundtrip_parity.py`, which calls the same public builder;
- `tests/conformance/test_constraint_catalog_determinism.py`,
  `test_diagnostic_screen.py`, `test_factory_calc_usage.py`, and `test_sanitize_invariance.py`;
- `tests/unit/test_hygiene_tail_agg_compile.py` and `test_matcher_fixes_item7.py`; and
- `tests/fixtures/golden/calc_def_compilation_golden.json` and
  `calc_compat_parity_golden.json`, both affected by the Fusion Tea formal renames.

`TEST-07` is a catch-all category rather than an explicit population. Production rows such as
`PROD-04` through `PROD-06` combine virtual-usage creation, binding repair, aggregation,
backtracking, signatures, and phantom detection under partial-file phrases such as “legacy
portions.” Those responsibilities do not share one independent oracle or necessarily one final
symbol owner. The agentic-mbse closure step is described as “analogous symbol scans” instead of
recording exact commands and results.

Several residue gates are also not executable as written:

- `NR-01` through `NR-05` require `rg` exit 1 while the static absence test must contain the banned
  symbol literals, so the command will find its own oracle unless that path or literal encoding is
  explicitly excluded.
- `NR-05`'s single regular expression cannot prove that two alternative functions in different
  files or lines do not coexist.
- `NR-09` promises a backreference-capable checker but does not name the command or script.

**Required correction:** generate a sorted inventory for both repositories and compare it to a
machine-readable census allowlist. Use a stable unique key of repository, path, symbol or command,
and responsibility. Split grouped rows when members have different owners, dispositions, or
independent oracles. Record exact agentic commands. Replace self-matching residue regexes with a
scanner that excludes only the encoded static-oracle literals and fails on every real import,
export, definition, call, or script entry. Preserve row IDs when expanding them with child IDs.

### DR-F7 — F26 still lacks an independent literal oracle

The spec requires the old live-oracle assertion to become independently pinned public names and
stable IDs. The census maps F26 to `CUT-V6-03` plus absence. Route parity compares three products of
the same new authority; it can preserve a shared naming or ID defect. Absence proves deletion, not
the expected public surface.

**Required correction:** add a dedicated F26 replacement that freezes the exact expected
`wi014_toy` parameter-group name, public source keys, output aliases, and constraint IDs as literals
derived from the reviewed model/ADR contract. It must not execute the old builder. Keep route parity
and static absence as separate proofs.

### DR-F8 — Fusion Tea fallout needs complete explicit migration rows

The 15 D-5 renames are internally consistent: seven IFE LCOE formals, two recirculating-power
formals, one viability formal, one reactor-cost formal, two COE formals, and two driver-cost formals.
Renaming each formal and its expression references preserves arithmetic, while module types, schema
class names, outputs, and source entry keys remain stable. The resulting population is correctly
14 v6 rows, 22 refusal rows, and one non-R7 control after the existing `fusion_tea` row changes from
refusal to v6. No 38th row is introduced.

The census nevertheless omits the two compiler golden files and does not give every direct
generated-call site its own final field-name disposition. Add them to `FIX-01`/the test census and
preserve their independent arithmetic expectations. `CUT-FT-01` should prove the exact 15 mapping;
`CUT-C25-01` and `CUT-C2-01` should separately assert the exact source node, exact positive consumer
set, and complete negative unaffected set under distinct mutations. `CUT-C19-01` remains separate
and must prove the literal `80.0` at one calculation and one constraint consumer on all three
routes. The real-TEAx LCOE is an additional end-to-end oracle, not a replacement for these structural
and arithmetic proofs.

### DR-F9 — Scale and repository gates are not yet exact commands

The real-TEAx proof is feasible and uses the correct public registry and execution surfaces. Two
gate details are incomplete:

- The design times internal “envelope construction/write” while spec R10 names
  “capture + envelope serialization <= 5.0 s.” The stock public `capture_snapshot` also loads and
  elaborates. Measure the public call against the stated threshold, with internal stage timings as
  supplemental evidence. If the intended threshold excludes load/elaboration, amend the spec rather
  than silently changing the measurement boundary.
- The repository's default pytest options exclude the `execution` marker
  (`pyproject.toml:47`). `uv run pytest tests/` therefore cannot prove `CUT-TEAX-01` or the scale
  test. Record an exact second command, exact venv/Python path, TEAx path/SHA/state, marker selection,
  and collected/pass count. A skip or deselection of either Item-7 test fails the gate.

The non-clean Ruff and mypy baselines also need executable comparison semantics. Record exact
machine-readable commands and baseline inventories, not only totals; require production Ruff and
all changed-file Ruff to be clean, no new full-tree Ruff identity, no mypy error in a changed file,
and no new mypy error identity after accounting for deleted files. Run the exact commands in both
repositories and record the intended licensed selection separately from the default suite. These
are local gate corrections if the thresholds and repository scope remain unchanged.

---

## Issues by Severity

### Critical — must address before implementation

- **DR-F1:** `PipelineContext` permits a mismatched or later-diverged `ComputationGraph`, so the
  claimed sole authority is unenforced.
- **DR-F2:** the manifest can bind bytes other than those parsed and lacks complete document-set and
  freshness semantics.
- **DR-F3:** the QN adapter has no final disposition and still performs an alternate association.
- **DR-F4:** preparatory-state exclusion and owner acceptance are not mechanically bound to the
  exact final two-repository candidate.

### Major — must correct before plan approval

- **DR-F5:** the nested v6 schema and projector compatibility-marker responsibility are not exact.
- **DR-F6:** the closed census omits confirmed callers/tests/goldens, groups divergent
  responsibilities, and contains residue commands that cannot meet their stated exit contract.
- **DR-F7:** F26's replacement remains same-authority parity, not independent literal evidence.
- **DR-F8:** Fusion Tea's arithmetic goldens and direct generated-call fallout are not fully
  enumerated, although the 15 mappings and 14/22/1 manifest arithmetic are correct.
- **DR-F9:** the performance measurement boundary, execution-marker command, and non-clean
  Ruff/mypy comparisons are not mechanically fixed.

### Minor

- None. The remaining issues affect authority, certifiability, proof independence, or closure.

---

## Required Corrections in Priority Order

1. Redesign `PipelineContext` construction and lifetime so the computation graph is provably the
   selected projection of the exact instance graph.
2. Specify race-free source capture and exact reproducible document-set/freshness semantics.
3. Choose the final QN-profile disposition and migrate every agentic caller/export to one
   association owner.
4. Bind owner acceptance and paired-repository atomicity to one immutable candidate identity, and
   mechanically prevent preparatory states from release.
5. Publish the complete typed v6 schema and semantic-marker bump rules.
6. Regenerate the two-repository census from exact commands; split grouped responsibilities and
   repair residue gates.
7. Add the literal F26 oracle and complete Fusion Tea golden/caller rows while keeping C19, C2,
   C25, and real-TEAx proofs independent.
8. Pin the public capture timing boundary, execution-marker command, and baseline-diff gate
   semantics.

## Rereview Boundary

**Material changes requiring design rereview:** DR-F1 through DR-F4. DR-F5 also requires rereview
if it adds or changes a compatibility marker rather than documenting the existing certifiability
profile's scope. DR-F9 requires a spec amendment and rereview if the 5-second threshold is redefined.

**Localized, objectively verifiable corrections:** an exact nested schema without changed
semantics; census expansion and unique-row checks; residue scanner repairs; the F26 literal test;
Fusion Tea golden/caller enumeration; explicit execution and quality-gate commands; and the already
correct 14-v6/22-refusal/1-control manifest count. A focused follow-up may close these without a
full architecture review if no new disposition or contract conflict appears.

## Resolutions

None recorded. This is an independent non-interactive review. The reviewer did not modify the
design, census, spec, product-lens ledger, or production code.

---

**Overall: Revise**

**Next Steps:** Return to the design agent and point it at this review. Amend the design and census,
then rerun `my-design-review` for DR-F1 through DR-F4 and any material branch of DR-F5/DR-F9. The
localized corrections may use focused objective verification. Do not proceed to implementation
planning until the material findings are closed.
