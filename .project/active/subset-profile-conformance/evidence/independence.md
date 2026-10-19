# Mutation evidence and its limits (Item 2a P2.4)

A mutation turns one detector off and checks that some case notices. This file says which detectors were turned off, what that shows, and where the evidence is not independent of the screen (design § Independence limits). Recorded 2026-10-18 at the P2.4 commits.

**Counts at the end of Item 2a (2026-10-19, after the final-audit fixes).** This file was written at P2.4, and its counts below are that phase's. P4–P6 and the final-audit fixes added generator mutations for stub causes, R3-row sites and tail sites. `tests/expectations/subset_profile/mutations.json` now holds 70 generator mutations (66 codegen sites, 4 shared agentic-mbse sites), 11 screen mutations and 9 unwitnessed sites (7 codegen: the two retired multiplicity shapes and five `calc_compat_renderer.py` sites P4 found unreachable; 2 agentic-mbse, as listed below). The method, the shared-table limit and the limits of the method are unchanged. `mutations.json` is the current list.

## What was mutated

- **Generator, codegen sites: 9 mutated, 2 unwitnessed.** The 11 codegen sites the account links to a shared rule (`site_account.csv` rows with a `rule`). Each of the 9 reachable sites is neutralized by `tests/helpers/subset_profile/mutate.py`, and every case that fires it in the generator half changes outcome or site reasons. The changed set equals the site's witnesses in each case, so no other case flips (`tests/expectations/subset_profile/mutations.json`, `generator`).
- **Generator, shared agentic-mbse sites: 4 mutated, 2 unwitnessed.** The 6 sites in `mutate.SHARED` (plan PD6): `executable_profile._evaluate_usage_against_definition` 993, 1014 and 1022 through hand patches, and `reference_use.py` 443, 514 and 702. These are **counted apart**. Both halves run them, so a mutation moves the generator and the screen together. It shows that a change at the site is noticed, not that the two sides agree on their own.
- **Screen: 11 shapes.** Each (rule, shape) with a refused context has its recognizer disabled (`mutate.disable_recognizer`). Its stored set is the cases whose agreement with the stored generator answer changes (`mutations.json`, `screen`). In `constraint-predicate/blocked_predicate`, 19 of 25 subjects change. The other 6 also carry a refused finding of another rule whose code the generator gives (design O7), so they keep agreeing.

The tests are `test_generator_mutations.py`, `test_screen_mutations.py` and `test_witnesses.py` (licensed), plus `test_mutation_record.py` and `test_mutator.py` (pure).

## Not mutated: the shared decision tables

- **The 19 expression-walker sites** in `executable_profile.py` (`_walk_arithmetic`, `_walk_value`, `_walk_comparison`, `_walk_proposition`, lines 542–852) are the predicate-eligibility table both sides read. Each has a packaged witness that fires it in the screen half (agentic-mbse `tests/test_subset_site_account.py`, checked live by codegen `test_witnesses.py`). None is mutated, so a wrong decision in the table would be wrong on both sides at once and no test here would see it.
- **`invocation_allowlist.py`** is the table `invocation-callable` reads on both sides. It is not mutated, for the same reason.

## Sites no case fires

| Site | Why no case fires it |
|---|---|
| codegen `occurrence.py` `_multiplicity_indices` nonunique (`SI_MULTIPLICITY_UNSUPPORTED::2`) | SysIDE rejects a nonunique part usage before elaboration. The shape left the records in P2.1 (owner retirement, 2026-10-18). |
| codegen `occurrence.py` `_multiplicity_indices` negative bound (`SI_MULTIPLICITY_INVALID::1`) | SysIDE rejects a negative bound before elaboration. Retired with the nonunique shape. |
| agentic `executable_profile.py` `block_unresolved_definition` (1014) | A definition-typed assertion always resolves to a `ConstraintDefinition`. An untyped `assert constraint c;`, and typings by an attribute def or a part def, all reach `block_missing_predicate` (1022) instead. Only synthetic facts reach it. |
| agentic `reference_use.py` `require_exact_reference_use` (702) | Only `decompose_aggregation_expression` calls it, and nothing under either `src/` tree calls that. |

`test_generator_mutations.py::test_an_unwitnessed_site_fires_in_no_case` fails if a case starts to reach one of these. The agentic-mbse half of the list is `tests/fixtures/subset_profile/inventory/scanner.toml` `[[unwitnessed_site]]`.

## Shapes with no screen mutation

A screen mutation can only break agreement through a refused finding, so a shape with no refused context has nothing to break:

- `conditional-expression/conditional_resolved_branches`: unconfirmed in every context, and recorded unobservable in all six (P2.2).
- `constraint-predicate/non_numerical_predicate`: excluded or admitted where decided; the generator builds and the constraint is omitted from execution.
- `string-value-omission/string_value`: omitted; the seams in the stored answers carry its evidence (design D9).

## Limits of the method

- **Firing is seen per line.** `mutate.recording_fired` records line events on the site's own statement, in the owning function's code only. It refuses a statement that shares its first line with an enclosing one (`if x: raise E`), because the event cannot tell the test from the raise. No target site has that form today.
- **A case that never runs a site cannot change under its mutation**, because the recompiled function differs from the original only at that statement. So each mutation runs only the cases that fire the site. That is exact for the flip sets, but it does not test the claim. A mutation with side effects outside the statement would break it, and none of these rewrites has any.
- **Judgment is by outcome and site reasons.** Stub causes join it when the harness observes them (P4). Two families share one relayed reason: `_indexed_refusal` and `reference_use.py:702` both relay `evidence_indexed_reference_unsupported`. That does not hide `_indexed_refusal`'s mutation, because its 5 witnesses build or refuse differently once it is off.
- **Hand patches.** The three usage-level profile sites are replaced by `return _unassessed(usage, form)`, the decision the function returns for a usage it does not assess. `_indexed_refusal` is disabled at both callers' raises (`require_exact_use`, `_acquire`). The private names involved are in `mutate.PATCHED_NAMES`, and `test_mutator.py` resolves each one.
