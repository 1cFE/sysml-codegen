# Implement Brief — Lifecycle Item 6: Public Documentation and F1 Evidence Reconciliation

**Stage:** implement (single stage: inventory → spec-as-checklist → fix → evidence; a light
independent audit follows)
**Epic authority:** Item 6 (register rows 6–7) in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`.

## Intent

Make public claims and F1 evidence agree with the pinned landed candidate chain — WITHOUT
reimplementing anything already landed. Current chain: sysml-codegen through Item 5
(`4c6223c` + audit commits), agentic-mbse `4c18d61`, TEAx `d545701f`.

## Scope (epic Item 6, verified current)

1. Public docs: profile/package versions, equality/ordering, subtype coverage, snapshot replay
   (now v5!), extension/final V11 (extension-time check DELETED by Item 3 — docs must say the
   settled branch), diagnostics severity (Item 4), portability (Item 5). Inventory every stale
   claim in docs/architecture/ against landed code before editing; fix with citations.
2. TEAx F1: record F1 evidence at `d545701f`, correct the stale `927a9e1` audit reference,
   compare complete report contents across evaluators (environment per Item 1 evidence §3).
3. `TEAX_SIMKIT_PATH`: scope invalid-path behavior to codegen test infrastructure and make an
   explicitly-set invalid path FAIL instead of discovering a sibling (this is the one
   production-behavior change in the item — RED-first, small).
4. PR-description reconciliation: draft updated descriptions for agentic-mbse PR #11 and
   codegen PR #9 reflecting Items 1–5 as landed locally, WITHOUT claiming release readiness
   and WITHOUT pushing or editing the PRs (drafts into the item directory; Item 13 owns the
   actual update). Note the machine-enforced merge order (#11 first — the _upstream_pins guard).
5. Delete stale comments, duplicate version literals, obsolete documentation helpers where
   safe. Docs 27/28 were updated by Item 1; verify they survived Items 2–5 accurately.

## Constraints

- No reimplementation of F1 normalization; no release-readiness claims anywhere.
- Correction law: fix stale claims by amendment; no compensating "this used to say X" prose.
- Every corrected claim carries a code/evidence citation. The epic's success criterion is
  "every correction-register claim agrees with landed code and versions."
- Standard environment gotchas apply (license sourcing, -rs skip check, fixture bytes,
  .claude/projects, unrelated dirty files).

## Deliverables

`.project/active/constraint-lifecycle-docs-f1/{spec,evidence}.md` (spec = the inventory with
per-claim disposition; folded plan), PR-description drafts, the TEAX_SIMKIT_PATH fix + tests,
doc amendments. Commit as candidate, report CANDIDATE_REV.
