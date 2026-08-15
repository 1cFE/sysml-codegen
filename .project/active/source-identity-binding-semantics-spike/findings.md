# Spike: Binding Semantics and Authoring-Form Referents (SOURCE-IDENTITY Item 1)

**Date started**: 2026-08-05
**Branch**: `nested-override-tripwire` @ `fa9e0d0`
**Upstream artifact**: `.project/backlog/epic_semantic_source_identity.md`, Item 1
**Invoked as**: `/_my_spike` (probes + findings + table; the epic's spec/design/plan
deliverables for this item were consciously skipped in favor of the spike shape —
noted here so the Item-3 reader knows why those files are absent)

## Summary of Findings

**Verdict: confirmed.** Every named authoring form now has a repeatable licensed
probe with retained raw referent evidence, reconciled against primary normative
text. No fix is designed here. The decision-input table is
`authoring-form-table.md`; raw evidence is in `probes/raw/` and `standards/`.

What the evidence establishes:

1. **The bare self-named form (`in R = R;`) is a degenerate self-binding by
   normative requirement, not a SysIDE quirk.** KerML nearest-scope resolution
   must reach the calc's own parameter first, and neither spec provides any
   mechanism by which the bare form reaches the outer attribute. It is legal,
   silent (no diagnostic required), and asserts the tautology `R == R`. The
   control probe (param renamed `r_in`, same bare RHS) resolves to the outer
   attribute — the param/attribute name collision is the entire cause.
2. **The two spec-correct replacements denote different elements.** An
   owner-qualified name (`'Probe Plant'::R`) resolves to the definition-level
   attribute; a feature chain (`plant.R`) resolves to the redefining feature at
   the concrete occurrence (the `:>> R = 12.7` site). The standards supply both
   and never adjudicate which is THE idiom for "the enclosing part's attribute";
   there is no `self`/`this` rooting. The Item-3 disposition must pick which
   correct form carries the intended occurrence semantics — the spec won't.
3. **The `#(i)` indexed form parses cleanly but carries value semantics only.**
   Its chain target is the def-level attribute; the occurrence index is not part
   of any feature identity. The `[i]` spelling is not indexing at all (undefined
   bracket operator, used by quantity/unit notation) and fails to load with 4
   errors. Neither indexed spelling exists anywhere in any corpus today.
4. **New identity-loss site found in the extractor (comparison column):** for
   `plants#(1).R` the current `_parse_chain_expression` silently drops the
   IndexExpression segment and records `source_path='R'`. Not named in either
   forensic report; belongs in Item 2's route matrix.
5. **SysIDE exposes the occurrence→definition bridge directly**: the `:>> R`
   node's `owned_redefinitions` yields a `Redefinition` edge with
   `.redefined_feature` (def attribute) and `.redefining_feature` (override
   site). Relevant to Item 2's evidence-sufficiency question.
6. **Prevalence**: bare self-named is the dominant authored form (~47% of usage
   bindings in both external corpora; 91 more in fixtures). The qualified form
   has zero external use. Rejecting the bare form is a real migration
   (~124 external + 91 fixture bindings); rejecting the indexed forms is free.

Ancillary fact worth keeping: SysIDE loudly rejects overriding a `=`-fixed value
(`feature-value-overriding` error) — `default` is what makes `:>>` overrides
legal. The customer shape depends on `default`/bare declarations.

## Question / Goal

Establish what each relevant SysML binding authoring form denotes and what SysIDE
actually reports, without designing a repair. The four forms under test, per the epic:

1. **Bare self-named**: `in R = R;` (calc param shadows the outer attribute?)
2. **Owner-qualified**: `in R = Plant::R;` (qualified name to the def attribute)
3. **Feature-chain**: `in R = plant.R;` (dotted path through a sibling part usage)
4. **Bracketed occurrence-index**: `in R = plants[1].R;` (and the `#(1)` spelling) —
   whether it parses at all is itself a probe outcome.

Confirmed if: every form has a repeatable licensed probe with retained raw referent
evidence (written form, SysIDE AST node type, resolved referent QN, owning namespace,
diagnostics), reconciled against KerML/SysML normative scoping rules, with corpus
prevalence per form. Disproved/blocked if: SysIDE referents cannot be observed
independently of the sysml-codegen extractor, or a form cannot be authored in a way
SysIDE will load.

Constraints from the epic (Out of Scope): no production code changes, no fixture-corpus
changes, no support-policy decision (Item 3 owns dispositions), no fix design.

## Log

Living record; commands and observations appended as they happen.

### 2026-08-05: setup

- Home folder created per the epic's designated location.
- Required reading done: both forensic reports, `test_self_named_binding_trap.py` +
  fixture, epic Item 1.
- Pinned what "bracketed occurrence-index" means in this codebase: `[i]` occurrence
  brackets on multi-occurrence `part_def` owner paths
  (`src/sysml_codegen/analysis/dependency_backtracker.py:540-543`,
  `constraint_lowering.py:116-126`). The authoring-form probe therefore tests the
  modeler-written indexed reference spellings.
- Probe strategy: load each fixture with `SysideAdapter.load_model` (returns
  `(model, diagnostics)` from `syside.try_load_model`) and read binding RHS
  expressions directly off SysIDE AST nodes (`feature_value_expression`, `referent`,
  `target_feature`, `operands`, CST byte spans) — NOT through
  `sysml_codegen.extraction`, so no field is inferred from the implementation under
  test. The extractor's view is recorded separately as a comparison column.

### 2026-08-05: probe run 1 (fixture defect found and fixed)

- Authored 6 probe models in `probes/models/` (4 forms + `#(i)`/`[i]` spellings split
  into two files + a renamed-param control), 2 consumers each, `:>> R = 12.7` at a
  concrete occurrence where expressible.
- Run 1 (`uv run python probes/probe_referents.py` with license env) surfaced a
  fixture defect of the spike's own making: declaring `attribute R : Real = 3.0;`
  (fixed `=`) makes the occurrence `:>> R = 12.7` illegal —
  `error (feature-value-overriding): Cannot override a binding feature value`.
  The customer shape declares the attribute bare or with `default`. Fixed all four
  affected fixtures to `default 3.0`. (Side observation kept: SysIDE **does** reject
  overriding a `=`-fixed value, loudly.)
- Also fixed two probe-script defects: `extract_calculation_usages` returns
  `(list, report)`; and a shorthand `:>> R = 12.7` parses as a **ReferenceUsage**,
  not AttributeUsage, so the occurrence-evidence sweep must cover both types.

### 2026-08-05: probe run 2 (clean; all referents recorded)

All six models: 0 hard failures; only `form_bracket_sq` has load errors (by design —
that is the finding). Raw JSON retained in `probes/raw/`. SysIDE-level referents:

| model | written RHS | node | SysIDE referent | diagnostics |
|---|---|---|---|---|
| form_bare | `R` | FeatureReferenceExpression | **calc's own param** `…::c1::R` (ReferenceUsage) | none — silent |
| form_control_renamed | `R` (param `r_in`) | FeatureReferenceExpression | outer `'Probe Plant'::R` (AttributeUsage) | none |
| form_owner_qualified | `'Probe Plant'::R` | FeatureReferenceExpression | def-level `'Probe Plant'::R` (AttributeUsage) | none |
| form_chain | `plant.R` | FeatureChainExpression | target = `Design Ctx::plant::R` — the **redefining feature at the part usage** (the `:>> R = 12.7` site), operand referent = the `plant` usage | none |
| form_bracket_sq | `plants[1].R` | FeatureChainExpression (broken) | target = `<placeholder Feature>` | **4 errors**: `quantity-operator-expression` ×2 + `No Feature named 'R'` ×2 — `[i]` is the quantity bracket, not an index |
| form_bracket_hash | `plants#(1).R` | FeatureChainExpression | operand = IndexExpression(`plants`, LiteralInteger i); target = **def-level** `'Probe Plant'::R` — the index is NOT part of the target identity | none |

Key observations beyond the table:

- **Shadowing is the entire cause of the bare-form degeneracy**: the control (param
  renamed `r_in`, same bare RHS `R`) resolves to the outer attribute.
- **Owner-qualified and `#(i)`-indexed forms resolve to the def-level attribute**,
  not an occurrence-distinct feature. Occurrence identity is not in the referent for
  those forms; it lives only in the expression structure (the IndexExpression) or in
  downstream occurrence evidence.
- **The feature-chain form is the only one whose referent is occurrence-relative**:
  `plant.R` targets the redefining `:>> R` ReferenceUsage under the part usage — a
  distinct element from `'Probe Plant'::R`, carrying the `12.7`.
- **NEW identity-loss site (implementation comparison column)**: for
  `plants#(1).R` the sysml-codegen extractor records `BindingType.CHAIN` with
  `source_path='R'` — the IndexExpression operand is dropped by
  `_parse_chain_expression` (its first operand is not a FeatureReferenceExpression,
  so the root segment is silently omitted). Not named in either forensic report.
- For the square-bracket file the extractor records `source_path='<placeholder
  Feature>'` — but `load_models()` returns False on errors, so the pipeline
  fail-closes before that garbage propagates (verified only to the extractor
  boundary here).
- The `:>> R = 12.7` occurrence override is visible as
  `design_ctx::plant::R (ReferenceUsage) = 12.7`; the redefinition **link** did not
  surface via `redefined_features`/`redefinitions` attribute names — follow-up
  micro-probe below.

### 2026-08-05: redefinition-link micro-probe (`probe_redef_link.py`)

The `:>> R = 12.7` shorthand node (`ReferenceUsage` at `Design Ctx::plant::R`)
**does** expose the occurrence→definition link directly on the SysIDE AST:
`owned_redefinitions` yields a `Redefinition` relationship with
`.redefined_feature = 'Probe Plant'::R` (the def attribute) and
`.redefining_feature = plant::R` (the override site). Also surfaced via
`owned_specializations`/`owned_subsettings` (Redefinition is a subtype). Raw:
`probes/raw/redef_link.txt`. Relevant to Item 2's evidence-sufficiency question:
the chain-form referent plus this edge recovers both the concrete occurrence and
the intended declaration without name matching.

### 2026-08-05: standards analysis (two expert readings, retained verbatim)

- kerml-expert and sysml-expert subagents (Opus) were each given the probe models
  plus the observed referents ("observation to reconcile, not truth") and asked
  for clause-cited verdicts per form. Full reports: `standards/kerml_ruling.md`,
  `standards/sysml_ruling.md`. Condensed into the table's standards section.
- Both reconcile all six observations with normative text; no observation
  contradicts the spec. Residual ambiguities are named per form in the table
  (visibility default for form 2; result-parameter/nested-redefinition wording for
  form 3; `#` over composite part usages for form 4a).

### 2026-08-05: corpus prevalence scan (`scan_corpus.py`, no license needed)

Textual scan of every `in <param> = <rhs>;` usage binding (typed calc-def parameter
defaults `in x : T = v;` counted separately and excluded). First run swept `.venv`
vendored stdlib and `archive/` trees in the external repos — restricted to live
authored trees (`tests/fixtures`, `fusion-tea/models`, `stellarator-demo/models`).
Raw with per-bucket file:line examples: `probes/raw/corpus_scan.json`.

| bucket | codegen fixtures (329) | fusion-tea models (32) | stellarator-demo models (236) |
|---|---|---|---|
| bare self-named | 91 | 15 | 109 |
| bare renamed | 45 | 2 | 56 |
| feature chain | 85 | 13 | 64 |
| qualified (`::`) | 85 | 0 | 0 |
| literal | 16 | 2 | 7 |
| expression | 7 | 0 | 1 |
| `#(i)` indexed | **0** | **0** | **0** |
| `[i]` bracketed | **0** | **0** | **0** |

Prevalence conclusions:

- **Bare self-named is the dominant authored form in both external corpora**
  (~47% of usage bindings in each). Rejecting it means touching ~124 bindings in
  live external models plus 91 in fixtures.
- **The qualified form appears only in the in-repo fixture corpus** (85, mostly
  catf_mfe). Neither customer-facing corpus uses the "spec-correct" spelling even
  once.
- **No indexed/bracketed occurrence reference exists anywhere today.** Rejecting or
  deferring that form has zero migration cost.

## Reproduction

From the repo root, with the syside license env loaded (the license only loads via
script/pytest entry, not bare `python -c` — see memory note):

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run python .project/active/source-identity-binding-semantics-spike/probes/probe_referents.py
```

Fixture models live in `probes/models/` (one file per form, loaded separately so a
parse failure in one form cannot poison another). Raw output is retained in
`probes/raw/`.

## Open Questions / Follow-ups

Handed to Item 2 (route/evidence spike) and Item 3 (owner disposition):

- **Occurrence recovery for def-level referents** (forms 2 and 4a): the referent
  alone does not name a concrete occurrence. Whether written reference +
  occurrence-owner evidence suffices, or extraction must emit an explicit semantic
  source ID, is exactly Item 2's evidence-sufficiency experiment. The
  `owned_redefinitions` edge found here is an input to that experiment.
- **The `#(i)` index-drop in `_parse_chain_expression`** (`source_path='R'`) is a
  route-matrix cell for Item 2. No corpus instance exists today, so it gates
  nothing, but any future support decision must know the extractor currently
  destroys the index silently.
- **Which correct form is the project idiom** — qualified (def-level general
  feature) vs chain (occurrence-scoped redefining feature) — is an Item-3 owner
  decision the standards do not make.
- Constraint and aggregation consumers of these same forms were deliberately not
  probed (Item 2 owns the route matrix; this spike is referent-only).
- The corpus scan is single-line-regex based; multi-line binding expressions would
  be missed (none observed in spot checks).
