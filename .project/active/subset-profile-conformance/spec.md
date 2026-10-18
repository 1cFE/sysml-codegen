# Spec: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Complexity:** HIGH
**Branch:** `subset-conformance` (sysml-codegen base `b5663c07`; agentic-mbse sibling worktree on `subset-conformance`, base `ccd57d83`)

---

## Problem

Item 1 wrote down which SysML shapes the generator executes. The record is the shared subset contract in agentic-mbse: `src/agentic_mbse/sysml/subset_profile.py`, `SUBSET_PROFILE_VERSION = "subset-profile/v1"`, with rule records in `subset_profile_rules.toml`. In this spec, **the screen** means that contract applied to a model (`extract_subset_facts`, then `evaluate_subset_profile`), and **the generator's route** means what `sysml-codegen generate` runs: admission, extraction, elaboration, projection and generation preflight.

Item 1 checked the screen against 80 probes. A probe ran the pinned generator's public CLI once on one small model in a throwaway tree and recorded what it did. That evidence was captured once, at codegen `b5663c07`, and lives in agentic-mbse. Nothing in sysml-codegen fails when the generator changes, so a relaxed or added refusal would leave the contract stale with every test green.

Item 1 also left gaps, which the approved disposition (agentic-mbse `.project/completed/20261018_exec-subset-profile/evidence/r3-proposal.md`, owner "agreed on all", 2026-10-18) sends to Item 2, and the split gives to 2a:

- refusal families with no rule;
- rule pairs reported `unconfirmed` because nobody probed them;
- 85 raise sites with no matrix row and no stable code;
- two open generator-correctness questions (G1, G2).

The governing obligation: **[INFERRED]** (ratified by owner, 2026-10-18, spec brief and `briefs/align.md`) prove, with evidence independent of the screen, that the contract matches what this generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself.

## Success Criteria

"Pinned" means the revisions recorded in the evidence at implementation time: the sysml-codegen and agentic-mbse revisions, `SUBSET_PROFILE_VERSION`, SysIDE 0.8.4, and the imported package identity (not checkout paths). A **conformance case** is a retained model plus its expected outcomes. A **witness** for a refusal site or rule is a conformance case that shows that site or rule firing.

The criteria fall into six groups, A–F. Each group can be audited without the others.

**A. Pins, mapping and occurrence parity**

- [ ] `_upstream_pins.py` carries `SUBSET_PROFILE_VERSION`, and `tests/conformance/test_upstream_pins.py` fails when the imported value differs.
- [ ] `pyproject.toml`'s agentic-mbse requirement admits no published version that lacks the pinned contract version. The evidence states which agentic-mbse version first carries it and how that was checked.
- [ ] A codegen mapping takes each reason in `SUBSET_REASON_CODES` to the `ElaborationCode` values the generator emits for it (one-to-many allowed; a reason that is never `refused`, such as `string_value_not_generated`, maps to an explicit "no refusal" entry). A test fails if the mapping's keys differ from `SUBSET_REASON_CODES`. A test fails if any (reason, code) pair has no conformance case in which the generator emitted that code for a finding with that reason.
- [ ] Codegen renders a finding to its own diagnostic (code, the rule record's remedy text, location). Unit tests cover every reason. `generate` does not call it in 2a.
- [ ] A sysml-codegen test compares agentic-mbse's occurrence summary with codegen's occurrence index on the 34-case seed, the v6 corpus fixtures and every conformance case with instantiation, and fails on any difference. Missing inputs make it fail or report itself unrun by name. A mutation that changes one codegen multiplicity reading makes it fail.
- [ ] The ADR 0012 amendment text, taken from agentic-mbse `evidence/adr-0012-amendment-draft.md`, names this parity test in its "until Item 2 lands" invariant and is staged in this item's folder for the owner to file. The archived draft is left as it is.

**B. Shared rules against the generator's route**

- [ ] With the screen made to fail (`extract_subset_facts` and `evaluate_subset_profile` raising), every conformance case's generator half still completes. This stays true after Item 2b adds the screen to `generate`.
- [ ] For every (rule, shape, context) the records decide as `refused`, a case shows the generator refusing it. For every refused shape, a case shows a context where it is `admitted`, `omitted` or `excluded`, or the shape carries its SA-1 "no admitted context" statement and has a case for each context the rule can compute.
- [ ] Where they apply to a rule, the cases cover: inherited and redefined contexts, alternate spellings, template versus instance, and the dc3 `proto3`, `proto4nest` and `conv` shapes rebuilt as minimal retained models. A case built from an Item 1 probe names the probe ID.
- [ ] Every directory under `tests/fixtures/` is classed as generating, refusing or not a model, and a test fails on an unclassed one. On every generating fixture the screen reports zero `refused`. Where it does, the contract is narrowed and a case records the fix.
- [ ] For each refusal site that witnesses a shared rule, disabling that site in the generator makes its case report a mismatch. For each rule and shape, disabling the screen's recognition makes its cases report a mismatch. These mutation checks run in the default licensed suite.
- [ ] Every `unconfirmed` pair r3-proposal § 3 routes to Item 2 (listed in Known Requirements → R3 rows) has a case, and its record moves to the observed outcome. A pair that cannot be observed keeps `unconfirmed`, and its record gives the reason.
- [ ] `part-multiplicity/nonunique` and `part-multiplicity/negative_bound`, retired by the owner, are gone from the records and the reason vocabulary.

**C. The R3 gaps**

- [ ] Every R3 row routed to Item 2 has the closing outcome given for it in Known Requirements → R3 rows, and the evidence has one line per row.
- [ ] Every known disagreement between generator and screen (a refusal family the contract has no rule for) is recorded with its case, generator code, screen outcome and owner. A disagreement that appears or disappears without a change to that record fails a test.
- [ ] Every refusing fixture under `tests/fixtures/` and every conformance case the generator refuses ends in either a screen `refused` finding whose reason maps to the generator's code, or a recorded disagreement. A test fails on a refusal that has neither. This is the check against a model the contract calls fine and the generator refuses.

**D. Silent losses and String metadata**

- [ ] Every family in Known Requirements → Silent-loss families has a case asserting the construct's presence or absence at a semantic seam (an instance-graph node by declaration identity, a computation-graph entry point, the generated catalog or contract, or a runtime value), and a control case where the carried form is present at the same seam. A name or literal search over emitted text does not count on its own.
- [ ] Each family's case states whether today's loss is an accepted omission or a loss that should block. For a loss that should block, the contract record and the case both mark it as a candidate refusal pending RG-1, so neither reads as an accepted outcome, and a written RG-1 recommendation exists for it. The same applies to the `MANUAL_REQUIRED` stub for an unsupported operator.
- [ ] String fixtures cover both spellings (`attribute x = "…"`, `:>> x = "…"`), a String on an uninstantiated template, on an instantiated part, bound to a calc input, and read by another attribute. A recommendation for RG-2 states the options, what each does to generated output and to native consumers, and a recommended choice.
- [ ] `docs/architecture/modeling-assumptions.md` describes what the generator does today with String values, NON_NUMERICAL constraints and calc-usage bare results, citing the cases. It links POSITIONAL-FORMAL-REDEFINITION's hazard entry as pending until Item 4 supplies it, without changing that item's status.

**E. Per-site codes and the inventory**

- [ ] A sysml-codegen test scans `src/sysml_codegen/` with the site scanner's recognized forms and fails on a raise site with no account row, or an account row whose site is gone.
- [ ] The inventory test detects, or reports as unrecognized by name, a synthetic new raise of each recognized form, a new exception class, a new raising helper and a computed code mapping. The account lists the blind spots that remain.
- [ ] Every site the account classes `public_capability` (including the 39 follow-ups and the 10 naming-collision sites) carries a stable reason that tells it apart from other sites emitting the same `ElaborationCode`, per site or per justified family, and has a witness that fails when the site is disabled.
- [ ] Each of the 46 `unknown` sites is classed reachable (and then meets the previous criterion), internal invariant with a cited guard, or still unknown with a recorded attempt, an owner and a stated limit.
- [ ] A recorded rescan of both trees at the final revisions reports zero unaccounted sites and zero orphan rows, and itemizes each added or removed site with its cause.

**F. Semantics questions and baseline evidence**

- [ ] A case reproduces G2 at the pinned generator and records what it does.
- [ ] For G1 and G2, the `kerml-expert` agent (`.claude/agents/kerml-expert.md`) is asked what SysML v2 / KerML semantics require, with the case models attached. The evidence records each question, the answer, the spec sections cited, and whether the generator's current behavior agrees.
- [ ] A recorded run evaluates dc3 baseline `808464df` and repaired `60b44d53` with the 2a contract, compares the findings with Item 1's `evidence/acceptance.md`, and itemizes each difference with its cause. The generator still generates dc3 repaired at the 2a codegen revision.
- [ ] `pytest`, `mypy` and `ruff` pass in both repositories by each repository's commands. The evidence comes from a run with `SYSIDE_LICENSE_KEY` set, lists skips, and names checks not run.

## Known Requirements

### Gates

- **[NEED]** (owner, 2026-10-18, `briefs/align.md`) RG-1: any change to what the generator accepts or refuses, including a G1/G2 fix after the `kerml-expert` check, is the owner's decision.
- **[NEED]** (owner, 2026-10-18, `briefs/align.md`) RG-2: String metadata policy (epic open decision 3) is the owner's decision. 2a brings fixtures and a recommendation.
- **[NEED]** (owner, 2026-10-18, `briefs/align.md`) RG-3: merges, PRs and filing the ADR 0012 amendment are the owner's.
- **[INFERRED]** Where an outcome in this spec needs an RG-1 change, 2a records the question, the evidence and a recommendation, and pins today's behavior in a case that an approved fix would flip on purpose. No other requirement depends on the answer. Reason: the spec brief asks that the rest of the spec stay independent of RG-1.
- **[NEED]** (`.project/product/0003-no-workarounds-for-bad-models.md`, owner-verbatim 2026-08-16: "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support") Recommendations on G1, G2 and losses that should block follow what KerML, SysML v2 and SysIDE support.
- **[INFERRED]** Correcting the contract to match the generator is not RG-1. That covers adding a rule, moving an `unconfirmed` pair to its observed outcome, narrowing an overbroad rule and removing the retired shapes. Each changes what the screen reports, not what the generator does. Such changes land in agentic-mbse with a `SUBSET_PROFILE_VERSION` bump, and codegen's pin moves in the same coordinated merge (`.project/adr/0008-cross-repo-merges-use-merge-commits.md`). Reason: R3 routed the rule decisions here, and the contract exists to describe the generator.
- **[INFERRED]** A stable site-level reason added to a diagnostic is not RG-1, provided every refusal keeps its current `ElaborationCode` and the same models are refused. Reason: RG-1 governs accept/refuse, and consumers keyed on today's codes keep working. Any changed golden output is listed in the evidence.

### Independence

- **[INHERITED: epic Design principle 3]** Conformance compares the screen with the generator's underlying route with the screen bypassed. An annotation or an early-screen refusal is not proof of equivalent behavior.
- **[INFERRED]** The generator half of a case runs the same route users run, with no stage reimplemented in tests. Reason: a test-only path could diverge from the real one.
- **[INFERRED]** Expected outcomes are fixed in reviewed artifacts, not computed from the screen or the generator at test time. Reason: this is what keeps the comparison from being circular.
- **[INHERITED: epic Item 2a scope 3]** Naming a rule does not establish coverage. Each relevant condition needs a witness, and a mutation that disables its detector must fail conformance.
- **[INHERITED: agentic-mbse `.project/adr/0001-subset-profile-capability-ownership.md` invariant 5]** After Item 2, ground truth for the contract is Item 2's independent corpus, not the pinned generator's one-time probes. Each record outcome therefore rests on a 2a conformance case; Item 1's 80 probes remain historical evidence and are not a second live authority for the same record.
- **[INFERRED]** A license-gated test counts toward a criterion only if the evidence shows a licensed run in which it ran. Reason: those tests skip, not fail, without the key (`CLAUDE.md`).

### Boundaries

- **[HARD]** agentic-mbse never imports sysml-codegen or its types: sysml-codegen already depends on agentic-mbse, so the reverse import would be a cycle (`.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`; agentic-mbse ADR 0001). Whatever codegen takes from agentic-mbse comes through its package, not its `tests/` tree.
- **[INHERITED: epic Item 2b]** 2a does not adopt the screen inside `generate`, add a `check` command, factor the read-only preparation path, or do snapshot authority, receipt, upgrade or skew work.
- **[INHERITED: epic Item 1 Out of Scope]** No new language support.
- **[INHERITED: epic evidence revisions]** Consumer models (dc3, fusion-tea) are read from isolated exports at pinned revisions; consumer checkouts are not changed.
- **[INFERRED]** Item 1's dev scripts in `scripts/subset_profile/` are reused only after their evidence output path is a parameter; nothing writes into the archived Item 1 folder. Reason: the archive is a closed record (spec brief).
- **[INFERRED]** The occurrence parity comparison uses one normalizer, and each codegen site has one editable account row. Reason: two copies that can drift would be another unguarded drift surface, the thing this item removes.

### R3 rows

The closing outcome for every row r3-proposal §§ 2–4 routes to Item 2. The routing is **[INFERRED]** (ratified by owner, 2026-10-18, r3-proposal "agreed on all"); the closing outcomes are **[INFERRED]** unless marked.

The **rule criterion** is **[INHERITED: Item 1 spec § Which candidates become evaluator rules]**: the generator shows a refusal branch whose reaching contexts can be stated, and the facts can be extracted from shared agentic-mbse facts without a heuristic. A rule reports `refused` only where a case has observed it. A **reproduced gap** is a refusal with a stable codegen reason, cases and a recorded disagreement entry (criterion C).

| Row | Today | Closes as |
|---|---|---|
| ES-002: constraint binds a calc usage's input | Reproduced, `SI_OCCURRENCE_MISSING`; site `occurrence.py:180` is wider than the shape | Rule if the criterion holds, else reproduced gap. Cases include the admitted neighbor (binding a calc output) and the site's other reaching shapes |
| ES-008: nested named subsets each redefining a value | Reproduced in 1 of 5 spellings, `SI_REDEFINITION_INVALID` | Same choice; cases for all five spellings and plain nesting as admitted control |
| ES-009: composition by subsetting a top-level usage | Reproduced, `SI_OCCURRENCE_MISSING`; site `elaborate.py:2345` wider than the shape | Same choice; cases include the site's other reaching shapes |
| ES-010 refusal side: String reaching an entry-point input | Reproduced on one path, `SI_RENDERING_COLLISION`; contract says `omitted` | Reproduced gap with a codegen-owned reason, cases for each of the three projection entry paths. Not a shared rule: entry-point membership is an output fact codegen owns (ADR 0007, Item 1 design D11). Policy is RG-2 |
| ES-011: arithmetic on a named calc return | Reported once, not reproduced, site not located | Reproduced gap, or retired with admitting cases for `return r` and `out attribute r` as evidence |
| CALC-DEF-BARE-RESULT | Reproduced, `SI_EVIDENCE_INCOMPLETE` "zero output attributes" | Rule if the criterion holds, else reproduced gap with its own reason. Cases for arithmetic, `max` and conditional bare results |
| CALC-USAGE-BARE-RESULT-DROP | Silent; reported `omitted` only for the three site rules' shapes | The contract reports every calc-usage bare result `omitted` if the criterion holds, else deferred with the limit stated. Making it refuse is RG-1 |
| DEEP-QUALIFIED-WIRING | Generator refuses `deep_cross_scope_probe`; contract says CLEAR | Reproduced gap, no rule: producer existence needs codegen's output wiring, which the contract does not model. Implementation stays sysml-codegen [DEEP-QUALIFIED-OUTPUT-WIRING] |
| G1: redefinition without bounds expands to one occurrence, loses `ordered` | Admitted, `fx__rack__servers__t__r` | Pinned current behavior plus the recorded `kerml-expert` finding. Any fix is RG-1 |
| G2: usage override of a definition-owned referenced bound ignored | Code-read only | Probe, then as G1 |
| `unconfirmed` pairs: `binding-source/expression_source` at `owner_other`; `self_reference_source` at `owner_other`, `writer_overridden`; `conditional_resolved_branches` everywhere; `calc_result_expression` for `conditional-expression`, `indexed-reference`, `invocation-callable`; `constraint-predicate/blocked_predicate` at `owner_other`; `non_numerical_predicate` at `owner_other`, `owner_package`, `owner_uninstantiated` | `unconfirmed` | Observed outcome, or `unconfirmed` with the reason recorded (for example, `calc_result_expression` is refused first by CALC-DEF-BARE-RESULT, `owner_other` constraints first by ES-001) |
| `part-multiplicity/nonunique`, `negative_bound` | **[NEED]** (owner, 2026-10-18, epic Item 1 status "retiring the unprobeable `part-multiplicity/nonunique` and `negative_bound` shapes") retired; still in the records | Removed |
| `beyond_generator_roots`, `beneath_refused_multiplicity` | `unconfirmed` by design | Unchanged; presentation is Item 3's |
| 85 follow-up sites | Inspected, no row | Per criterion group E |
| PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS | Candidate sites of unknown role: `reference_use.py:545, :557, :594, :618`; `binding_source.py:236, :243, :251` | Each site classified (group E); the row goes to Item 3 with the verdicts |
| PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR | An unsupported operator in a calc def output becomes a `MANUAL_REQUIRED` stub (`calc_compat_renderer.py:115, :120`) | Pinned current behavior plus a refuse-vs-stub recommendation; refusing is RG-1. Row goes to Item 3 |
| PUSH-DOWN-AGG-PROFILE-SUM-SHAPE | One candidate site, `project.py:812`, unknown role | Site classified, with a case if reachable. Row goes to Item 3 |
| PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE | No site located | `sum(5.0)` probed: reproduced gap or admitted with a case. Row goes to Item 3 |
| PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE, -AMBIG-INHERITED-ATTR | Item 3 rows waiting on Item 2 to publish precedence and type selection | Published as pinned cases plus a written statement of which value wins and which typing is chosen. Turning them into shared agentic-mbse facts is Item 3's |

Rows R3 routes elsewhere (Items 3–6, the agentic-mbse backlog, `L6-LIBRARY-ALIAS-SOURCE`, the `sump_pump` nondeterminism) get no 2a work.

### Silent-loss families

**[INFERRED]** (ratified by owner, 2026-10-18; epic Item 2a scope 4, `briefs/align.md`) The requirement covers the known families below. A general detector for unknown losses is a recorded limit, not an acceptance gate, because name search over output is not a strong enough oracle. A family found during the work joins the table.

| Family | Loss | Today | Control |
|---|---|---|---|
| ES-010 String values, both spellings | String attribute absent from generated output | Accepted omission, policy open (RG-2) | Numeric value on the same feature |
| CALC-USAGE-BARE-RESULT-DROP | Calc usage's bare result never examined | Silent; candidate must-block (RG-1) | Same usage without a bare result |
| ES-007 NON_NUMERICAL constraint | Constraint left out of the generated contract | Accepted exclusion | Numeric constraint in the catalog |
| G1 | Bounds and `ordered` dropped; one unindexed occurrence | Silent; semantics question (RG-1) | Redefinition with explicit bounds |
| G2 | Usage override of a referenced bound ignored | To be probed | Bound with no override |
| PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR | Calc def output not executed | Handwritten stub (`MANUAL_REQUIRED`) | Supported operator, compiled |

## Non-Goals

- Deciding RG-1, RG-2 or RG-3 questions.
- L6 wiring, severity, execution-target settings or any change to `agentic-mbse validate` output (Item 3); the positional-binding check, hazard register and subtraction counterexample (Item 4); rendering `docs/patterns/generator-subset.md` or correcting shipped examples (Item 5).
- Converting `ElaborationCode` into per-site enum members; epic scope 3 says not every exception needs a new enum member.
- Re-verifying the 154 internal-invariant guards Item 1 cited, except where 2a changes the code or finds a guard broken. This is a recorded limit.

## Open Questions / Deferred to design

- **How expectations are stored:** one directory per conformance case with its model and an expectation file, or a table; and the schema.
- **How detectors are disabled:** in-process replacement or another means. The criterion is that each mutation is tied to one named detector and runs in the default licensed suite.
- **The form of the disagreement record** (criterion C).
- **Whether the generator half calls `run_codegen` or its stage functions in order.** Either satisfies "same route, no stage reimplemented".
- **Which seam each silent-loss family is asserted at.**
- **Where the occurrence parity seed and normalizer live:** promoted into agentic-mbse's package, or copied into sysml-codegen with a recorded content hash.
- **Whether the codegen half of `site_account.csv` moves to sysml-codegen.** If it does, agentic-mbse's matrix tests read a frozen copy.
- **How the stable site-level reason is spelled and carried,** and whether it renders.
- **How agentic-mbse records cite conformance cases.** The records' loader validates `probe:` citations inside agentic-mbse, and a citation into sysml-codegen's test tree cannot be checked there. agentic-mbse ADR 0001 invariant 1 names only probes and corpus snapshot fixtures as evidence, so it may need an amendment; filing it is the owner's (RG-3).
- **How a record marks a loss as a candidate refusal pending RG-1.** `omitted` alone cannot say it; the existing `Qualification` field (`subset_profile.py:235`) is one place it could go.
- **Rule or reproduced gap** for ES-002, ES-008, ES-009 and CALC-DEF-BARE-RESULT, decided per row by the rule criterion once the cases exist.
- **Whether the package requirement needs an agentic-mbse version bump.**
- **ADR 0012 filing time has passed (surfaced, not resolved).** The amendment draft's ratified filing time is "when Item 1 merges"; Item 1 merged (PR #30) and the amendment is not filed in `.project/adr/`. Filing stays RG-3; criterion A only stages the text.
- **Group order and effort, deferred to plan.** Groups C, D and E each need B. F needs C, D and E. The carried estimate is 17–27 engineer-days (epic; agentic-mbse `evidence/re-estimate.md` minus the preparation-path and snapshot line). It is an `[AGENT]` figure and challengeable. Most of its uncertainty is in group E: each unknown-role site found reachable adds a reason, a witness and a mutation.

---

## Related Artifacts

- **Epic:** agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2a (with Design principles, Success Criteria, Items 2 and 2b, Owner decisions)
- **Required Reading:** the epic lists none for Item 2a.
- **Align record:** `briefs/align.md`; spec brief: `briefs/spec.md`
- **Item 1 archive** (agentic-mbse `.project/completed/20261018_exec-subset-profile/`): `spec.md`, `design.md`, `evidence/r3-proposal.md`, `evidence/re-estimate.md`, `evidence/matrix.md`, `evidence/site-reconciliation.md`, `evidence/acceptance.md`, `evidence/adr-0012-amendment-draft.md`
- **agentic-mbse code and fixtures:** `src/agentic_mbse/sysml/subset_profile.py`, `subset_profile_rules.toml`; `tests/fixtures/subset_profile/{probes,inventory,occurrence}/`; `tests/helpers/occurrence_oracle_schema.py`; `scripts/subset_profile/`
- **sysml-codegen:** `src/sysml_codegen/_upstream_pins.py`, `src/sysml_codegen/elaboration/diagnostics.py`, `tests/conformance/test_upstream_pins.py`, `tests/conformance/test_public_diagnostic_totality.py`, `tests/conformance/test_diagnostic_provenance_sites.py`, `tests/fixtures/v6_recapture_batch/batch.json`, `docs/architecture/modeling-assumptions.md`, `.project/adr/0012-exclusive-semantic-evidence-ownership.md`, `.project/product/0003-no-workarounds-for-bad-models.md`
- **Product-lens:** `product-lens.md`, latest block 2026-10-18: gate DISPOSED (spec-F1, spec-F2, spec-F3, all fixed in this spec)
- **Design:** `design.md` (to be created)

---

**Next Steps:** After approval, `/_my_spec_review` in a fresh session, then `/_my_design`.
