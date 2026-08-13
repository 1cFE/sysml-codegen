# Brief: design stage — CONSTRAINT-SEMANTICS Item 4 (Predicate Defect Hardening)

Orchestrated run (owner-invoked `/_my_orchestrate`, check-ins waived). You are the design stage.
Work synchronously: never pause for background agents or schedule check-backs — finish the
artifact this turn and end with `ARTIFACT: <path>`.

## Input

The approved spec: `.project/active/constraint-predicate-hardening/spec.md`. Read it in full —
it is the requirements authority, including the Known Requirements grades, Non-Goals, Open
Questions, and the Surfaced section. The epic section
(`.project/backlog/epic_constraint_semantics_contract.md` Item 4) is the scope authority.

## What design must settle (the spec's deferred questions)

1. **Where Defect A's cure lands** — the reference walk itself vs the predicate entry. Price
   both; pick by the rule's actual scope ("a unit annotation contributes its value and never a
   reference" has ONE owner — the cure extends its reach, it must not mint a second special
   case).
2. **Defect B's split across repos** — where the blocked chain's written reference and location
   are captured (companion profile payload vs codegen re-derivation), and whether multi-chain
   identification is one diagnostic per distinct reference or one listing them. Note
   `tests/conformance/test_elaboration_payload_identity.py:236-266` asserts on the rendered
   detail string; any change to it must be a stated design decision, not a silent test edit.
3. **The fourth lane** (`in tol = 0.05 [m]` binding refused as
   `SI_EXPRESSION_SOURCE_UNSUPPORTED`). Orchestrator ruling **[AGENT]**, recorded in the spec
   commit: probe it, price both options, and decide by the spec's rule — cure it in this item
   iff the cure is the same unit-annotation rule reaching one more lane; otherwise
   characterize + file it, and phrase Defect B's advertised rewrite so it does not point at a
   refused form. This lane sits on Item 5's blessed tolerance-band recipe, so if it is cheaply
   curable under that rule, cure it.

## Probe before you commit to a mechanism

You have execution in this session. The spec's companion-side statements were made WITHOUT
reading companion source (sandbox restriction, now lifted for you) — verify them against
`/home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/sysml/executable_profile.py`
before designing the Defect B split. Throwaway probes (scratchpad, not committed) that confirm
where the `[` operand walk raises and what payload the profile can carry are cheap and have
repeatedly refuted design assumptions in this project — use them.

- Test interpreter: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`
- License for live-model probes: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`
- Companion worktree: `/home/reid/1cfe/agentic-mbse-item7-rebuild` (tip `bc69f04`); codegen
  branch `item7-rebuild` (tip `cb5be20`). Do NOT commit code in this stage; design only.

## Constraints to carry (do not re-decide)

- Bindings-only stays (Q4); no chain admission; no `==` tolerance semantics; no profile
  expansion in either direction.
- The Item 2 disposition/severity contract is unchanged: plain+blocked still generates and
  catalogs unassessed; asserted+blocked still halts. Defect B changes only what the message
  says.
- The cure's demonstration predicate is an inequality on a supported shape, never
  `== <literal> [unit]`.
- Kept characterizations land red before fixes (plan must sequence this).
- Frozen twins untouched; new fixtures for characterizations.

## Deliverable

`.project/active/constraint-predicate-hardening/design.md` — mechanism-level: exact files and
seams touched in each repo, the diagnostic's message shape (show the rendered text), the
de-duplication/ordering key, fixture plan, test plan mapped to the spec's success criteria,
and landing order across the two repos (companion editable-install coupling: a companion
change that hard-errors breaks codegen's licensed tests instantly — sequence so both trees
stay green at every commit). Record every decision with provenance. End with
`ARTIFACT: <path>`.
