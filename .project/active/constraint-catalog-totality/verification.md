# Verification: Canonical Usage Domain and Catalog Totality

**Item:** CONSTRAINT-SEMANTICS Item 2
**Date:** 2026-08-12
**Branch:** `item7-rebuild` in both worktrees
**Codegen tip:** `d03a415` **Companion tip:** `bc69f04` (`/home/reid/1cfe/agentic-mbse-item7-rebuild`)

---

## The headline

`catf_mfe_d5` authors **65** constraint usages. The domain holds **65**, the shipped catalog
holds **65** `usage_records`, **9** of them reach at least one occurrence, and generation
succeeds. Before this item the same fixture produced **9** carriers and an **empty**
`usage_records` list.

**Correction to a design premise, and it is load-bearing enough to state first.** The design, the
plan, and the completion criteria all say "9 **eligible**". Measured, that is wrong: every one of
`catf_mfe_d5`'s 65 usages is a bare `constraint`, so the 9 that expand grade `excluded` /
`unassessed_form` and the fixture has **zero** eligible constraints. The 9 was always the count of
*visible dispositions* — at the parent commit the catalog carried 9 `excluded_records`, 0
`usage_records`, and 0 `concrete_entries`. Nothing mechanical moves; the correction strengthens the
item's premise, because the pre-item usage tier on this fixture was not merely truncated but
empty. Read every "9 eligible" in the design and plan as "9 reaching, 0 eligible".

The 65 split by disposition reason: **51** `owner_kind_unattachable` (calc-def owners), **5**
`owner_has_no_occurrences` (untyped design parts), **9** `unassessed_form`. The 51/5 split matches
the research's cause account exactly.

---

## Gates

### Codegen — full licensed suite

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/
```

**1826 passed / 34 skipped / 65 deselected / 0 failed.** Zero `no live syside license` lines
(the only valid licence proof; pass counts do not discriminate).

**The interpreter is not the documented one, and that is a finding.** `uv run --extra dev pytest`
resolves `agentic_mbse` to the **main checkout** `/home/reid/1cfe/agentic-mbse`, not the companion
worktree, and under it the suite does not even collect (`test_exact_constraint_route.py` cannot
import `preflight_identified`). Every gate here ran under
`/home/reid/1cfe/item7-rebuild-venv/bin/python`, whose editable `.pth` reads
`/home/reid/1cfe/agentic-mbse-item7-rebuild/src`. This is the F2 class in `CURRENT_WORK.md`
recurring, and it matters beyond convenience: under `uv run` the PD4 pin test would have compared
against a companion nobody was editing.

### Codegen — focused

**155 passed** across the eleven modules this item owns: totality, mint/precedence, attachment
cause, severity-by-cause, non-raising mint, annotation (+ both halt shapes), codec fail-closed ×2,
three-route parity, catalog totality + constructibility, seven mutations, the oracle, the companion
advisory sink + independence, and the upstream pin.

### Companion — full licensed suite, run in the companion worktree

```
cd /home/reid/1cfe/agentic-mbse-item7-rebuild && … -m pytest tests/
```

**1821 passed / 1 skipped / 5 deselected / 10 failed.** The 10 are the **pre-existing baseline**,
verified by stashing the change and re-running at HEAD: identical set, 1816 passed. **Zero new
failures.** The single skip is `Requires fusion_modeling CATF models not in this repo`, not a
licence skip; zero `no live syside license` lines.

### Lint and types — zero-new in both repos

| | before | after | verdict |
|---|---|---|---|
| codegen `ruff check src` | 14 | **12** | below baseline (two findings lived in the deleted `constraint_report.py`) |
| codegen `mypy src` | 57 | **55** | below baseline, same cause |
| companion `ruff check src` | 1 | **1** | unchanged |
| companion `mypy src` | 108 in 26 files | **108 in 26 files** | unchanged |

`git diff --check` clean in **both** repos. Companion working tree clean at `bc69f04`.

---

## The recapture, and its reviewed diff

**21 fixtures recaptured, once, at the final schema** — the count the design predicted.
`scripts/capture_v6_batch.py --verify` reported **15 captured / 22 refused / 0 deviations**; the
other **6** snapshot-bearing fixtures (`catf_mfe_d5`, `chain_spike_d5`,
`constraint_occurrence_demand_overrides_d5`, `gate_a_d5`, `solar_battery_d5`,
`nested_occurrence_override_probe`) sit outside the 37-fixture batch corpus and were captured
through `capture_instance_graph_snapshot`, the same public entry point the batch uses.

**Timestamp-churn protocol: nothing to revert.** No fixture changed by `captured_at` alone — the
envelope carries no such field, and all 21 changed substantively because the schema moved. The
diff was reviewed key by key across all 21:

| what moved | fixtures | expected? |
|---|---|---|
| `authority.instance_graph_schema` v2 → v3, `integrity.digest`, `instance_graph.fingerprint` | 21 | yes — the schema token and the digests it forces |
| `instance_graph.graph.constraint_usages` added | 21 | yes — the new tier |
| `instance_graph.graph.constraints[].owner_kind` | 3 | **a fourth cause the plan did not list — see below** |

**SURFACED — the fourth churn cause is real and it is a correction, not a rendering change.**
`catf_mfe_d5`, `gate_a_d5`, and `modeled_default_fidelity` move `owner_kind` from `partusage` to
`part_usage` on part-usage-owned constraints. `partusage` was never a graded kind: it came from the
`.get(..., type(owner).__name__.lower())` fallback that invariant 8 replaced with a closed map in
Phase 2. The plan's three legitimate causes (schema token, widened/re-keyed `usage_records`,
`satisfy_reference` moving expanded satisfy rows) did not anticipate it. The third of those did
**not** fire at all: no snapshot-bearing fixture authors an expanded `satisfy`.

**The frozen v2-refusal list is discharged.** From Phase 3 to Phase 7 the suite carried a fixed,
enumerated set of failures — committed at `v2-refusal-list.txt`, **61 nodes**, every one traced to
committed snapshot bytes that predate `constraint_usages`. It was the phase gate in that window
("no failure outside the list"), and it is now **zero**.

---

## Oracle coverage

**42 expectation files** at `tests/expectations/constraint_population/`, one per constraint-bearing
fixture directory. The design measured 31 at `ccf4c21`; the 11 new ones are this item's own
severity-by-cause, precedence, and annotation fixtures. **93 oracle nodes.**

- **24** fixtures are compared domain-against-file and agree exactly, usage for usage, line for
  line.
- **18** refuse elaboration by design (fail-closed probes, halting authoring errors, models not
  loadable alone). Their file still records the authored population and the source-drift rule still
  guards it; only the domain comparison is skipped, and the list is explicit in the test module.
- **Both loudness rules proven by breaking them**: removing `wi014_toy.json` fails naming
  `wi014_toy`; corrupting one `source_line` in it fails the drift check. Restored after each.

**Deviation, stated plainly: the expectation files are scanner-derived, not typed by hand.** The
design says "authored by reading the `.sysml` source". They were generated by the license-free
scanner — which *is* a source read — and then checked. The load-bearing property holds exactly: the
oracle does not descend from the domain, because the scanner shares no code, no adapter, and no
parse with the elaborator. What is weaker is independence between the scanner and the files, so the
drift rule cannot catch a scanner bug present at generation time. The mitigating evidence is real:
**the scanner and the domain were compared on all 42 fixtures before any file was written, and on
the 24 that elaborate they agreed with zero differences.** Two disagreements found in that
comparison were scanner bugs and were fixed (`assert not constraint` was unmatched; quoted names
needed the parser's own rule — quotes survive only when the inner text is not already a legal
identifier). Three files were spot-checked by hand against source.

---

## Cross-repo

| | value | pinned at |
|---|---|---|
| companion `CONSTRAINT_FACTS_SCHEMA_VERSION` | `constraint-facts/v3` (was v2) | `constraint_facts.py:54` |
| codegen `_upstream_pins.CONSTRAINT_FACTS_SCHEMA_VERSION` | `constraint-facts/v3` | `_upstream_pins.py:38`, compared against the installed companion by `test_upstream_pins.py` |
| `INSTANCE_GRAPH_SCHEMA_VERSION` | `instance-graph/v3` (was v2) | `snapshot/instance_graph.py:68` |
| `CATALOG_SCHEMA_VERSION` | `3.0.0` (was `2.0.0`) | `contracts/versions.py:18` |

**PD4's pin window was real and was closed inside Phase 4C.** C1 (companion bump) and C2 (codegen
pin) landed in one window; in between, every codegen run fails `test_upstream_pins.py`, because it
reads the *installed* editable companion.

**C0 seam confirmation (PD5): the mechanism is exactly as designed; three cited line numbers had
moved.** `CONSTRAINT_FACTS_SCHEMA_VERSION` `:54` ✓, `DiagnosticSeverity` `:57` ✓,
`EXTRACTION_DIAGNOSTIC_SEVERITY` `:78` ✓, `severity_for_kind` `:87` (design cited `:78-95`),
`ExtractionDiagnosticFact` `:217` with `__post_init__` at `:234-235` (design cited `:230-233`). No
stop-and-surface was triggered.

**Hand-off, not work this item performs: TEAx must re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to
include `3.0.0` after this repo lands.** B3 forbids TEAx importing this repo, so nothing here can
enforce it. While pending, TEAx fails closed on every newly generated package — loudly, the
intended direction. Do not bump TEAx first. Recorded in the epic's Item 3 section.

**Item 7 evidence-invalidation register** — three entries filed in
`.project/backlog/epic_constraint_semantics_contract.md`: v2-derived snapshot-route observations,
byte-identity comparisons on the 21 recaptured fixtures, and any evidence citing
`collect_constraint_manifest` as the population definition.

---

## Documentation anchors actually edited (PD3)

Re-`grep`ed before each edit rather than trusted:

| file | design anchor | actual | change |
|---|---|---|---|
| `docs/architecture/modeling-assumptions.md` | `:476-477` | `:476-477` | the "no carrier at all" parenthetical → the three `non_reaching` reasons |
| same | `:489-496` | `:489-496` | pending-proof paragraph + `collect_constraint_manifest` subject → the domain and the oracle |
| `docs/architecture/reference/01-extraction.md` | `:20` | `:20` | REQ-EXT-09 rewritten per D6 |
| `docs/architecture/verification-matrix.md` | `:214` | `:214` | REQ-CL-04 → **PASS**, audit-7 F2 closed |
| same | `:336` | `:336` | REQ-EXT-09 re-anchored to the oracle |
| `docs/architecture/reference/30-diagnostic-severity.md` | added by PD4 | `:60`, `:69`, `:157` | ADVISORY row, `constraint-facts/v3`, REQ-DIAG-03 "synthetic" note |

`grep` for `constraint-facts/v2` across `docs/` and `src/` returns nothing. The doc commit
(`5b1308a`) precedes the deletion commit (`f4f9698`) — landing-order step 3.

---

## What does not change — checked

- **Frozen CATF twins:** neither `catf_mfe_model` nor `catf_mfe_d5` had a line of constraint syntax
  edited. `catf_mfe_d5` still generates and stays byte-reversal-pinned (`test_d5_variants.py:29`
  passes).
- **The four `all_satisfied` assertions in `tests/execution/`** — untouched (Item 3's).
- **`SI_CONSTRAINT_BLOCKED` inside the scope loop** — unchanged, and pinned by the
  non-reaching-BLOCK fixture, which must produce *no* such diagnostic.
- **The occurrence tier** — `ConstraintNode` gains and loses nothing; per-module generation, the
  report aggregator, name safety, and the same-IR guard all still read `concrete_entries`.
- **Fixtures with no snapshot did not gain one** (D8). The 12 new fixtures carry none.
- **Companion scope** — one change only: the advisory, its severity-map entry, and the schema bump
  it forces.

---

## Left open, honestly

1. **An `inline`-form vacuous gate cannot be marked `@inapplicable:`.** SysIDE drops a `doc`
   comment written inside an inline-predicate constraint body entirely — and duplicates the
   predicate expression while doing so. So on that one shape the marker never reaches elaboration
   and D2's strict near-miss halt cannot fire. Not fixable here (it is upstream parser behavior).
   **Guarded rather than hidden:** `test_every_authored_inapplicable_marker_reached_the_domain`
   compares markers in source against `Inapplicability` on the domain across every comparable
   fixture, so a swallowed marker fails a test. The author workaround is a non-expression body
   (`assert constraint c : SomeDef { doc /* @inapplicable: … */ }`), confirmed working.
2. **Invariant 5's `classification_incomplete` has no constructible corpus trigger.** Implemented
   as designed, but neither path can be reached at this upstream version:
   `extract_expression_ir` returns an `UnsupportedNode` for every unrecognized construct and `None`
   only for a `None` expression, so the `SI_REDEFINITION_INVALID` raise is dead; the
   definition-identity `SI_EDGE_DANGLING` path needs a profile/live disagreement no fixture can
   author. Reachable by construction and pinned by the closed vocabulary, not by a behavioural
   fixture. Recorded rather than faked with a mock.
3. **The residual invariant-9 gap, accepted by design.** A vacuous gate whose owning `part def`
   *is* typed, but by a usage that is never instantiated, gets codegen's disposition and **no**
   author advisory. Closing it means reimplementing occurrence resolution in the companion — the
   second-representation smell this item removes. The containment direction is pinned from both
   sides (`constraint_domain_containment` codegen-side, `typed_but_uninstantiated.sysml`
   companion-side), so the gap can only ever be a missing advisory, never a false one.
4. **The two `.project/concepts/` references to `ConstraintManifestEntry`** are decision records of
   a superseded era and were deliberately left. The verification-matrix REQ-EXT-09 row names the
   retired sweep on purpose, to say what it was re-anchored *from*.
5. **Not run:** `/_my_audit`, `/_my_close`, `/_my_pre_pr`. Nothing was pushed; `main` untouched in
   both repos.

---

## Completion criteria

**sysml-codegen (`item7-rebuild`, `d03a415`)**

- [x] `catf_mfe_d5`: 65 usage carriers, generation succeeds, both twins byte-pinned. *(9 reaching,
      0 eligible — see the correction above.)*
- [x] Domain minted pre-expansion, one disposition each, `declaration_id` join end to end, gated at
      the fail-before-mutate boundary.
- [x] v3 codec, catalog `3.0.0`, single reviewed recapture, oracle over every constraint-bearing
      fixture, doc + requirement rows corrected, manifest sweep retired.
- [x] `_upstream_pins.py` matches the companion's bumped `CONSTRAINT_FACTS_SCHEMA_VERSION`.
- [x] All gates green, counts above.

**agentic-mbse (`item7-rebuild`, `bc69f04`)**

- [x] `vacuous_asserted_gate` at `ADVISORY`, naming usage and detached owner, with a location;
      severity writer-side in the closed map; schema bumped; companion tests and full licensed
      companion suite green (zero new failures).

**Spanning both**

- [x] Invariant 61 has both halves — the fingerprinted `non_reaching` disposition that travels, and
      the author-time advisory that does not.
- [x] Invariant 9's containment direction proven: companion trigger ⊆ codegen vacuous set.
- [x] Invariant 59 independence proven: the domain is byte-identical with the advisory suppressed.
