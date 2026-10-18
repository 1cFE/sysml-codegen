# Product-lens ledger: subset-profile-conformance

Append-only.

## 2026-10-18 — spec draft

Epic: EXEC-SUBSET-CONTRACT

- **Verdict:** none. The product-lens was not run.
- **Why:** the instruction file `~/.claude/scripts/product-lens.md` could not be read from the spec session, so no subagent could run it as written.
- **Epic findings referenced:** none. The epic's Product-Lens section reads "Not yet run."
- **Partial check done instead (not a substitute):** the spec author read `.project/product/INDEX.md` and P-0003. P-0003 ("we do NOT create workarounds to accept bad models", owner-verbatim) is now cited in the spec's Gates. No contradiction with P-0001 to P-0007 was found from the index lines alone; entry bodies other than P-0003 were not read.
- **Open:** run the product-lens on the spec before or during `/_my_spec_review`.

## spec — 2026-10-18 — rev .project/active/subset-profile-conformance/spec.md

Epic: EXEC-SUBSET-CONTRACT (no epic findings exist: the epic's Product-Lens section reads "Not yet run.")

Supersedes the "spec draft" block above: the product-lens has now run, by a `general-purpose` subagent whose instruction set was `.claude/scripts/product-lens.md`.

Point (re-derived): 2a makes codegen's real route (screen bypassed) the independent ground truth for the agentic-mbse subset contract, with drift failing a codegen test; it changes nothing about what the generator accepts/refuses and does not normalise silent loss of authored math (refuse-with-diagnostic, no workarounds)   [source: agentic-mbse epic "Owner gates for both halves"; .project/product/0003-no-workarounds-for-bad-models.md; .project/product/0004-product-identity-parse-walk-emit.md; agentic-mbse .project/adr/0001-subset-profile-capability-ownership.md inv. 5, grade: owner/HARD (gates, P-0003/P-0004) | agent/ratified (ADR 0001)]
Falsifier: the spec lets the screen be checked against itself, changes generator accept/refuse without parking it for the owner, leaves a model the screen calls CLEAR but the generator refuses undetected, or records a silent drop as accepted before RG-1
Findings:
- spec-F1 [DO]    The screen runs only on generating fixtures (B4); no criterion requires every refusing fixture/case to produce a matching `refused` rule or a disagreement-record row, so C's "every known disagreement" is only as complete as what was noticed — briefs/align.md reading + agentic-mbse P-0001 (agent/ratified) — disposition: FIXED in spec, criterion group C (every refusing fixture and refused case ends in a mapped `refused` finding or a recorded disagreement)
- spec-F2 [DO]    The ground-truth handover is unstated: the spec does not say whether agentic-mbse records cite 2a corpus cases or what happens to Item 1's 80 probes; two evidence sets back one record (smell 1; same shape in the site_account.csv frozen-copy option) — agentic-mbse .project/adr/0001-subset-profile-capability-ownership.md inv. 5 (agent/ratified) — disposition: FIXED in spec, Known Requirements → Independence (record outcomes rest on 2a cases; Item 1 probes are historical, not a second live authority); citation mechanism and a possible ADR 0001 invariant 1 amendment filed under Open Questions
- spec-F3 [DO]    CALC-USAGE-BARE-RESULT-DROP closes as contract `omitted` with no way to mark "loss, candidate must-block, RG-1 pending"; the record would read as an accepted outcome for a silent drop (same exposure: the UNSUPPORTED-OPERATOR MANUAL_REQUIRED stub). Parked to RG-1, not overridden — .project/product/0003-no-workarounds-for-bad-models.md, 0004-product-identity-parse-walk-emit.md (owner/HARD) — disposition: FIXED in spec, criterion group D (record and case mark the candidate refusal pending RG-1; a written RG-1 recommendation is required, stub included); marking mechanism under Open Questions
Smells: two representations must be manually kept synchronized (spec-F2; also the site_account.csv frozen-copy option) — escalate to design / design_review
Gate: DISPOSED (spec-F1, spec-F2, spec-F3)
