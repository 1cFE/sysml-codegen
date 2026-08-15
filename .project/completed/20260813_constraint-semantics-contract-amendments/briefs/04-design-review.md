# Stage brief — design_review (Item 1: Contract and Authoring Policy)

Review target: `.project/active/constraint-semantics-contract-amendments/design.md` — the
amendment-execution design for CONSTRAINT-SEMANTICS Item 1 (documentation/contract item).

Authorities: the item spec `.project/active/constraint-semantics-contract-amendments/spec.md`
(+ `spec-review.md` Resolutions), the umbrella spec and rulings in
`.project/active/constraint-semantics-contract/`, and the two documents being amended:
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` and
`.project/concepts/constraint-execution-lifecycle-requirements.md`.

For companion-repo (agentic-mbse) facts your sandbox cannot read, use the orchestrator-verified
block in `briefs/03-design.md` — do not count companion unreadability as a design defect, but do
check the design consumed those facts correctly.

## Review pressure to apply

1. **Quoted-current-text accuracy.** The design quotes current contract/companion text per
   amendment. Verify the quotes against the actual files — a misquoted "current text" makes the
   implementer edit the wrong thing or fail to find it.
2. **The invariant-61 move.** The design adds a NEW invariant (vacuous-gate warning tier) plus a
   new "Headline states and coverage truth" subsection, self-flagged as a bigger move than an
   amendment. Challenge it: does a new invariant in a ratified contract need anything the design
   doesn't provide (numbering collision with future amendments, Appendix cross-refs, companion
   mirror)? Is the single-definitions-home claim real (do all other amendments actually point
   there rather than restating)?
3. **Equality-instruction home.** Design rejected the `Status: Proposed` design-space-studies
   concept and put the authority in the lifecycle contract's Supported boundary section. Check
   the owner's verbatim payload ("call out in our concept WHEN...") is satisfied and that the
   agentic-mbse guidance rendering actually instructs modelers (not just cites).
4. **Semantic correctness of amended text.** Each amended invariant/requirement must state the
   umbrella spec's ruling exactly — check especially invariant 33 precedence, the
   applicable-asserted-gate definition (vacuous counts as missing assessment until explicit
   inapplicability), invariant 32's restatement over applicable asserted gates, and 46a's
   fail-closed extension. Meaning only — flag any normative token spelling or report field name
   (Item 3's).
5. **Provenance.** Amendments must not re-grade amended statements; rulings stay [AGENT]
   (ratified by owner, 2026-08-12); the R-POL-4 taxonomy content stays agent-grade with the
   need owner-grade. Check the drafted amendment texts, not just the design's preamble.
6. **The parked D-2 vs D-4/SRC-01 conflict**: verify no drafted amendment touches either
   statement (check the actual target list against where those statements live).
7. **Sweep adequacy**: are S1/S2/S3 patterns sufficient for the "no remaining statement"
   criterion, and is the `.project/` exclusion defensible?
8. **Implementability**: could an implementing agent execute this without re-deriving decisions?
   Is verification.md's format specified?

## Process

Work synchronously — never pause for background agents; finish the artifact this turn. Write
`.project/active/constraint-semantics-contract-amendments/design-review.md` with verdict
(Approve / Revise) and findings by severity, each citing the design text it targets. End with
`ARTIFACT: <path>`.
