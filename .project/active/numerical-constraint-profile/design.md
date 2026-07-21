# Design: Numerical Constraint Executable Profile

**Status:** Approved (revised per design-review.md; M2 containment rule and M6 location
fallback ratified by owner, 2026-07-18)
**Owner:** Reid W
**Created:** 2026-07-18 08:55 PDT (revised 2026-07-18)
**Branch:** constraint-exec-epic (commit 036ec39 + uncommitted remediation)
**Epic:** CONSTRAINT-EXEC — Item 3 contract correction (coordinated pair: agentic-mbse + sysml-codegen)

## Overview

Narrow the executable profile to numerical validity predicates and replace the single BLOCK-halts
outcome with the owner's three-way rule: an admitted numerical claim must execute; a malformed
numerical claim is a generation error naming its fix; a non-numerical statement warns in both
tools, stays visible in the catalog, and never prevents generation.

## Related Artifacts

- **Spec:** `.project/active/numerical-constraint-profile/spec.md` (Reviewed 2026-07-18; the
  three-way rule is owner-resolved; ratified `[INFERRED]` items remain challengeable per
  capture-fidelity — M2 below exercises exactly that)
- **Spec review:** `.project/active/numerical-constraint-profile/spec-review.md`
- **Design review:** `.project/active/numerical-constraint-profile/design-review.md`
  (this revision addresses M1–M6, m1–m6)
- **Triggering audit:** `.project/active/constraint-exec-code-quality-remediation/audit.md`
  (findings 1–2) and its design addendum D5 (owner-ratified direction)
- **Prior profile contract:** `../agentic-mbse/.project/completed/20260713_executable-profile/design.md`
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  (Design Principles 4–5; executable-profile paragraph)

## Research Findings

- **The profile is one pure module with a closed walk.**
  `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py` (722 lines):
  `evaluate_profile` → per-usage form gate → predicate resolution → recursive
  proposition/value walk → operand-fact gates (`classify_equality`, `unit_compatibility`,
  `_derive_arithmetic_fact`). Diagnostics accumulate per usage; outcome is 3-valued. Every seam
  the new rule needs already exists; nothing new is extracted.
- **Codegen consumes the profile at two sites.** `lower_constraints`
  (`src/sysml_codegen/analysis/constraint_lowering.py:720-742`) pins
  `PROFILE_SEMANTIC_VERSION == "executable-profile/v2"` and halts on any BLOCK; its non-ADMIT
  loop (`:748-776`) already catalogs a defensive `ConcreteConstraint(eligible=False)` per
  usage. `collect_bare_actual_demand` (`constraint_lowering.py:405-440`) also calls
  `evaluate_profile` as a read-only ADMIT filter — safe under a fourth outcome (non-ADMIT is
  skipped) but part of the consumer inventory. The current BLOCK formatter (`:729-736`) emits
  identity + location + construct + reason and **omits** `EligibilityDiagnostic.message`.
- **There is exactly one profile-version pin.** The snapshot loader's skew guard
  (`snapshot/loader.py:199-212`) pins the constraint-facts and expression-IR *schema* versions;
  it references `PROFILE_SEMANTIC_VERSION` only in a comment. Both live and from-snapshot
  routes reach the real behavior gate through shared `lower_constraints` — snapshots store
  facts, and decisions are always recomputed at load by the installed profile, so capture-time
  profile semantics are irrelevant by construction.
- **The catalog drops non-executed usages today.**
  `src/sysml_codegen/generation/constraint_catalog.py:79` filters `eligible=False` out of
  `concrete_entries`; `source_records` (`:80-86`) are definitions-only. A non-executed asserted
  usage reaches no generated artifact — SC 5 requires a catalog extension.
- **Lowering has a third non-execution route.** The `eligible=False` branch fires for profile
  non-ADMIT *or* owner kind outside `part_def`/`calc_def`/`package`
  (`constraint_lowering.py:752-754`) — a profile-ADMIT usage under an unsupported owner kind is
  excluded with no kind or diagnostics today. Exclusion must be totalized over all three
  causes.
- **Validation consumers.** L4 counts (`level4_constraints.py:64-76`; rate denominator is
  currently admitted+blocked); L6 warns per blocked construct (`level6_architecture.py:600-641`)
  and **already fails the level on any ERROR-severity issue** (`level6_architecture.py:953`) —
  the D4 parity mechanism needs no new gating.
- **Warning channel.** Codegen's established surface is `logger.warning`
  (`orchestration/pipeline_builder.py:90-91` and five more sites).
- **Companion dependency shape.** `pyproject.toml` requires `agentic-mbse>=0.1.0` with a local
  editable uv source — a version floor, not an exact pin; exact-revision evidence is a
  discipline, not a lockfile (see D3).
- **Frozen golden.** `../agentic-mbse/tests/fixtures/constraint_fact_shapes/golden.json` is the
  S1 oracle, never regenerated; its `decision` codes are v1/v2 truth that v3 deliberately
  changes — tests re-anchor without editing the frozen file.
- **Fixture disposition census (2026-07-18, both repos).** Walked-equality asserts in committed
  codegen fixtures: exactly one — `constraint_blocked_profile/model.sysml:18` (`value == 5.0`,
  real equality; blocked today, blocked under v3 — no family flip). `catf_mfe`'s equality and
  feature-chain constraints (`designs/catf_mfe/radial_build.sysml:605-630` etc.) are plain
  non-asserted usages — form-gated UNASSESSED before any walk, unchanged under v3. agentic-mbse's
  `type_units.sysml` is the frozen S1 profile-test fixture (D8's re-anchor territory). **No
  committed fixture changes family under v3.** Catalog *payloads* do change wherever constraint
  facts exist (catf_mfe included) once excluded-records land — a versioned re-capture, not a
  behavior flip.
- **Compiler side is already cured for the surviving matrix** (parent remediation worktree:
  quantity references and the full ordering/arithmetic matrix compile). This item only narrows.

## Core Concept

The profile stays a whitelist decision procedure; what changes is that "not admitted" stops
being one fate and becomes two, decided by **provable intent**. A statement that contains a
numerical claim anywhere — an ordering or arithmetic node, or equality/`!=` touching a
numerical-category operand — is a *numerical statement*: if it is not fully admitted, the
author reached for this executor and missed, so it is malformed and generation errors, naming
statement, construct, and fix. A statement that is provably free of numerical claims —
equality/`!=` over Boolean/string/enum operands, `xor`/`implies` over such terms, a bare
Boolean assertion — is a valid statement outside this executor's purpose: it warns in both
tools, is cataloged as a non-executed record, and never stops the build. Anything the facts
cannot prove non-numerical defaults to error — default-deny governs *force*, not just
admission.

No new mechanism is needed: a fourth outcome value and a force axis on the diagnostics the
walk already emits. Codegen's defensive `eligible=False` cataloging already carries every
non-executed usage to lowering; the two genuine gaps are that the catalog then drops those
records (so it gains an excluded-record projection) and that exclusion causes are not total
(so exclusion becomes one validated payload covering all three routes). The change is
semantic, so it ships as `executable-profile/v3` behind the single existing behavior gate in
shared lowering.

## Key Bets

- **B1. The landed operand facts suffice to *prove* the absence of numerical claims** —
  operand categories at equality/`!=`, node kinds, and connective operators decide every
  warn-vs-error call without new extraction. *If false → some valid non-numerical statement
  defaults to error (default-deny): safe but noisy, and the fact schema must grow.*
- **B2. The census method caught every family-relevant fixture shape.** The 2026-07-18 census
  (Research Findings) found no family flips; the residual bet is census completeness. *If
  false → the byte-identity/baseline gates trip on an unexpected flip, which is then
  re-captured with justification, never silently regenerated.*
- **B3. Within these two repos, the profile's consumers are exactly the four censused sites**
  (L4, L6, `lower_constraints`, `collect_bare_actual_demand`), each updated in this change.
  The claim is scoped to in-repo consumers; the v3 pin protects only the guarded
  `lower_constraints` gate, and no protection is claimed for external users of the public
  API — the version bump is their notice. *If false → an in-repo match on the 3-value enum
  silently mishandles NON_NUMERICAL; mitigated by the consumer census + exhaustive dispatch.*

## Key Decisions

- **D1. Fourth `Eligibility` value `NON_NUMERICAL`, carrying warning diagnostics.**
  BLOCK keeps meaning exactly "generation error"; UNASSESSED keeps meaning "non-assert form,
  never walked" — resolving spec Open Q 1 without overloading either label. *Rejected:*
  routing non-numerical to UNASSESSED with a new kind (overloads a word that today implies
  "zero diagnostics, form-gated"); a severity field on BLOCK (leaves "BLOCK sometimes halts"
  ambiguity).
- **D2. Force is decided by numerical-claim containment, error-dominates-warn.**
  *Ratified by owner, 2026-07-18 (review M2).* A predicate is a **numerical statement** iff it
  contains, at any depth, an ordering comparison, an arithmetic node, or an equality/`!=`
  with any operand of category integer/real/quantity (or any unprovable operand: unresolved,
  unknown, construct-blocked). A numerical statement that is not fully admitted → BLOCK, with
  each failing construct's diagnostic at error force. A statement containing **no** numerical
  claim → NON_NUMERICAL (warn), regardless of connective (`xor flag`, `status == "on"`, bare
  Boolean). Consequences worth naming: `(x > 0) and flag` errors (a valid numerical claim
  would otherwise be silently unenforced); `(x > 0) xor (y > 0)` errors (numerical claims
  under an unsupported connective); `flag xor other_flag` warns. `xor`/`implies` therefore
  now walk their operands (today they stop — `executable_profile.py:565-569`) solely to
  classify containment. *Rejected:* whole-statement warn when the numerical branch is valid
  (this design's first draft — silently unenforces an intended numerical check, against the
  owner's error-leaning rule); a separate pre-classification pass (duplicates the walk;
  drift risk).
- **D3. One version gate; durable companion evidence by discipline.**
  `PROFILE_SEMANTIC_VERSION` → `"executable-profile/v3"`; the single behavior pin stays in
  shared `lower_constraints` (`constraint_lowering.py:720`), which both live and snapshot
  routes traverse; the loader keeps its existing *schema* pins and gains nothing (no
  capture-time profile semantics exist to prove — decisions are recomputed at load).
  Exact-companion-revision evidence (SC 8) is: (a) the runtime v3 assert — the durable
  consumer-environment gate; (b) an agentic-mbse version floor bump to the release carrying
  v3; (c) the exact companion commit recorded in the execution record with the companion
  suite run at that commit — the established `82fef09` discipline
  (`audit.md:dependency_baseline`). *Rejected:* a duplicate profile literal in the loader
  (drift without protection — review M4); CI/lockfile infrastructure (does not exist in this
  repo and exceeds this correction's scope).
- **D4. L6 severity splits: ERROR per malformed-numerical diagnostic, WARNING per
  non-numerical statement; L4 adds per-family counts.** ERROR already fails the level
  (`level6_architecture.py:953`) — design review parity with the codegen halt is existing
  behavior, verified; only a regression test remains for the plan. The L4 rate becomes
  **executable share of asserted constraints** = admitted / (admitted + blocked +
  non_numerical), so a model of purely non-numerical asserts reads 0%, not a vacuous 100%;
  each family also gets its own count line. *Rejected:* keep everything WARNING (model checks
  would pass a model codegen refuses); keep the admitted+blocked denominator (hides excluded
  statements).
- **D5. Codegen warning and error rendering both carry the actionable message.** One
  `logger.warning` per non-numerical statement: identity + location + its warn diagnostics
  in walk order (one warning per statement — m2). The BLOCK halt rendering is **extended**
  to append `EligibilityDiagnostic.message` per line (`constraint_lowering.py:729-736`
  currently omits it), because the fix guidance — e.g. the two-inequality band rewrite for
  numerical equality — lives in the message (spec SC on malformed claims). Live and
  from-snapshot generation share the site. *Rejected:* unchanged halt rendering (fails the
  name-the-fix criterion — review M1); a new diagnostics channel.
- **D6. Exclusion is one tagged, validated payload; the catalog projects it.**
  `ConcreteConstraint` gains a single optional nested `exclusion` value —
  `{kind: "non_numerical" | "unassessed_form" | "unsupported_owner", reasons: [ordered reason
  codes], location}` — **required exactly when `eligible=False` and forbidden when eligible**
  (model validator, extending the existing tagged-union validators and remediation
  assignment-validation). This totalizes all three non-execution routes, including the
  owner-kind route that today has no cause (`constraint_lowering.py:752-754`). The catalog
  gains `excluded_records`, a direct projection of that payload plus usage identity, source
  form, and membership kind — no second classification. Catalog fingerprints change for every
  constraint-facts-bearing fixture (catf_mfe included): a one-time versioned re-capture; SC 7
  demands behavior retention, not fingerprint identity. *Rejected:* loose parallel optional
  fields (permits contradictory records — review M5); deriving exclusion from
  `(eligible, source_form)` with no record (invisible in artifacts — fails SC 5); the full
  concept-shape source-record rework (`[CONSTRAINT-ARCH-UNIFY]`).
- **D7. No cross-tool warning dedup.** Independent reporting is what guarantees either tool
  alone reports (spec Open Q 3); duplication in a combined workflow is accepted. *Rejected:*
  a suppression handshake (can silence the only report).
- **D8. The frozen golden stays frozen; v3 gets its own answer key** mapping the golden's
  certified operand facts to v3 outcomes. *Rejected:* regenerating/editing `golden.json`.
- **D9. `!=` walks its operands and follows the same containment bucketing as `==`** (was:
  unconditional block before any operand walk). Neither ever executes; the walk only decides
  force. *Rejected:* keep the unconditional block (`status != "off"` would error while
  `status == "off"` warns — incoherent).
- **D10. Locations render when present, with an explicit `<no location>` fallback.**
  *Ratified by owner, 2026-07-18 (review M6).* `UsageDecision.location` and diagnostic locations
  are `LocationFact | None` in the schema; the halt formatter already uses this fallback
  (`constraint_lowering.py:731-735`). Warnings and excluded records do the same, and a kept
  test pins that live extraction supplies a location for every assessed assertion — so the
  fallback is a schema-honesty measure, not an expected path. *Rejected:* making location
  mandatory in the fact schema (an Item-1 schema change this correction doesn't own; would
  turn a missing location into a hard failure for otherwise-valid models).

## Architecture

One data flow; four in-repo consumers; one behavior gate:

```
ConstraintFacts ──> evaluate_profile ──> UsageDecision{ADMIT | BLOCK | NON_NUMERICAL | UNASSESSED}
        │
        ├─ L4 (agentic-mbse): per-family counts + executable-share rate (D4)
        ├─ L6 (agentic-mbse): BLOCK → ERROR (fails level), NON_NUMERICAL → WARNING, else silent
        ├─ collect_bare_actual_demand (codegen): read-only ADMIT filter — unchanged behavior
        └─ lower_constraints (codegen, v3 pin — the single behavior gate, both routes):
             BLOCK → halt, rendering message-bearing diagnostics (D5)
             NON_NUMERICAL → logger.warning + eligible=False record with exclusion payload
             UNASSESSED / unsupported-owner → eligible=False record with exclusion payload
             ADMIT → expand/resolve (unchanged)
                          ▼
        ConstraintCatalog{concrete_entries (eligible), excluded_records (projection of
                          exclusion payloads)} ──> graph ──> generation / snapshot re-lowering
```

Inside the profile, the walk's shape is untouched except that `xor`/`implies` recurse for
containment (D2); each diagnostic gains a force; `_evaluate_usage` folds forces (error > warn
> admit). `PreflightResult` gains a `non_numerical` list; `ok` remains `not blocking`. The
same-IR seam (I5 of the prior design) is untouched.

## Required Invariants

- **I1 (totality).** Every `ConstraintUsageFact` receives exactly one of the four outcomes;
  unprovable intent is BLOCK, never NON_NUMERICAL.
- **I2 (never silent, total exclusion).** BLOCK ⇔ generation halts with diagnostics whose
  rendering includes the fix message. NON_NUMERICAL ⇔ exactly one source-specific warning per
  statement in each tool that runs, plus a catalog excluded-record. Every
  `eligible=False` record carries a validated exclusion payload; every eligible record
  carries none. ADMIT ⇔ compiles and executes (totality gate).
- **I3 (numerical meaning).** The numerical domain is IEEE double (spec `[HARD]` #1); the
  admitted matrix is v2's minus all equality — no new admissions in v3.
- **I4 (equality never compiles).** No `==`/`!=` node reaches the predicate compiler from an
  admitted decision; the compiler boundary continues to reject them defensively.
- **I5 (parity).** Live and from-snapshot generation produce identical warnings (values, not
  just counts), excluded records, halts, and admitted behavior for the same model.
- **I6 (single gate).** Codegen refuses any profile version other than
  `executable-profile/v3` at the shared lowering pin; the loader's schema pins are unchanged.

## Component Overview

- **`agentic-mbse: sysml/executable_profile.py`** — force axis on `EligibilityDiagnostic`,
  `Eligibility.NON_NUMERICAL`, D2 containment classification (incl. `xor`/`implies`
  recursion, `!=` operand walk), v3 version string, updated `REASON_CODES` (equality
  `support_*` retire; warn codes + integer-equality error code arrive).
- **`agentic-mbse: validation/level4_constraints.py`, `level6_architecture.py`** — D4 updates.
- **`agentic-mbse: tests`** — v3 answer key over the frozen golden (D8); containment/force
  tests (mixed predicates, connective recursion, default-deny); import hygiene.
- **`sysml-codegen: analysis/constraint_lowering.py`** — v3 pin; NON_NUMERICAL branch
  (warning + exclusion payload); message-bearing halt rendering; unsupported-owner exclusion.
- **`sysml-codegen: resolution/models.py`** — the exclusion payload model + the
  eligible⇔exclusion validator; `ConstraintCatalog` excluded-record model.
- **`sysml-codegen: generation/constraint_catalog.py`** — project exclusion payloads into
  `excluded_records`; fingerprint payload gains the key.
- **`sysml-codegen: tests + fixtures`** — non-numerical fixture (generates, warns, catalogs,
  snapshot-parity on values); malformed-numerical fixture (halts naming the fix);
  constraint-bearing fixture re-capture; non-constraint corpus byte-identity.

## Non-Goals

- Typing the generated data path; executing non-numerical assertions; tolerance semantics.
- The concept-shape per-usage source-record catalog rework (`[CONSTRAINT-ARCH-UNIFY]`).
- Inline owner-reference wiring, model-lifetime invariants, package verification — parent
  remediation findings 3–5.
- Fact-schema changes (mandatory locations, new operand facts).
- CI/lockfile dependency infrastructure.

## Implementation Notes

- **Force lives on the diagnostic** (`force: "error" | "non_numerical"`), not in string
  prefixes; exact new reason-code spellings and message texts are plan-stage, but the
  equality-error message **must** name the two-inequality band rewrite and the integer
  message must name the float-path reason (D5 renders them).
- **`classify_equality` keeps its name, changes contract:** never returns `support_*` in v3.
- **Bare-Boolean proposition split:** a proposition-position leaf warns only when its operand
  fact proves `category == "boolean"`; every other category stays error.
- **Containment classification (D2)** can be computed during the existing walk (does this
  subtree contain an ordering/arithmetic/numerical-equality node?) — no second traversal.
- **Aggregation (m2):** one `logger.warning` per NON_NUMERICAL usage, reasons in walk order;
  one excluded record per usage, `reasons` ordered identically — deterministic across routes.
- **Fixture re-capture** follows the byte-identity discipline (timestamp-only diff check;
  `byte-identity captured_at churn` memory); catf_mfe baselines change by catalog payload
  only — diff must show excluded-records additions and nothing else.
- **Coordinated-pair order:** agentic-mbse v3 first; codegen re-pins and lands against the
  exact companion commit, recording it per D3(c).

## Potential Risks

- **Golden re-anchor churn** — v2 golden-driven tests fail wholesale until the v3 answer key
  lands; sequence profile edit + tests in one commit.
- **L6 ERROR flips existing models** — only malformed-numerical shapes, which codegen would
  refuse anyway; any validation fixtures carrying them need updating.
- **Enum-widening misses a match site** — mitigated by B3's census (four sites, all updated)
  and exhaustive dispatch where possible.
- **catf_mfe baseline churn is broad** — catalog fingerprints shift across the corpus's
  constraint-bearing fixtures; the re-capture diff discipline (Implementation Notes) is the
  containment.
- **Warn-family narrowness** — default-deny may error on statements an author meant as
  harmless annotations (e.g. mixed `and flag`). Deliberate (owner's error-leaning rule);
  any later warn↔error move is a semantic change and bumps the version again.

## Integration Strategy

Replaces the v2 halt-on-any-block contract at its four existing consumer seams; adds no new
entry points. The parent remediation's compiler-parity work becomes the totality gate for the
narrowed matrix; its finding-2 conflict dissolves (no non-float category admitted). Addendum
D5 is discharged by this item; findings 3–5 remain the parent's. Ships as one coordinated
pair of branches under the epic-branch discipline.

## Validation Approach

- **Profile matrix:** v3 answer key over every golden operand-fact row + containment/force
  tests: `(x > 0) and flag` → BLOCK; `(x > 0) xor (y > 0)` → BLOCK; `flag xor other` →
  NON_NUMERICAL; malformed numerical branch under a warn connective → BLOCK; `!=` bucketing;
  bare-Boolean split; default-deny unprovables. Import hygiene, `python -O`.
- **Consumer parity:** L4 family counts + executable-share denominator; L6 ERROR/WARNING
  split + a regression test that an ERROR issue fails the level (evidence already at
  `level6_architecture.py:953`).
- **Codegen families:** malformed-numerical fixture halts, and the halt text contains the
  rewrite guidance (M1 pin); non-numerical fixture generates, warns (caplog: exact statement
  + location + reasons), catalogs an excluded record, executes admitted siblings unchanged,
  and round-trips live/snapshot with identical warning and record *values* (I5).
- **Totality gate (SC 1):** matrix-driven ADMIT → compile → generated-execution over the v3
  admitted set, extending the parent remediation's differential test.
- **Regression:** admitted-constraint fixtures retain verdicts/margins/behavior (SC 7);
  non-constraint corpus byte-identical; constraint-bearing fixtures re-captured with
  excluded-records-only diffs; companion suite at the recorded exact commit, both repos.

## Next-Stage Handoff

- **Fixed:** four-outcome vocabulary (D1); single-gate v3 versioning + companion-evidence
  discipline (D3); consumer severity + L4 denominator (D4); message-bearing rendering (D5);
  the tagged exclusion payload and its eligible⇔exclusion invariant (D6); no-dedup (D7);
  frozen-golden discipline (D8); `!=` bucketing (D9).
- **Fixed by owner ratification (2026-07-18):** D2's containment rule for mixed predicates
  (review M2) and D10's location fallback (review M6).
- **Open (plan-stage):** exact reason-code spellings and message texts; L4 metric labels;
  excluded-record field spelling; whether report coverage counts excluded records; the L6
  ERROR regression test.
- **De-risk first:** none remaining — the fixture census and consumer census are done and
  recorded above; the first implementation step is the profile's v3 answer key (it fails
  wholesale until the force axis lands, making it the natural RED anchor).

---
Next Step: `/_my_plan`.
