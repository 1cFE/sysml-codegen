# Provenance — C18 language-rejected coordinate

Constructed for SOURCE-IDENTITY Item 4 as an aggregation-term reference to a feature that does not
exist in the model.

## Measured language boundary

The licensed SysIDE loader rejects the model with:

```text
[ERROR] model.sysml:19: error (reference-error): No Feature named 'ghost_cost' found.
```

**[AGENT] (ratified by owner, 2026-08-09):** C18 ends at this language load error. Codegen does not
repeat language name resolution. The kept matrix test requires load refusal and preserves
`ghost_cost` in the parser diagnostic.
