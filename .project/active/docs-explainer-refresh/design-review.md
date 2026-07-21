# Design Review: Docs + Explainer-Brief Refresh (post-CONSTRAINT-EXEC)

**Design:** `.project/active/docs-explainer-refresh/design.md`
**Spec:** `.project/active/docs-explainer-refresh/spec.md` (revised 2026-07-13 post spec_review)
**Review File:** `.project/active/docs-explainer-refresh/design-review.md`
**Date:** 2026-07-13

---

## Fundamental Assessment

**Sound.** The design is the right shape for the work. It introduces no new mechanism: it frames
the item as one routing decision applied per surveyed finding — *what is the correct claim at HEAD,
which surface owns it, in place or new home*. That is the minimal correct abstraction for a
docs-truth-up sweep. It is not over-engineered; the only two structural additions (a new reference
doc, a new matrix family) are each justified against the codebase's own one-concept-per-file and
family-of-REQ-rows conventions. Every home-repo claim I spot-checked against HEAD held. Proceed to
the detailed review.

The findings below are tightenings, not a redirection: one Major (the explainer bar secures
truthfulness but not buildability) and two Minor (an invariant-namespace collision that dents
audit clarity; an overstated test count). None is Rework-level.

**Code-claim verification (sysml-codegen HEAD, this session):**

- Matrix lives at `docs/architecture/verification-matrix.md`. Summary: 264 reqs / 263 PASS / 1
  UNTESTED / **31 families** / **71 test files** (`:7-14`); Index `:32-64`; CL family `:156-171`
  (5 rows + partial-register note). REQ-AST-06 `:96`, REQ-CA-02 `:144`, REQ-SNAP-09 `:506` — all
  design cites **accurate**.
- `ModuleKind` has five values; `PipelineModule.module_kind` is required and replaces the retired
  bool flags (`resolution/models.py:161-205`). **Confirmed.**
- Contracts machinery present and real: `ModelContract`/`PackageContract` (`contracts/models.py:51,92`),
  `seal_package` (`contracts/seal.py:57`), `verify_package` (`contracts/verify.py:100`), `seal` CLI.
  **Confirmed.**
- Neither `test_contract_models.py` nor `test_seal_step9.py` appears in any matrix row. **Confirmed**
  → INV-4's "+2 test files (71→73)" guidance is correct.
- `overview.md:218` says "29 requirement families" vs the matrix's 31. **Confirmed stale.**
- Doc 28's "Contracts (seam disposition)" stub is real at `28:75-80` and points at a run report.
  **Confirmed** — the D2 plan to convert it to a forward pointer is grounded.
- **All nine D1 candidate rows map to real, behavior-exercising tests** (verified below). B3 holds.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every success criterion has a discharge path in the Validation Approach, and an auditor would know
where to look — SC-1 grep, SC-2/3 presence + recount, SC-4/5/7 re-grep, SC-8 INV audit, SC-9 BACKLOG.
Provenance is carried faithfully: the settled `[OWNER]` calls (brief-only deliverable, fusion-tea
pointer-only, alias=drop) are treated as fixed, and the five delegated calls are decided with
rejected alternatives, as the brief authorized.

The one real gap is **SC-6 buildability** (Major, detailed in Dimension 3 / Issues). The design's
explainer bars secure *truthfulness* (retire caveats grep-clean, no claim contradicted by HEAD) but
do not secure *buildability* — the responsibility-map rows, reading-list data sources, and reuse
guidance the v2 HTML agent actually builds from. The spec's stated intent (Overview: "truthful,
buildable v2 brief") and review-hardest #3 both put buildability in scope; the design's audit does
not operationalize it.

### 2. Pattern Consistency
**Assessment:** Pass

The two structural additions follow existing codebase conventions exactly. D2 (new
`29-contracts-and-sealing.md`) follows the one-concept-per-file reference-doc pattern; D1 (new `CON`
family) follows the family-of-REQ-rows-anchored-to-test-files pattern and explicitly mirrors the CL
precedent — a short register with an honest "partial coverage" note (CL itself carries exactly such
a note at `:158-162`). D5 (reword retired-symbol rows in place, preserve REQ IDs) is the
count-stable choice consistent with how the matrix treats stable ID↔test mappings.

### 3. Abstraction Quality
**Assessment:** Concerns

The routing abstraction is right and earns its place. The concern is that the explainer is folded
into "the same routing applied to a generation brief" (Core Concept) and then audited only for
truth. That under-abstracts the explainer's actual structure. `EXPLAINER_PROMPT.md` is buildable
today because it carries three infrastructure pieces beyond prose:

- a **responsibility-map skeleton** (owner → one-sentence responsibility → reference-doc pointer),
- a **reading list** (ordered, concrete data-source files),
- **reuse guidance** (which Gen-1 machinery to reuse, what to treat as unverified).

"Slot the eight areas per the survey map" targets *narrative placement* (lowering phase, module_kind
as a 4th/5th family with colors, Kleene as an Act-3 hard part, ...). It does not require refreshing
that infrastructure for the new mechanisms. Concrete evidence the infrastructure is itself stale:
the brief's reading list still says "253 = 249 PASS + 4 UNTESTED, 30 families"
(`EXPLAINER_PROMPT.md:~189`) — a stale data-source claim the content-slot bar doesn't obviously
target. A brief that names the eight areas in prose but leaves the responsibility map and reading
list pointing at pre-epic docs is truthful-looking and **not buildable**: the v2 agent would not
know where to read for constraint lowering, `ModuleKind`, contracts/sealing, or doc 28/29.

### 4. Duplication Avoidance
**Assessment:** Pass

D2's rejected-alternative reasoning correctly keeps contracts out of doc 28 (coupled only by
ModelContract embedding the catalog), and turns 28's stub into a forward pointer rather than
duplicating content. D5 preserves REQ IDs rather than minting parallel renamed rows. No parallel
structures introduced.

### 5. Data Structure Clarity
**Assessment:** Pass

The Component Overview table makes surface → repo → action explicit and traceable. The five module
kinds, `constraint_catalog`, and the four contract surfaces are named against their code homes.

### 6. Route Safety
**Assessment:** Pass

INV-4 is the safety-critical route (the matrix-recount trap) and the design handles it well: recount
families / total reqs / distinct test files **from the family Index, not the summary block**, and
set `overview.md:218` equal to the recounted family count — which also sweeps up the pre-existing
29-vs-31 drift. The "+2 test files" and "families 31→32" deltas are both verified correct against
HEAD. The cross-repo route is gated by re-grep-before-edit backed by symbol-named cites; adequate.

### 7. Bets & Decisions Integrity
**Assessment:** Pass

The three bets are genuine reality-claims each with a stated "if false" and a bounded failure mode.
**B3 is verified true**, not merely asserted: all nine D1 candidate rows anchor to real tests that
exercise the claimed behavior —

| D1 candidate row | Anchoring test | Exercises the claim? |
|---|---|---|
| graph-only build | `test_model_contract_is_graph_only` | yes (patches FS to raise; build still succeeds) |
| deterministic fingerprints | `test_fingerprints_are_deterministic` | yes |
| zero-constraint seal | `test_zero_constraint_graph_seals` | yes |
| stable on-disk bytes | `test_model_contract_json_bytes_are_stable` | yes |
| three emitted files + verify-on-load | `test_generate_emits_three_contract_files` | yes |
| verbatim emitted verifier | `test_emitted_verifier_is_verbatim` | yes (byte-identity drift guard) |
| seal-excludes-itself | `test_seal_ordering_excludes_itself_from_coverage` | yes |
| re-seal recomputes only PackageContract | `test_reseal_after_stencil_edit` | yes (asserts `mc_after == mc_before`) |
| `seal` requires existing ModelContract | `test_seal_subcommand_requires_existing_model_contract` | yes |

D1–D5 each name the rejected alternative with a real reason (extend CL / absorb into 28 / full
architecture doc / BACKLOG-mention-only / re-anchor to new IDs). No mechanism choice is dressed as
a bet. No hidden bet surfaced beyond B2's already-stated cross-repo cite risk.

### 8. Reader Comprehension
**Assessment:** Concerns

The document is well-structured and a tired engineer can follow the routing model. One comprehension
defect blocks clean auditing: **the "INV-N" token means two different things.** The design's
`Required Invariants` section defines INV-1..INV-5 as inherited-history + matrix-recount bars (and
SC-8 / Validation say "audit every edited doc against INV-1/2/3"). But D1's candidate rows borrow
the **contracts machinery's own** invariant numbering — "graph-only build (INV-1)", "verbatim
emitted verifier (INV-8)" — which is a different namespace living in `contracts/*.py` and the two
test files (INV-1 = graph-only projection, INV-8 = verbatim verifier). A plan author resolving D1's
"(INV-1)" against the design's Required Invariants section lands on the wrong invariant. The
collision is contained to D1's parenthetical labels (the SC-8 audit instruction unambiguously points
at the Required Invariants section), so it is Minor — but it dents exactly the auditability this item
is graded on.

---

## Issues by Severity

### Critical
- None.

### Major
- **SC-6 secures truthfulness, not buildability.** The explainer bars (grep-clean caveats, spot-read
  no-contradiction) do not require refreshing the brief's *buildability infrastructure* — the
  responsibility-map rows, reading-list data sources, and reuse guidance the v2 HTML agent builds
  from — for the eight new mechanisms. Evidence it is stale: reading list still reads "253 … 30
  families." — Dimensions 1 & 3.

### Minor
- **INV-N namespace collision.** D1 borrows the contracts machinery's INV-1/INV-8 numbering, which
  collides with the design's own Required Invariants INV-1..5. — Dimension 8.
- **Overstated test counts.** Research Findings says `test_contract_models.py` has "10 tests" and
  `test_seal_step9.py` has "6 tests"; actual is 7 functions (8 collected — one 2-way parametrize)
  and 5 functions. The named behaviors are all real, so B3 is unharmed and D1 defers exact row
  count to the plan — but the "well-tested" narrative overstates. — Dimension 1.

---

## Recommendations

1. **Add a buildability bar to the SC-6 mechanical checklist.** Require that each of the eight new
   areas gets: (a) a responsibility-map row with owner + reference-doc pointer (including new docs 28
   and 29), (b) reading-list data sources (the new docs + `test_contract_models.py` /
   `test_seal_step9.py` for the contracts area), (c) any reuse-guidance delta. Add one concrete
   check: the reading list's matrix counts/family number match the recounted matrix (fixes the
   "253 … 30 families" staleness). This makes "buildable" auditable instead of implicit.
2. **Disambiguate the invariant references in D1.** Either label the contract-machinery invariants
   distinctly (e.g. "graph-only build (contract INV-1)", "verbatim verifier (contract INV-8)") or
   drop the parentheticals, so the design's INV-1..5 namespace stays clean for the SC-8 audit.
3. **Correct the test counts** in Research Findings to 7/8 and 5 (or restate as "the behaviors below"
   without a total), so the anchor claim is exact.

---

## Resolutions

_(Filled in during Stage 4, once the owner engages with the findings.)_

---

**Overall:** Revise
**Next Steps:** Record resolutions above, then return to the design-agent session (or re-run
`/_my_design`) and point it at this review to incorporate. The reviewer does not edit the design.
The approach is sound — these are tightenings to the explainer's buildability bar and to audit
clarity, not a redirection. After incorporation → `/_my_plan`.
