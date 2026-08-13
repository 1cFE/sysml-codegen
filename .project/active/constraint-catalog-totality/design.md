# Design: Canonical Usage Domain and Catalog Totality

**Status:** Draft (rev 2 — resolves design-review F1–F12)
**Owner:** Reid W
**Created:** 2026-08-12
**Branch:** `item7-rebuild` (worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`; companion
worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild`)
**Git:** `ccf4c21` (2026-08-12)
**Epic:** CONSTRAINT-SEMANTICS, Item 2

---

## Overview

Give the instance graph a usage tier: one record per authored `ConstraintUsage`, minted before
occurrence expansion, each carrying exactly one disposition. Everything downstream — catalog,
snapshot, gate, requirement rows — reads that tier, joined end to end by `DeclarationId`.

## Related Artifacts

- **Spec:** `.project/active/constraint-catalog-totality/spec.md` (reviewed; 11 findings resolved
  in `spec-review.md`)
- **Design review:** `.project/active/constraint-catalog-totality/design-review.md` (verdict
  Revise; F1–F12 resolved in this revision, resolution notes recorded in that file)
- **Product-lens ledger:** `.project/active/constraint-catalog-totality/product-lens.md` —
  design-stage entry appended 2026-08-12
- **Stage brief:** `.project/active/constraint-catalog-totality/briefs/design.md`
- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (Item 2)
- **Required Reading:** `.project/active/constraint-semantics-contract/spec.md`;
  `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2–4;
  `.project/active/constraint-semantics-contract/product-lens.md`;
  `.project/backlog/epic_elaborate_first_architecture.md` (Item 7);
  `.project/active/cutover-recovery/plan.md`
- **Item 1 authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  (invariants 9, 28, 40, 48, 61; Appendix C "Asserted vacuous gate")
- **Decision records:** `.project/adr/` does not exist in this tree. No prior entries to check or
  supersede.

## The Point

**[INHERITED: `.project/active/constraint-semantics-contract/spec.md`, Problem]** Constraints are
how these models enforce physics, so that design search stays viable. The contract already
promises every authored constraint usage stays visible with exactly one disposition (invariants 1
and 28). The exact route does not keep that promise. On `catf_mfe_d5`, 65 authored usages produce
9 catalog carriers; the other 56 are simply absent — not eligible, not excluded, nothing.

The cause is structural, not a missing check. Records only begin after owner-to-scope expansion
(`_build_constraint_nodes`, `elaboration/elaborate.py:997`), and a usage whose owner yields zero
scopes emits nothing. Every downstream artifact descends from that already-truncated set, so a
totality gate written against today's data would compare two projections of the same truncation
and pass. Until the graph accounts for every authored usage, Item 3's coverage denominator,
Item 5's disposition table, and Item 6's calc-def gate decision all rest on a population that
silently lost 86% of its members.

## Research Findings

**The pre-expansion sweep already exists and is already cross-checked.**
`_index_constraint_associations` (`elaboration/elaborate.py:343-414`) enumerates every
`ConstraintUsage` in the model with subtypes and *refuses* when the constraint-profile decision
inventory disagrees with that sweep in either direction (`:388-395`). Its result is retained as
`self._constraint_associations` (`:304`), whose key set that cross-check proves equal to the
sweep. The complete authored domain is therefore constructed inside elaboration today and then
discarded. This item promotes it rather than inventing it — that is the whole design.

**The truncation point is one function.** `_scopes_for_owner` (`elaborate.py:521-539`) has
branches for `PartDefinition`, `PartUsage`, and `Package`, and returns `()` otherwise. Empty comes
back for three structurally different reasons the return value cannot distinguish: `owner is None`
(`:522-523`), the owner kind has no branch (a `calc def`, 51 of the 56 CATF cases), or the owner
is attachable in principle but has zero occurrences (an untyped design part, the other 5). The
severity rule needs that distinction, so the function has to return the cause, not just the tuple.

**Form classification is already in the exact route, and it raises.** `_constraint_metadata`
(`elaborate.py:1119-1224`) emits five source forms — `requirement_constraint`,
`named_usage_reference`, `definition_typed`, `inline`, `plain_usage` — with owner kind, owner QN,
source file and line beside them. It is scope-independent, so calling it pre-expansion is sound as
far as classification goes. But its body also derives predicate IR and cross-checks definition
identity, and both paths raise: `SI_REDEFINITION_INVALID` when a predicate expression yields no
representable IR (`:1166-1175`) and `SI_EDGE_DANGLING` when the live definition identity disagrees
with the profile's selection (`:1149-1163`). Today it runs only inside the scope loop (`:1007`),
so it has never executed for a non-reaching usage. `_typed_definition` already runs pre-expansion
for every usage (`:1002`), so its raise is not newly reached; only `_constraint_metadata`'s body
is.

Note the companion module it reads facts from (`agentic_mbse/sysml/constraint_extraction.py`) is
not being deleted wholesale by ELABORATE-FIRST Item 7; scope 2 says "fold
`extract_identified_constraint_facts` into one live constraint-fact extraction pass"
(`epic_elaborate_first_architecture.md:443-444`). The spec's conclusion holds — build against
`_constraint_metadata`, not the companion classifier — but the exact route's dependency on that
module survives the fold.

**`satisfy` really does fall through, and the spec's premise checks out.**
`SatisfyRequirementUsage` subclasses `RequirementUsage`, not `AssertConstraintUsage` — verified
against the syside stub in `.project/active/subtype-enumeration/spec-review.md:26` (stub line
16063). So a satisfy usage is swept as a `ConstraintUsage` subtype, misses the
`AssertConstraintUsage` branch, and lands on `plain_usage`, indistinguishable from a bare
`constraint`. The named exclusion Q7 requires is genuinely new classification work.

**There is already a usage tier in the catalog; it is admitted-only and keyed by strings.**
`ConstraintCatalogUsageRecord` (`resolution/models.py:474-503`) is one row per *admitted* usage,
deduped in `project.py:1145-1146` on `(usage_qualified_name, display_name)`. That key is sound
only while it dedups occurrences *of one usage*; the moment the row set becomes the domain it is
doing identity *between distinct usages*, and the model's own docstring says `<anonymous>` is a
real value in this corpus. It carries no `declaration_id`. Related: `_build_constraint_catalog`
returns `None` when `graph.constraints` is empty (`project.py:1084-1085`) — a model whose
constraints are all calc-def-owned gets no catalog at all, the totality hole in its purest form.

**The codec is exact-match on both version and key set.** `decode_instance_graph`
(`snapshot/instance_graph.py:918-982`) refuses any `schema_version` other than
`INSTANCE_GRAPH_SCHEMA_VERSION` (`:68`, currently `instance-graph/v2`), requires the graph key set
to be exactly `{occurrences, attrs, calcs, constraints, diagnostics}`, verifies the whole-document
fingerprint, and then calls `graph.validate()`. `validate()` also runs on the live route
(`elaborate.py:486`) and on the sealed context (`exact_pipeline_context.py:210`), so structural
invariants placed there are enforced everywhere for free.

**Generation preflights are a named sequence at one boundary.**
`_generate_package_from_graph` (`cli/__init__.py:1064-1079`) runs constraint name safety,
duplicate output paths (1.5), params coverage (1.6), and registry class names (1.7) before
`_clear_output_directory`. That is the fail-before-mutate seam a fifth check joins.

**The manifest sweep has no `src/` caller.** `collect_constraint_manifest`
(`extraction/extractor.py:98-139`) plus `ConstraintManifestEntry` / `ConstraintKind`
(`extraction/constraint_report.py`) are reached only from `tests/conformance/test_extractor.py`
(7 call sites), yet both REQ-EXT-09 and REQ-CL-04 define their population by it.

**Corpus shape.** 31 of the 96 `tests/fixtures/` directories author at least one constraint usage
(measured at `ccf4c21`); 21 fixture directories carry an `instance_graph_snapshot.json`.

**Cross-repo pin.** `CATALOG_SCHEMA_VERSION = "2.0.0"` (`contracts/versions.py:18`) rides inside
the fingerprinted model contract (`model_contract.py:67, 78`) and is pinned by
`tests/conformance/test_catalog_schema_version.py:19`. TEAx vendors an accepted set by copy; B3
forbids importing this repo, so a bump is a manual cross-repo act.

## Core Concept

The instance graph gains a **usage tier**: one `ConstraintUsageRecord` per authored
`ConstraintUsage`, minted at the top of the loop `_build_constraint_nodes` already runs — before
the scope loop that truncates. Each record carries the classification `_constraint_metadata`
already produces plus exactly one **disposition** — kind, reason token, severity — computed by an
ordered rule from the usage's form and the reason its owner did or did not expand. The existing
per-occurrence `ConstraintNode`s become the second tier and are unchanged; the join between the
tiers is the `DeclarationId` both already carry, so no new key is minted.

The key insight is that **totality is a property of where records are born, not of a check added
later**. Today the population is defined by expansion, so no check written against it can see what
expansion dropped. Move the birth point upstream of expansion and the domain is complete by
construction; the gate's remaining job is join integrity — one disposition per member, every
occurrence entry joining to a member — which is a real, non-circular thing to check. Proof that
the domain itself is complete comes from outside it: reviewed expected-population files, asserted
by identity, over every constraint-bearing fixture.

Moving the birth point upstream has a cost the frame has to absorb: work that used to run only on
usages that reached an instance now runs on usages that never did. So the mint path is deliberately
narrower than the expansion path. **The form gate runs before any predicate walk**, and for a
non-asserted form the mint derives identity metadata only — never a predicate, never a definition
cross-check, and therefore never a raise. A non-asserted usage that cannot be fully understood gets
a visible record, which is exactly the disposition-not-absence promise applied to itself.

This composes with existing pieces rather than adding parallel ones. Elaboration owns minting (it
is where the pre-expansion sweep lives, and it is the loop that already enumerates usages).
`graph.validate()` owns per-record structure (it already runs on the live route, both decode paths,
and the sealed context). The codec carries the tier (a version bump, no shim). Projection renders
the tier into the catalog's existing `usage_records` list, widening its population from
admitted-only to the whole domain. A fifth generation preflight owns the join gate at the
fail-before-mutate boundary.

## Key Bets

- **B1.** The pre-expansion sweep behind `self._constraint_associations` sees every authored
  constraint usage — the profile-inventory cross-check at `elaborate.py:388-395` means a usage
  invisible to it is already a hard failure, not a silent drop. *If false → the domain is complete
  only relative to the adapter's sweep, and a usage the adapter cannot see stays absent with no
  diagnostic; the independent oracle would have to become the load-bearing detector rather than a
  guard.*
- **B2.** Emptiness of the attachment lookup decomposes into exactly three causes — no owner, the
  owner kind has no attachment capability, or an attachable owner has zero occurrences — and that
  split is enough to key the severity rule. *If false → a fourth cause exists that is neither a
  halt nor a warning, and the severity rule mis-grades it in one direction or the other.*
- **B3.** Classifying a usage's *form* — membership kind and type tests only — is total and cannot
  raise, so a mint path that stops at the form gate is safe over the previously-invisible
  population. *If false → moving the birth point upstream takes down elaboration model-wide for
  any model containing a non-reaching usage the form gate mishandles — the failure mode invariant
  5's `classification_incomplete` disposition exists to convert into a named, per-usage halt.*
- **B4.** Recording an inapplicability decision as a field beside the disposition, never as a
  rewrite of it, is sufficient for Item 3 to compute the feasibility denominator without a second
  usage-tier schema change. *If false → Item 3 pays the schema bump this item was supposed to
  absorb, and every fixture snapshot recaptures twice.*
- **B5.** `catf_mfe_d5`'s 56 invisible usages are all bare `constraint`, so the severity rule keyed
  on form-and-cause leaves the fixture generating. *If false → the frozen twin stops generating,
  and either the fixture or the severity rule has to move; the fixture cannot (byte-pinned at
  `tests/.../test_d5_variants.py:29`), so the rule would.*

  **Recorded fact, not an assumption (design-review F2).** The reason B5 holds today is narrow and
  worth writing down: all 56 are bare `constraint`, so `source_form` is `plain_usage`, so
  `predicate_source` is `None` (`elaborate.py:1146-1147`), so `predicate_ir` stays `None` and the
  `SI_REDEFINITION_INVALID` raise is unreachable for them. That is luck about this fixture, not a
  property of the corpus. The form gate in B3 is what turns the luck into a rule, and the
  `plain_usage`-with-raising-predicate regression fixture (Validation Approach) is what pins it.

## Key Decisions

Numbered to the eight questions the brief assigns; D9 was added in revision.

- **D1 — Domain representation.** One usage-tier record kind on the instance graph,
  `InstanceGraph.constraint_usages: dict[DeclarationId, ConstraintUsageRecord]`, joined to the
  per-occurrence tier by the `declaration_id` `ConstraintNode` already carries
  (`elaboration/graph.py:196`). The identity travels all the way into the catalog:
  `ConstraintCatalogUsageRecord` gains a `declaration_id` field and the projection dict keys on it,
  replacing the `(usage_qualified_name, display_name)` string pair. QN and display name stay as
  display metadata. *Rejected: a separate parallel inventory beside the graph (violates D-3 /
  invariants 40, 48). Rejected: widening `ConstraintNode` itself (a non-reaching usage has no
  scope, so no `NodeId`, and the two-tier accounting Q5 requires collapses). Rejected: keeping the
  QN string key on the catalog row (sound only for the narrower admitted-only population; once the
  rows are the domain, two anonymous usages sharing a short name silently merge, and the
  preflight's domain↔catalog join could only be made by qualified-name string matching — which the
  spec's `[HARD]` identity row forbids).*
- **D2 — Inapplicability mechanism.** Model annotation: a doc comment on the constraint usage whose
  first line is exactly `@inapplicable: <reason>`, read at elaboration and recorded as an
  `Inapplicability` record on the usage-tier record — so it travels in the graph and the snapshot,
  and no downstream route re-reads the source. Strictly parsed — a first line beginning
  `@inapplicable` that does not match the shape is a generation-halting error, never a silent
  no-op. *Rejected: a reviewed catalog-level acceptance file (a second hand-maintained inventory
  joined by identity — the parallel authority D-3 purged, needing its own fingerprinting seam).
  Rejected: a SysML `metadata def` in a shipped support library (more SysML-native and
  parser-validated, but this repo ships no `.sysml` library and reads no `MetadataUsage`).*
- **D3 — Gate home.** Two layers, both on the graph, none at extraction. Elaboration asserts the
  minting invariant where the sweep and the mint are both in scope; `graph.validate()` asserts
  per-record structure (closed vocabulary, exactly one disposition, join arity); a fifth generation
  preflight `_preflight_constraint_totality(graph)` asserts the domain↔catalog↔entry join **by
  `declaration_id`** at the fail-before-mutate boundary in `_generate_package_from_graph`, beside
  steps 1.5–1.7. *Rejected: extraction-time. Extraction no longer owns constraint facts on the
  exact route, and a gate there would not run at all on the from-snapshot route — forfeiting the
  three-route parity criterion.*
- **D4 — Snapshot version rule.** Bump `INSTANCE_GRAPH_SCHEMA_VERSION` to `instance-graph/v3`. No
  v2 reader is kept. Fail-closed needs no new code: a v2 payload is refused by the exact version
  comparison (`instance_graph.py:927-932`), and a v3-labelled payload missing `constraint_usages`
  is refused by the exact graph key-set check (`:933-937`). *Rejected: an additive-optional field
  at v2 (the document fingerprint covers the whole graph, so there is no additive free ride, and an
  optional field would let a truncated payload load silently).*
- **D5 — Token spellings and precedence.** See
  **[Token Vocabulary](#token-vocabulary-item-3-cites-this-section)** — three kinds, a closed reason
  set per kind, derived severity, and an ordered precedence rule so co-firing causes resolve the
  same way every run. *Rejected: the epic's `executable` spelling for the first kind (contract
  vocabulary governs, and `eligible` matches the existing `Eligibility` field). Rejected: a flat
  match table (rows demonstrably co-fire, and invariant 2 requires exactly one disposition).*
- **D6 — REQ-EXT-09's internal conflict.** Row rewrite, not a domain-boundary change. The domain
  becomes every `ConstraintUsage` *including* `RequirementUsage` and its `satisfy` subtype; the
  named satisfy exclusion is then a disposition *inside* the domain, which removes the
  contradiction. The row's subject also stops being "swept by `collect_constraint_manifest`", and
  its new evidence pointer lands **before** the sweep is deleted. *Rejected: narrowing the domain
  to exclude requirement-side forms (Q7 requires an out-of-scope form to carry a named visible
  exclusion, and a form outside the domain cannot carry one).* Neither resolution moves the
  headline: `catf_mfe_d5` authors no `satisfy` and no requirement usage, so its authored population
  is 65 either way.
- **D7 — Manifest fate and the independent oracle, together.** Retire the sweep: delete
  `collect_constraint_manifest`, `_classify_constraint_kind`, `_constraint_owner_kind`,
  `ConstraintManifestEntry`, `ConstraintKind`, and the seven `test_extractor.py` call sites. The
  oracle that replaces it is a reviewed expected-population file per constraint-bearing fixture,
  with a license-free scanner guarding the expectations. Coverage is closed in
  **[Oracle Coverage](#oracle-coverage)**, not left to the plan. *Rejected: demoting the sweep to a
  test-side oracle. It runs through the same adapter enumeration the domain uses, so it cannot
  detect the failure mode that matters (a usage the sweep never sees), and keeping it means keeping
  a classifier that duplicates `_constraint_metadata`.*
- **D8 — Recapture scope: the 21 snapshot-bearing fixtures, not 37.** The 16 corpus fixtures that
  carry no snapshot do not gain one. Minting a snapshot where none existed is new coverage, not
  recapture: it enlarges the byte-identity gate surface and the fixture corpus, which is scope
  growth past the Item 7 register's "one reviewed recapture at its final schema". The schema change
  does not force it — a fixture with no snapshot exercises no snapshot route. *Rejected: the
  37-fixture reading. 37 is the corpus row count (`epic_elaborate_first_architecture.md:302`,
  `:378`), 21 is the snapshot-bearing subset; the count is recorded at execution in
  `verification.md` rather than taken as a target.*
- **D9 — Mint site: inside the existing loop.** The record is minted at the top of
  `_build_constraint_nodes`'s existing per-usage loop (`elaborate.py:998-1004`), before the scope
  loop, and each `ConstraintNode` takes its form and identity metadata from the record. One
  enumeration, one classification, and the tier join is true by construction rather than by
  assertion. *Rejected: a separate `_build_constraint_usage_records()` pass (a second
  `elements_of_type` enumeration and a second `_constraint_metadata` call over one population —
  the drift the one-authority rule exists to stop, at a smaller scale).*

## Token Vocabulary (Item 3 cites this section)

Contract vocabulary governs (`eligible`, not the epic's `executable`). Disposition kinds are a
closed set of three; reason tokens are a closed set per kind; severity is derived, never authored.

### Precedence — an ordered rule, not a match table

Exactly one disposition per usage is an invariant, and the causes below co-fire (a `satisfy` owned
by a `calc def` matches two rows; a `BLOCK` decision on a usage that expands to nothing matches
two more). Evaluate in this order and stop at the first match:

1. **Form gate.** Runs first, before any predicate walk (this is also the rule that keeps minting
   non-raising — see B3). `source_form == "satisfy_reference"` → `excluded` /
   `out_of_scope_satisfy`.
2. **Expansion cause.** If the attachment lookup returned no scopes → `non_reaching`, with the
   cause token from `_attachment`. Profile eligibility is **not** consulted.
3. **Profile eligibility.** Consulted only for a usage that expanded to at least one scope.

| step | kind | reason | when | severity |
|---|---|---|---|---|
| 1 | `excluded` | `out_of_scope_satisfy` | source form `satisfy_reference` | `info` |
| 1 | `excluded` | `out_of_profile_owner` | owner kind is `requirement_def` | `info` |
| 2 | `non_reaching` | `owner_absent` | no semantic owner (`elaborate.py:522-523`) | `error` if asserted, else `info` |
| 2 | `non_reaching` | `owner_kind_unattachable` | owner kind has no scope expansion and is in executable scope (`calc_def`, …) | `error` if asserted, else `info` |
| 2 | `non_reaching` | `owner_has_no_occurrences` | attachable owner kind, zero occurrences (vacuous) | `warning` if asserted, else `info` |
| 2 | `non_reaching` | `classification_incomplete` | zero scopes **and** an asserted form whose classification cannot complete | `error` |
| 3 | `eligible` | `admitted` | `Eligibility.ADMIT` | `info` |
| 3 | `excluded` | `non_numerical` | `Eligibility.NON_NUMERICAL` | `info` |
| 3 | `excluded` | `unassessed_form` | `Eligibility.UNASSESSED` | `info` |
| 3 | `excluded` | `profile_blocked` | `Eligibility.BLOCK` | `info` |

**A `requirement_def` owner is an out-of-profile exclusion, not an unreachable assert.** Shipped
documentation already rules this: an out-of-profile owner "draws a named visible exclusion rather
than an unreachable-assert error" (`docs/architecture/modeling-assumptions.md:473-474`). So
`requirement_def` is resolved at step 1 by owner kind, before the expansion cause is consulted, and
never produces `error` — even for an asserted form. Only owner kinds that are *in executable scope*
and lack attachment capability (`calc_def` today) reach `owner_kind_unattachable` and invariant 9's
halt. Collapsing the two would halt where the shipped doc promises a visible exclusion.

**A non-reaching BLOCK usage emits no halt, and that is deliberate.** `SI_CONSTRAINT_BLOCKED` is
raised inside the scope loop (`elaborate.py:1018-1029`), so a usage whose profile decision is
`BLOCK` but which reaches no instance produces no diagnostic — step 2 wins and it catalogs as
`non_reaching`. Blocking is a statement about executing a predicate; there is nothing to execute.
For a usage that *does* expand, the existing `SI_CONSTRAINT_BLOCKED` halt is unchanged (a Non-Goal).

**Asserted forms** are `definition_typed`, `inline`, `named_usage_reference`. `plain_usage`,
`requirement_constraint`, and the new `satisfy_reference` are not asserted. The severity column's
`error` cells are invariant 9's halt, and their diagnostic names the usage **and the missing
attachment**; the `warning` cell is invariant 61's vacuous gate, whose authoring advisory names the
usage and its detached owner.

**Source forms** become six: the five `_constraint_metadata` emits today plus `satisfy_reference`,
tested ahead of the `plain_usage` fall-through.

**Item 3 coordination.** Every input Item 3's feasibility denominator needs is present after this
item — `declaration_id`, `source_form`, `disposition.kind`, `disposition.severity`,
`inapplicability`, and `occurrence_count`. Item 3 adds no usage-tier field and renames nothing; it
reads `inapplicability is not None` to drop a vacuous asserted gate from the denominator
(invariant 61) and `occurrence_count` to relate the two tiers.

## Architecture

The flow, with the changed hop marked:

```
model → _index_constraint_associations (pre-expansion sweep, exists today)
      → _build_constraint_nodes' per-usage loop
          → [NEW] form gate → mint ConstraintUsageRecord + disposition   (pre-expansion)
          → scope loop → per-occurrence ConstraintNodes (unchanged)
      → graph.validate()  (per-record structure; live, both decode paths, sealed context)
      → codec v3          (carries constraint_usages; fingerprint covers it)
      → project()         → catalog.usage_records = the whole domain, keyed by declaration_id
      → _preflight_constraint_totality → generation
```

**Boundaries.** Elaboration decides dispositions; nothing downstream re-derives one. Projection
renders, it does not classify — the rule the exact route already follows for entry points. The
preflight reads and refuses, it never repairs.

**The join, by identity end to end.** `ConstraintUsageRecord.declaration_id` ↔
`ConstraintNode.declaration_id` ↔ `ConstraintCatalogUsageRecord.declaration_id`. Each usage record
carries `occurrence_count`, so the join has a checkable arity in both directions: every occurrence
node's declaration id resolves to exactly one usage record, and every usage record's count equals
the number of occurrence nodes that name it. `eligible` with `occurrence_count == 0` is a
contradiction and fails. No step of this join uses a qualified-name string.

**Three-route parity is proven by test, not by the fingerprint.** The document fingerprint shows
the snapshot bytes are internally coherent; it says nothing about whether the live route,
re-elaborating the same model, mints the same domain. Those are different claims, and the second is
the one that can drift. The concrete drift risk is D2: reading an `@inapplicable:` doc comment is a
live-only elaboration step, so if doc-comment reachability differs — for a relocated source tree,
say — live and snapshot could diverge while both seal cleanly. This repo has been bitten by exactly
that class before, where a multi-hop EXPOSE resolved correctly live and mis-wired from a snapshot
with every seal passing. The field-for-field parity test in Validation Approach carries this
weight and is not redundant with the fingerprint.

## Required Invariants

1. **Minting totality.** The declaration-id set of `graph.constraint_usages` equals the key set of
   `self._constraint_associations`, which `elaborate.py:388-395` already proves equal to the
   pre-expansion sweep. Asserted in elaboration, where both are in scope.
2. **Exactly one disposition per member.** Each record has exactly one disposition; its kind is one
   of the three; its reason is in that kind's closed set; its severity matches the table; the
   precedence rule produced it. Asserted in `graph.validate()`.
3. **Join integrity, both directions, by identity.** Every `ConstraintNode.declaration_id` resolves
   to exactly one usage record; every record's `occurrence_count` equals its node count; every
   catalog usage row's `declaration_id` resolves to exactly one domain member. Asserted in
   `graph.validate()` and re-asserted against the catalog in the preflight. No qualified-name
   string matching anywhere in the join.
4. **Catalog totality.** `catalog.usage_records` has exactly one row per domain member. The catalog
   is `None` only when the domain is empty — never when the domain is non-empty and expansion
   produced nothing.
5. **Minting never raises, for any form.** The form gate runs before any predicate walk or
   definition cross-check. A `plain_usage`, `requirement_constraint`, or `satisfy_reference` usage
   always yields a visible record, whatever its predicate would do if walked. An **asserted**
   non-reaching usage whose classification cannot complete — the `SI_REDEFINITION_INVALID`
   (`elaborate.py:1166-1175`) and definition-identity (`:1149-1163`) paths — also yields a record,
   with `classification_incomplete` at error grade, and the completeness gate halts with a
   diagnostic naming the usage. The halt is preserved; what changes is that it arrives as a named
   disposition rather than a bare invariant error that leaves *every* usage in the model without a
   carrier. For a usage that **does** expand, today's raises are unchanged.
6. **Inapplicability never rewrites a disposition.** Carrying an `Inapplicability` record leaves
   kind, reason, and severity unchanged, including for the halting case. Marking an asserted,
   structurally-unattachable gate inapplicable does not suppress the halt: invariant 9 is about a
   structural authoring error, invariant 61 is about coverage.
7. **Severity keys on form and cause together.** No non-asserted form ever produces `error`.
8. **Owner-kind classification refuses rather than guesses.** The owner-kind map at
   `elaborate.py:1177-1182` ends in `.get(..., type(owner).__name__.lower())` — a silent fallback
   that would let an unmapped owner kind be graded by accident. It becomes a refusal: an owner kind
   not in the closed map fails elaboration by name.

## Component Overview

- **`ConstraintUsageRecord`, `UsageDisposition`, `Inapplicability`** — `elaboration/graph.py`,
  beside `ConstraintNode`. The domain member and its disposition. Sketch:

  ```python
  @dataclass(frozen=True)
  class UsageDisposition:
      kind: str            # eligible | excluded | non_reaching
      reason: str          # closed set per kind
      severity: str        # info | warning | error
      detail: str          # names the usage and the cause
  ```

  `ConstraintUsageRecord` carries `declaration_id`, `usage_qualified_name`, `display_name`,
  `source_form`, `owner_kind`, `owner_qualified_name`, `membership_kind`, `is_negated`,
  `source_file`, `source_line`, `occurrence_count`, `disposition`, `inapplicability`, and
  `definition_qualified_name` — the last non-`None` iff `source_form == "definition_typed"`,
  keeping the existing FK convention (`resolution/models.py:499-501`). That field plus
  `declaration_id` **is** the explicit definition-to-usage join invariant 28 / LC-E05 require, and
  it is what keeps the name of a `constraint def` that went unassessed because its usage never
  reached an instance. The record carries no `predicate_ir` — that authority stays on the
  occurrence tier, which is also what lets the mint path stop before the predicate walk.
- **`_attachment(owner)`** — `elaboration/elaborate.py`, replacing `_scopes_for_owner`'s bare tuple
  return with `(scopes, cause)` over the three-cause split so an empty result carries why.
- **The form gate and mint, inside `_build_constraint_nodes`** — same file, at the top of the
  existing per-usage loop (D9). Classifies form from membership and type tests only, mints the
  record, then runs the unchanged scope loop.
- **`_constraint_metadata`** — same file, split so the form/identity half is callable without the
  predicate-IR and definition-identity half, and gaining the `satisfy_reference` form.
- **Codec `constraint_usages` encode/decode** — `snapshot/instance_graph.py`, plus the version
  constant.
- **`_build_constraint_catalog`** — `elaboration/project.py`, rendering the domain into
  `usage_records` keyed by `declaration_id`, and keying its `None` return on the domain.
- **`ConstraintCatalogUsageRecord`** — `resolution/models.py`, gaining `declaration_id` (the new
  identity and dedup key, replacing the QN string pair), `disposition`, and `inapplicability`;
  population widens from admitted-only to the whole domain.
- **`_preflight_constraint_totality`** — `cli/__init__.py`, the fifth preflight.
- **Expected-population files + scanner** — `tests/`, the independent oracle (see below).

## Oracle Coverage

Closing design-review F4 — the oracle's coverage is its load-bearing property, so it is decided
here rather than parked.

- **Which fixtures carry expectation files: all 31 constraint-bearing fixture directories** under
  `tests/fixtures/` (measured at `ccf4c21`; the count is re-measured and recorded at execution).
  Not a chosen subset — a corpus-wide totality claim needs corpus-wide expectations.
- **What an expectation file holds.** One row per authored constraint usage: usage qualified name,
  display name, owner qualified name, source file, source line. Authored by reading the `.sysml`
  source, reviewed as source-derived. The totality test asserts the domain against it **by identity
  list**, not by count, so a swap of one usage for another fails.
- **What the scanner enumerates, and the rule for a missing file.** The license-free scanner walks
  every fixture directory, not only those with expectation files. A directory that contains a
  constraint declaration and has no expectation file is a **test failure naming the directory** —
  a missing expectation is a visible gap, never silent coverage. This is what keeps a newly added
  fixture from quietly reducing the oracle's reach.
- **The scanner's matching rule.** Strip `//` line comments and `/* … */` blocks first, then match
  statement-initial `constraint`, `assert`, `require constraint`, `assume constraint`, and
  `satisfy`, excluding `constraint def` (a definition, not a usage). It emits declaration
  identities — keyword plus name plus line — and compares them to the expectation file's rows, so
  the guard is identity-shaped like everything else here, not a count.
- **Known false-positive and false-negative classes, stated because the scanner is a heuristic.** A
  declaration split across lines between the keyword and the name; the keyword inside a string
  literal; annotation-prefixed forms. The scanner's job is drift detection on the expectation file
  as fixtures change — it is not a parser, and it is never the thing the domain is checked against.
  When it and an expectation file disagree, the expectation file is re-derived from source by hand.

## Non-Goals

Carried from the spec: the coverage denominator, report vocabulary, and TEAx projection (Item 3);
executing calc-def-owned gates (Item 6); the CATF derivative migration and the all-65 disposition
table (Item 5); the `[m]`-unit-literal defect (Item 4); any parallel manifest or catalog inventory;
changing BLOCK-halts-generation semantics for expanded usages; migrating the frozen CATF twins;
re-planning ELABORATE-FIRST Item 7. Additionally: this design does not add snapshots to fixtures
that lack them (D8), and does not edit TEAx (the re-vendor is ordered below but lands there).

## Cross-Repo Landing Order

Closing design-review F6. An ordered list, with what breaks if it is violated.

1. **This repo (`sysml-codegen`) lands first, complete and self-sufficient.** Domain, v3 codec,
   catalog `3.0.0`, preflight, oracle, doc corrections, recapture. Generation does not depend on
   any other repo accepting the new schema, so this step is releasable alone. *Violate it by
   splitting the codec bump from the catalog bump and a package seals with a v3 graph and a 2.0.0
   catalog token — an internally inconsistent artifact that no version check catches.*
2. **The companion (`agentic-mbse`) needs no change, stated affirmatively.** The reason is checkable
   rather than assumed: `_index_constraint_associations`'s cross-check (`elaborate.py:388-395`)
   already requires the constraint profile to return a decision for *every* swept `ConstraintUsage`
   subtype, `satisfy` included — a usage with no decision is already a hard failure today. So the
   domain never asks the companion for a decision it does not already produce. *Violate this by
   assuming a companion change is needed and the companion worktree drifts from the codegen branch
   for no reason.*
3. **Documentation corrections land before confirmation tests run** (owner-directed sequence), and
   specifically D6's REQ-EXT-09 rewrite lands its new evidence pointer **before**
   `collect_constraint_manifest` is deleted. *Violate it and there is a window where the shipped
   row cites a function that no longer exists — the doc-before-tests rule broken in the one place
   this item was supposed to fix.*
4. **The single reviewed recapture is the last *fixture-committing* step within this repo**, at the
   final schema, under the timestamp-churn diff protocol. It is not the last step overall: the
   three-route parity and fail-closed tests need v3 snapshot bytes to run at all, so during
   development they capture to a temp directory, and the committed-fixture forms of those tests run
   *after* the recapture. Stating it this way keeps the owner's "expected outputs captured before
   confirmation tests run" rule honest — the reviewed bytes are the expected output, and the
   confirmation run reads them, not the other way round. *Violate it by recapturing before the
   schema settles and the item pays a second recapture, which the Item 7 register forbids; violate
   it the other way — reverse-engineering the expectation from whatever the recapture produced —
   and the confirmation is circular.*
5. **TEAx re-vendors `ACCEPTED_CATALOG_SCHEMA_VERSIONS` after this repo lands**, tracked as a
   follow-up in the CONSTRAINT-SEMANTICS epic's cross-repo notes. B3 forbids TEAx importing this
   repo, so no automated check can enforce it from here. *Violate it by bumping TEAx first and TEAx
   accepts a schema no generator produces; skip it entirely and TEAx fails closed on every newly
   generated package — loudly, which is the intended failure direction.*

**Item 7 evidence-invalidation register — entries written now, not discovered later.** The v3
schema bump plus the 21-fixture recapture invalidates: every paused Item 7 snapshot-route
observation taken against `instance-graph/v2` bytes; the byte-identity comparisons on the 21
recaptured fixtures; and any Item 7 evidence citing `collect_constraint_manifest` as the population
definition. These go into the epic's register in this landing.

## Implementation Notes

- **Documentation edit set**, in order: `docs/architecture/modeling-assumptions.md:476-477` (drop
  the "today a usage that reaches no instance gets no carrier at all" parenthetical; state the
  disposition); `:489-496` (replace the pending-proof paragraph and the
  `collect_constraint_manifest` subject with the domain and the reviewed expected-population
  oracle); `docs/architecture/reference/01-extraction.md:20` (REQ-EXT-09 rewrite per D6);
  `docs/architecture/verification-matrix.md:336` (REQ-EXT-09 row + grade) and `:214` (REQ-CL-04
  row, PARTIAL note replaced by what the new tests prove).
- **`CATALOG_SCHEMA_VERSION` bumps `2.0.0` → `3.0.0`** with its pin in
  `tests/conformance/test_catalog_schema_version.py`. The population *and* the key of
  `usage_records` change, both breaking for a consumer reading it as admitted-only and QN-keyed. A
  consumer recovers the old set exactly by filtering `disposition.kind == "eligible"`.
- **The `@inapplicable:` parse must be defined against the seam, not against "the doc comment".**
  `_extract_documentation` (`extraction/extractor.py:803-814`) collects every `Comment` owned
  member, applies `.strip().strip("*").strip()` to each body, and joins the survivors with `\n`.
  So: "first line" means the first line of the **joined** string; a usage with multiple comments
  where a later one carries the marker is a malformed-annotation halt, not a silent accept; and the
  `strip("*")` means a `/* @inapplicable: … */` body arrives already trimmed. The de-risk spike
  (below) confirms this reading on a real annotated fixture before the parse is written.
- **`satisfy_reference` also moves expanded satisfy usages.** Adding the form changes
  `ConstraintNode.source_form` for satisfy usages that *do* expand, which moves their catalog rows
  and the catalog fingerprint. Behaviorally inert — `predicate_source` is `None` either way — but
  baseline churn comes from this as well as from the schema token, and the plan should expect it.
- **Mutate the graph, not the bytes.** A snapshot with a record removed fails the document
  fingerprint before the gate ever runs, so the mutation tests must drop / duplicate / misjoin at
  the in-memory `InstanceGraph` level, then project and run the preflight.
- **`ConstraintCatalog` with usage rows and nothing else has never existed.** Moving the `None` rule
  from `graph.constraints` to the domain creates that combination (a model whose constraints are
  all calc-def-owned: `usage_records` populated, `concrete_entries` and `source_records` empty).
  Confirm the model constructs and its fingerprint is stable before relying on it.
- **Recapture protocol.** A full recapture rewrites every `captured_at`. Review is a timestamp-only
  diff check, then revert the fixtures whose only change is the timestamp.
- **Licensed runs** need `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; verify zero
  license-skip lines. There is no `.env` in this repo.

## Potential Risks

- **The doc-comment annotation is a magic string in prose.** Mitigated by anchoring it to the first
  line of the joined documentation and failing closed on a near-miss, so a typo halts rather than
  silently doing nothing. Residual: a doc comment that legitimately opens with that token.
  Accepted — the token is unambiguous and the failure is loud.
- **Newly-reached classification (B3).** The form gate is the mitigation, and invariant 5 is its
  statement. Residual: a model with an asserted, malformed, non-reaching gate now fails generation
  where it previously generated — intended severity-by-cause, but a real behavior change. It fails
  as a named `classification_incomplete` halt at the completeness gate, not as a bare elaboration
  invariant error, so every other usage in the model still has a visible carrier when it does. The
  regression fixture and the severity-by-cause fixtures pin both directions.
- **TEAx skew.** The catalog bump requires a manual re-vendor that cannot be done from this repo.
  Generation does not depend on TEAx accepting, and the failure direction is fail-closed. Ordered
  in the landing list above.
- **Cause mis-split (B2).** If an owner kind exists that is attachable in principle but has no
  branch today, it would grade as `owner_kind_unattachable` and halt an asserted usage that should
  only warn. Mitigated by invariant 8: the owner-kind map's silent `.get()` fallback becomes a
  refusal, so an unmapped kind fails by name instead of being graded by accident.
- **Expectation files go stale.** Mitigated by the scanner's missing-file failure rule, which is
  what makes a newly added fixture visible rather than silently uncovered.

## Integration Strategy

The usage tier is additive to the graph and replaces nothing at the occurrence tier, so per-module
generation, the report aggregator, name safety, and the same-IR guard are untouched — they all read
`concrete_entries`. The catalog's `usage_records` list is widened in place and re-keyed rather than
joined by a second list, which keeps one authority. The manifest sweep and its models are deleted
in the same landing, with their seven test call sites, so nothing dead is stranded. Snapshot v3
lands with the single reviewed recapture of the 21 snapshot-bearing fixtures, which Item 7 then
consumes. The cross-repo sequencing is the ordered list above.

## Validation Approach

- **Independent totality (the row-anchoring evidence).** For each of the 31 constraint-bearing
  fixtures, assert the domain's identity list equals the reviewed expected-population file — 65 rows
  for `catf_mfe_d5`, zero absences. A regression that drops a usage pre-expansion fails by identity.
  The scanner asserts every constraint-bearing fixture directory *has* an expectation file and that
  its rows still match the source.
- **Mutation.** Remove a disposition, duplicate a usage record, and misjoin one (point a record's
  declaration id at another usage) at the graph level; each must fail generation with a diagnostic
  naming the usage's declaration id and QN.
- **Severity by cause.** Three fixtures: an asserted usage owned by a `calc def` (halts, diagnostic
  names the usage and the missing attachment per invariant 9); an asserted usage on a detached part
  def (warning-grade `non_reaching` + authoring advisory naming usage and detached owner, generation
  continues); a plain constraint whose predicate would BLOCK if asserted (generates, catalogs
  `excluded` / `unassessed_form`).
- **Non-raising mint (new, design-review F2).** A regression fixture holding a `plain_usage`
  constraint whose predicate *would* raise `SI_REDEFINITION_INVALID` if walked. It must produce a
  visible record and generate, proving the form gate runs before the predicate walk rather than
  relying on `catf_mfe_d5`'s luck.
- **Precedence.** Two fixtures for the co-firing cases the precedence rule resolves: a `satisfy`
  owned by a `calc def` (must be `out_of_scope_satisfy`, step 1) and a `BLOCK`-decision usage that
  reaches no instance (must be `non_reaching`, step 2, with no `SI_CONSTRAINT_BLOCKED`).
- **The frozen twin still generates.** `catf_mfe_d5` produces 65 usage carriers, 9 of them
  `eligible`, generation succeeds, and both twins stay byte-pinned.
- **Inapplicability.** An annotated vacuous asserted gate carries the record with its disposition
  kind, reason, and severity unchanged; a malformed annotation halts; a marker on a later comment
  body halts; the annotation's presence moves the graph fingerprint.
- **Three-route parity, field for field (strengthened, design-review F5).** On a fixture that
  carries `@inapplicable:` annotations, assert the live-minted domain equals the
  snapshot-round-tripped domain **field for field, record for record** — not just fingerprint
  equality, which would pass while diverging. Run it on the in-place snapshot and the relocated
  snapshot. This is the test that catches a live-only source read leaking into the domain.
- **Fail-closed shapes.** A v2 payload and a v3 payload missing `constraint_usages` each fail
  closed.
- **Catalog constructibility.** A domain with `usage_records` populated and `concrete_entries` /
  `source_records` empty builds a valid, deterministically fingerprinted `ConstraintCatalog`.
- **Suite gates.** Focused tests, full licensed codegen and companion suites with zero license-skip
  lines, `ruff` zero-new, `mypy` zero-new, fixture diff review, `git diff --check` — exact counts,
  including the recapture count and the re-measured constraint-bearing fixture count, recorded in
  `verification.md`.

## Next-Stage Handoff

**Fixed.** D1 (usage tier, `declaration_id` join end to end including the catalog row), D2
(annotation captured into the graph at elaboration), D3 (two-layer gate, no extraction-time check),
D4 (v3 bump, no v2 reader), D5 (tokens + precedence), D6 (row rewrite, evidence pointer before
deletion), D7 + Oracle Coverage (retire the sweep; all 31 constraint-bearing fixtures get
expectation files; missing file is a failure), D8 (21 fixtures), D9 (mint inside the existing
loop). The cross-repo landing order and the Item 7 register entries are fixed.

**Open for the plan.** The precise wording of the three diagnostics; whether the expectation files
are one per fixture directory or one consolidated file; the exact line anchors for the doc edits
after the earlier edits shift them.

**De-risk first.** The `@inapplicable:` doc-comment read (D2) is the only place this design depends
on behavior it has not observed — that a `ConstraintUsage`'s documentation is reachable at
elaboration the way it is at extraction (`extraction/extractor.py:803-814`), and that the
multi-comment join behaves as the Implementation Notes assume. A `/_my_spike` on one annotated
fixture confirms both in minutes and costs nothing if they hold.

---
Next Step: After approval → `/_my_plan`
