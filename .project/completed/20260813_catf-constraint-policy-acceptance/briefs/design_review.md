# Orchestration brief — design_review stage — CONSTRAINT-SEMANTICS Item 5

Review `.project/active/catf-constraint-policy-acceptance/design.md` (committed at `2821c38`)
against its spec (`spec.md`, note SC-3 is AMENDED to the accounting identity) and the ruled
authority `owner-disposition.md` (RULED 2026-08-13 — do not re-litigate its rows; they are
owner-ratified/owner-originated per its Provenance section).

Context you need before judging:

- The design ran seven licensed probes (harness in `probes/`). Two owner-ruled row groups
  REFUSE at elaboration (`SI_RENDERING_COLLISION`): A9's assert-band and 26 of 27 A5/A6 radius
  derivations. The design SURFACED these as D-S1/D-S2 and parked them for owner ruling —
  the owner has been notified and their ruling may land in parallel with this review. The
  orchestrator independently verified the code diagnosis (unit metadata minted only for
  CalcNode consumers, elaborate.py:1679-1689; collision at project.py:394-397).
- Judge the design's handling of that surprise (capture-fidelity §4 discipline: no silent
  re-disposition, identity left in force, dependent conclusions parked), not the surprise
  itself. The owner ruling on D-S1/D-S2 is out of the review's scope.

Review focus, in order of value:

1. **Bets B1–B4** — are the falsifiers real and checkable? B2 (composite stability) has a named
   de-risk step; is it sequenced correctly in the handoff?
2. **D2's integrity manifest** — does the three-way join actually prove the accounting identity
   without reading the catalog for counts (the one-direction rule)? Any circularity?
3. **D3's unit story** — the probes showed a constraint formal cannot carry unit text at all;
   does D3's "both surviving gates are dimensionless-safe" argument hold for A3's edges and
   A2's zero floor?
4. **D6's mutation design** — is inputs-JSON mutation through one generated package a faithful
   SC-5 proof (satisfied path + reject path, durable case records)?
5. **D4/D7 mechanics** — computed-attribute derivation shape (measured in P6) and the R3
   baseline placement: any gap between what was probed and what will be authored?
6. **SC-6 layout** — does the expected-outputs plan actually produce a commit-order argument?

The usual review dimensions apply (contradictions with owner/[HARD] statements, ownership
ambiguity, unverifiable claims), but do not manufacture findings — this design was probe-first
and cites measurements; check that the citations hold rather than asking for more process.
End with your verdict and `ARTIFACT: <path>`.
