# Design Revision Comments on 08_algorithm_revised.md

**Date:** 2026-02-13
**Reviewer:** Claude
**Document under review:** `.project/reports/08_algorithm_revised.md` (Desired-State Algorithm Design)
**Context:** Reports 06 (algorithm overview), 07 (open issues), bug research on EXPOSE_PURE two-hop failure

---

## What the Design Gets Right

### OutputRegistry is the correct central idea

Report 07 nails the root cause: five indexes with incompatible key formats and ad-hoc
bridging code. The OutputRegistry replaces all of them with a single resolution interface.
This is the right structural fix. A binding source_path goes in, a canonical channel name
comes out (or `None`). No cascade, no format guessing spread across 200 lines.

### ChannelAlias as a first-class data model

The current state -- aliases as `list[str]` on `AggregationExpressionData` plus a
heuristic param_name scan in Step 3.6 -- is exactly the kind of "patch on a patch" that
breeds bugs. Making aliases explicit with provenance tracking
(`source: "redefinition" | "expose_pure"`) is clean and auditable.

### EXPOSE_PURE producing aliases instead of index entries

This directly fixes Bug 2. The current code builds a channel name for a module that
doesn't exist because it treats EXPOSE_PURE and FORMULA identically in
`_computed_attr_index`. The revised design eliminates this entire failure mode by making
EXPOSE_PURE a ChannelAlias -- it never enters any module index.

### Eliminating Steps 3.6 and 4.7

Removing the alias enrichment heuristic (3.6) and relocating aggregation scoping (4.7)
into OutputRegistry construction is a genuine simplification, not reshuffling. The alias
enrichment in particular was semantically wrong -- param_name divergence is not evidence
of aliasing.

---

## Critical Issues

### Issue 1: OutputRegistry doesn't solve the virtual CalcUsage instance_name problem

**Severity: Blocks correctness. This is the exact bug you just hit.**

Virtual CalcUsages (from template expansion) set `instance_name` to the full qualified
name. See `usage_extractor.py:255`:

```python
instance_name=qualified_name,
# e.g., "SolarBatteryDesign__solar_battery_plant__pv_module__cost_model"
```

The OutputRegistry registration in Section 6 says:

```python
registry.register(channel, [
    f"{usage.instance_name}.{output_attr.name}",  # dotted
    f"{usage.qualified_name}__{output_attr.name}", # EQN
])
```

For a virtual CalcUsage, the dotted key becomes:
`"SolarBatteryDesign__solar_battery_plant__pv_module__cost_model.total_cost"`

But an EXPOSE_PURE alias's `canonical_name` comes from the SysML expression text:
`"component_cost.total_cost"` (the **short** instance name as written in the model).

When the registry tries to resolve this alias:

```python
canonical_channel = registry.resolve("component_cost.total_cost")
```

- Exact match? **No** -- the registered key uses the full qualified instance name.
- `::` normalization? No `::` present.
- Bare name extraction? Produces `"total_cost"` -- ambiguous across every CalcUsage
  that has a `total_cost` output.

**This is the EXACT same failure mode documented in the bug research doc** (Hypothesis 1:
"Template expansion creates virtual CalcUsages with qualified instance_names"). The
OutputRegistry as designed doesn't solve it -- it moves the failure from the backtracker
cascade into `OutputRegistry.resolve()`.

**Proposed fix:** Registration must also index the **short instance name** form. For
virtual CalcUsages, extract the template's original `instance_name` (before qualification)
and register `f"{original_instance_name}.{output_attr.name}"` as an additional lookup key.
This requires either:

- (a) Carrying the original template instance name through `_create_virtual_calc_usage()`
  as a new field on `CalcUsageData` (e.g., `template_instance_name: str | None`), or
- (b) Extracting it at registration time by splitting `qualified_name` on `__` and taking
  the last segment.

Option (b) is simpler but fragile if any CalcUsage instance name itself contains `__`.
Option (a) is authoritative.

Additionally, for concrete CalcUsages (non-virtual), `instance_name` is already the short
form, so the dotted key is already correct. The fix only affects virtual CalcUsages.

> **UPDATE (2026-02-13, Spike 2 results):** Issue is **narrower than feared**. Spike 2
> confirmed that **no CHAIN binding in any tested model targets a virtual CalcUsage
> output**. Virtual CalcUsage outputs are consumed exclusively via aggregation (`:>>`
> expressions), not via direct CHAIN wiring. Short-key collisions exist (9 instances of
> `cost_model.total_cost` in solar_battery) but are irrelevant for CHAIN resolution.
>
> The fix is still needed for **aggregation scoping** (which maps `child_part.attr` to
> the correct virtual CalcUsage channel), but the urgency is lower -- aggregation scoping
> already resolves by hierarchy path, not by short instance name.
>
> **Resolution: Register both short and full keys.** Short-key collisions don't affect
> CHAIN wiring. Aggregation scoping handles virtual outputs via hierarchy path, not
> OutputRegistry lookup. No new field on CalcUsageData needed.

---

### Issue 2: Bare-name ambiguity is acknowledged but not handled

**Severity: Silent wrong wiring.**

The design says `bare (if unambiguous)` in parentheses next to several registrations, but
the `register()` implementation just overwrites on collision with a `logger.debug`:

```python
if key in self._index and self._index[key] != canonical_channel:
    logger.debug(
        "OutputRegistry key collision: '%s' already maps to '%s', "
        "overwriting with '%s'",
        key, self._index[key], canonical_channel,
    )
    self._index[key] = canonical_channel
```

This means **last-registered wins**, which is order-dependent and silent. Example:

- CalcUsage A has output `total_cost` -> registered as bare `"total_cost"` -> maps to channel A
- CalcUsage B has output `total_cost` -> overwrites bare `"total_cost"` -> maps to channel B

Any binding to bare `"total_cost"` now resolves to B regardless of intent.

**Proposed fix -- choose one:**

- **Option A (strict):** Don't register bare names at all. Require dotted format
  (`instance.output`). This is safest but may break bindings that legitimately use bare
  names (PartDef-scoped references).

- **Option B (recommended -- conditional registration):** Track whether a bare name has
  been seen before. On first registration, store it. On collision, REMOVE the bare-name
  entry and log a warning. This means ambiguous bare names resolve to `None`, forcing
  explicit dotted references.

  ```python
  def _register_bare_name(self, bare: str, channel: str) -> None:
      if bare in self._ambiguous_bare:
          return  # already known ambiguous, skip
      if bare in self._index and self._index[bare] != channel:
          del self._index[bare]
          self._ambiguous_bare.add(bare)
          logger.warning("Bare name '%s' is ambiguous -- removed from index", bare)
          return
      self._index[bare] = channel
  ```

- **Option C (deferred):** Detect ambiguity at resolve-time by storing a set of channels
  per key, and returning `None` when the set has more than one entry.

Option B is the right balance: safe, zero silent wrong wiring, and diagnostic.

> **UPDATE (2026-02-13, Spike 4 results):** Issue is **entirely theoretical**. Spike 4
> tested 94 bindings across 4 models: **zero bare-name references**. All bindings use
> either DOTTED (`instance.output`) or SYSML_QN (`Namespace::Part::attr`) format.
> Ambiguous bare names exist (5 per model, e.g., `total_cost` from 9 virtual
> CalcUsages), but no binding ever references them.
>
> **Resolution: Skip bare-name registration entirely.** Don't register bare names,
> don't need collision detection. The OutputRegistry only needs dotted keys and
> SysML QN normalization. This eliminates Options A/B/C and simplifies the registry.
> **CLOSED -- no action required.**

---

### Issue 3: Design attribute resolution is split across two mechanisms

**Severity: Architectural inconsistency that preserves the two-hop problem.**

The backtracker in Section 7 shows:

```python
channel = self._output_registry.resolve(binding.source_path)
if channel is not None:
    ...  # MODULE_OUTPUT
else:
    design_attr = self._resolve_to_design_attribute(binding.source_path)
    ...  # ENTRY_POINT
```

The backtracker still has TWO lookup paths: OutputRegistry for channels, plus its own
`_resolve_to_design_attribute()` for entry points. The document doesn't specify what
`_resolve_to_design_attribute` does, what index it uses, or what key formats it handles.

This matters because the current Bug 2 failure chain goes:

```
binding source_path
    -> design_attr_binding_index (first hop: finds "component_cost.total_cost")
    -> output catalog (second hop: resolves to MODULE_OUTPUT)
```

If the first hop is still in a separate `_resolve_to_design_attribute()` and the second
hop is in the OutputRegistry, you still have two mechanisms that need to agree on formats.

**Proposed fix -- two options:**

- **Option A (clean, recommended):** Design attributes that point to module outputs
  (the transitive case) get registered in the OutputRegistry as aliases during Step 5.
  For each DesignAttributeData whose `default_value` is a dotted path (like
  `"component_cost.total_cost"`), register:

  ```python
  registry.register_alias(
      f"{attr.parent_part}.{attr.name}",  # "e2e_plant.total_capex"
      channel_for_component_cost_total_cost,  # resolved transitively
  )
  ```

  Then the backtracker only needs `_resolve_to_design_attribute` for attrs with **literal**
  defaults (true entry points). No two-hop resolution. No separate index.

- **Option B (pragmatic):** Keep the two-mechanism split but specify exactly what
  `_resolve_to_design_attribute` does, what index it uses, and document the interaction
  contract with OutputRegistry.

Option A collapses the two-hop problem entirely and eliminates a class of bugs.

> **UPDATE (2026-02-13, Spike 3 results):** Issue confirmed, but **critical new
> discovery** about EXPOSE_PURE alias construction.
>
> The design assumed `expression_text = "component_cost.total_cost"` for EXPOSE_PURE
> attributes. SysIDE actually produces `expression_text = ".(component_cost)"` -- the
> raw FeatureChainExpression AST text, which is **not a parseable dotted key**.
>
> The actual target information is in the `references` field:
> - `references[0].name = "total_cost"` (the output attribute name)
> - `references[1].name = "component_cost"` (the CalcUsage instance name)
> - Combined: `component_cost.total_cost` -- which IS in the output catalog
>
> **Option A is still correct** (register transitive design attrs as aliases in the
> OutputRegistry), but the alias construction must use `references`, NOT
> `expression_text`. The ChannelAlias `canonical_name` field must be built as
> `f"{references[1].name}.{references[0].name}"` (instance.output), not from
> `ca.expression_text`.
>
> The existing two-hop path (design_attr_binding_index -> output_catalog) works when
> keys match, but Option A is more reliable because it doesn't depend on
> `DesignAttributeData` having correct `parent_part` (solar_battery showed a broken
> key with empty parent).
>
> **Resolution: Adopt Option A. Update EXPOSE_PURE alias construction to use
> `references` field.** Update Section 5 (Step 4.5) and Section 6 (Step 5) in the
> algorithm document.

---

### Issue 4: Alias registration order dependency is implicit

**Severity: Latent bug if registration order changes.**

Section 6 shows:

```
Register CalcUsage outputs         ... first
Register aggregation outputs       ... second
Register FORMULA outputs           ... third
Register aliases (from 3.5, 4.5)   ... LAST
```

Aliases are registered last with `registry.resolve(alias.canonical_name)` for transitive
resolution. This means CalcUsage outputs **must** be registered before EXPOSE_PURE aliases.

More concerning: what if an EXPOSE_PURE alias points to an aggregation output that is
itself reached via a `:>>` CHAIN alias?

```
EXPOSE_PURE: total_capex -> capital_cost
CHAIN alias: capital_cost -> solar_array__capital_cost (channel)
```

This requires `:>>` CHAIN aliases to be registered before EXPOSE_PURE aliases, or the
transitive resolve of `total_capex` fails (it resolves `capital_cost`, which isn't yet
in the registry).

**Proposed fix:** Make the registration order an explicit numbered protocol:

```
Phase 1: Register canonical channels (CalcUsage outputs, aggregation outputs, FORMULA outputs)
Phase 2: Register :>> CHAIN aliases (these alias canonical channels)
Phase 3: Register EXPOSE_PURE aliases (these may alias CHAIN aliases)
Phase 4: Register design-attribute transitive aliases (if Option A from Issue 3)
```

Document that each phase can only reference names registered in prior phases. If a
Phase N alias can't resolve, log a warning -- don't silently drop it.

Alternatively, make alias resolution iterative (resolve, re-resolve until fixed point),
but that adds complexity and requires cycle detection.

> **UPDATE (2026-02-13, Spike 3 results):** Phase ordering confirmed as critical.
> Spike 3 traced the e2e_attr_expr resolution chain and confirmed EXPOSE_PURE aliases
> must resolve against already-registered CalcUsage outputs. The proposed 4-phase
> ordering is correct and validated by empirical data:
>
> ```
> Phase 1: CalcUsage outputs + aggregation outputs + FORMULA outputs (canonical)
> Phase 2: :>> CHAIN aliases (resolve against Phase 1)
> Phase 3: EXPOSE_PURE aliases (resolve against Phase 1+2, using references field)
> Phase 4: Design-attribute transitive aliases (if adopting Issue 3 Option A)
> ```
>
> **Resolution: Adopt the explicit 4-phase protocol.** Add it to the OutputRegistry
> design in the algorithm document. **CLOSED -- ready to implement.**

---

### Issue 5: Aggregation scoping complexity is hidden, not eliminated

**Severity: Design gap -- missing specification.**

The document says:

> Aggregation scoping (was 4.7) moves into Step 5 (OutputRegistry construction).

But current Step 4.7 has three matching strategies plus a BF-6 child-walk heuristic.
The OutputRegistry section shows registration code that assumes `agg.module_eqn` and
`agg.instance_path` already exist -- which means the scoping logic (the hard part) must
have already run.

Where does it run? The design doesn't say.

**Proposed fix:** Either:

- (a) Show the scoping logic inline in OutputRegistry construction (making Step 5 more
  complex than currently depicted), or
- (b) Keep scoping as a sub-step of Step 3.5 that produces `ScopedAggregationData`
  before Step 5 consumes it. This is probably correct since scoping depends on the
  hierarchy extraction results from 3.5, not on the OutputRegistry.

Option (b) is cleaner: Step 3.5 extracts and scopes, Step 5 registers.

> **UPDATE (2026-02-13, Spike 2 results):** Confirmed. Spike 2 showed that virtual
> CalcUsage outputs are consumed via aggregation, not CHAIN. Scoping must run before
> OutputRegistry construction so that scoped aggregation data can be registered as
> channels.
>
> **Resolution: Adopt Option (b).** Step 3.5 extracts and scopes aggregation
> expressions (producing `ScopedAggregationData`). Step 5 registers the scoped
> results into the OutputRegistry. The algorithm document already says this
> conceptually but needs clearer language separating the scoping logic from
> registration. **CLOSED -- minor wording fix.**

---

### Issue 6: AggregationDecomposer registry is premature abstraction

**Severity: Over-engineering.**

The design defines a `Protocol` with `decompose()` for a registry that currently has
exactly one implementation (`SumDecomposer`). The project's own guidelines say:
*"Don't create helpers, utilities, or abstractions for one-time operations. Don't design
for hypothetical future requirements."*

**Proposed fix:** Keep the `sum()` handling as direct code. Add the validation the doc
correctly calls for (verify operands are child-part attribute references, document the
uniform-array assumption as a precondition). Create the registry later when you actually
need a second decomposer. Right now it's complexity with zero consumers.

---

### Issue 7: The diagnostic probe MUST be step 1, not step 10

**Severity: Blocks design confidence.**

Migration step 10 is: *"Write probe for template binding format."*

But the design document itself says:

> **PREREQUISITE -- must verify:** We need to determine what `source_path` format
> the SysIDE parser produces for template CalcUsage bindings...

If SysIDE produces full-QN format for template bindings, then:

- The entire virtual binding rewrite mechanism (Step 3.5E) is dead code today
- The `source_path` format for virtual CalcUsage bindings changes, which affects
  OutputRegistry key design
- The design's `_extract_leaf_name()` normalization in Step 3.5E may be solving a
  problem that doesn't exist (if SysIDE already produces bare names) or insufficient
  (if SysIDE produces a format not covered)

**Proposed fix:** Move the probe to migration step 1. Block design finalization on its
results. The probe is:

```python
"""Spike: What source_path format does SysIDE produce for template CalcUsage bindings?

Load a model with CalcUsages inside PartDefinitions (e.g., solar_battery).
For each template CalcUsage, print each binding's source_path.
Determine: bare name? dotted? full SysML QN?
"""
```

> **UPDATE (2026-02-13, Spike 1 results):** Probe completed. Results are definitive:
>
> - **REFERENCE bindings:** Always SYSML_QN format (e.g.,
>   `SolarBatteryLibrary::'PV Module'::cost_model::wattage`)
> - **CHAIN bindings:** Always DOTTED format (e.g.,
>   `annualized_financial.annualized_capital_cost`)
> - **Bare names:** **Never observed.** Zero instances across 94 bindings in 3 models.
> - **Template bindings** use the same SYSML_QN format as concrete bindings.
> - **Virtual CalcUsages** inherit the original source_path unchanged.
>
> **Implications:**
> 1. The virtual binding rewrite for bare-name source_paths (Step 3.5E) is dead code.
> 2. The OutputRegistry needs exactly two source_path formats: SYSML_QN and DOTTED.
> 3. The `_extract_leaf_name()` normalization handling bare names is unnecessary.
>
> **Resolution: Update design to remove bare-name handling from OutputRegistry and
> Step 3.5E. Simplify resolve() to handle only DOTTED (exact match) and SYSML_QN
> (normalize to dotted). CLOSED.**

---

### Issue 8: Missing spike/test strategy

**Severity: Process gap -- high risk of repeating the bug cycle.**

The original `expression-aware-codegen.md` had an excellent bottom-up testing strategy
with specific scripts (Q1-Q6), pass criteria, and questions to answer before touching the
pipeline. The revised design has no comparable strategy.

Given that this redesign exists precisely because the previous implementation devolved
into cascading bugs from untested assumptions, the revised design should define:

**Spike 1: Template binding source_path format** (blocks everything)
- Load solar_battery + e2e_attr_expr models
- For each CalcUsage, log `is_template`, `instance_name`, and every binding's
  `source_path` and `binding_type`
- Pass criteria: document the exact format for each binding type

**Spike 2: OutputRegistry standalone validation**
- Build the OutputRegistry from a real model's extracted data
- For every binding in the model, call `registry.resolve(binding.source_path)`
- Assert every CHAIN/REFERENCE binding that currently resolves to MODULE_OUTPUT
  also resolves correctly through the registry
- Pass criteria: 100% match with current backtracker results

**Spike 3: Parallel validation**
- Run old backtracker and new OutputRegistry-backed backtracker side by side
- Assert identical `binding_resolutions` for every binding
- Pass criteria: zero divergences on solar_battery and e2e_attr_expr models

**Spike 4: EXPOSE_PURE transitive resolution**
- Specifically test the Bug 2 scenario with both concrete and virtual CalcUsages
- Create a unit test with virtual CalcUsage instance names (qualified format)
- Pass criteria: `financial.total_capex` resolves to MODULE_OUTPUT (not ENTRY_POINT)
  for both concrete and virtual CalcUsage formats

> **UPDATE (2026-02-13):** Spikes 1-4 from the `syside-assumption-spikes` spec have
> been completed. See `.project/research/20260213_spike_results_syside_assumptions.md`
> for full results. These spikes provide the empirical ground truth for design
> finalization and satisfy the process gap identified here.
>
> **Resolution: CLOSED.** The spike/test plan was executed and results are
> documented. Remaining validation work is implementation-time unit tests.

---

## Summary

The design is 80% there. The architectural direction (OutputRegistry, ChannelAlias,
EXPOSE_PURE as alias) is correct. The critical gap is that the OutputRegistry's resolution
logic **doesn't account for the concrete-vs-virtual instance name format divergence** --
which is the exact root cause of Bug 2.

### Required changes before implementation

| # | Issue | Action |
|---|-------|--------|
| 1 | Virtual instance_name format | Register short instance name as additional lookup key |
| 2 | Bare-name ambiguity | Choose and specify a collision policy (recommend: remove on conflict) |
| 3 | Design attr two-hop split | Decide: register transitive design attrs as aliases in registry (recommended) or specify the separate mechanism |
| 4 | Alias registration order | Make the phase ordering an explicit contract |
| 7 | Probe is step 10 | Move to step 1, block design finalization on results |
| 8 | No spike/test plan | Define spikes 1-4 with pass criteria |

### Recommended changes (improve quality but don't block)

| # | Issue | Action |
|---|-------|--------|
| 5 | Aggregation scoping hidden | Clarify that scoping runs in 3.5, Step 5 only registers |
| 6 | AggregationDecomposer | Drop the Protocol/registry, keep direct sum() code with validation |

---

## Post-Spike Status (2026-02-13)

All 8 issues now have UPDATE notes with spike-backed resolutions. Summary:

### Resolved -- ready to update algorithm document

| # | Issue | Resolution | Spike |
|---|-------|-----------|-------|
| 1 | Virtual instance_name | Narrower than feared. No CHAIN wires to virtual outputs. Register both keys; aggregation scoping handles virtual outputs separately. | Spike 2 |
| 2 | Bare-name ambiguity | **Skip entirely.** Zero bare-name references across 94 bindings. No collision handling needed. | Spike 4 |
| 3 | Design attr two-hop | Adopt Option A (aliases in registry). EXPOSE_PURE alias must use `references` field, NOT `expression_text`. | Spike 3 |
| 4 | Alias registration order | Adopt explicit 4-phase protocol. Confirmed by Spike 3 resolution chain. | Spike 3 |
| 5 | Aggregation scoping | Adopt Option (b). Scoping in 3.5, registration in Step 5. | Spike 2 |
| 6 | AggregationDecomposer | **OPEN.** No spike data. Decision pending: drop Protocol or keep. | N/A |
| 7 | Probe first | **Done.** SysIDE produces SYSML_QN for REFERENCE, DOTTED for CHAIN. Zero bare names. Bare-name handling in resolve() is dead code. | Spike 1 |
| 8 | Missing spikes | **Done.** Spikes executed and documented. | All |

### Key algorithm document changes needed

1. **OutputRegistry.resolve():** Remove bare-name extraction (step 3). Only handle exact match and `::` -> `__` normalization.
2. **OutputRegistry.register():** Remove bare-name registration. Remove collision handling code.
3. **EXPOSE_PURE alias construction (Step 4.5):** Use `references` field to build `canonical_name`, not `expression_text`.
4. **Registration phases:** Add explicit 4-phase protocol to Section 12.
5. **Step 3.5E (binding rewrite):** Remove bare-name normalization. Only handle SYSML_QN and DOTTED.
6. **Section 4 (Step 3.5C):** Drop `AggregationDecomposer` Protocol. Show direct sum() code.
7. **Section 4 (Step 3.5):** Clarify aggregation scoping runs here, Step 5 only registers.
8. **Migration path:** Remove step 10 (probe). Reorder: OutputRegistry as step 1-2, parallel validation, then remove old indexes.
