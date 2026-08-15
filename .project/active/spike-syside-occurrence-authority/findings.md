# Spike: SysIDE occurrence authority

## Summary of Findings

The assumption is confirmed for SysIDE 0.8.4. Native `nested_occurrences`, `nested_parts`,
`nested_usages`, and `usages` expose semantic declaration objects. None of the five probe models
returned a second object with the same declaration ID to represent a parent context or
multiplicity index. Codegen must therefore keep the exact-ID occurrence walker described by D3.
The boundary is narrower than the current implementation: native `Usage.usages` already supplies
the inherited/redefined effective declaration view. Codegen should consume that view, filter the
supported composite part declarations, and own only concrete expansion and context.

The clearest counterexample is `d38_caret`: SysIDE exposes one `cell` `PartUsage` declaration,
while codegen materializes four concrete occurrences with the same effective declaration ID and
distinct structured occurrence IDs carrying indices 0 through 3. In
`nested_occurrence_override_probe`, SysIDE reports no `nested_occurrences` at all for definition-
owned `panel` and `source` declarations, while codegen materializes the contextual
`the_design/panel/source` tree. Retyping also remains contextual: `spec_chain_twolevel` uses the
base containment slot in the occurrence ID and records the redefining declaration as the effective
usage.

## Question / Goal

Assumption under test: SysIDE 0.8.4 exposes semantic usage declarations and their inherited
feature views, but it does not materialize the finite, contextualized runtime occurrences that
the exact-ID codegen walker records with containment-slot paths and multiplicity indices.

The assumption is confirmed if `Usage.nested_occurrences` and related native surfaces return the
same declaration objects/IDs visible in the document, while multiplicity, inheritance, and retyping
produce additional context only in codegen's `OccurrenceIndex`. It is disproved if SysIDE exposes a
canonical API whose objects distinguish every concrete parent context and multiplicity index.

This spike serves ELABORATE-FIRST Item 6 and the occurrence-ownership decision in
`.project/active/elaborator-design/design.md` D3.

## Log

- 2026-08-09 15:26 PDT: the generated SysIDE 0.8.4 API reference defines
  `Usage.nested_occurrences` as the `OccurrenceUsages` that are `nested_usages` of a `Usage`, and
  defines `nested_usages` as `Usages` that are `owned_features`. That wording describes semantic
  feature declarations, not a concrete occurrence population.
- 2026-08-09 15:39 PDT: the first live probe compared native surfaces with codegen's exact-ID
  `OccurrenceIndex` across five maintained fixtures. The probe initially reported standard-library
  declarations as “foreign” because `Usage.usages` includes inherited library features. That field
  did not test contextual identity, so it was removed rather than interpreted.
- 2026-08-09 15:46 PDT: the reduced probe completed. Native surfaces returned only the canonical
  declaration objects for every target ID. Concrete codegen counts were 3 for
  `nested_occurrence_override_probe`, 2 for `spec_chain_twolevel`, 4 for `retype_model`, 6 for
  `d38_caret`, and 5 for `deep_cross_scope_probe`. The native surfaces returned no contextual
  clones in any fixture.

## Reproduction

From the `sysml-codegen` repository:

```bash
uv run python .project/active/spike-syside-occurrence-authority/probe.py
```

The command requires the same SysIDE license used by the maintained licensed tests.

## Open Questions / Follow-ups

- Item 6 should retain the SysIDE-version gate. A future SysIDE release could add a canonical
  concrete-occurrence API, but 0.8.4 does not expose one through the tested usage surfaces.
- Replace or parity-pin the current global owner/type-closure child selection against
  `Usage.usages` before the atomic cutover. This is an authority-boundary repair, not grounds to
  delete codegen's `OccurrenceIndex`.
