# Design: Canonical Usage Domain and Catalog Totality

**Status:** Draft
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
snapshot, gate, requirement rows — reads that tier.

## Related Artifacts

- **Spec:** `.project/active/constraint-catalog-totality/spec.md` (reviewed; 11 findings resolved
  in `spec-review.md`)
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
`ConstraintUsage` in the model with subtypes, builds `stable_usage_ids`, and *refuses* when the
constraint-profile decision inventory disagrees with that sweep in either direction
(`:388-395`). The complete authored domain is therefore constructed inside elaboration today and
then discarded. This item promotes it rather than inventing it — that is the whole design.

**The truncation point is one function.** `_scopes_for_owner` (`elaborate.py:521-539`) has
branches for `PartDefinition`, `PartUsage`, and `Package`, and returns `()` for everything else.
Empty comes back for two structurally different reasons that the return value cannot distinguish:
the owner kind has no branch (a `calc def`, 51 of the 56), or the owner is attachable in principle
but has zero occurrences (an untyped design part, the other 5). The severity rule needs that
distinction, so the function has to return the cause, not just the tuple.

**Form classification is already in the exact route.** `_constraint_metadata`
(`elaborate.py:1119-1137`) emits five source forms — `requirement_constraint`,
`named_usage_reference`, `definition_typed`, `inline`, `plain_usage` — with owner kind, owner QN,
source file and line beside them (`:1209-1224`). This is the anchor the spec names. Note the
companion module it reads facts from (`agentic_mbse/sysml/constraint_extraction.py`) is not being
deleted wholesale by ELABORATE-FIRST Item 7; scope 2 says "fold `extract_identified_constraint_facts`
into one live constraint-fact extraction pass" (`epic_elaborate_first_architecture.md:443-444`).
The spec's conclusion holds — build against `_constraint_metadata`, not the companion classifier —
but the exact route's dependency on that module survives the fold.

**`satisfy` really does fall through, and the spec's premise checks out.**
`SatisfyRequirementUsage` subclasses `RequirementUsage`, not `AssertConstraintUsage` — verified
against the syside stub in `.project/active/subtype-enumeration/spec-review.md:26` (stub line
16063). So a satisfy usage is swept as a `ConstraintUsage` subtype, misses the
`AssertConstraintUsage` branch, and lands on `plain_usage`, indistinguishable from a bare
`constraint`. The named exclusion Q7 requires is genuinely new classification work.

**There is already a usage tier in the catalog, but it is admitted-only.**
`ConstraintCatalogUsageRecord` (`resolution/models.py:474-503`) is one row per *admitted* usage,
deduped from eligible occurrence entries in `project.py:1145-1155`. It is the right shape in the
wrong population. Related: `_build_constraint_catalog` returns `None` when `graph.constraints` is
empty (`project.py:1084-1085`) — a model whose constraints are all calc-def-owned gets no catalog
at all, the totality hole in its purest form.

**The codec is exact-match on both version and key set.** `decode_instance_graph`
(`snapshot/instance_graph.py:918-982`) refuses any `schema_version` other than
`INSTANCE_GRAPH_SCHEMA_VERSION` (`:68`, currently `instance-graph/v2`), requires the graph key set
to be exactly `{occurrences, attrs, calcs, constraints, diagnostics}`, verifies the whole-document
fingerprint, and then calls `graph.validate()`. Structural invariants placed in `validate()` are
therefore enforced on the live route and the decode route alike, for free.

**Generation preflights are a named sequence at one boundary.**
`_generate_package_from_graph` (`cli/__init__.py:1044-1079`) runs constraint name safety,
duplicate output paths (1.5), params coverage (1.6), and registry class names (1.7) before
`_clear_output_directory`. That is the fail-before-mutate seam a fifth check joins.

**The manifest sweep has no `src/` caller.** `collect_constraint_manifest`
(`extraction/extractor.py:98-139`) plus `ConstraintManifestEntry` / `ConstraintKind`
(`extraction/constraint_report.py`) are reached only from `tests/conformance/test_extractor.py`
(7 call sites), yet both REQ-EXT-09 and REQ-CL-04 define their population by it.

**Cross-repo pin.** `CATALOG_SCHEMA_VERSION = "2.0.0"` (`contracts/versions.py:18`) rides inside
the fingerprinted model contract and is pinned by `tests/conformance/test_catalog_schema_version.py`.
TEAx vendors an accepted set by copy; B3 forbids importing this repo, so a bump is a manual
cross-repo act.

## Core Concept

The instance graph gains a **usage tier**: one `ConstraintUsageRecord` per authored
`ConstraintUsage`, minted from the sweep that already exists in
`_index_constraint_associations`, *before* `_scopes_for_owner` runs. Each record carries the
classification `_constraint_metadata` already produces plus exactly one **disposition** — kind,
reason token, severity — computed from the usage's form and the reason its owner did or did not
expand. The existing per-occurrence `ConstraintNode`s become the second tier and are unchanged;
the join between the tiers is the `declaration_id` both already carry, so no new key is minted.

The key insight is that **totality is a property of where records are born, not of a check added
later**. Today the population is defined by expansion, so no check written against it can see what
expansion dropped. Move the birth point upstream of expansion and the domain is complete by
construction; the gate's remaining job is join integrity — one disposition per member, every
occurrence entry joining to a member — which is a real, non-circular thing to check. Proof that
the domain itself is complete comes from outside it: a reviewed expected-population file per
fixture, asserted by identity.

This composes with existing pieces rather than adding parallel ones. Elaboration owns minting
(it is where the pre-expansion sweep lives). `graph.validate()` owns per-record structure (it
already runs on both the live and decode routes). The codec carries the tier (a version bump,
no shim). Projection renders the tier into the catalog's existing `usage_records` list, widening
its population from admitted-only to the whole domain. A fifth generation preflight owns the
join gate at the fail-before-mutate boundary. Nothing new is invented that an existing seam
already handles.

## Key Bets

- **B1.** The pre-expansion sweep in `_index_constraint_associations` sees every authored
  constraint usage — the profile-inventory cross-check at `elaborate.py:388-395` means a usage
  invisible to it is already a hard failure, not a silent drop. *If false → the domain is
  complete only relative to the adapter's sweep, and a usage the adapter cannot see stays absent
  with no diagnostic; the independent oracle would have to move from a reviewed expectation to a
  source-text parse of the `.sysml` files.*
- **B2.** Emptiness of `_scopes_for_owner` decomposes cleanly into exactly two causes — the owner
  kind has no attachment capability, or an attachable owner has zero occurrences — and that split
  is enough to key the severity rule. *If false → a third cause exists that is neither a halt nor
  a warning, and the severity rule mis-grades it in one direction or the other.*
- **B3.** Recording an inapplicability decision as a field beside the disposition, never as a
  rewrite of it, is sufficient for Item 3 to compute the feasibility denominator without a second
  usage-tier schema change. *If false → Item 3 pays the schema bump this item was supposed to
  absorb, and every fixture snapshot recaptures twice.*
- **B4.** `catf_mfe_d5`'s 56 invisible usages are all bare `constraint` (unasserted), so the
  severity rule keyed on form-and-cause leaves the fixture generating. *If false → the frozen twin
  stops generating, and either the fixture or the severity rule has to move; the fixture cannot
  (byte-pinned at `tests/.../test_d5_variants.py:29`), so the rule would.*

## Key Decisions

Numbered to the eight questions the brief assigns.

- **D1 — Domain representation.** One usage-tier record kind on the instance graph,
  `InstanceGraph.constraint_usages: dict[DeclarationId, ConstraintUsageRecord]`, joined to the
  per-occurrence tier by the `declaration_id` `ConstraintNode` already carries
  (`elaboration/graph.py:196`). *Rejected: a separate parallel inventory beside the graph
  (violates D-3 / invariants 40, 48 — a second thing to keep in sync). Rejected: widening
  `ConstraintNode` itself to carry non-reaching usages (a node with no scope has no `NodeId`, and
  it would erase the two-tier accounting Q5 requires).*
- **D2 — Inapplicability mechanism.** Model annotation: a doc comment on the constraint usage
  whose **first line is exactly** `@inapplicable: <reason>`, read at elaboration and recorded as
  an `Inapplicability` record on the usage-tier record. Strictly parsed — a first line beginning
  `@inapplicable` that does not match the shape is a generation-halting error, never a silent
  no-op. *Rejected: a reviewed catalog-level acceptance file (a second hand-maintained inventory
  joined by identity — exactly the parallel authority D-3 purged, and it would need its own
  fingerprinting seam). Rejected: a SysML `metadata def` in a shipped support library (more
  SysML-native and parser-validated, but this repo ships no `.sysml` library and reads no
  `MetadataUsage`; that is a new authoring dependency and new adapter surface for a consumer that
  does not exist until Item 3).*
- **D3 — Gate home.** Two layers, both on the graph, none at extraction. Elaboration asserts the
  minting invariant where the sweep and the mint are both in scope; `graph.validate()` asserts
  per-record structure (closed vocabulary, exactly one disposition, join arity); a fifth
  generation preflight `_preflight_constraint_totality(graph)` asserts the domain↔catalog↔entry
  join at the fail-before-mutate boundary in `_generate_package_from_graph`, beside steps 1.5–1.7.
  *Rejected: extraction-time. Extraction no longer owns constraint facts on the exact route, and
  a gate there would not run at all on the from-snapshot route — which would forfeit the
  three-route parity criterion.*
- **D4 — Snapshot version rule.** Bump `INSTANCE_GRAPH_SCHEMA_VERSION` to `instance-graph/v3`.
  No v2 reader is kept. Fail-closed needs no new code: a v2 payload is refused by the exact
  version comparison (`instance_graph.py:928`), and a v3-labelled payload missing
  `constraint_usages` is refused by the exact graph key-set check (`:936`). *Rejected: an
  additive-optional field at v2 (the document fingerprint covers the whole graph, so there is no
  additive free ride, and an optional field would let a truncated payload load silently).*
- **D5 — Token spellings.** See **[Token Vocabulary](#token-vocabulary-item-3-cites-this-section)**
  below — the named section Item 3 cites.
- **D6 — REQ-EXT-09's internal conflict.** Row rewrite, not a domain-boundary change. The domain
  becomes every `ConstraintUsage` *including* `RequirementUsage` and its `satisfy` subtype; the
  named satisfy exclusion is then a disposition *inside* the domain, which is what removes the
  contradiction. The row's subject also stops being "swept by `collect_constraint_manifest`".
  *Rejected: narrowing the domain to exclude requirement-side forms (Q7 requires an out-of-scope
  form to carry a named visible exclusion, and a form outside the domain cannot carry one).*
  Neither resolution moves the headline: `catf_mfe_d5` authors no `satisfy` and no requirement
  usage, so its authored population is 65 either way.
- **D7 — Manifest fate and the independent oracle, together.** Retire the sweep: delete
  `collect_constraint_manifest`, `_classify_constraint_kind`, `_constraint_owner_kind`,
  `ConstraintManifestEntry`, `ConstraintKind`, and the seven `test_extractor.py` call sites. The
  oracle that replaces it is a **reviewed expected-population file per constraint-bearing
  fixture** — usage identity plus QN plus source line, authored by reading the `.sysml` source,
  reviewed as source-derived, and asserted by identity list (not by count). A small license-free
  source-text scanner guards the *expectation*, not the domain: it counts constraint declarations
  in the fixture's `.sysml` files and fails when a fixture's authored count drifts from its
  expectation file. *Rejected: demoting the sweep to a test-side oracle. It runs through the same
  adapter enumeration the domain uses, so it cannot detect the failure mode that matters (a usage
  the sweep never sees), and keeping it means keeping a classifier that duplicates
  `_constraint_metadata`.*
- **D8 — Recapture scope: the 21 snapshot-bearing fixtures, not 37.** The 16 corpus fixtures that
  carry no snapshot do not gain one. Minting a snapshot where none existed is new coverage, not
  recapture: it enlarges the byte-identity gate surface and the fixture corpus, which is scope
  growth past the Item 7 register's "one reviewed recapture at its final schema". The schema
  change does not force it — a fixture with no snapshot exercises no snapshot route. *Rejected:
  the 37-fixture reading. 37 is the corpus row count (`epic_elaborate_first_architecture.md:302`,
  `:378`), 21 is the snapshot-bearing subset; the count is recorded at execution in
  `verification.md` rather than taken as a target.*

## Token Vocabulary (Item 3 cites this section)

Contract vocabulary governs (`eligible`, not the epic's `executable`). Disposition kinds are a
closed set of three; reason tokens are a closed set per kind; severity is derived, never authored.

| kind | reason | when | severity |
|---|---|---|---|
| `eligible` | `admitted` | expanded, `Eligibility.ADMIT` | `info` |
| `excluded` | `non_numerical` | expanded, `Eligibility.NON_NUMERICAL` | `info` |
| `excluded` | `unassessed_form` | expanded, `Eligibility.UNASSESSED` | `info` |
| `excluded` | `profile_blocked` | expanded, `Eligibility.BLOCK` | `info` (the existing `SI_CONSTRAINT_BLOCKED` diagnostic still halts) |
| `excluded` | `out_of_scope_satisfy` | source form `satisfy_reference` | `info` |
| `non_reaching` | `owner_kind_unattachable` | owner kind has no scope expansion (`calc_def`, `requirement_def`, …) | `error` if the form is asserted, else `info` |
| `non_reaching` | `owner_has_no_occurrences` | attachable owner kind, zero occurrences (vacuous) | `warning` if asserted, else `info` |

**Asserted forms** are `definition_typed`, `inline`, `named_usage_reference`. `plain_usage`,
`requirement_constraint`, and the new `satisfy_reference` are not asserted.

**Source forms** become six: the five `_constraint_metadata` emits today plus `satisfy_reference`,
tested ahead of the `plain_usage` fall-through.

**Item 3 coordination.** Every input Item 3's feasibility denominator needs is present after this
item — `source_form`, `disposition.kind`, `disposition.severity`, `inapplicability`, and
`occurrence_count`. Item 3 adds no usage-tier field and renames nothing; it reads
`inapplicability is not None` to drop a vacuous asserted gate from the denominator (invariant 61)
and `occurrence_count` to relate the two tiers.

## Architecture

The flow, with the changed hop marked:

```
model → _index_constraint_associations (pre-expansion sweep, exists today)
      → [NEW] mint one ConstraintUsageRecord per swept usage, with its disposition
      → _scopes_for_owner → per-occurrence ConstraintNodes (unchanged)
      → graph.validate()  (per-record structure; runs live AND on decode)
      → codec v3          (carries constraint_usages; fingerprint covers it)
      → project()         → catalog.usage_records = the whole domain
      → _preflight_constraint_totality → generation
```

**Boundaries.** Elaboration decides dispositions; nothing downstream re-derives one. Projection
renders, it does not classify — the same rule the exact route already follows for entry points.
The preflight reads and refuses, it never repairs.

**The join.** `ConstraintUsageRecord.declaration_id` ↔ `ConstraintNode.declaration_id`. Each
usage record carries `occurrence_count`, so the join has a checkable arity in both directions:
every occurrence node's declaration id resolves to exactly one usage record, and every usage
record's count equals the number of occurrence nodes that name it. `eligible` and
`occurrence_count == 0` is a contradiction and fails.

**Three-route parity** is structural, not a separate mechanism: the live route and both snapshot
routes reach projection through the same decoded `InstanceGraph`, and the codec fingerprint
covers the usage tier, so a route that disagreed could not have decoded.

## Required Invariants

1. **Minting totality.** The number of `ConstraintUsageRecord`s equals the number of usages in
   `stable_usage_ids`, and their declaration ids are the same set. Asserted in elaboration, where
   both are in scope.
2. **Exactly one disposition per member.** Each record has exactly one disposition; its kind is
   one of the three; its reason is in that kind's closed set; its severity matches the table.
   Asserted in `graph.validate()`.
3. **Join integrity, both directions.** Every `ConstraintNode.declaration_id` resolves to exactly
   one usage record; every record's `occurrence_count` equals its node count. Asserted in
   `graph.validate()` and re-asserted against the catalog in the preflight.
4. **Catalog totality.** `catalog.usage_records` has exactly one row per domain member. The
   catalog is `None` only when the domain is empty — never when the domain is non-empty and
   expansion produced nothing.
5. **Inapplicability never rewrites a disposition.** Carrying an `Inapplicability` record leaves
   kind, reason, and severity unchanged, including for the halting case. Marking an asserted,
   structurally-unattachable gate inapplicable does not suppress the halt: invariant 9 is about a
   structural authoring error, invariant 61 is about coverage.
6. **Severity keys on form and cause together.** No non-asserted form ever produces `error`.
7. **Identity vocabulary only.** The domain keys on `DeclarationId`; no qualified-name string
   matching is introduced.

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
  reached an instance.

- **`_attachment(owner)`** — `elaboration/elaborate.py`, replacing `_scopes_for_owner`'s bare
  tuple return with `(scopes, cause)` so an empty result carries why.
- **`_build_constraint_usage_records()`** — `elaboration/elaborate.py`, minting the domain from
  the existing sweep before `_build_constraint_nodes` expands it, and reading the
  `@inapplicable:` doc-comment annotation.
- **`_constraint_metadata`** — same file, gaining the `satisfy_reference` form.
- **Codec `constraint_usages` encode/decode** — `snapshot/instance_graph.py`, plus the version
  constant.
- **`_build_constraint_catalog`** — `elaboration/project.py`, rendering the domain into
  `usage_records` and keying its `None` return on the domain.
- **`ConstraintCatalogUsageRecord`** — `resolution/models.py`, gaining the disposition and
  inapplicability fields; population widens from admitted-only to the whole domain.
- **`_preflight_constraint_totality`** — `cli/__init__.py`, the fifth preflight.
- **Expected-population fixtures + scanner** — `tests/`, the independent oracle (D7).

## Non-Goals

Carried from the spec: the coverage denominator, report vocabulary, and TEAx projection (Item 3);
executing calc-def-owned gates (Item 6); the CATF derivative migration and the all-65 disposition
table (Item 5); the `[m]`-unit-literal defect (Item 4); any parallel manifest or catalog
inventory; changing BLOCK-halts-generation semantics; migrating the frozen CATF twins; re-planning
ELABORATE-FIRST Item 7. Additionally: this design does not add snapshots to fixtures that lack
them (D8), and does not change TEAx (the re-vendor is named as a handoff, below).

## Implementation Notes

- **Documentation is corrected before confirmation tests run** (owner-directed sequence). The edit
  set, in order: `docs/architecture/modeling-assumptions.md:476-477` (drop the "today a usage that
  reaches no instance gets no carrier at all" parenthetical; state the disposition);
  `:489-496` (replace the pending-proof paragraph and the `collect_constraint_manifest` subject
  with the domain and the reviewed expected-population oracle);
  `docs/architecture/reference/01-extraction.md:20` (REQ-EXT-09 rewrite per D6);
  `docs/architecture/verification-matrix.md:336` (REQ-EXT-09 row + grade) and `:214` (REQ-CL-04
  row, PARTIAL note replaced by what the new tests prove).
- **`CATALOG_SCHEMA_VERSION` bumps `2.0.0` → `3.0.0`** with its pin in
  `tests/conformance/test_catalog_schema_version.py`. The population of `usage_records` changes
  meaning, which is breaking for a consumer that reads it as admitted-only. A consumer recovers
  the old set exactly by filtering `disposition.kind == "eligible"`.
- **Mutate the graph, not the bytes.** A snapshot with a record removed fails the document
  fingerprint before the gate ever runs, so the mutation tests must drop / duplicate / misjoin at
  the in-memory `InstanceGraph` level, then project and run the preflight.
- **The catalog fingerprint moves on every constraint-bearing fixture**, and so does
  `semantic_fingerprint` (the catalog schema token rides inside the model contract). Expect
  baseline churn on constraint-bearing packages; baselines are format-exempt.
- **Recapture protocol.** A full recapture rewrites every `captured_at`. Review is a
  timestamp-only diff check, then revert the fixtures whose only change is the timestamp.
- **Licensed runs** need `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; verify zero
  license-skip lines. There is no `.env` in this repo.

## Potential Risks

- **The doc-comment annotation is a magic string in prose.** Mitigated by anchoring it to the
  first line and failing closed on a near-miss, so a typo halts rather than silently doing
  nothing. Residual: a doc comment that legitimately opens with that token. Accepted — the token
  is unambiguous and the failure is loud.
- **TEAx skew.** The catalog bump requires a manual re-vendor of `ACCEPTED_CATALOG_SCHEMA_VERSIONS`
  in TEAx, which cannot be done from this repo. Generation does not depend on TEAx accepting, so
  this lands without it; the handoff is named below.
- **Vacuous-versus-unattachable mis-split (B2).** If an owner kind exists that is attachable in
  principle but has no branch today, it would grade as `owner_kind_unattachable` and halt an
  asserted usage that should only warn. Mitigated by enumerating owner kinds explicitly against
  `_constraint_metadata`'s owner-kind map (`elaborate.py:1177-1182`) rather than defaulting.
- **Expected-population files go stale.** Mitigated by the scanner guard (D7); it exists for
  exactly this failure.

## Integration Strategy

The usage tier is additive to the graph and replaces nothing at the occurrence tier, so per-module
generation, the report aggregator, name safety, and the same-IR guard are untouched — they all read
`concrete_entries`. The catalog's `usage_records` list is widened in place rather than joined by a
second list, which keeps one authority. The manifest sweep and its models are deleted in the same
landing, with their seven test call sites, so nothing dead is stranded. Snapshot v3 lands with the
single reviewed recapture of the 21 snapshot-bearing fixtures, which Item 7 then consumes.

**Handoffs out:** Item 3 reads the [Token Vocabulary](#token-vocabulary-item-3-cites-this-section)
section and needs no schema change. The TEAx `ACCEPTED_CATALOG_SCHEMA_VERSIONS` re-vendor is a
cross-repo follow-up, tracked outside this item. Anything this landing newly invalidates in the
paused Item 7 evidence goes into the epic's evidence-invalidation register in this item.

## Validation Approach

- **Independent totality (the row-anchoring evidence).** For each constraint-bearing fixture,
  assert the domain's declaration-id/QN list equals the reviewed expected-population file — 65
  rows for `catf_mfe_d5`, with zero absences. Deleting a usage from a fixture, or a regression that
  drops one pre-expansion, fails by identity, not by count. The scanner guard asserts each
  expectation file's row count against the fixture's `.sysml` declaration count.
- **Mutation.** Remove a disposition, duplicate a usage record, and misjoin one (point a record's
  declaration id at another usage) at the graph level; each must fail generation with a diagnostic
  naming the usage's identity and QN.
- **Severity by cause.** Three fixtures: an asserted usage owned by a `calc def` (halts, diagnostic
  names usage and missing attachment); an asserted usage on a detached part def (warning-grade
  `non_reaching` + authoring advisory naming usage and detached owner, generation continues); a
  plain constraint whose predicate would BLOCK if asserted (generates, catalogs `excluded` /
  `unassessed_form`).
- **The frozen twin still generates.** `catf_mfe_d5` produces 65 usage carriers, 9 of them
  `eligible`, generation succeeds, and both twins stay byte-pinned.
- **Inapplicability.** An annotated vacuous asserted gate carries the record with its disposition
  kind, reason, and severity unchanged; a malformed annotation halts; the annotation's presence
  moves the graph fingerprint.
- **Three-route parity.** Live, in-place snapshot, and relocated snapshot produce identical domains
  and dispositions; a v2 payload and a v3 payload missing `constraint_usages` each fail closed.
- **Suite gates.** Focused tests, full licensed codegen and companion suites with zero license-skip
  lines, `ruff` zero-new, `mypy` zero-new, fixture diff review, `git diff --check` — exact counts,
  including the recapture count, recorded in `verification.md`.

## Next-Stage Handoff

**Fixed.** D1 (usage tier on the graph, `declaration_id` join), D3 (two-layer gate, no
extraction-time check), D4 (v3 bump, no v2 reader), D5 (token vocabulary), D6 (row rewrite), D7
(retire the sweep, reviewed expected-population oracle), D8 (21 fixtures). Documentation is
corrected before confirmation tests run.

**Open for the plan.** The exact ordering of the doc edits against the test landing; whether the
scanner guard covers all constraint-bearing fixtures or only the pinned twins; the precise wording
of the three diagnostics.

**De-risk first.** The `@inapplicable:` doc-comment read (D2) is the only place this design depends
on behavior it has not observed — that a `ConstraintUsage`'s documentation is reachable at
elaboration the way it is at extraction (`extraction/extractor.py:803-810`). A `/_my_spike` on one
annotated fixture confirms it in minutes and costs nothing if it holds. Everything else composes
with code read directly in Research Findings.

---
Next Step: After approval → `/_my_plan`
