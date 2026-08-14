# Probe results — Item 9 design stage

**Run:** 2026-08-13, design stage, on `item7-rebuild` @ `0596f5c`.
**Interpreter:** `/home/reid/1cfe/item7-rebuild-venv/bin/python`.
**License:** `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` — every run below is licensed.
**Scratch:** `/tmp/claude-1000/item9-probe/` (throwaway copies of the fixture; the repo tree was
never edited — `git status` shows only this `probes/` directory).

The epic's binding lesson is that a probe gating a landing must run **generation**, not only
elaboration. Every result below is a full `sysml-codegen generate` through the public route
(`sysml_codegen.cli:main`), except where a script is named.

## Scripts

| script | what it does |
|---|---|
| `apply_item9_edits.py` | authors all 27 A5/A6 derivations + A9 on a scratch copy (`--only a56` / `--only a9` to split) |
| `collect_collisions.py` | enumerates **every** `SI_RENDERING_COLLISION` instead of stopping at the first |
| `trace_mints.py` | logs each entry-point mint with the consuming lane and its `unit_text` |
| `lane_units.py` | per-lane port `unit` for a named consumer, via Item 8's own accessor |
| `measure_after.py` | entry-point key diff, module count, coverage account, disposition histogram |
| `check_literal_identity.py` | replays the derived radius chain in IEEE-754 against the authored literals |
| `diagnose_collision.py` | field-level diff of the two colliding `EntryPoint` candidates |

## Headline

**Both ruled forms build.** Full generation succeeds with all five preflights passing and the
package sealed. Nothing about the ruled forms had to be adapted.

Getting there took one non-obvious authoring requirement that the first attempt missed, and
finding it is what the probe was for.

## Result 1 — the naive authoring refuses; the cause is unit text, not the ruled form

First attempt (ruled forms authored with no unit annotation on the new declarations) refused:

```
ERROR: Code generation failed: exact graph projection failed: SI_RENDERING_COLLISION:
entry point 'CATFMFERadialBuild__catf_radial_build__tf_coil__thickness'
has conflicting projected metadata
```

Elaboration ADMITs; this is a **projection** refusal (`elaboration/project.py:394-397`). The
complete refusing set, measured by swallowing each collision and continuing
(`collect_collisions.py`) — **exactly three keys, one root cause**:

| key | disagreement | from |
|---|---|---|
| `CATFMFERadialBuild__catf_radial_build__tf_coil__thickness` | `None` vs `'m'` | A5/A6 |
| `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` | `'Dimensionless'` vs `None` | A9 |
| `CATFMFEVacuum__catf_vacuum_pumping__pumping_speed_total` | `'m³/s'` vs `None` | A9 |

`unit_text` is the **only** differing field — `entry_type`, `python_type`, `default_value` and
`source_calc_usage` all match (`diagnose_collision.py`).

Split runs confirm each form refuses independently: A9 alone → the 2 vacuum keys; A5/A6 alone →
`tf_coil.thickness`. The **unedited fixture generates cleanly**, so the refusals are introduced
by the authoring, not pre-existing.

## Result 2 — which lane reads `None`, measured

`lane_units.py` on the edited fixture, using the accessor Item 8's own conformance test uses:

```
CATFMFEVacuum__catf_vacuum_pumping__pump_load        (calc lane)
    pumping_speed_total_in  unit='m³/s'      pump_count  unit='Dimensionless'
CATFMFEVacuum__catf_vacuum_pumping__pumping_speed_agrees   (constraint lane)
    observed  unit=None   count  unit=None   each_capacity  unit=None   rel_tol  unit=None

CATFMFERadialBuild__catf_radial_build__magnet_surface_calc  (calc lane)
    thickness  unit='m'
CATFMFERadialBuild__catf_radial_build__tf_coil__outer_radius  (computed lane)
    inner_radius  unit='m'    thickness  unit=None
```

**The calc lane reads units correctly. The lanes I authored read `None`.** This is the reverse of
the natural guess and it is the whole finding:

- A port's unit comes from the **formal's own declaration** (`elaborate.py:1764`,
  `extract_feature_unit` in `extraction/feature_metadata.py:57`). My first `ProductWithinBand`
  declared four bare `Real` formals with no unit comment → all four ports `None`.
- `_unit_from_source` (`feature_metadata.py:84-122`) reads a trailing `//` comment whose first
  token is a unit. `tf_coil.thickness`'s authored comment is `// From line 83 (= tf_dr)`, and
  `from` is in the extractor's stop-word list → `None`. The `[m]` on the *value*
  (`: Real = 0.25 [m]`) never reaches port metadata.
- Only `tf_coil.thickness` collides among the 14 thicknesses because it is the only free
  thickness a calc also consumes (`magnet_surface_calc`, whose calc-def formal carries `// m`).

Item 8's own A9 fixture (`tests/fixtures/unit_lane_a9/model.sysml:5-8`) annotates every formal
(`// Dimensionless`, `// m³/s`), which is why it passes there and the real fixture did not. Item 8
is not incomplete — it made the three lanes carry authored unit text and pinned unequal text as a
refusal. That refusal is doing its job here: it caught two genuinely unlabelled declarations.

## Result 3 — the fix, and full generation green

Two annotation changes, no change to any ruled form:

1. `ProductWithinBand`'s four formals carry unit comments (`// m³/s`, `// Dimensionless`), the
   spelling Item 8's customer fixture uses.
2. `tf_coil.thickness`'s trailing comment becomes `// m - from line 83 (= tf_dr)`.

Full generation through the public route then completes:

```
INFO: Generated 62 TEAx module wrappers
INFO: Generated 58 implementation stencils
WARNING: Module class name collisions detected: ['outer_radiusModule'].
         Generating aliased imports for 15 modules.
INFO: Generated module registry with 62 modules
INFO: Generated 9 parameter group schemas ... 9 JSON input templates
INFO: Sealing package...
INFO: Code generation complete
```

All five preflights pass. The registry line is a **warning that the registry preflight handles**,
not a refusal: 15 modules now mint a class named `outer_radiusModule` (the 14 derived layer radii
plus the existing vacuum-vessel one) and are aliased. `constraint_name_safety` did not fire — none
of `observed`/`count`/`each_capacity`/`rel_tol` collides with the `value` generated local.

Minted port units on the new surface, all carrying the authored text:

```
CATFMFEVacuum__catf_vacuum_pumping__pumping_speed_total             unit='m³/s'
CATFMFEVacuum__catf_vacuum_pumping__n_pumps                         unit='Dimensionless'
CATFMFEVacuum__catf_vacuum_pumping__pump_capacity_each              unit='m³/s'
CATFMFEVacuum__catf_vacuum_pumping__pumping_speed_agrees__rel_tol   unit='Dimensionless'
CATFMFERadialBuild__catf_radial_build__tf_coil__thickness           unit='m'
```

**No cross-part collapse.** Every sibling-reaching initializer
(`plasma_region.inner_radius = axis_region.outer_radius`, and 12 more) wires correctly; the bare
sibling spelling resolves and no channel collapsed.

## Result 4 — measured shape, confirming the spec's pre-committed numbers

`measure_after.py baseline v2`:

```
modules: 47 -> 62
entry points: 65 -> 55        (26 keys left, 16 arrived)
coverage account: 56 / 3 / 3 / 0 / 0 / {} / complete
disposition histogram: {'eligible': 3, 'non_reaching': 53}     (no 'excluded' rows remain)
catalog usage rows: 56
```

These **agree exactly** with what the spec fixed from the ruled table in advance. They are
recorded here as confirmation; they are not the source of the committed expectations (SC-6).

**Module count, measured (the spec left this open): 62.**

Public key movement, both directions fully accounted:

- **26 keys leave** — the derived radii that were entry points. Not 27:
  `axis_region.outer_radius` was never a key (that layer carries no geometry calc), which is the
  same 26/27 split Item 5 measured when it found 26 of 27 refusing.
- **16 keys arrive** — 13 layer `thickness` keys + `axis_region.inner_radius` +
  `axis_region.thickness` (14 radial-build keys; `tf_coil.thickness` was already a key), plus
  `pump_capacity_each` and `pumping_speed_agrees__rel_tol` from A9.

Note for the spec's wording: the free parameters do **not** "stay keys" — 14 of the 15 free radial
parameters were not keys before and *arrive*, because nothing consumed them until the derived
`outer_radius` did. Direction of the movement is as ruled; the phrasing needs correcting.

## Result 5 — float drift, a surfacing item

The spec makes it `[HARD]` that "the derivations must reproduce the authored literals exactly"
and that any downstream number moving is a surfacing event. Decimal equality holds. **IEEE-754
equality does not**, for 4 of the 14 layers (`check_literal_identity.py`):

```
vacuum_gap.outer_radius   derived 4.199999999999999   authored 4.2    delta -8.882e-16
first_wall.outer_radius   derived 4.3999999999999995  authored 4.4    delta -8.882e-16
blanket.outer_radius      derived 5.199999999999999   authored 5.2    delta -8.882e-16
reflector.outer_radius    derived 5.3999999999999995  authored 5.4    delta -8.882e-16
```

(plus the four `inner_radius` values that read them). The chain **re-converges at
`ht_shield.outer_radius`** (`5.3999999999999995 + 0.2 == 5.6` exactly) and the final
`bioshield.outer_radius` is exactly `8.55`. The `tf_coil` legs are exact, so the
`magnet_volume_total` → cryogenic-load chain behind the manifest's 16-digit
`cooling_power = 8396.054399837172` is untouched.

Surfaced, not absorbed: this is float accumulation, not a modeling error, and it does not change
any generated byte (generation emits code, not computed values). It can only appear at execution
time, in volumes downstream of `vacuum_gap`/`first_wall`/`blanket`/`reflector`/`ht_shield`.

## Result 6 — the per-occurrence anchoring works

`apply_item9_edits.py` locates each layer by its `part <name> {` header and closes the block by
brace depth, then asserts **exactly one** matching declaration inside that block. It succeeded for
all 27 derivations. That is direct evidence that the prover's per-occurrence anchoring (design
decision D2) has a unique anchor for every one of the 14 byte-identical
`inner_radius + thickness` initializers.
