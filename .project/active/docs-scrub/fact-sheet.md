# Fact Sheet: What Is True at Epic HEAD

**Purpose:** the single truth source for the docs scrub (plan Phase 1). Every doc claim is
verified against these facts, never against another doc. Each fact carries provenance —
a code symbol or a release-note/epic section.

Provenance shorthand: `RN-7/9/10/11` = `.project/active/{warning-reconciliation,
plant-prefill,cross-part-wiring,alias-surfacing}/release-notes.md`; `EPIC` =
`.project/backlog/epic_upstream_findings.md`.

---

## F1 — Snapshot-driven generation (Item 2)

- `src/sysml_codegen/snapshot/` package exists (`loader.py`, `graph_rebuild.py`, …). [ls src/]
- CLI: `generate --from-snapshot`, mutually exclusive with `--models`; combining with
  `--design-path-filter` is rejected. [`cli` — `from_snapshot` config field; the
  `--design-path-filter cannot be combined` error; "Exactly one extraction input" comment]
- Snapshot path calls `build_pipeline_context_from_snapshot` (orchestration). [cli import]
- Format has `snapshot_format_version` with hard error on mismatch; stale-source hash
  warning; `compilation_results` serialized (SC-10) so CalcUsage auto-impl survives
  offline. [EPIC Item 2 scope + success criteria (checked); doc 27 is its reference doc]
- REQ-SNAP-08..19 live in doc 27 / verification matrix. [handoff Context, Item 2]

## F2 — Capture-script roles (license split)

- `capture_baseline_yaml.py`: renders YAML **from committed extraction snapshots** via
  `build_full_graph_from_snapshot` — **license-free** (moved off live path by Item 11 F-B).
  [script docstring]
- `capture_pipeline_baselines.py`: captures graph JSON + registry through the **snapshot
  serialization boundary** — license-free. [script docstring]
- `capture_extraction_snapshots.py`: runs **live extraction** (needs syside license).
  [script docstring: "Runs extraction on each fixture model"]

## F3 — Item 7: matchers, V11, warning reconciliation (RN-7)

- Matcher Bug A (REQ-BT-09): FORMULA `::`-QN REFERENCE path per-segment sanitizes via
  `sanitize_qualified_name`, so quoted-owner QNs match.
- Matcher Bug B (REQ-BT-10): design attribute owned by a part **def** (empty
  `parent_part`) matches by leaf-unique fallback over design-part attributes; calc-def
  I/O excluded, so dotted calc-output refs stay unresolved and loud.
- V11 (REQ-GA-08): params-coverage check — pure collector `collect_uncovered_params` +
  always-strict generation boundary. Fires on fell-through ∩ valueless ∩ wired entry
  point. First **generation-boundary** rule; V1–V10 are extraction-time.
- Per-binding Step-4 "Registry unresolved" lines and per-collision alias lines are
  DEBUG; single WARNING summaries (reconciliation summary; alias count-summary).
- README null-key correction: the JSON template **omits** null-default keys (schema
  declares them required) — docs must not say they appear awaiting values.
- Entry-point reclassification (USAGE_LITERAL → DESIGN_ATTRIBUTE) happened only for
  retype_model in the committed corpus; no solar_battery changes.

## F4 — Item 9: plant literal pre-fill (RN-9)

- `extract_design_overrides` (hierarchy_resolver) scans plain typed usages' member `:>>`
  overrides; plain-usage override kept only when RHS is LITERAL
  (`_keep_plain_usage_override`). REQ-HR-08.
- Bare-name `source_path` in `_rewrite_virtual_bindings` is skip-with-DEBUG, not a
  ValueError. REQ-VBR-09.
- Virtual instances copy `BindingInfo` per instance (`copy.copy` per binding) — no shared
  mutable bindings. REQ-VBR-08.
- No V-rule added; V11 is *satisfied* for the plain-usage LITERAL class.

## F5 — Item 10: cross-part channel wiring (RN-10)

- `reference_chain` (extraction/data_models.py): full dotted segments of a pure
  FeatureChainExpression derived attribute; additive snapshot field, **no**
  `SNAPSHOT_FORMAT_VERSION` bump; absent → None → FORMULA (old behavior). REQ-CA-10.
- `EXPOSE_CHAIN_TENTATIVE` classification + **Phase 3b confirm pass** — Phase 3b is a
  phase of **registry build** (`output_registry_builder.py`, "Phase 3b: Confirm
  multi-hop EXPOSE tentatives"), NOT a backtracker phase. Walk finalizes tentative →
  EXPOSE_PURE (registering the real transitive channel) or reverts → FORMULA; INV-F
  raises if any tentative survives to a reader.
- Part-def EXPOSE (shape A) expands per design instance into the structured
  `_scoped_alias` namespace; backtracker reads it by splitting consumer `source_path`
  at the last dot. REQ-CA-03 revised; REQ-BT-11.
- `ScopedAliasKey = NewType("ScopedAliasKey", tuple[str, str])`
  (core/identifier_types.py). **Renamed from `ConsumerScopedKey` during Item 10** —
  grep confirms the old name appears nowhere in src/ or docs/.
- `_rewrite_specialized_chain` (REQ-VBR-10): rewrites `part_usage.attr` CHAIN bindings
  through the retyped part's specialized-def `:>>` chain. Precedence: **usage override >
  specialized-def `:>>` > base def**.
- Sibling disambiguation via consumer-scope prepend (REQ-BT-11); self-named-binding
  rescue (`in x = x` rewritten to resolvable outer EXPOSE channel, else left as-is —
  `self_named_binding_trap` stays a modeling error).
- Two-level specialization: `_index_usage_level_retypes` (REQ-LVP-09, genuine retypes
  only) + instance-aware type-select in `_rewrite_specialized_chain` (REQ-VBR-11).
- Offline == live: the confirm walk is reconstructed on snapshot load (D-C fix). See
  memory: verify channel identity, not just fallback removal.

## F6 — Honest caveats that must survive verbatim-or-stronger (RN-10, EPIC Item 10)

- **SC-2 is met at the GRAPH level only.** The gamma→lcoe edge exists in the
  ComputationGraph from generated wiring alone; the **full fusion-tea YAML does NOT
  emit** — generation aborts at V11 on **10 other** pre-existing cross-part bindings
  (`driver.efficiency`, `driver.energy`, `driver.lifetime_shots`,
  `chamber.blanket_energy_multiple`, `chamber.yield_cost_constant`,
  `target_factory.cost_per_target`, `hif_driver_instance`). BACKLOG P1.
- fusion-tea workarounds (`hif_driver_instance` scaffold, two-pass gamma feedback)
  **stay in place** — not yet deletable.
- Run-C anchor ($270.12/MWh) is recorded, **not reproduced** in-repo.
- `attribute :>> attr = <expression>` is **known-unsupported** (silently dropped at
  extraction); the supported value-carrying form is the bare `:>> attr = value`.

> **POST-EPIC UPDATE (PIPELINE-TRUTH Item 10, 2026-07-06).** The bullets above were true at
> *docs-scrub* HEAD and are kept as that record. PIPELINE-TRUTH retired most of them —
> re-read them as history, not current state:
> - **SC-2 / the 10-offender V11 abort — RETIRED.** fusion-tea's full YAML now emits at TRUE
>   ZERO V11 offenders; the supplied-value materializer (`resolution/supplied_values.py`,
>   REQ-SVM) resolves the cross-part/in-part supplied values (Item 2). SC-2 is met at the
>   pipeline level, not just the graph level.
> - **fusion-tea workarounds — DELETED upstream** (`sanitize_names.py`, `hif_driver_instance`,
>   two-pass gamma feedback, hand-written input JSONs) — SC-C (Item 3).
> - **Run-C anchor ($270.1211779380445/MWh) — now REPRODUCED**, bit-exact, through the
>   generated package alone (Item 3); plus a perturbed-input rerun proving the JSON is consumed.
> - **`attribute :>> attr = <expr>` — still genuinely unsupported** (dropped at extraction);
>   agentic-mbse now WARNs on it (Item 9), but codegen extraction is unchanged. This one stands.
> The current caveat truth lives in `EXPLAINER_PROMPT.md` §7 and modeling-assumptions §8.

## F7 — Item 11: alias surfacing (RN-11)

- `OutputAlias` (resolution/models.py): `alias_name`, `canonical_channel`,
  `instance_path`, `shape: Literal["part_def","part_usage"]`, `output_filename`
  property = `{instance_path}__{alias_name}.json`. REQ-DM-09.
- `ComputationGraph.output_aliases: list[OutputAlias]` — **serialized** (deliberate
  contrast with `fallback_entry_points: set[str]`, which is `exclude=True`, in-memory
  only). Stable-sorted by `(instance_path, alias_name)` (INV-5); channels validated to
  exist (INV-3); built in `build_computation_graph`; threaded through BOTH build sites
  (live `pipeline_builder` and snapshot `graph_rebuild`).
- Exit-point filename override (REQ-PY-08): `generate_pipeline_yaml` →
  `_build_alias_filename_map` (first-wins per channel over the sorted list) →
  `_build_exit_points`. The exit **key stays the canonical channel**; type token
  unchanged (REQ-PY-06 intact).
- Shape-A warning retirement (REQ-CA-11): `_build_attribute_resolution_map` splits
  EXPOSE_PURE on `is_on_part_definition`; registered `_scoped_alias` leaf → silent;
  unregistered → warns naming the real cause. Shape B byte-identical.
- The surfaced name is the **sanitized** `python_name` (`'total cost'` → `total_cost`).
- EXPOSE_COMPUTED still rejected / does not surface. Redefinition and design_override
  name surfacing: BACKLOG follow-up.
- Aliased channels' output files MOVED `{channel}.json` → `{instance_path}__{alias_name}.json`
  (behavioral change; 4 committed YAML filenames moved + wi014_toy new).

## F8 — Items 1/3/4/5/6 (EPIC items + handoff)

- Item 1: constraints-are-not-executable WARN (summary + per-item INFO) + a
  modeling-assumptions §8 section; EXPOSE_PURE warning reworded to say the *name* is
  dropped and name the canonical channel (superseded for resolvable cases by Items
  10/11); zero-output calc def is a hard diagnostic (V7 territory).
- Item 3: `return x : Real = expr` and bare `in x : Real` extract correctly; anonymous
  `return` → clear diagnostic (V8); doc 01's canonical example was corrected (was
  false). V7 reworded, V8 added.
- Item 4: retyped part usages (`part :>> x : Subtype`) index under the owned
  FeatureTyping target **plus every user-model PartDefinition in `usage.types`**;
  same fix in `extract_hierarchy_data`. modeling-assumptions §5 retyping + V9/V10.
- Item 5: `sanitize_name` / `sanitize_qualified_name` (core/qualified_names.py) applied
  at the source; duplicate-output-path fail-fast (two names sanitizing to one filename
  is a hard error). Quoted names are supported, identifiers derived. Docs 15/20; SC-11
  closed as intended/documented/tested.
- Item 6: `reconstruct_expression` literal branches ordered above the invocation
  catch-all; precedence-aware parenthesization. REQ-AST-03 revised in place,
  REQ-AST-08/09 added; `_walk_aggregation_ast` known-deviation note in doc 19.

## F9 — Terminology at HEAD (grep-verified in src/)

Present: `ScopedAliasKey`, `reference_chain`, `EXPOSE_CHAIN_TENTATIVE`,
`fallback_entry_points`, `output_aliases`, `sanitize_qualified_name`,
`collect_uncovered_params`, `_scoped_alias`, `_rewrite_specialized_chain`.
Absent everywhere: `ConsumerScopedKey`.

## F10 — Gate baseline (must be unchanged by the scrub)

1989 passed / 4 skipped / 5 xfailed; `ruff check src/` = 21; `mypy src/` = 109.
[handoff Context]

> **POST-EPIC UPDATE (PIPELINE-TRUTH Item 10, 2026-07-06).** The docs-scrub gate above is
> superseded by the post-epic gate: **2069 passed / 4 skipped / 5 xfailed; `ruff check src/`
> = 17; `mypy src/` = 104** (both linters better than the docs-scrub baseline; new tests from
> Items 1–9 account for the count growth). Item 10 is docs-only, so it does not move the gate.

## F11 — Known dead template

`src/sysml_codegen/templates/pydantic_schema.py.jinja2` has zero render sites (verified
during Item 2). Doc references to it are doc bugs; deleting it is a code change — file,
don't fix. [handoff Discovery 5]

## F12 — Cross-repo constraint

agentic-mbse `docs/patterns/plant-idiom.md` (branch `upstream-findings-sync`) names
`ife_plant` / `spec_chain_*` fixtures as reference shapes — no fixture renames/moves in
this scrub. [handoff Discovery 8]
