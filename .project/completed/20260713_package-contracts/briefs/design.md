# Brief: Item 9 design — Contracts and Sealing

You are the design stage for Item 9 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 8 implement session may be committing to this tree — write ONLY design.md (+ CURRENT_WORK entry); touch no code. Its committed design (`.project/active/snapshot-v3/design.md` rev 2) is your reference for the snapshot path's landed shape; `git log` shows its phases as they land.
- Artifact: `design.md` in `.project/active/package-contracts/`.

## Input
- Spec (committed): `.project/active/package-contracts/spec.md` — three-fingerprint separation, graph-only ModelContract, verified-on-load seal, S4-gap requirements are fixed; Open Questions (env-compat fatal-vs-advisory, runtime-version source, the stencil/re-seal tension) are yours to decide and record.
- S4's test-only seal: `s4_lib.py` (verify_seal + its named gaps).
- Item 7's landed catalog + CATALOG_FINGERPRINT; the teax loader seam (Item 0 mismatch 8: load by declared package name; Item 10's provisional loader noted "pending Item 9").

## Design guidance (orchestrator, agent-grade)
- The stencil tension: prefer seal-at-package-time (the seal is the LAST generation step over final on-disk state, including preserved handwritten files as they exist) — re-sealing after human edits is the documented workflow (a modified stencil invalidates the seal until re-sealed; that is correct behavior, not a bug). Decide and record with the alternative.
- Env-compat: advisory-by-default with a strict flag is the usual shape — but decide from what the teax loader can actually enforce; record the rule.
- Contract file formats: JSON beside the package (matching S4's shape) — pin canonical serialization (sort_keys etc.) so fingerprints are byte-stable.
- Design the teax-loader verification contract precisely enough that a small teax-side wiring change (Items 10's loader hardening note) is mechanical — but that change itself lands with Item 14's integration sweep or a follow-on, not this item; state the seam.
- A design_review follows only if genuinely contested calls emerge; this is a well-trodden shape (S4 proved it) — keep it boring and proportional.
