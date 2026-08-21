# Phase 1 Findings: Product-Ledger Migration Shape

**Completed:** 2026-08-21 07:54 PDT
**Plan:** `.project/completed/20260821_scaffolding-register-boundary/plan.md`, Phase 1
**Scratch root:** `/tmp/scaffolding-register-boundary-phase1.bDGvKX`

## Question

Can a pack-compatible frontmatter block be prepended to the existing P-003 entry while leaving
every byte of its prose unchanged, and will the unmodified pack `product.sh` discover it?

## Scratch entry

The scratch entry used the target filename
`0003-no-workarounds-for-bad-models.md` and metadata derived from the existing entry and its Git
history:

- `id: 0003`
- `title: No workarounds to accept bad models`
- `date: 2026-08-16`
- `owner: Reid W`
- `status: active`
- `provenance: "[OWNER]"`; the `[OWNER-VERBATIM]` quote remained in the unchanged entry body
- `surfaces: [extraction, elaboration, generation]`
- `checked: null`

## Results

The normal path passed:

- `product.sh index` exited 0 and emitted exactly one identified `0003` row.
- The row title was `No workarounds to accept bad models`.
- The original body and the body below the new frontmatter both had SHA-256
  `ffdbdf03991965c252005da39d4cc28149f4c4ab1d4b0cd2b7ff62dd48ec5f32`.
- A byte comparison of those bodies was empty.

The leading-blank-line failure also reproduced, with one correction to the plan's prediction:

- `field()` read every frontmatter value as empty because line 1 was not `---`.
- `product.sh index` still exited 0.
- The identifiable `0003` row was absent.
- The entry did not vanish completely. The generated index retained an empty ghost row rendered
  as `-  ·  · `. This is silent malformed output, not a clean omission.

## Execution adjustment

The plan's `PRODUCT_DIR=$T product.sh index` stencil cannot isolate the source script because
`product.sh` unconditionally derives `PRODUCT_DIR` from the current project's `.project/`
directory. The proof instead ran the same unmodified script from a temporary project root whose
only data was the scratch ledger. This preserved the intended isolation and did not touch the
repository's product register.

## Conclusion

B3 is supported. Frontmatter is the script-managed metadata surface, and prepending it leaves the
promise body byte-identical. The kill criterion did not trigger.

The plan's exact full-suite gate remains unresolved. This checkout has no
`STOP_PARSER_ARTIFACT_SOURCE_INPUTS` manifest for its current commit, and the retained process
tests fail closed without one. The licensed working-checkout run reached 2,387 passed and 9 policy
skips; its 10 failures and 2 setup errors were all the named missing-manifest refusal. Creating a
current manifest requires a separate five-repository artifact build, so Phase 2 remains parked
until the owner either requests that build or accepts the phase with this environment limitation.

## Owner Disposition

`[OWNER, 2026-08-21]` The owner accepted the recorded artifact-manifest limitation and authorized
Phase 2. This acceptance allows implementation to continue with the limitation visible. It does not
make the unavailable exact full-suite gate green.
