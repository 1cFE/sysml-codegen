# Spec Brief — Lifecycle Item 11: TEAx Constraint Evidence Durability

**Stage:** spec (TEAx-owned; artifacts here for register continuity)
**Epic authority:** Item 11 (register rows 13–15); contract rows 13–15 + invariant 46a.

## Intent

- [INHERITED: ratified contract] Absence of a constraint report = EMPTY constraint evidence
  through BOTH evaluator routes (prepared and file-backed); every unconditional report read
  dies. **Opening RED is already reproduced:** Item 9's constraint-free probe hit
  `KeyError: 'constraint_report'` in `evaluate()` (recorded in Item 9's
  codegen-gap-zero-entry finding and evidence) — invariant 46a live.
- Evidence immutability: deep-freeze or defensively isolate the envelope, generated report,
  nested results, observations, status, and margin BEFORE policy can access them; nested
  mutation attempts cannot change authoritative or persisted evidence.
- Register/route/persist/harvest EXACT completed report JSON for satisfied / violated /
  indeterminate / assessment_failed, with package identity.
- Pin expected failure phase per arithmetic shape (fixture-pinned, never
  evaluator-agreement-established); emit OUTPUT_WRITE honestly or collapse the unused phase —
  Item 6's F1 evidence recorded OUTPUT_WRITE as defined-never-emitted; settle it.
- Excluded-only zero-eligible packages → exact `not_assessed` surface; zero-usage packages →
  empty evidence. (Distinct axes — Item 9's zero_channel fixture is constraint-BEARING and
  does not cover these; new fixtures needed.)
- Delete generic/duplicate report adapters and incidental encode-before-policy protection
  once the explicit mechanism owns durability.
- [OWNER] No LOC metrics; deletion over shims.

## Ground truth

- Chain: codegen `b987869`, agentic-mbse `4c18d61`, teax `07eb0ac`, fusion-tea `2422e715`,
  stellarator `c4dcdf27`+diagnostic commits.
- TEAx's evaluator surface post-Items-8/9: load_model_contract seam, multi-channel
  CandidateBridge, the relocated failure switch, EmbeddedCatalogView. Inventory the CURRENT
  report-read paths, evidence object flow, and persistence/harvest surface before specifying.
- Generated-package fixtures come from codegen (epic-sanctioned): the constraint-free fixture
  (reuse/extend Item 9's zero-entry work — a constraint-free variant now has a valid
  EntryPoint pipeline thanks to the Item 9 template fix), an excluded-only fixture, and the
  four-status arithmetic shapes.

## Out of scope (firewall)

Reinterpreting verdicts as study policy; consumer-specific catalog/report schemas (D-3
settled); Item 12's legacy/tracking closure.

## Spec shape

Provenance-graded; RED-first (the 46a KeyError is coordinate one); acceptance per
row 13/14/15 with exact fixture shapes and both routes; the deletion inventory
(adapters/duplicate reads, file:line); phasing.
