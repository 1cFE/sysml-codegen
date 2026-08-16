# Probe: authored bare-reference discriminator authorability

**Date:** 2026-08-15
**Status:** The proposed u6-style candidate is falsified; broader authorability remains open.
**Environment:** SysIDE 0.8.4 through the repository's licensed `uv` environment.

## Question

Can the bare-reference regression proposed in
`.project/research/20260815-142743_bare-expression-side-measurement.md:251-256` make the exact
`PartUsage` owner and consumer-lineage selection disagree?

The proposed shape has sibling usages `comp_a` and `comp_b`, each redefining `length`, with a bare
computed expression authored inside one sibling. A parent-scope variant asks whether bare `length`
can instead select one of those sibling-owned redefinitions from above them.

## Result

The inside-sibling model loads. SysIDE resolves bare `length` to the redefining feature owned by the
same sibling as the consumer:

```text
inside-sibling loaded= True resolved= [('BareInsideSibling::Plant::comp_b::length', 'BareInsideSibling::Plant::comp_b')]
```

Both positional and owner-aware routes therefore select `comp_b`; the shape does not discriminate.

The parent-scope variant does not load. Bare `length` is not visible from the parent:

```text
error (reference-error): No Feature named 'length' found.
parent-scope loaded= False resolved= [("'<placeholder Feature>'", 'None')]
```

## Disposition

This probe falsifies the one candidate topology named by the measurement report. It does **not**
prove that no legal authored discriminating topology exists. The design keeps authorability open
and requires a broader learning test or an owner-approved amendment to the success criterion before
production implementation.

## Reproduction

From the repository root, with the normal SysIDE license available:

```bash
uv run python \
  .project/active/qualified-reference-occurrence-anchoring/spike/\
bare-discriminator-authorability/probe.py
```

Inputs and the reporting script are retained beside this file.
