# Verdict: scope-beyond-the-16 (Item 5 spec-phase probes)

**Execution note.** Live `uv run python` was blocked at the permission layer for this
agent AND for a delegated Bash-capable subagent — every python invocation was denied
before any script ran (not a script error). The three probes are written and ready to
run once the orchestrator grants `uv run python .project/.../probes/*.py`:

- `probe_a_sanitizer.py` — pure string, no license needed.
- `probe_b_nonfloat_ep.py` — drives extraction on `plant_value_shapes`.
- `probe_c_binding_drift.py` — drives extraction on `self_named_rescue`.

Verdicts below rest on: (A) exact by-hand evaluation of a pure deterministic function
read in full; (C) committed git artifacts + source (no runtime needed); (B) the exact
drop sites in source + the fixture, with one runtime-dependent detail flagged.

---

## A. `sanitize_name` injectivity + isidentifier (adversarial SC-4)

**Intended behavior.** `sanitize_name` (`src/sysml_codegen/core/qualified_names.py:13`)
must map a raw SysML name to a valid, unique Python identifier. Doc
`15-naming-conventions.md` + ADR-003: identifiers feed channel keys / EP keys / module
names, which must be distinct and be legal Python.

There is exactly ONE production sanitizer: `core/qualified_names.py:13`. (A second,
throwaway copy exists inside `scripts/probes/probe_alias_resolution.py:54` — a probe-local
helper that only strips quotes/spaces; not production, noted per the two-sanitizer ask.)

The function: strip quotes → replace spaces with `_` → `re.sub` non-alnum/underscore to
`_` → collapse `_+` → strip leading/trailing `_` (`or "unnamed"`) → guard only
`{class, def, import, from, return, yield}` by appending `_`.

**Probe:** `probe_a_sanitizer.py`

### A1 — INJECTIVITY: CONFIRMED (many-to-one, no collision guard)

Every pair below sanitizes to an identical output (hand-evaluated):

| input pair | both map to |
|---|---|
| `'a b'` / `'a-b'` | `a_b` |
| `'a.b'` / `'a_b'` | `a_b` |
| `'a&b'` / `'a$b'` | `a_b` |
| `'net electric'` / `'net-electric'` | `net_electric` |
| `"'wall type'"` / `'wall-type'` | `wall_type` |

Two sibling SysML names differing only in a char that sanitizes to `_` collapse to the
same identifier. There is NO fail-fast: nothing in `qualified_names.py`, and no channel/EP
key registration, checks for two distinct source names colliding on one sanitized key —
they silently overwrite/merge. Confirmed against the register.

### A2 — ISIDENTIFIER: CONFIRMED (two distinct gaps)

`sanitize_name(x).isidentifier()` does NOT always hold.

**Gap 1 — leading digit (the register's claim): non-identifier output.**
- `'2nd stage'` → `2nd_stage` → `.isidentifier()` = **False**
- `'3phase'` → `3phase` → **False**
- `'123'` → `123` → **False**
- `"'99 bottles'"` → `99_bottles` → **False**
- `''` (empty input) → `''` (early return) → **False**

The keyword guard appends `_` for six keywords but never PREPENDS for leading digits and
never handles the empty-string early return, so a quoted leading-digit SysML name produces
an illegal identifier. Confirmed exactly as the register states.

**Gap 2 (adjacent, bonus) — keyword coverage is incomplete.** The guard set is only
`{class, def, import, from, return, yield}`. Python keywords `for`, `while`, `if`, `None`,
`True`, `lambda`, `global` pass through unchanged. `.isidentifier()` returns True for them
(it does not check keywords), but each is a SyntaxError if emitted as a variable/field
name. So `.isidentifier()` alone is an insufficient pin — the fix should test
`keyword.iskeyword()` too, or the guard should use `keyword.kwlist`.

**Fix shape (for spec):** prepend a safe prefix (or `_`) when the result starts with a
digit or is empty; broaden the keyword guard to `keyword.kwlist`; and add a collision
guard / fail-fast where sanitized names become channel or EP keys.

---

## B. Non-float entry-point literals dropped by `float(value_str)` (adversarial SC-5)

**Intended behavior.** Docs `06-entry-point-classifier.md`, `17-parameter-group-deriver.md`,
`18-literal-value-propagation.md`: an entry-point literal (LIBRARY_DEFAULT /
DESIGN_ATTRIBUTE / USAGE_LITERAL, ADR-001) should become a typed JSON-input parameter
carrying its value. A value the pipeline can't type should surface as a diagnostic, not
vanish.

**Probe:** `probe_b_nonfloat_ep.py` (drives `tests/fixtures/plant_value_shapes`).

**Fixture inspection.** `plant_value_shapes/library.sysml` + `design.sysml` carry the
enum shape (shapes 6+9): `enum def 'Wall Kind' { dry_wall; wetted_wall; liquid_wall; }`;
`part def 'Chamber Unit'` has `attribute wall : 'Wall Kind'` fed one hop to
`ChamberSelectCalc` via `calc select { in wall = wall; in footprint = footprint; }`; and
`design.sysml` sets `part chamber_unit : 'Chamber Unit' { :>> wall = 'Wall Kind'::liquid_wall; }`.
So `wall` is a DESIGN_ATTRIBUTE entry point whose value is an enum literal (non-float);
`footprint` is the float control (`12.0`).

**Two non-float drop sites in `analysis/parameter_groups.py` (source-confirmed):**

1. `_parse_default_value` (line 710) does `float(value_str)`; on `ValueError`/`TypeError`
   it logs only `logger.debug` (line 717) and returns `None`.
2. In `_derive_from_design_attributes` (line 600-602), a design attribute whose parsed
   default is `None` hits `continue` — the parameter is **silently dropped** from every
   group. No warning, no error, no typed pre-fill.
3. Adjacent literal path: `_build_literal_index` (line 415-422) does `float(binding.source_path)`
   for USAGE_LITERAL bindings; non-float → `logger.warning` (line 419) AND the param is
   never indexed → still dropped, just with a warning rather than silence.

**Verdict: CONFIRMED (mechanism).** An enum/bool/string-valued entry-point literal cannot
survive `float()`; it is mapped to `None` and then either silently omitted (design-attr
path, `debug`-only) or emitted with a null default (binding-index path, line 626-641,
`default_value=None`) — never a typed value, and the design-attr path emits no diagnostic
at all. This is distinct from Item 2's two `0.0`-truthiness sites (`_classify_entry_points`
~482, `graph_builder.py` ~1133); this is `float()` rejecting non-numerics, not `0.0`
being falsy.

**Pending the live run (one runtime-dependent detail):** which of the two fates `wall`
actually takes — silently dropped (design-attr loop) vs kept-with-null (binding-index
loop) — depends on whether extraction files `wall` under `design_attributes` or
`_binding_index`. The probe prints both the design-attr table and the derived-group param
list, so a single run pins the exact vanished/null param. Either outcome is the SC-5
finding shape.

---

## C. `self_named_rescue` binding_type drift (reference → chain) — ATTRIBUTION

**Intended behavior.** Item 5 owns raw binding classification
(`usage_extractor._extract_single_binding`, line 683): a bare-name RHS resolving to a
single feature is a REFERENCE; a multi-segment feature chain is a CHAIN.

**Probe:** `probe_c_binding_drift.py`. But this item is fully resolved from committed
artifacts — no runtime needed.

**The committed v1→v2 recapture diff** (commit `5d77856`, on the
`self_named_rescue/extraction_snapshot.json` `sink_calc` binding) is decisive:

```
-  "source_path": "RescueLib::'Rescue Plant'::sink_calc::throughput",
-  "binding_type": "reference",
+  "source_path": "rescue_plant.throughput",
+  "binding_type": "chain",
   "raw_expression": "FeatureReferenceExpression -> RescueLib::'Rescue Plant'::sink_calc::throughput",
```

`raw_expression` is BYTE-IDENTICAL across v1 and v2 and still says
`FeatureReferenceExpression`. That string is the format literal from the REFERENCE branch
(`usage_extractor.py:724`). So the raw classifier still produced REFERENCE in BOTH
captures — the classifier did NOT change. Only `binding_type` and `source_path` were
rewritten downstream.

**The rewriter:** `_rescue_self_named_bindings` in
`orchestration/pipeline_builder.py:516-573` (mechanism-D self-named rescue, Item 10). For a
self-named `in x = x` whose raw REFERENCE points at the consuming calc's OWN param, if an
outer same-named EXPOSE resolves to a real channel, it sets
`binding.source_path = f"{instance}.{leaf}"` and `binding.binding_type = BindingType.CHAIN`
(lines 567-568). Called at pipeline step 5.56 (line 734), and mirrored on the from-snapshot
path (`snapshot/graph_rebuild.py:66`).

**Why the flip between captures:** the v1 snapshot was committed in `92fe5db`
("item-10b Phase 6 — three stage-(b) fixtures captured **current-incomplete**") — captured
BEFORE the rescue was wired, so the self-named binding dead-ended on the calc's own param
(the trap failure mode). The rescue landed in `89e6f80` (UPSTREAM-FINDINGS #3). The v2
recapture (`5d77856`) shows the rescue now firing: it redirects the binding to the exposed
upstream `rescue_plant.throughput` channel as a CHAIN.

**Verdict: EXPLAINED — NOT A FINDING.** The reference→chain flip is the intended
mechanism-D rescue firing where it previously didn't. The new `chain` classification is
CORRECT for this shape (`in throughput = throughput` with a resolvable upstream EXPOSE);
`reference` at `...sink_calc::throughput` was the pre-rescue dead-end. Item 5's raw binding
classifier is not implicated — it still emits REFERENCE (raw_expression proves it). No
change owed by Item 5.
