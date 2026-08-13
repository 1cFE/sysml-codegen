# Expected Coverage Ledger (PD2)

**Epic:** CONSTRAINT-SEMANTICS, Item 3
**Created:** 2026-08-13 (Phase 0), extended Phase 1
**Authority:** the design's D3 bucket table, applied to each fixture's `.sysml` source.

## The expectation rule (PD2, DR-6)

Every account below is derived from **what the author wrote** — the fixture's SysML source read
against D3's bucket table — never transcribed from a catalog dump, a generated report, or Item 2's
disposition table. Each entry cites the file and line of every constraint usage it counted.

Reading the projected catalog to confirm *which usages a model declares* is a legitimate cross-check
of the source reading, and was used that way in the Phase 0 corpus probe. Reading it to obtain *the
counts* is the shortcut this rule forbids, and no entry below does it.

## D3's bucket table, restated for the reader

Two predicates decide the bucket:

- **asserted** ≡ the declaration is `assert constraint …` (source forms `definition_typed`, `inline`,
  `named_usage_reference`). A bare `constraint …`, a `require constraint …` inside a requirement, and
  a `satisfy` reference are **not** asserted.
- **inapplicable** ≡ the usage's doc comment carries an `@inapplicable:` marker.

| # | asserted | inapplicable | reaches an occurrence | bucket | contributes to |
|---|---|---|---|---|---|
| 1 | no | either | either | inventory only | `authored_usage_total` |
| 2 | yes | yes | either | inapplicable gate | `authored_usage_total`, `inapplicable_gate_count` |
| 3 | yes | no | yes (and admitted by the profile) | assessed gate | `authored_usage_total`, `applicable_gate_total`, `assessed_gate_count` |
| 4 | yes | no | no, or blocked by the profile | unassessed gate | `authored_usage_total`, `applicable_gate_total`, `unassessed_gate_count`, `unassessed_reasons[reason] += 1` |

`coverage_state` is `complete` when `applicable_gate_total > 0 and unassessed_gate_count == 0`,
`partial` when `applicable_gate_total > 0 and unassessed_gate_count > 0`, `none` when
`applicable_gate_total == 0`.

Headline (D6, over runtime statuses **and** the account): `violation` → `indeterminate` →
`full_satisfaction` (iff `unassessed_gate_count == 0 and assessed_gate_count > 0`) →
`partial_coverage` (iff `applicable_gate_total > 0`) → `not_assessed`.

---

## Ledger

Field order in every entry: `authored_usage_total` / `applicable_gate_total` / `assessed_gate_count` /
`unassessed_gate_count` / `inapplicable_gate_count` / `unassessed_reasons` / `coverage_state`.

### `fusion_tea` — the whole-dump site (`tests/execution/test_fusion_tea_real_teax.py:245`)

**Source evidence.** One constraint *usage* is declared in the whole fixture tree:

- `designs/generic_ife/ife_plant.sysml:155` — `assert constraint viability : 'Viability Threshold'`,
  inside `part def 'IFE Power Plant'`, which the model instantiates.

The other three grep hits are not usages:
`library/analyses/fusion_cycle.sysml:29` is `constraint def 'Viability Threshold'` — a *definition*;
`designs/generic_ife/ife_plant.sysml:159` and `designs/hif_ife/hif_plant.sysml:223` are prose inside a
doc comment and a `//` comment respectively.

**The open check from the design, resolved.** `hif_plant.sysml:223` reads
`// viability constraint is inherited from IFE Power Plant`. It is a comment; the HIF design declares
no second usage. The account is for **one** usage.

Asserted, not marked inapplicable, owner instantiated → bucket 3.

| field | value |
|---|---|
| `authored_usage_total` | 1 |
| `applicable_gate_total` | 1 |
| `assessed_gate_count` | 1 |
| `unassessed_gate_count` | 0 |
| `inapplicable_gate_count` | 0 |
| `unassessed_reasons` | `{}` |
| `coverage_state` | `"complete"` |

`headline = "full_satisfaction"`, `assessed_entry_count = 1`.

### `gate_a_d5` — bare-assert site (`test_constraint_verdicts_exact_route.py:171`)

**Source evidence.** `model.sysml:57` — `assert constraint viability : 'Viability Threshold'` inside
`part def Host`; `model.sysml:54` instantiates `part the_host : Host`. `model.sysml:21` is a
`constraint def`, not a usage. One usage, bucket 3.

**1 / 1 / 1 / 0 / 0 / `{}` / `complete`** → `headline = "full_satisfaction"`, `assessed_entry_count = 1`.

### `constraint_multi_instance` — bare-assert site (`:416`), and the two-tier asymmetry (DR-12)

**Source evidence.** `model.sysml:24` — `assert constraint nonneg : 'Nonneg Power'` inside
`part def Cell`; `model.sysml:30` declares `part cell : Cell [3]`, so the one authored usage expands to
three occurrences. `model.sysml:9` is a `constraint def`. One usage, bucket 3.

**1 / 1 / 1 / 0 / 0 / `{}` / `complete`** → `headline = "full_satisfaction"`,
**`assessed_entry_count = 3`**.

This is the deliberate asymmetry: `assessed_gate_count = 1` (usage tier) beside
`assessed_entry_count = 3` (occurrence tier). It is the two-tier rule working, not a defect.

### `constraint_def_owned_redefining` — bare-assert site (`:540`)

**Source evidence.** `model.sysml:27` — `assert constraint within : 'Within Limit'` inside
`part def Panel`; `model.sysml:39` instantiates `part panel : Panel`. `model.sysml:14` is a
`constraint def`. One usage, bucket 3.

**1 / 1 / 1 / 0 / 0 / `{}` / `complete`** → `headline = "full_satisfaction"`, `assessed_entry_count = 1`.

### `catf_mfe_d5` — descriptive-only (frozen twin, not edited)

**Source evidence — the two documented greps, re-run 2026-08-13** over
`tests/fixtures/catf_mfe_d5/**/*.sysml`:

- `assert constraint` → **0**
- `^\s*constraint def ` → **0**
- bare `^\s*constraint <name>` declarations → **65**

(70 source lines mention the word `constraint`; the other 5 are prose.) All 65 are bare `constraint`
usages — not asserted — so all 65 land in bucket 1 and nothing reaches the denominator.

**65 / 0 / 0 / 0 / 0 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

This is the shape that motivates the item: 65 authored checks, none assessed, and today the package
emits no report at all.

### `constraint_domain_plain_forms` — non-asserted inventory

**Source evidence.** `model.sysml:15` — `constraint blocked_if_asserted` (bare, inside
`part def Host`, instantiated at `:27`); `model.sysml:22` — `constraint unreached_plain` (bare, inside
the never-instantiated `part def Detached`). Neither is asserted → both bucket 1.

**2 / 0 / 0 / 0 / 0 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

Note the contrast with `catf_mfe_d5`: whether the owner is instantiated does not matter for a
non-asserted form. Bucket 1 is decided by the form alone.

### `constraint_domain_satisfy` — requirement-side inventory

**Source evidence.** `model.sysml:16` — `require constraint within` inside a requirement definition
(`requirement_constraint`); `model.sysml:25` — a `satisfy` reference on `part the_rig`
(`satisfy_reference`). Neither form asserts → both bucket 1.

**2 / 0 / 0 / 0 / 0 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

### `constraint_domain_detached_owner` — mixed partial (reused for the `partial_mixed` shape, PD4)

**Source evidence.** `model.sysml:14` — `assert constraint vacuous_gate` inside `part def Detached`,
which nothing instantiates → asserted, not marked, reaches nothing → bucket 4, reason
`owner_has_no_occurrences`. `model.sysml:21` — `assert constraint reached_gate` inside `part def Live`,
instantiated at `:26` → bucket 3.

**2 / 2 / 1 / 1 / 0 / `{"owner_has_no_occurrences": 1}` / `partial`**
→ `headline = "partial_coverage"`, `assessed_entry_count = 1`.

The assessed gate passes, and full satisfaction is still unclaimable. That is spec success criterion 3.

### `constraint_non_numerical` — partial by profile exclusion

**Source evidence.** Both usages are asserted and both owners are instantiated
(`part the_host : MixedPurposeHost`, `model.sysml:22`). `model.sysml:13` —
`assert constraint status_annotation`, whose predicate is a non-numerical equality the executable
profile does not admit → bucket 4, reason `non_numerical`. `model.sysml:17` —
`assert constraint positive_value` → bucket 3.

**2 / 2 / 1 / 1 / 0 / `{"non_numerical": 1}` / `partial`**
→ `headline = "partial_coverage"`, `assessed_entry_count = 1`.

This is the row-4 case that is *not* about reachability: an asserted gate the profile excluded stays in
the denominator as an unassessed one.

### `constraint_domain_inapplicable` — Appendix C's vacuous-gate cell, non-degenerate

**Source evidence.** `model.sysml:19-20` — `assert constraint marked_vacuous : Positive` whose doc
comment carries `@inapplicable: no build of this variant is planned`, inside the never-instantiated
`part def Detached` → asserted **and** marked → bucket 2. `model.sysml:27` —
`assert constraint reached_gate` inside `part def Live`, instantiated at `:32` → bucket 3.

**2 / 1 / 1 / 0 / 1 / `{}` / `complete`** → `headline = "full_satisfaction"`,
`assessed_entry_count = 1`.

The marked gate drops out of the denominator and one gate remains, so full satisfaction is claimable —
Appendix C's cell read with its antecedent satisfied. D4 rules only the degenerate case, below.

---

## New fixtures authored for this item (Phase 1)

Named `constraint_coverage_*`. One shape per fixture (PD4).

### `constraint_coverage_zero_eligible` — asserted gates, zero eligible entries

**Intended source.** One `assert constraint` inside a `part def` nothing instantiates, and no live
gate anywhere. Asserted, unmarked, reaches nothing → bucket 4.

**1 / 1 / 0 / 1 / 0 / `{"owner_has_no_occurrences": 1}` / `partial`**
→ `headline = "partial_coverage"`, `assessed_entry_count = 0`.

The zero-input aggregator's *partial* branch: a report with an empty input set that still says the
model has an unchecked gate. Today this model emits no report at all.

### `constraint_coverage_all_inapplicable` — D4's ruling

**Intended source.** One `assert constraint` carrying `@inapplicable:` in its doc comment, on a
`part def` nothing instantiates, and no other gate. Asserted and marked → bucket 2, and nothing lands
in bucket 3 or 4.

**1 / 0 / 0 / 0 / 1 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

D4: the full-satisfaction arm requires `assessed_gate_count > 0`, so zero assessments cannot claim it.
`inapplicable_gate_count = 1` is what distinguishes this from a descriptive-only model, whose
`inapplicable_gate_count` is `0`.

### `constraint_coverage_violation_partial` — spec success criterion 2

**Intended source.** One `assert constraint` on an instantiated part whose modelled values make the
predicate **false**, plus one `assert constraint` on a `part def` nothing instantiates.

**2 / 2 / 1 / 1 / 0 / `{"owner_has_no_occurrences": 1}` / `partial`**
→ `headline = "violation"` (the top precedence arm), `coverage_state = "partial"`,
`assessed_entry_count = 1`.

Coverage survives a higher-precedence headline: the report says "rejected on physics, *and* one gate
was never checked", which is the distinction the study policy needs.

### `constraint_coverage_eligible_inapplicable` — D9's refusal (generation must fail)

**Intended source.** One `assert constraint` on an **instantiated** part, carrying `@inapplicable:` in
its doc comment. Asserted, marked, and it expands → `disposition_kind == "eligible"` beside
`inapplicability_reason is not None`.

**No account.** Generation refuses by name at the coverage preflight, before any output is written:
*"`<usage QN>` (`<declaration_id>`) is marked inapplicable but produced `<n>` executable entries…"*.
This fixture is registered wherever a corpus sweep enumerates fixtures, so a sweep expects the refusal.

---

## Corpus probe cross-check (Phase 0, read-only)

The Phase 0 probe elaborated and projected every fixture directory that elaborates standalone (57 of
104) and scanned all 105 resulting usage records. It was used to confirm *which usages each model
declares*, never to obtain a count. Two results:

- **B3 holds.** `catf_mfe_d5`, `constraint_domain_plain_forms`, `constraint_domain_satisfy`, and
  `constraint_domain_satisfy_calc_def` all project a non-`None` `constraint_catalog` with non-empty
  `usage_records` and zero `eligible` rows. D5's trigger is readable from the catalog.
- **D9 breaks nothing that exists.** Zero of the 105 records are both `eligible` and carry an
  `inapplicability_reason`. The marker appears in five fixtures; four of them refuse elaboration
  already (they are negative fixtures), and in `constraint_domain_inapplicable` the marker sits on a
  `non_reaching` record.
