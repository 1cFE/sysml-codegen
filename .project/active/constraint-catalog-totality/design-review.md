# Design Review: Canonical Usage Domain and Catalog Totality

**Design:** `.project/active/constraint-catalog-totality/design.md`
**Spec:** `.project/active/constraint-catalog-totality/spec.md` (reviewed; 11 findings resolved)
**Brief:** `.project/active/constraint-catalog-totality/briefs/design.md`
**Review File:** `.project/active/constraint-catalog-totality/design-review.md`
**Date:** 2026-08-12
**Epic:** CONSTRAINT-SEMANTICS, Item 2 · Branch `item7-rebuild` · Git `bb5e1b4`

---

## The Point

Constraints are how these models enforce physics, which is what keeps design search viable. The
lifecycle contract already promises that every authored constraint usage stays visible with exactly
one disposition (invariants 1 and 28). The exact route does not keep that promise, and the reason is
structural rather than a missing check.

Records only begin *after* owner-to-scope expansion. `_build_constraint_nodes`
(`elaboration/elaborate.py:997`) enumerates every `ConstraintUsage` and emits one node per scope
returned by `_scopes_for_owner` (`:522-539`); a usage whose owner yields zero scopes emits nothing at
all. On `catf_mfe_d5` that means 65 authored usages produce 9 catalog carriers. The other 56 — 51
owned by a `calc def` (no branch in `_scopes_for_owner`), 5 owned by a `part def` whose design parts
are untyped — are simply absent. Not eligible, not excluded, nothing.

Because every downstream artifact descends from that already-truncated set, a totality gate written
against today's data would compare two projections of the same truncation and pass. So the fix has
to move the birth point of the record, not add a check. Until it does, Item 3's coverage
denominator, Item 5's disposition table, and Item 6's calc-def-gate decision all rest on a
population that silently lost 86% of its members.

---

## Fundamental Assessment

**Sound.** This is the right piece of work and the approach is right.

The design's central move — promote the pre-expansion sweep that `_index_constraint_associations`
already performs (`elaborate.py:343-414`) into a first-class usage tier, rather than invent an
inventory — is the correct and the simplest available answer. I verified the claim: that function
does enumerate every `ConstraintUsage` with subtypes, does build `stable_usage_ids`, and does refuse
in both directions when the profile decision inventory disagrees (`:388-396`). The complete authored
domain really is constructed inside elaboration today and then thrown away.

The non-circularity story holds up. Making the domain complete by construction, then reducing the
gate's job to join integrity (which is a real, checkable property), and sourcing the proof that the
domain itself is complete from outside it (reviewed expected-population files, asserted by identity)
is a genuine answer to umbrella spec-review L3-2 — not a restatement of it.

The one-authority rule is genuinely kept. I looked for a smuggled second inventory and did not find
one. The expected-population files are test-side, never read from `src/`, which is exactly the
latitude the spec granted ("kept solely as a test-side independent oracle that no generation path
consults"). The catalog's `usage_records` list is widened in place rather than joined by a parallel
list. `graph.validate()` and the fifth preflight both read the one graph. Nothing new is invented
where an existing seam already exists — and I confirmed each seam the design leans on is real:
`validate()` runs on the live route (`elaborate.py:486`) and both decode paths
(`snapshot/instance_graph.py:904, 977`); the codec is exact-match on version (`:928`) and on the
graph key set (`:936`); the four preflights are a named fail-before-mutate sequence at
`cli/__init__.py:1064-1079`.

Neither design-level smell fires. Nothing here makes a consumer compensate for a producer guarantee
(the opposite — it moves the guarantee upstream to where it can be made), and the invariant's owner
does not move silently: elaboration already owned classification and continues to.

> **Gate note — the formal product-lens pass did not run.** `~/.claude/scripts/product-lens.md` is
> outside this session's readable path scope; both a direct read and a subagent read were denied by
> the permission system, and neither could confirm the file exists. Rather than invent a §3 ledger
> format and corrupt `product-lens.md`, which already carries real spec-stage entries,
> **`product-lens.md` was left untouched and no design-stage verdict block was appended.** The two
> §4 structural smells were checked directly against their descriptions in the review command and
> both are clear, as stated above; "The Point" here was derived independently from the spec, the
> umbrella spec, and the code, not inherited from the design's framing. **Consequence:** there is no
> owner/`[HARD]` lens finding on record for this stage, so nothing forces Rework on that route — but
> the design-stage lens gate is **NOT DISCHARGED**. To close it, grant read access to
> `/home/reid/.claude/scripts/` (or copy the script under `.project/`) and re-run that step.

Abstraction quality is good enough that I want to say so explicitly. Two tiers joined by a
`declaration_id` that both records already carry, no new key minted, no wrapper, no strategy object.
A senior engineer reading this would not ask "why?"

So: proceed to the detailed review. The findings below are correctness and completeness problems
inside a sound frame, not a challenge to the frame. Two of them (F1, F2) are must-fix before
implementation.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Most requirements land cleanly. Every one of the eight brief-assigned decisions is decided, with a
named rejected alternative. The severity rule does key on form and cause together, and `catf_mfe_d5`
does survive it (see the B4 check in Dimension 7). Provenance is carried faithfully — `[INHERITED]`
tags survive into "The Point", and D6 does not harden the spec's parked REQ-EXT-09 question into a
premise; it decides it in the direction the spec called likelier and says so.

Three gaps:

- **The oracle's coverage is left open, and the spec forbids that (F4).** The spec is explicit:
  "design resolves the fate and names the oracle together, and may not close the first while leaving
  the second open." D7 closes the fate (retire `collect_constraint_manifest`, plus
  `_classify_constraint_kind`, `_constraint_owner_kind`, `ConstraintManifestEntry`, `ConstraintKind`
  — I confirmed the 7 `test_extractor.py` call sites and no `src/` caller) and names the oracle. But
  Next-Stage Handoff then parks "whether the scanner guard covers all constraint-bearing fixtures or
  only the pinned twins" as Open for the plan. That is the oracle's coverage, which is its
  load-bearing property. An oracle that guards two fixtures does not discharge a corpus-wide totality
  claim.
- **Identity vocabulary is not preserved into the catalog (F1).** The spec's `[HARD]` row says the
  domain uses `DeclarationId` identity and "does not introduce qualified-name string matching." The
  design's invariant 7 restates it. But the catalog tier the design widens keys on a QN string pair.
  Detail under Dimension 5.
- **The evidence-invalidation register is named but not populated (F6).** The spec says anything
  newly invalidated in the paused Item 7 evidence "is added to that register in this item, not
  discovered later." The design says the same sentence and defers the enumeration entirely. A v3
  schema bump plus a 21-fixture recapture plainly invalidates Item 7's snapshot-route evidence; that
  much can be written down now rather than found during implementation.

The doc-correction obligation is handled well — the edit set is enumerated with line anchors and
ordered before confirmation tests, which is the owner-directed sequence.

### 2. Pattern Consistency
**Assessment:** Concerns

The design composes with the codebase's existing shapes rather than inventing new ones, and I
checked each: the `(scopes, cause)` return is an ordinary refactor of a private helper; the record
follows `ConstraintNode`'s frozen-dataclass-in-`elaboration/graph.py` pattern; the
"non-`None` iff `source_form == "definition_typed"`" convention for `definition_qualified_name`
matches the existing FK convention exactly (`resolution/models.py:495-497`, and the same rule at
`elaborate.py:1193-1197`); "projection renders, it does not classify" is the rule the exact route
already follows for entry points.

The one break is F7 (Dimension 4): a second enumeration and a second classification pass where the
existing loop already has both.

### 3. Abstraction Quality
**Assessment:** Pass

I tried to remove each new thing and the design got worse each time.

- Drop `ConstraintUsageRecord` and widen `ConstraintNode`: a non-reaching usage has no scope, so it
  has no `NodeId`, and the two-tier accounting Q5 requires collapses. The design says this.
- Drop `UsageDisposition` as a struct and inline three fields: you lose the closed-vocabulary check
  in `validate()` and the "exactly one disposition" invariant becomes unstateable.
- Drop `Inapplicability` as a separate record and set a flag: invariant 5 (never rewrites the
  disposition) becomes a convention instead of a shape.

`_attachment(owner)` returning `(scopes, cause)` is the minimum change that makes the severity rule
expressible. No wrapper, no registry, no strategy. This is the right size.

### 4. Duplication Avoidance
**Assessment:** Concerns

**F7.** `_build_constraint_usage_records()` and `_build_constraint_nodes()` would both enumerate
`SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True)` and both call
`_constraint_metadata` on every usage — two independent computations of one classification, which is
the drift the one-authority rule exists to stop, at a smaller scale. The simpler shape: mint the
record at the top of the loop `_build_constraint_nodes` already runs (`:998-1004`), before the scope
loop, and let each `ConstraintNode` take its form from the record. That removes the second
enumeration, removes the second classification, and makes the join true by construction rather than
by assertion.

Related precision point: invariant 1 is stated against `stable_usage_ids`, which is a local variable
inside a `@staticmethod` and does not survive the call. The retained equivalent is
`self._constraint_associations`, whose key set the cross-check at `:388-396` already proves equal to
`stable_usage_ids`. State the invariant against the object that exists.

Otherwise the design avoids duplication well — widening `usage_records` in place instead of adding a
second list is the right call, and deleting the manifest sweep with its test call sites in the same
landing leaves nothing stranded.

### 5. Data Structure Clarity
**Assessment:** Fail

Two problems, one of them the most serious finding in this review.

**F1 (Critical) — the catalog's usage-record key is a QN string pair, and widening the population
breaks it.** `ConstraintCatalogUsageRecord` (`resolution/models.py:474-501`) carries no
`declaration_id`. `_build_constraint_catalog` dedups on `(usage_qualified_name, display_name)`
(`project.py:1145-1146`), and the model's own docstring says why: "Dedup identity is
`(usage_qualified_name, source_local_identity)`, not `usage_qualified_name` alone — anonymous usages
all share `"<anonymous>"` and are distinguished by `source_local_identity`."

Under today's semantics that key is doing dedup *across occurrences of one usage*, so a collision is
benign. Once the row set **is** the domain, the same key is doing identity *between distinct
usages*, and a collision silently merges two domain members. Two anonymous inline asserts sharing a
short name is the concrete case, and the docstring confirms `<anonymous>` is a real value in this
corpus. The consequence is either invariant 4 quietly false (fewer rows than members, no diagnostic)
or the preflight's arity check halting a legitimate model — and which one you get depends on join
direction, which the design does not specify.

Worse, the preflight is specified to assert a "domain↔catalog↔entry join," and with no
`declaration_id` on the catalog row that join *cannot be made by identity at all*. It would have to
be made by qualified-name string matching, which is precisely what the spec's `[HARD]` row and the
design's own invariant 7 forbid.

Fix: add `declaration_id` to `ConstraintCatalogUsageRecord`, key the dict on it, and say so in
Component Overview (which currently says only "gaining the disposition and inapplicability fields").
`catf_mfe_d5` happens not to collide — I checked, all 65 constraint usages there are named, with
repeated short names like `PositiveInputs` (×7) always under distinct owner QNs — so this is a latent
break rather than a headline break. It is still a break, and the schema bump to 3.0.0 is the one
free moment to fix it.

**F3 (Major) — the disposition table has no precedence, but invariant 2 requires exactly one.** The
Token Vocabulary table flattens two orthogonal axes plus a form-keyed row into seven flat entries,
and rows can co-fire:

- A `satisfy` usage owned by a `calc def` matches both `out_of_scope_satisfy` (keyed on form) and
  `owner_kind_unattachable` (keyed on cause).
- A usage whose profile decision is `Eligibility.BLOCK` but whose owner yields no scopes matches both
  `profile_blocked` and `owner_has_no_occurrences`.

Four rows say "expanded" in the *when* column and three do not, which hints at an intended ordering,
but it is never stated. Two implementers would build two different domains from this table. State it
as an ordered decision — form-based exclusions first, then expansion cause, then profile eligibility
— and say explicitly that eligibility is consulted only for a usage that expanded.

One consequence to record while you are there: the parenthetical "the existing
`SI_CONSTRAINT_BLOCKED` diagnostic still halts" is true only for expanded usages. That diagnostic is
emitted inside the scope loop (`elaborate.py:1018-1029`), so a BLOCK-decision usage that reaches no
instance produces no diagnostic and no halt. That is probably the behavior you want, but it is a
statement about semantics and it belongs in the design rather than in the reader's head.

Everything else here is good: the record's field list is explicit and typed, `UsageDisposition` is
sketched in code, and the closed vocabularies are named.

### 6. Route Safety
**Assessment:** Concerns

The fail-closed story for snapshots is correct and I verified it needs no new code: a v2 payload is
refused by the exact version comparison (`instance_graph.py:927-932`) and a v3-labelled payload
missing `constraint_usages` is refused by the exact graph key-set check (`:933-937`), because
`_mapping` takes the expected key set as an argument. D4's "no v2 reader, no shim" matches the
standing deletion-over-shims direction.

Two concerns:

**F2 (Critical) — minting pre-expansion newly runs classification on usages it has never run on, and
classification raises.** Today `_constraint_metadata` is called *inside* the scope loop
(`elaborate.py:1007`), so it has never executed for the 56 invisible CATF usages or their equivalents
across the corpus. It contains at least two hard raises:

- `SI_REDEFINITION_INVALID` when a predicate expression exists but yields no representable IR
  (`:1166-1175`);
- an `SI_EDGE_DANGLING` when the live definition identity disagrees with the profile's selection
  (`:1149-1163`).

Move classification upstream of expansion and every previously-invisible usage is newly subjected to
both. A usage that until now only failed to matter because it was dropped can halt elaboration for
the entire model. This is not hypothetical: the `[m]`-unit-literal elaboration defect is an explicit
Item 4 non-goal in this very spec, and a non-reaching usage carrying one would now take the model
down.

The design does not name this anywhere — not in Key Bets, not in Potential Risks. It needs a stated
rule. The natural one, and the one consistent with the record's own field list: the usage tier
records classification but does **not** derive predicate IR (the record carries no `predicate_ir`,
and the catalog tier deliberately carries none either — `resolution/models.py:481-483`), so mint
should call a classification path that stops before the predicate-IR block. Where classification
genuinely cannot complete for a non-reaching usage, that is a disposition, not a raise.

B4 does survive for `catf_mfe_d5` specifically: all 56 are bare `constraint`, so `source_form` is
`plain_usage`, so `predicate_source` is `None` (`:1146-1147`), so `predicate_ir` stays `None` and
nothing raises. That is real, and it is also luck. Record it as the reason rather than leaving it
unsaid.

**F5 (Major) — three-route parity is claimed as structural, and it is not.** The Architecture section
says parity is free "because the codec fingerprint covers the usage tier, so a route that disagreed
could not have decoded." The fingerprint proves the snapshot bytes are internally coherent. It says
nothing about whether the live route, re-elaborating the same model, mints the same domain. Those are
different claims, and the second is the one that can drift.

The design's own D2 supplies the mechanism: reading an `@inapplicable:` doc comment is a live-only
elaboration step. If doc-comment reachability differs — for a relocated source tree, say — live and
snapshot diverge and both still fingerprint cleanly. This repo has been bitten by exactly this class
before, where a multi-hop EXPOSE resolved correctly live and mis-wired from a snapshot while every
seal passed.

The Validation Approach does list a real three-route parity test, so the coverage exists. The problem
is the claim, which invites a future reader to trim that test as redundant. Delete the "structural,
not a separate mechanism" framing and let the test carry the weight.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The four stated bets are genuine claims about reality, each with a real "if false → what fails," and
none is a mechanism choice in disguise. B1 checks out against the code. B4's premise I verified as
far as the source allows. The eight decisions each name a rejected alternative with a reason, and the
reasons are substantive rather than decorative — D2's rejection of a `metadata def` on the grounds
that this repo ships no `.sysml` library and reads no `MetadataUsage` is the kind of concrete reason
that makes a rejection trustworthy.

**Hidden bets, in descending order of cost:**

- **H1 — that classification is total and side-effect-free over the previously-invisible
  population.** This is F2. It is load-bearing for every fixture in the corpus and it is unstated.
- **H2 — that the live route and the snapshot routes mint identical domains.** This is F5. The design
  states it as a consequence of the fingerprint, which is not where it comes from.
- **H3 — that the catalog's existing key survives the population widening.** This is F1. The design
  treats "widen the population of `usage_records`" as a population change; it is also an identity
  change, because the key was only ever sound for the narrower population.
- **H4 — that a source-text scanner can count authored constraint declarations reliably.** D7 leans
  on it as the guard on the expectation files, but never states its matching rule or its known
  false-positive classes (`constraint def` versus `constraint` usage versus `assert constraint`,
  multi-line declarations, commented-out code). It is also a *count* guard inside a design whose
  stated principle everywhere else is identity-not-count.

On **B2** specifically: `_scopes_for_owner` returns `()` for three reasons, not two — the third is
`owner is None` (`:523-524`). Minor, but the design says "exactly two causes," and an invariant
stated as exhaustive should be. The mitigation in Potential Risks (enumerate owner kinds explicitly
against the map at `:1177-1182` rather than defaulting) is the right instinct, but note that map ends
in `.get(..., type(owner).__name__.lower())` — a silent fallback. Making the mitigation real means
turning that fallback into a refusal, which the design should say out loud.

### 8. Reader Comprehension
**Assessment:** Pass

This reads well. "Totality is a property of where records are born, not of a check added later" is a
genuine mental model, stated plainly and before any mechanism. The Research Findings section leads
with a claim per paragraph and anchors each to a file and line, which is what let me verify the
design quickly rather than reconstruct it. The Architecture flow diagram earns its place — it shows
where the new hop goes in one glance.

Two small things. The Token Vocabulary table is where a reader will spend the most time and it is the
one place that hides complexity behind flatness (F3) — the ordering is the model, and the table does
not show it. And D5 is a pointer rather than a decision, which is fine for the section-citation
purpose but means the eight-decision list has a hole in it when skimmed.

---

## Issues by Severity

### Critical
- **F1** — `ConstraintCatalogUsageRecord` has no `declaration_id`; widening its population to the
  whole domain makes a QN-string dedup key into an identity key, which can silently merge two domain
  members and makes the preflight's domain↔catalog join impossible by identity. Violates the spec's
  `[HARD]` identity row and the design's own invariant 7. — *Data Structure Clarity*
- **F2** — Minting pre-expansion newly runs `_constraint_metadata` on every previously-invisible
  usage, and that function raises (`SI_REDEFINITION_INVALID` at `:1171`, definition-identity
  disagreement at `:1159`). A usage that only failed to matter because it was dropped can now halt
  elaboration model-wide. Unstated bet. — *Route Safety*

### Major
- **F3** — The disposition table has no precedence rule, but invariant 2 requires exactly one
  disposition; rows demonstrably co-fire. — *Data Structure Clarity*
- **F4** — D7 closes the manifest fate but leaves the oracle's coverage open, which the spec
  explicitly forbids. — *Spec Compliance*
- **F5** — Three-route parity is claimed as structural; the fingerprint does not prove it, and D2's
  live-only doc-comment read is the mechanism by which it could drift. — *Route Safety*
- **F6** — Cross-repo consequences are named without a landing order: the TEAx
  `ACCEPTED_CATALOG_SCHEMA_VERSIONS` re-vendor is "tracked outside this item" with no register, the
  companion's no-change status is never stated affirmatively, and the Item 7 evidence-invalidation
  entries are deferred rather than written. — *Spec Compliance*

### Minor
- **F7** — Two enumerations and two classification passes over one population; mint inside
  `_build_constraint_nodes`'s existing loop instead. Also: invariant 1 cites `stable_usage_ids`, a
  local that does not survive; use `self._constraint_associations`. — *Duplication Avoidance*
- **F8** — B2's two-cause split misses `owner is None` (`:523`), and the mitigation depends on
  removing a silent `.get()` fallback (`:1182`) that the design does not mention. — *Bets*
- **F9** — The catalog's `None` rule moves from `graph.constraints` to the domain; confirm
  `ConstraintCatalog` is constructible with `usage_records` populated and `entries`/`source_records`
  empty. That combination has never existed. — *Spec Compliance*
- **F10** — The `@inapplicable:` parse is underspecified at the seam: `_extract_documentation`
  (`extraction/extractor.py:803-810`) joins multiple `Comment` bodies after `.strip().strip("*")`, so
  "first line" needs a definition and multi-comment precedence needs a rule. The mechanism is
  otherwise sound on all four spec properties, and the de-risk spike is correctly named. —
  *Abstraction Quality*
- **F11** — Adding `satisfy_reference` to `_constraint_metadata` also changes
  `ConstraintNode.source_form` for satisfy usages that *do* expand, moving catalog rows and
  fingerprints. Behaviorally inert (`predicate_source` is `None` either way) but the design predicts
  baseline churn only from the schema token. — *Route Safety*
- **F12** — D6's row rewrite must land its new evidence pointer before the manifest sweep is deleted,
  to keep the doc-before-tests sequence honest. — *Spec Compliance*

---

## Recommendations

1. **Fix F1 in this landing.** Add `declaration_id` to `ConstraintCatalogUsageRecord` and key the
   catalog dict on it. The 3.0.0 bump is the one free moment; doing it later costs a fourth version.
2. **Fix F2 with a stated rule**, not a case-by-case patch: the usage tier records classification and
   does not derive predicate IR. Add it as a bet or a risk so the next reader sees why the mint path
   is not simply `_constraint_metadata`.
3. **Restate the Token Vocabulary as an ordered decision** (form exclusions → expansion cause →
   profile eligibility), and say eligibility is consulted only for expanded usages. Add the note that
   a non-reaching BLOCK usage emits no `SI_CONSTRAINT_BLOCKED`.
4. **Close the oracle's coverage in the design** (F4): name which fixtures get expectation files and
   which get the scanner guard, and state the scanner's matching rule with its known false-positive
   classes.
5. **Replace the "parity is structural" claim** (F5) with the parity test as the load-bearing
   evidence, and name the doc-comment read as the specific thing that could diverge.
6. **Write the cross-repo landing order down** (F6): this repo lands first and generates without
   TEAx; TEAx re-vendors `ACCEPTED_CATALOG_SCHEMA_VERSIONS` after, tracked *where*; the companion
   needs no change *because* `_index_constraint_associations`'s cross-check at `:388-396` already
   requires a profile decision for every swept `ConstraintUsage` subtype, `satisfy` included. Add the
   Item 7 snapshot-route evidence to the invalidation register now.
7. **Mint inside the existing loop** (F7) and restate invariant 1 against
   `self._constraint_associations`.

---

## What I Checked and Found Correct

Recording this so the next reader does not re-verify it:

- `_index_constraint_associations` (`elaborate.py:343-414`) sweeps every `ConstraintUsage` with
  subtypes and refuses inventory disagreement in both directions (`:388-396`). B1's premise holds.
- `_constraint_metadata` (`:1119-1224`) is scope-independent — every input is the usage, its
  definition, and its association — so calling it pre-expansion is sound as far as *classification*
  goes. F2 is about its raises, not about scope leakage.
- `declaration_id` is already on `ConstraintNode` (`elaboration/graph.py:196`), so the join mints no
  new key, exactly as D1 claims.
- The codec is exact-match on both version (`instance_graph.py:927-932`) and graph key set
  (`:933-937`), and `graph.validate()` runs on the live route (`elaborate.py:486`), both decode paths
  (`instance_graph.py:904, 977`), and the sealed context (`exact_pipeline_context.py:210`). D3's
  "free on both routes" and D4's "fail-closed needs no new code" both check out.
- The preflight seam is real and ordered before `_clear_output_directory`
  (`cli/__init__.py:1064-1079`), so a fifth check joins fail-before-mutate as described.
- `collect_constraint_manifest` has no `src/` caller and exactly 7 `test_extractor.py` call sites, as
  D7 states.
- `CATALOG_SCHEMA_VERSION = "2.0.0"` (`contracts/versions.py:18`) rides inside the model contract
  (`model_contract.py:67, 78`) and is pinned at `tests/conformance/test_catalog_schema_version.py:19`.
- `catf_mfe_d5` authors no anonymous constraint usages and no `satisfy`, so neither F1's collision nor
  D6's boundary question moves the headline 65.

---

## Resolutions

*(Recorded 2026-08-12 by the design agent, revising `design.md` to rev 2. Every finding resolved;
no finding was declined.)*

**F1 (Critical) — catalog usage-record identity key. RESOLVED, adopted as reviewed.**
`ConstraintCatalogUsageRecord` gains `declaration_id`, and `_build_constraint_catalog`'s dict keys
on it instead of `(usage_qualified_name, display_name)`. QN and display name stay as display
metadata. The join is now `ConstraintUsageRecord.declaration_id` ↔ `ConstraintNode.declaration_id`
↔ `ConstraintCatalogUsageRecord.declaration_id`, by exact identity end to end with no
qualified-name string matching at any step. Recorded in D1 (with the QN key as a named rejected
alternative and the anonymous-usage merge as the reason), in Component Overview, in Architecture's
join paragraph, and in invariant 3. The reviewer's point that the 3.0.0 bump is the one free moment
is taken — the re-key rides the same bump, and Implementation Notes now say the *key* changes as
well as the population, since both are breaking for a QN-keyed consumer.

**F2 (Critical) — newly-reached usages can raise. RESOLVED with a structural rule, not a patch.**
The umbrella spec's form-first rule is made structural: **the form gate runs before any predicate
walk**. Minting is non-raising for non-asserted forms — a `plain_usage`, `requirement_constraint`,
or `satisfy_reference` usage always gets its visible record (cataloged per its form) and never
halts, whatever its predicate would do if walked. Asserted forms may raise as they do today, which
is severity-by-cause as specced. `_constraint_metadata` splits so the form/identity half is callable
without the predicate-IR and definition-identity half. Landed as invariant 5, bet B3 (with its "if
false" fallback), the Core Concept's fourth paragraph, and a Potential Risks entry naming the
residual (an asserted malformed non-reaching gate now stops elaboration where it used to vanish).
The reviewer's catch that `_typed_definition` already runs pre-expansion (`:1002`) is recorded in
Research Findings, so the plan does not chase a raise that was never newly reached. The CATF luck is
now a **recorded fact** under B5 rather than an implicit bet — all 56 are `plain_usage`, so
`predicate_source` is `None` (`:1146-1147`), so the `SI_REDEFINITION_INVALID` path is unreachable
*for that fixture* — and a new regression fixture (a `plain_usage` whose predicate would raise if
walked) pins the rule instead of the luck.

**F3 (Major) — disposition precedence. RESOLVED as an ordered rule in the Item 3 section.** The
Token Vocabulary is restated as three ordered steps that stop at the first match: (1) form gate —
`satisfy_reference` → `out_of_scope_satisfy`; (2) expansion cause → `non_reaching`, with profile
eligibility explicitly **not** consulted; (3) profile eligibility, consulted only for a usage that
expanded. Both co-firing cases the reviewer constructed now resolve deterministically (satisfy under
a `calc def` → step 1; BLOCK with no scopes → step 2), and both became precedence test fixtures. The
reviewer's semantic note is written into the design rather than left in the reader's head: a
non-reaching BLOCK usage emits no `SI_CONSTRAINT_BLOCKED`, because that diagnostic lives inside the
scope loop (`:1018-1029`) — deliberate, since blocking is a statement about executing a predicate
and there is nothing to execute. Invariant 2 now names the precedence rule as its producer. D5 is no
longer a bare pointer; it states the decision and its rejected alternative (a flat match table).

**F4 (Major) — oracle coverage. RESOLVED and closed in the design.** New **Oracle Coverage**
section, and the parked question is deleted from Next-Stage Handoff. Coverage is **all 31
constraint-bearing fixture directories** (measured at `ccf4c21`, re-measured and recorded at
execution), not a subset. Expectation files hold one identity row per authored usage and are
asserted by identity list, not by count. The rule for a fixture with no expectation file is a **test
failure naming the directory** — a missing expectation is a visible gap, never silent coverage,
which is what stops a newly added fixture from quietly shrinking the oracle's reach. H4 is addressed
directly: the scanner's matching rule is stated (strip comments, then statement-initial `constraint`
/ `assert` / `require constraint` / `assume constraint` / `satisfy`, excluding `constraint def`), it
emits declaration identities rather than a count so the guard is identity-shaped like the rest of the
design, and its known false-positive/negative classes are listed. Its job is explicitly drift
detection on the expectation file — it is never what the domain is checked against.

**F5 (Major) — three-route parity claimed as structural. RESOLVED; the claim is deleted.** The
"structural, not a separate mechanism" framing is gone. Architecture now says plainly that the
fingerprint proves the snapshot bytes are internally coherent and says nothing about whether the
live route re-elaborating the same model mints the same domain, names D2's live-only doc-comment
read as the concrete drift mechanism, and cites the multi-hop EXPOSE precedent the reviewer alluded
to. Two reinforcements beyond deleting the claim: D2 now states that the annotation is **captured
into the graph at elaboration** so it travels in the snapshot and no from-snapshot route re-reads
source; and the parity test is strengthened to **field for field, record for record** on a fixture
that exercises annotations, run on both the in-place and relocated snapshot, with an explicit note
that fingerprint equality would pass while diverging.

**F6 (Major) — cross-repo landing order. RESOLVED as an ordered list with failure modes.** New
**Cross-Repo Landing Order** section: (1) this repo lands first and is releasable alone — splitting
the codec bump from the catalog bump would seal a v3 graph with a 2.0.0 token that no version check
catches; (2) the companion needs no change, stated affirmatively with the reviewer's own reason —
`_index_constraint_associations`'s cross-check (`:388-395`) already requires a profile decision for
every swept subtype, `satisfy` included; (3) doc corrections before confirmation tests, and
specifically D6's REQ-EXT-09 evidence pointer before `collect_constraint_manifest` is deleted (this
also closes F12); (4) the single reviewed recapture last, at the final schema; (5) TEAx re-vendors
`ACCEPTED_CATALOG_SCHEMA_VERSIONS` after, tracked in the epic's cross-repo notes, with the
fail-closed direction noted as the intended failure. The Item 7 evidence-invalidation entries are
**written now**, not deferred: every paused v2-bytes snapshot-route observation, the byte-identity
comparisons on the 21 recaptured fixtures, and any evidence citing `collect_constraint_manifest` as
the population definition.

**F7 (Minor) — two enumerations, two classification passes. RESOLVED; adopted as recommended.** New
**D9**: the record is minted at the top of `_build_constraint_nodes`'s existing per-usage loop
(`:998-1004`), before the scope loop, and each `ConstraintNode` takes its form and identity metadata
from the record. One enumeration, one classification, and the tier join true by construction rather
than by assertion. The separate `_build_constraint_usage_records()` pass is recorded as the rejected
alternative. The precision point is taken too: invariant 1 is restated against
`self._constraint_associations` (`:304`), whose key set `:388-395` already proves equal to the
sweep, rather than against `stable_usage_ids`, which does not survive the `@staticmethod` call.

**F8 (Minor) — B2's cause split and the silent fallback. RESOLVED.** B2 now says **three** causes,
adding `owner is None` (`:522-523`), and `owner_absent` is a real row in the precedence table with
the same asserted/non-asserted severity split. The mitigation is made real rather than gestured at:
new **invariant 8** turns the owner-kind map's `.get(..., type(owner).__name__.lower())` fallback
(`:1177-1182`) into a refusal, so an unmapped owner kind fails elaboration by name instead of being
graded by accident. Potential Risks now points at invariant 8 as the mitigation.

**F9 (Minor) — untested catalog shape. RESOLVED.** Called out in Implementation Notes as a
combination that has never existed (`usage_records` populated, `concrete_entries` and
`source_records` empty — the all-calc-def-owned model), and added to Validation Approach as an
explicit constructibility and deterministic-fingerprint check.

**F10 (Minor) — `@inapplicable:` parse underspecified at the seam. RESOLVED.** Implementation Notes
now defines the parse against `_extract_documentation`'s actual behavior
(`extraction/extractor.py:803-814`): it collects every owned `Comment`, applies
`.strip().strip("*").strip()` per body, and joins with `\n`. So "first line" means the first line of
the **joined** string; a marker carried by a later comment body is a malformed-annotation halt, not
a silent accept; and `strip("*")` means a `/* @inapplicable: … */` body arrives already trimmed. The
multi-comment halt became a validation case, and the de-risk spike is extended to confirm the join
behavior as well as reachability.

**F11 (Minor) — satisfy churn beyond the schema token. RESOLVED.** Implementation Notes now records
that adding `satisfy_reference` also changes `ConstraintNode.source_form` for satisfy usages that
*do* expand, moving their catalog rows and the catalog fingerprint — behaviorally inert
(`predicate_source` is `None` either way) but a second, independent source of baseline churn the
plan should expect.

**F12 (Minor) — doc-before-tests ordering for D6. RESOLVED.** Stated twice, deliberately: in D6
("its new evidence pointer lands **before** the sweep is deleted") and as step 3 of the Cross-Repo
Landing Order, with the failure mode named — a window in which the shipped row cites a function that
no longer exists, breaking the doc-before-tests rule in the one place this item exists to fix.

**O-1 (Orchestrator must-fix, raised against rev 2 from the plan stage's output) — "the companion
needs no change" narrows invariant 61. RESOLVED in rev 3; the finding is correct as stated.**

Verified against landed authority before acting. Invariant 61 and LC-E13
(`constraint-execution-lifecycle-requirements.md:334-341`) both split the vacuous-gate obligation
across two surfaces: the catalog carries the `non_reaching` disposition **and** "authoring
validation emits an advisory naming the usage and its detached owner." Invariant 59
(`contract:394-400`) fixes what authoring validation means — the companion's validator layer, whose
diagnostics are author feedback, with codegen enforcing the same conditions unconditionally and
independently. Appendix C's acceptance cell repeats it. Rev 2 built only codegen's half and then
asserted affirmatively that the companion needs no change, which reads the contract as satisfied
while half of it was never designed. The downstream plan's PD2 routing the advisory to a codegen
`logger.warning` is the same narrowing, one stage further on.

What rev 3 does:

- **New D10 and a new section, [The Companion Advisory](design.md#the-companion-advisory-invariant-61--lc-e13).**
  The advisory lands as a new `ExtractionDiagnosticFact` kind, `vacuous_asserted_gate`, registered
  `ADVISORY` in the closed `EXTRACTION_DIAGNOSTIC_SEVERITY` map
  (`agentic-mbse constraint_facts.py:78-82`, severity set writer-side at `:230-233`). No new
  mechanism is invented: this is the companion's existing authoring-validation channel, and codegen
  already reads it at exactly one sink, `screen_extraction_diagnostics`
  (`elaboration/extraction_screen.py`), which halts on `BLOCKING` and renders `ADVISORY` at warning
  grade. Codegen-side work is zero. Message names usage QN and detached-owner QN; the diagnostic's
  `location` carries the usage's source position so the existing renderer prints `file:line:column`.
- **Codegen's half stays independent, per invariant 59.** The fingerprinted warning-grade
  `non_reaching` disposition remains codegen's own enforcement and does not consult the advisory. A
  codegen log line is explicitly demoted to optional color, and D10 records the `logger.warning`
  route as the rejected alternative with the reason.
- **Landing-order step 2 rewritten.** It no longer says "no companion change." It now separates two
  true things: the *domain* needs nothing from the companion (the cross-check at
  `elaborate.py:388-395` already forces a profile decision for every swept subtype), while
  *invariant 61's advisory half* does. Order between repos is free because invariant 59 makes
  codegen independent — codegen may land first, and the window costs author feedback, not
  enforcement. But the companion change is part of **this** item, not a follow-up, because
  invariant 61 is unsatisfied until both halves exist. The named violation is precisely rev 2's
  error: treating codegen's disposition as discharging invariant 61 alone.
- **Trigger alignment — delivered as far as it honestly goes, with the residual surfaced.** The
  orchestrator asked to align the trigger so the two surfaces cannot disagree. They cannot be made
  equal: codegen grades vacuous from the occurrence index, the companion has no occurrence index,
  and its structural trigger (an asserted usage whose owning `part def` is typed by zero part
  usages) is a **strict subset** — a part def typed by a usage that never instantiates has non-zero
  typings and zero occurrences. Equalising them means reimplementing occurrence resolution in the
  companion, which is the second-representation smell this item exists to remove. So the alignment
  is stated as a checkable **direction** instead: new **invariant 9** — the companion's trigger set
  is a subset of codegen's vacuous set, never a superset, so the advisory can only ever be missing,
  never false. The residual (a vacuous gate codegen grades with no author advisory) is surfaced in
  Potential Risks rather than resolved silently, per the surfacing duty.
- **The advisory deliberately does not travel in the graph.** It is author feedback at authoring
  time; codegen's disposition is what travels and is route-invariant. This also keeps it off the
  three-route parity surface, so it cannot become the live-only read that F5 warned about.
- **Validation added:** the advisory's emission and grade; the existing codegen sink handling the
  new kind with no codegen change; the containment direction on a typed-but-never-instantiated
  fixture; and an independence check that codegen produces the identical disposition with the
  advisory suppressed.

**Gate note — product-lens pass. DISCHARGED in the revision session.** The reviewer could not read
`~/.claude/scripts/product-lens.md` and correctly left `product-lens.md` untouched rather than
inventing a format. The script is equally unreadable from this session, so the method was
reconstructed from the in-tree examples — this item's own spec-stage entry and the two other
ledgers — and the design-stage entry is appended to
`.project/active/constraint-catalog-totality/product-lens.md` with that reconstruction noted in the
entry itself. Verdict: **DISPOSED** (design-F1..design-F3, none blocking, all applied in rev 2). No
owner-graded or `[HARD]` statement is contradicted by this design.

---

**Overall:** Revise

The frame is right and the mechanism is right. F1 and F2 are correctness problems that must be
resolved before implementation starts, and F3 is an ambiguity that would produce two different
implementations from the same document. None of the three touches the design's foundation, and none
requires re-deciding any of the eight owned decisions — D1 through D8 all stand.

**Next Steps:** Record resolutions in the section above, then re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The reviewer does not edit the
design.
