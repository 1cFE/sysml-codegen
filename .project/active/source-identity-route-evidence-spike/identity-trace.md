# Identity Trace (SOURCE-IDENTITY Item 2)

**Date**: 2026-08-05 · **Branch**: `nested-override-tripwire` @ `fa9e0d0`
**Method**: committed-snapshot inspection + full pipeline builds (license-free) plus a
licensed live-parity leg (`probes/parity_probe.py`, ALL PARITY on 4 fixtures).
Narrative version with the discovery log:
`.project/research/20260805-054752_source-identity-route-evidence.md`.

For a model-derived consumed value, what each pipeline stage holds and loses:

| Stage | Code | Identity in | Identity out |
|---|---|---|---|
| 0. Extraction | `src/sysml_codegen/extraction/usage_extractor.py:831-842` | AST referent | Self-named `in R = R` resolves to the calc's **own formal** (normatively required — Item 1 ruling); `source_path` = self-ref QN. Written-form fields (`source_attribute_name`, `source_written_qualifier`) captured from the CST. Outer-source identity is **never established** for this form. Additional stage-0 loss (Item 1, form 4a): `#(i)` IndexExpression segments are silently dropped by `_parse_chain_expression` (zero corpus prevalence today). |
| 1. VBR (live Step 3.5) | `src/sysml_codegen/orchestration/pipeline_builder.py:336-379` | self-ref QN + written fields | Occurrence `:>>` override matched by `(parent_path, leaf)` **name coincidence** → `binding_type=LITERAL`, `source_path=None`. Written fields survive (measured). Route identity destroyed. |
| 2. Snapshot capture | `src/sysml_codegen/snapshot/capture.py:48-70` | post-VBR bindings | **Stamp persisted**: capture runs the full live pipeline, then serializes the mutated bindings. The rebuild (`src/sysml_codegen/snapshot/graph_rebuild.py`) has no VBR step — the offline route replays the baked-in stamp. |
| 3. SVM enrichment (live Step 5.65 / rebuild) | `src/sysml_codegen/resolution/supplied_values.py:502` | bindings + overrides | Skips bindings with no `source_path` → stamped literals invisible to source-QN collapse. Synthesizes occurrence attributes from demands (solar's converged `pack_count` field exists only as a synthesized attribute). Definition-relative captures vs occurrence-relative demands fail the tier match — `[NESTED-OCCURRENCE-OVERRIDE]`, tripwire warns. |
| 4. Backtracker | `src/sysml_codegen/analysis/dependency_backtracker.py:445-463, 571-631` | binding state | LITERAL arm mints `{usage_qn}__{param}` per consumer and **never calls the resolver**. REFERENCE arm reaches the 22-form table; row 16 (`owner + written`) hits only when the occurrence attribute exists in the enriched index; the `::`-qualified self-ref QN misses rows 17/19-21. |
| 5. Classification | `src/sysml_codegen/resolution/graph_builder.py:534-579` | EP name | Catch-all else → `USAGE_LITERAL` for both fan-out paths — reference-derived mints wear an authored-literal label. |
| 6. Value backfill | `src/sysml_codegen/resolution/graph_builder.py:620-630` | group deriver's parallel resolution | Def-default value quietly attached to the per-consumer EP ("ParameterSource may have resolved bindings that EntryPoint classification missed"). Value repaired, identity not — why every single-point run looks correct. |

## The pinned answers

- **First stage at which identity is absent**: extraction (stage 0) for self-named
  forms — the outer-source link is never established; downstream stages either
  reinterpret it (constraint route, row 16, SVM) or destroy the route (VBR stamp).
- **First stage at which it is unrecoverable on the current offline route**: capture
  (stage 2) — the stamp is persisted; only the written-form fields survive.
- **Live/snapshot/relocated parity**: identical entry-point topology and watched binding
  states on fusion_tea, ife_plant, shared_producer, solar_battery_model
  (`probes/raw/parity_*.json`). The fan-out is a pipeline property, not a snapshot
  artifact, and relocation changes nothing.
- **Value provenance ≠ identity provenance**: values reach per-consumer entry points
  through (at least) four authorities — the VBR stamp, the SVM ladder, the resolver
  table's design-attribute tier, and the group-deriver backfill — which coincide at
  capture and diverge under mutation.
