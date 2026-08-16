# Post-repair spike recheck

**Date:** 2026-08-16  
**Codegen:** `main` at `0f89673`  
**Purpose:** Re-establish self-binding spike findings F-2 through F-5 after the exact-owner repair
landed at `98970c9`.

The original spike ran before the repair. This recheck uses the same fixtures and scripts against
the current shipped route. It records evidence only; it does not change the findings' dispositions.

## Results

| finding | post-repair result | evidence |
|---|---|---|
| F-2 | **Reproduced.** `validate_structure()` still rejects `s4a_qual_one_occ` as `L2_SELF_NAMED_BINDING`, while accepting D-5 and D-7. | `spike/probe_validation.py`; exit 0 |
| F-3 | **Reproduced.** Generating `s5_sibling_formal` still exits 1 with a raw `GraphValidationError: SI_EDGE_DANGLING: typed producer dependency cycle` from `elaborate.py:631` / `graph.py:448`. | licensed `sysml-codegen generate` run |
| F-4 | **Reproduced.** `s6_qual_sibling_scope` still generates and wires `unit_cost` to `S6QualSiblingScope__plant__bop__the_unit__cost = 7.0`. This is the definition-owned `_resolve_leaf` route. | licensed `sysml-codegen generate` run; generated `inputs` and `pipeline.yaml` inspected |
| F-5 | **Reproduced.** `extract_bindings()` still reports the D-7 chain beginning `cost.result.self.involvedObjects...` instead of `driver.cost`. | `spike/probe_validation.py`; exit 0 |

The F-2 run also reconfirmed the negative and controls: the self-named fixture is refused; D-5 and
D-7 pass agentic validation. The F-4 run reconfirmed that the positional sideways-reach behavior
survives only on the definition-owned route. The exact-owner conformance test remains the authority
for usage-owned references.

## Commands

Both commands loaded the SysIDE license from the companion `agentic-mbse` checkout.

```bash
uv run python .project/active/self-binding-replacement/spike/probe_validation.py

uv run sysml-codegen generate \
  --models .project/active/self-binding-replacement/spike/fixtures/s5_sibling_formal \
  --output <temporary-directory> \
  --package-name spike_pkg --overwrite

uv run sysml-codegen generate \
  --models .project/active/self-binding-replacement/spike/fixtures/s6_qual_sibling_scope \
  --output <temporary-directory> \
  --package-name spike_pkg --overwrite
```
