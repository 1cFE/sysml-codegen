# Brief: audit remediation — re-audit findings 1, 5, and 6

Sent to an `implement` stage session by the orchestrator.

## Work item

The independent re-audit at `audit.md` (2026-08-16) reopened certification with seven findings. The
owner has authorized fixing **1, 5, and 6**. Findings 2, 3, 4, and 7 are **out of scope** — they are
wording and disposition calls reserved for the owner at close. Do not touch them.

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` One modeled source occurrence must become exactly one runtime
  source reaching every and only its bound consumers.
- `[OWNER, 2026-08-16]` Fix findings 1, 5, and 6.
- `[AGENT — orchestrator]` The repair itself is not in question; both audits agree the resolver does
  what the design says. What failed is the **evidence**, and in one place the code's honesty about a
  case it cannot currently reach. Restore both.

## Finding 1 — SC12's identity proof covers 13 roots, not 153 (High)

Verified independently by the orchestrator: `verification/corpus_compare.py:507` captures the 140
frozen corpus roots with `with_identity=False`; only the 13 promoted roots at `:508` get identity.
`verification/adjudicate.py:98-104` then maps a missing block to `None`, compares `None == None`, and
counts those roots as compared — printing "0 of 153". Absence was counted as agreement.

**Sharper than the audit states, and it drives the fix:** four *corpus* roots actually changed —
the `.project/active/self-binding-replacement/spike/fixtures/` originals of u4–u7 — and those sit in
the identity-less section. It is not only unchanged roots that went unmeasured.

Required:

1. Capture identity for **all** frozen roots, before and after. The "before" side must be
   regenerated under the **pre-repair** resolver, not reconstructed — check out
   `src/sysml_codegen/elaboration/elaborate.py` at `98970c9^`, regenerate, then restore and verify
   `git diff -- src/` is empty. The rest of `before.json` must stay byte-identical to what is
   committed apart from the added identity blocks; if anything else moves, stop and report it.
2. Make `adjudicate.py` **refuse** a missing identity block rather than compare `None == None`. An
   absent block must count as a problem, not as agreement. This is the bug that let the hole hide.
3. Update every artifact carrying the false claim: `plan.md`, `verification/README.md`,
   `verification/adjudication.md`. State the real root count and the real comparison.

## Finding 5 — absent live leaf fails open, and the verifier shares the blind spot (Low)

`_resolve_direct_reference` falls through to `_resolve_leaf` when `self._elements` lacks the exact
leaf (`elaborate.py:2314-2317`), because `_stable_elements` skips Features with no `qualified_name`
(`elaborate.py:641-642`). `verification/corpus_compare.py:220-223` excludes the same shape, so the
branch and the tool that measures it share one blind spot. A fresh scan of 138 loadable roots found
zero such one-segment facts, so this is latent.

Required:

1. Make the absent-leaf case **explicit and deliberate** in the code, not an implicit fall-through
   that reads as the definition-owned path. The item's declared intent is *fail loudly rather than
   fall back*; weigh that against the fact that no reachable site exists, decide, and record the
   reasoning in the code and in your notes.
2. **If you make it raise**, you must prove no corpus site regresses — regenerate the ledger and
   show the changed-row set is unchanged — and you must keep a test that reaches the new path.
   If you instead keep the existing route, the case must still be explicit and separately tested or
   explicitly documented as unreachable with the evidence for that.
3. Remove the verifier's matching exclusion so `corpus_compare.py` **measures** the shape instead of
   dropping it. A verifier blind in the same place as the code is the failure mode here.

## Finding 6 — two fail-closed edges weakly pinned (Low)

Verified: `tests/conformance/test_elaboration_fail_closed.py:215-225` asserts only a `Counter` of
diagnostic **codes**, while the design asks for the full consumer/parameter/detail tuple. And
`grep` for the selected-owner-but-missing-leaf-target message (`elaborate.py:2335-2341`) across
`tests/` returns nothing — that raise has no kept test.

Required: pin the arrayed strict/lenient edge on the full tuple the design names, and add a kept
test that reaches the missing-leaf-target raise. If that raise is genuinely unreachable from an
authored model, say so with evidence rather than inventing a fixture that does not represent one.

## Constraints

- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. No license-related skip.
- **Do not weaken, delete, or rewrite an existing assertion to make anything pass.** If one looks
  wrong, stop and report it.
- Do not touch findings 2, 3, 4, or 7. Do not edit `spec.md` success criteria. Do not absorb the
  pre-existing ruff/mypy backlog (131/52, verified identical at `2768c68`) or the 17 environmental
  missing-`pandas` suite failures.
- Any production edit stays confined to `elaborate.py` and must not widen a schema, index,
  projection, or codec. If you believe it must, that is a premise conflict: stop and report.
- Full suite must end no worse than 17 failed / 2143 passed, with the failing node set identical by
  name.

## Deliverable

The three fixes, the regenerated ledgers, corrected artifacts, and a short remediation note in
`audit.md` recording what now holds and on what evidence. Report results exactly — including any
finding you could not close and why. End with `ARTIFACT: <path>`.
