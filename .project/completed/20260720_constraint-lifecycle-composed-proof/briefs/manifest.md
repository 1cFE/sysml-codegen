# Manifest Brief — Lifecycle Item 13: Composed Public Lifecycle Proof (Stage 1 of 3)

**Stage:** spec (producing the evidence-coordinate manifest — Stage 1; execution and
release/PR stages follow)
**Epic authority:** Item 13 (register row 17); the ratified contract's proof matrix and
LC-I09 coordinate schema.

## The pinned revision set (final candidates, all certified)

- sysml-codegen `7526665` — agentic-mbse `4c18d61` — teax `c342b10`
- fusion-tea `2422e715` (+ ife regen commits on item8-fusion-embedded-catalog)
- stellarator `c4dcdf27` + `c2f10960` + `342cc799` (feat/stellarator-mbse-demo)

## Stage 1 task: the manifest

Enumerate ALL 41 mandatory acceptance cases from the ratified contract's proof matrix
(.project/concepts/constraint-execution-authoritative-lifecycle-contract.md) into
`.project/active/constraint-lifecycle-composed-proof/evidence-coordinate-register.md`:

For each case: the LC-I09 coordinate fields (exact commits/locks, fixture shape,
source-originated semantics, open predecessor rows — should be NONE now; both public routes;
artifact identity), and its STATUS classification:
- **inherit** — certified by an Items 1–12 audit at the final pinned set with no intervening
  change to its surface (cite the audit + verify the surface is unchanged since);
- **rerun** — certified earlier but the surface moved since (the chain advanced through 97
  commits — most early-item evidence predates later candidates; be strict: evidence at a
  superseded rev REQUIRES rerun);
- **compose** — never run as a single thread (the sealed artifact thread through
  generate→seal→trusted-load→evaluate→persist→query; live A/live B/relocated on the FINAL
  set; IFE 2,301; stellarator five-constraint; the negative mutations).

Also manifest: the required negative mutations (each fails at its intended boundary), the
full-tree byte checks, and the final repository quality gates (focused/optimized/full suites,
lint/format/type baselines, fixture diff review) per the epic's Item 13 scope.

Rules: no failure discovered here gets fixed here — it returns to its owning item (a
composition failure is a finding, and the epic's dependency discipline governs). No skipped
cell, no private-seam substitute, no stale-revision evidence counted. Superseded-epic Items
1/2/4/6 behavior is inherited but the composed run must still exercise it (the epic's
criterion).

Finish THIS turn — never park on subagent notifications.
